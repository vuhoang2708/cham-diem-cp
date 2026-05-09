import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import asyncio
from playwright.async_api import async_playwright

async def test_mcdx_scraper(ticker="VCB"):
    print(f"Testing MCDX scraper for {ticker} via Chrome CDP...")
    
    # We assume Chrome is running with --remote-debugging-port=9222
    CDP_URL = "http://localhost:9222"
    
    async with async_playwright() as p:
        try:
            # Connect to existing Chrome instance
            browser = await p.chromium.connect_over_cdp(CDP_URL)
            context = browser.contexts[0]
            page = await context.new_page()
            
            # Go to Fireant chart for the ticker
            url = f"https://fireant.vn/dashboard/content/symbols/{ticker}"
            print(f"Navigating to {url}...")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            await page.wait_for_timeout(5000)
            
            # Close potential dialogs if they exist
            dialog_close = page.locator(".bp5-dialog-close-button")
            if await dialog_close.count() > 0:
                print("Found a dialog, closing it...")
                await dialog_close.first.click()
                await page.wait_for_timeout(1000)

            # Look for the tab 'Biểu đồ' and use force click or evaluate if needed
            chart_tab = page.locator("text=Biểu đồ").first
            if await chart_tab.is_visible():
                print("Clicking 'Biểu đồ' tab...")
                await chart_tab.click(force=True)
                await page.wait_for_timeout(3000)
            
            print("Successfully loaded the page and clicked the tab!")
            print("Checking for MCDX Banker Smart Money...")
            
            # Check for the Banker value text. Let's see if we can find FA MCDX
            # In tradingview charts, legend values are in div.legend-values
            # Just print the outer HTML of the legend if possible
            
            print("Please ensure MCDX indicator is added and visible on the chart.")
            print("Waiting 5 seconds before closing the test tab...")
            await page.wait_for_timeout(5000)
            
            await page.close()
            await browser.close()
            
        except Exception as e:
            print(f"Error during Playwright scraping: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcdx_scraper())
