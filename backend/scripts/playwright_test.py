# python scripts/playwright_test.py
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup, NavigableString


[{
next_page_element = 'a.pager__link--next'
base_url = "https://uwaterloo.ca/theatres/events"
}, 
{
next_page_element = 'a.pager__link--next'
base_url = "https://uwaterloo.ca/theatres/events"
},
{
next_page_element = 'a.pager__link--next'
base_url = "https://uwaterloo.ca/theatres/events"
},
{
next_page_element = 'a.pager__link--next'
base_url = "https://uwaterloo.ca/theatres/events"
}]


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        page = await browser.new_page()
        await page.goto(base_url, timeout=30000)
        await page.wait_for_load_state("networkidle", timeout=30000)
        
        page_num = 1
        while True:
            try:
                content = await page.content()
                condensed = ''.join(content.split())
                print(f"=== PAGE {page_num} HTML ===")

                soup = BeautifulSoup(content, 'lxml')
                for element in soup.descendants:
                    if element.name == 'a' and element.has_attr('href'):
                        text = element.get_text(strip=True)
                        if text:
                            print(f"LINK: {text}  -> {element['href']}")

                    elif isinstance(element, NavigableString) and element.parent.name not in ['script', 'style']:
                        text = element.strip()
                        if text and element.parent.name != 'a':
                            print(f"{' '.join(text.split())}")

                print(f"=== END PAGE {page_num} ===\n")
                await page.click(next_page_element)
                await page.wait_for_load_state("networkidle", timeout=30000)
                page_num += 1
            except:
                break
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
