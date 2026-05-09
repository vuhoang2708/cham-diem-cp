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
            
            # Close dialogs if any
            dialog_close = page.locator(".bp5-dialog-close-button")
            if await dialog_close.count() > 0:
                await dialog_close.first.click()
                await page.wait_for_timeout(1000)
            
            # Ensure we are on Chart tab
            chart_tab = page.locator("text=Biểu đồ").first
            if await chart_tab.is_visible():
                await chart_tab.click(force=True)
                await page.wait_for_timeout(2000)

            # Locate MCDX legend value
            # Based on user description, it's "Banker Smart Money" in a legend
            # We look for text that contains 'Banker' and extract the following number
            
            # This part is tricky as Fireant uses canvas. We hope there's a legend text element.
            # Usually indicators have legends like "FA MCDX (..., ..., ...)"
            # We search for elements containing "Banker" or "FA MCDX"
            
            # Strategy: Find all text elements and look for the pattern
            # Or use a specific selector if known.
            
            # Let's try to find elements with "Banker" text
            banker_elements = page.locator("text=Banker")
            count = await banker_elements.count()
            
            banker_value = 0.0
            
            # If we find "Banker Smart Money", the value might be in a sibling or nearby element
            # Many charts show legend values in a 'legend-value' class or similar
            
            # For now, we'll try a common pattern for Fireant/TradingView:
            # Look for "Banker Smart Money" and then the numeric value next to it.
            
            # If direct extraction fails, we might need a more specific selector
            # derived from inspecting the live DOM.
            
            # Placeholder: In a real scenario, we'd use page.evaluate to find the exact DOM node
            # containing the MCDX values.
            
            val_text = await page.evaluate('''() => {
                const elements = Array.from(document.querySelectorAll('div, span'));
                // Look for MCDX legend
                const mcdxLegend = elements.find(el => el.innerText.includes('Banker Smart Money'));
                if (mcdxLegend) {
                    // Try to find the value which is usually a number after the label
                    // The value might be in a child span or just trailing text
                    return mcdxLegend.innerText;
                }
                return null;
            }''')
            
            if val_text:
                print(f"Found legend text: {val_text}")
                # Parse number from "Banker Smart Money: 15.5" or similar
                import re
                match = re.search(r'Banker Smart Money[:\s]*([\d\.]+)', val_text)
                if match:
                    banker_value = float(match.group(1))
            else:
                # Fallback: search for generic legend values if "Banker" not found
                print(f"Could not find 'Banker Smart Money' text for {symbol}")
            
            return {
                'banker_value': banker_value,
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
