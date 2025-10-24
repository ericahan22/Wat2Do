# python scripts/playwright_test.py
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup, NavigableString
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.openai_service import OpenAIService
openai_service = OpenAIService()


next_page_element = 'a.pager__link--next'
base_url = "https://uwaterloo.ca/theatres/events"
unique_links = set()


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
                page_text_lines: list[str] = []
                content = await page.content()
                print(f"=== PAGE {page_num} HTML ===")

                soup = BeautifulSoup(content, 'lxml')
                for element in soup.descendants:
                    if element.name == 'a' and element.has_attr('href'):
                        text = element.get_text(strip=True)
                        if text:
                            line = f"LINK: {text}  -> {element['href']}"
                            print(line)
                            page_text_lines.append(line)

                    elif isinstance(element, NavigableString) and element.parent.name not in ['script', 'style']:
                        text = element.strip()
                        if text and element.parent.name != 'a':
                            line = ' '.join(text.split())
                            print(line)
                            page_text_lines.append(line)

                print(f"Collected {len(page_text_lines)} context lines for page {page_num}")

                try:
                    page_context = "\n".join(page_text_lines)
                    urls = openai_service.extract_event_links_from_website(page_context, base_url=base_url)
                    if urls:
                        print(f"FOUND CANDIDATE EVENT LINKS (page {page_num}):")
                        for url in sorted(urls):
                            print(f"  {url}")
                        unique_links.update(urls)
                    else:
                        print("AI extractor returned no links for this page.")
                except Exception as e:
                    print(f"AI extractor failed on page {page_num}: {e}")

                print(f"=== END PAGE {page_num} ===\n")

                # Handle next page: stop if there's no next button
                try:
                    locator = page.locator(next_page_element)
                    cnt = await locator.count()
                    if cnt == 0:
                        break
                    await locator.first.click()
                    try:
                        await page.wait_for_load_state("networkidle", timeout=30000)
                    except Exception:
                        print("Warning: wait_for_load_state timed out after clicking next; stopping pagination.")
                        break
                    page_num += 1
                except Exception as e:
                    print(f"Failed to navigate to next page (page {page_num}): {e}")
                    break
            except:
                break
        
        await browser.close()

        if unique_links:
            print("\n=== UNIQUE EVENT LINKS ===")
            for u in sorted(unique_links):
                print(u)

if __name__ == "__main__":
    asyncio.run(main())
