import asyncio
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
        
    async def connect(self):
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.connect_over_cdp(self.cdp_url)
            self.context = self.browser.contexts[0]
            print("Connected to Chrome via CDP")
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
                # y = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
                return round(y0 + (y1 - y0) * (value - x0) / (x1 - x0), 2)
        return 0.0

    async def get_banker_value(self, symbol):
        """
        Navigate to Fireant and extract Banker Smart Money value.
        """
        if not self.context:
            return None
            
        page = await self.context.new_page()
        try:
            url = f"https://fireant.vn/dashboard/content/symbols/{symbol}"
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000) # Wait for indicators to load
            
            # 1. Wait for Chart tab and click it
            chart_tab = page.locator("text=Biểu đồ").first
            if await chart_tab.is_visible():
                await chart_tab.click(force=True)
                await page.wait_for_timeout(5000) # Wait longer for indicators to compute

            # 2. Extract values from FA MCDX legend
            # Pattern: FA MCDX (input_params) Value1 Value2 Value3
            # Value1: Retailer (Green), Value2: Hot Money (Yellow), Value3: Banker (Red)
            
            val_text = await page.evaluate('''() => {
                const legends = Array.from(document.querySelectorAll('div[class*="legend"]'));
                const mcdxLegend = legends.find(el => el.innerText.includes('FA MCDX'));
                return mcdxLegend ? mcdxLegend.innerText : null;
            }''')
            
            banker_value = 0.0
            if val_text:
                print(f"Found MCDX legend: {val_text}")
                # Use regex to find all numbers (including decimals)
                import re
                # We skip the input parameters (usually in parentheses) and look for the values after
                # Example: "FA MCDX (50, 20, 1) 0.0000 6.3925 13.6075"
                
                # Split by closing parenthesis to isolate values
                parts = val_text.split(')')
                if len(parts) > 1:
                    values_part = parts[1]
                    numbers = re.findall(r'[\d\.]+', values_part)
                    if len(numbers) >= 3:
                        # Index 2 is the 3rd number (Banker)
                        banker_value = float(numbers[2])
                    elif len(numbers) > 0:
                        # Fallback: if fewer numbers, maybe only some are shown, take the last one
                        banker_value = float(numbers[-1])
            else:
                print(f"Could not find 'FA MCDX' legend for {symbol}")
            
            return {
                'banker_value': round(banker_value, 2),
                'mcdx_score': self.calculate_mcdx_score(banker_value)
            }

        except Exception as e:
            print(f"Error scraping {symbol}: {e}")
            return None
        finally:
            await page.close()

async def test():
    scraper = MCDXScraper()
    if await scraper.connect():
        res = await scraper.get_banker_value("VCB")
        print(f"Result for VCB: {res}")
        await scraper.disconnect()

if __name__ == "__main__":
    asyncio.run(test())
