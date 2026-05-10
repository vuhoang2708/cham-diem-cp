import asyncio
import re
from playwright.async_api import async_playwright
import sys
import io

# Fix encoding for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class MCDXScraper:
    def __init__(self):
        self.cdp_url = "http://localhost:9222"
        self.browser = None
        self.context = None
        self.page = None  # Dùng 1 tab duy nhất cho toàn bộ quá trình
        
    async def connect(self):
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.connect_over_cdp(self.cdp_url)
            self.context = self.browser.contexts[0]
            # Lấy tab đầu tiên đang mở, KHÔNG tạo tab mới
            if self.context.pages:
                self.page = self.context.pages[0]
                print(f"Đã kết nối Chrome CDP, dùng tab hiện có: {self.page.url[:60]}")
            else:
                self.page = await self.context.new_page()
                print("Đã kết nối Chrome CDP, tạo tab mới (không có tab nào mở sẵn).")
            return True
        except Exception as e:
            print(f"Failed to connect to Chrome: {e}")
            return False

    async def disconnect(self):
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

    def calculate_mcdx_score(self, value):
        """
        Linear interpolation for MCDX score.
        0->0, 3->0.2, 8->0.4, 12->0.6, 16->0.8, 20->1.0
        """
        breakpoints = [(0, 0.0), (3, 0.2), (8, 0.4), (12, 0.6), (16, 0.8), (20, 1.0)]
        
        if value <= 0: return 0.0
        if value >= 20: return 1.0
        
        for i in range(len(breakpoints) - 1):
            x0, y0 = breakpoints[i]
            x1, y1 = breakpoints[i+1]
            if x0 <= value <= x1:
                return round(y0 + (y1 - y0) * (value - x0) / (x1 - x0), 2)
        return 0.0

    async def get_banker_value(self, symbol):
        """
        Điều hướng đến Fireant trên TAB HIỆN TẠI và trích xuất giá trị Banker Smart Money.
        Quy trình: Vào trang CP -> Click Biểu đồ -> Click f(x) -> Gõ MCDX -> Chọn chỉ báo
                    -> Hover lên biểu đồ -> Đọc tooltip Banker Smart Money.
        """
        if not self.page:
            return None
            
        page = self.page  # Dùng tab hiện có, KHÔNG mở tab mới
        
        try:
            # 1. Điều hướng đến trang mã CP trên chính tab hiện tại
            url = f"https://fireant.vn/dashboard/content/symbols/{symbol}"
            print(f"[{symbol}] Đang mở trang {url}...")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000)
            
            # 2. Click đúng tab "Biểu đồ" TRONG dialog (không phải menu trên cùng)
            print(f"[{symbol}] Đang tìm tab Biểu đồ trong dialog...")
            try:
                # Tìm tất cả phần tử chứa text "Biểu đồ" và click phần tử trong dialog
                # Dialog nằm trong div có class chứa "dialog" hoặc "modal" hoặc "symbols"
                dialog_tab = page.locator('.bp5-tab:has-text("Biểu đồ"), [role="tab"]:has-text("Biểu đồ")').first
                await dialog_tab.wait_for(state="visible", timeout=10000)
                await dialog_tab.click(force=True)
                print(f"[{symbol}] Đã nhấn tab Biểu đồ trong dialog.")
            except:
                # Fallback: click bằng evaluate để tìm chính xác
                try:
                    await page.evaluate('''() => {
                        const tabs = Array.from(document.querySelectorAll('div, a, span'));
                        const bieuDoTab = tabs.find(el => {
                            const t = (el.innerText || '').trim();
                            return t === 'Biểu đồ' && el.closest('[class*="dialog"], [class*="overlay"], [class*="symbol"]');
                        });
                        if (bieuDoTab) bieuDoTab.click();
                    }''')
                    print(f"[{symbol}] Đã click Biểu đồ bằng JS evaluate.")
                except:
                    print(f"[{symbol}] Không tìm thấy tab Biểu đồ trong dialog.")
            
            # Đợi lâu hơn để TradingView iframe load hoàn toàn
            await page.wait_for_timeout(5000)
            
            # 3. Tìm iframe biểu đồ TradingView
            chart_frame = None
            for frame in page.frames:
                try:
                    count = await frame.locator("text=Các chỉ báo").count()
                    if count > 0:
                        chart_frame = frame
                        break
                except:
                    continue
            
            target = chart_frame if chart_frame else page
            print(f"[{symbol}] Dùng {'iframe' if chart_frame else 'page chính'} để thao tác.")

            # 4. Click nút "Các chỉ báo" f(x) và thêm MCDX
            print(f"[{symbol}] Đang mở menu f(x)...")
            try:
                indicators_btn = target.locator("div.js-button-text:text('Các chỉ báo')").first
                await indicators_btn.click(force=True, timeout=10000)
                print(f"[{symbol}] Đã click nút Các chỉ báo.")
                await page.wait_for_timeout(1500)
                
                # Gõ MCDX vào ô tìm kiếm
                print(f"[{symbol}] Đang gõ MCDX...")
                search_input = target.locator("input[placeholder*='Tìm kiếm'], input[placeholder*='Search'], input[type='text']").first
                await search_input.wait_for(state="visible", timeout=5000)
                await search_input.click()
                await search_input.fill("")
                await search_input.type("MCDX", delay=100)
                await page.wait_for_timeout(2000)
                
                # Chọn chỉ báo "FireAnt - MCDX" - click vào dòng chứa text
                print(f"[{symbol}] Đang chọn FireAnt - MCDX...")
                await page.wait_for_timeout(2000)  # Đợi kết quả tìm kiếm hiện
                # Click trực tiếp vào text "MCDX" trong kết quả
                mcdx_result = target.locator("text=MCDX").first
                await mcdx_result.click(force=True, timeout=5000)
                print(f"[{symbol}] Đã click MCDX trong kết quả.")
                await page.wait_for_timeout(2000)
                
                # Đóng dialog bằng nút X (góc trên bên phải dialog)
                close_btn = target.locator('[data-name="close"], button:has-text("×"), [class*="close"]').first
                try:
                    await close_btn.click(force=True, timeout=3000)
                except:
                    # Fallback: nhấn ESC 2 lần
                    await page.keyboard.press("Escape")
                    await page.wait_for_timeout(500)
                    await page.keyboard.press("Escape")
                await page.wait_for_timeout(1000)
                print(f"[{symbol}] Đã đóng dialog chỉ báo.")
            except Exception as e:
                print(f"[{symbol}] Lưu ý f(x): {e}")
                # Đảm bảo đóng dialog nếu còn mở
                await page.keyboard.press("Escape")
                await page.wait_for_timeout(500)
                await page.keyboard.press("Escape")

            # 5. Đợi chỉ báo tính toán
            await page.wait_for_timeout(5000)
            
            # 6. Hover lên cây nến cuối cùng (điểm mới nhất) và đọc legend
            print(f"[{symbol}] Đang hover lên điểm mới nhất và đọc legend...")
            banker_value = 0.0
            
            # Hover vào vùng MCDX - nến cuối cùng (bên phải nhất)
            # Thử nhiều vị trí x từ phải qua trái để tìm nến cuối
            await page.mouse.move(1130, 600)  # Nến cuối cùng (hôm nay)
            await page.wait_for_timeout(2000)
            
            # Đọc legend text từ tất cả frames — legend chứa "FA MCDX" và các giá trị số
            for frame in page.frames:
                try:
                    legend_info = await frame.evaluate(r'''() => {
                        // Tìm div chứa text "FA MCDX" với giá trị số
                        const all = Array.from(document.querySelectorAll('div, span'));
                        let best = null;
                        let bestLen = 99999;
                        for (const el of all) {
                            const t = el.innerText || '';
                            // Legend line chứa "FA MCDX" và các số thập phân
                            if (t.includes('FA MCDX') && /\d+\.\d{4}/.test(t) && t.length < bestLen && t.length > 30) {
                                best = t;
                                bestLen = t.length;
                            }
                        }
                        return best;
                    }''')
                    if legend_info and 'FA MCDX' in legend_info:
                        print(f"[{symbol}] Legend raw: {repr(legend_info[:200])}")
                        # Tách legend theo ký hiệu ∅ (pi/null)
                        # Giá trị Banker đa phần nằm BÊN TRÁI ∅, nhưng có khi nằm BÊN PHẢI
                        # => Lưu CẢ 2 giá trị, tính điểm theo bên trái trước
                        parts = legend_info.split('∅')
                        if len(parts) >= 2:
                            left_part = parts[0]   # Phần bên trái ∅
                            right_part = parts[1]  # Phần bên phải ∅
                            
                            left_numbers = re.findall(r'-?[\d.]+', left_part)
                            right_numbers = re.findall(r'-?[\d.]+', right_part)
                            
                            banker_left = float(left_numbers[-1]) if left_numbers else 0.0
                            banker_right = float(right_numbers[0]) if right_numbers else 0.0
                            
                            print(f"[{symbol}] Bên trái ∅: {banker_left}")
                            print(f"[{symbol}] Bên phải ∅: {banker_right}")
                            
                            # Tính điểm: ưu tiên cột bên trái, nếu = 0 thì dùng bên phải làm backup
                            banker_value = banker_left if banker_left != 0.0 else banker_right
                            banker_backup = banker_right if banker_left != 0.0 else banker_left
                        else:
                            print(f"[{symbol}] Không tìm thấy ký hiệu ∅ trong legend!")
                            decimal_numbers = re.findall(r'\d+\.\d{4}', legend_info)
                            print(f"[{symbol}] Fallback values: {decimal_numbers}")
                            banker_backup = 0.0
                        break
                except:
                    continue
            
            # Chụp screenshot để verify
            await page.screenshot(path=f"debug_{symbol}.png")
            print(f"[{symbol}] Banker = {banker_value} (backup = {banker_backup})")
            
            return {
                'banker_value': round(banker_value, 4),
                'banker_backup': round(banker_backup, 4),
                'banker_left': round(banker_left if 'banker_left' in dir() else 0.0, 4),
                'banker_right': round(banker_right if 'banker_right' in dir() else 0.0, 4),
                'mcdx_score': self.calculate_mcdx_score(banker_value)
            }

        except Exception as e:
            print(f"Error scraping {symbol}: {e}")
            return None
        # KHÔNG đóng tab ở finally — vì ta dùng lại tab này cho mã tiếp theo

async def test():
    scraper = MCDXScraper()
    if await scraper.connect():
        for symbol in ["VIC"]:
            res = await scraper.get_banker_value(symbol)
            print(f"=== Result for {symbol}: {res} ===")
        await scraper.disconnect()

if __name__ == "__main__":
    asyncio.run(test())
