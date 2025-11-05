import os
import sys
import django
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup, NavigableString
from asgiref.sync import sync_to_async

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from scraping.logging_config import logger
from scraping.instagram_feed import insert_event_to_db, append_event_to_csv
from services.openai_service import extract_events_from_caption

next_page_element = 'a.pager__link--next'
base_url = "https://uwaterloo.ca/theatres/events"
unique_links = set()

async def collect_unique_event_links():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        page = await browser.new_page()
        await page.goto(base_url, timeout=30000)
        await page.wait_for_load_state("networkidle", timeout=30000)
        
        page_num = 1
        while True:
            try:
                page_text_lines = []
                content = await page.content()
                soup = BeautifulSoup(content, 'lxml')
                for element in soup.descendants:
                    if element.name == 'a' and element.has_attr('href'):
                        text = element.get_text(strip=True)
                        if text:
                            line = f"LINK: {text}  -> {element['href']}"
                            page_text_lines.append(line)
                    elif isinstance(element, NavigableString) and element.parent.name not in ['script', 'style']:
                        text = element.strip()
                        if text and element.parent.name != 'a':
                            line = ' '.join(text.split())
                            page_text_lines.append(line)
                page_context = "\n".join(page_text_lines)
                # Use OpenAI to extract event links
                from services.openai_service import OpenAIService
                openai_service = OpenAIService()
                urls = openai_service.extract_event_links_from_website(page_context, base_url=base_url)
                if urls:
                    unique_links.update(urls)
                # Handle next page: stop if there's no next button
                locator = page.locator(next_page_element)
                cnt = await locator.count()
                if cnt == 0:
                    break
                await locator.first.click()
                try:
                    await page.wait_for_load_state("networkidle", timeout=30000)
                except Exception:
                    break
                page_num += 1
            except Exception as e:
                logger.error(f"Error during pagination: {e}")
                break
        await browser.close()
    return unique_links

async def scrape_event_details(page, url):
    """Visit an event link, extract page text, and add event to DB."""
    try:
        await page.goto(url, timeout=30000)
        await page.wait_for_load_state("networkidle", timeout=30000)
        content = await page.content()
        soup = BeautifulSoup(content, 'lxml')
        page_text_lines = []
        for element in soup.descendants:
            if element.name == 'a' and element.has_attr('href'):
                text = element.get_text(strip=True)
                if text:
                    page_text_lines.append(f"LINK: {text}  -> {element['href']}")
            elif isinstance(element, NavigableString) and element.parent.name not in ['script', 'style']:
                text = element.strip()
                if text and element.parent.name != 'a':
                    page_text_lines.append(' '.join(text.split()))
        page_context = "\n".join(page_text_lines)
        events_data = extract_events_from_caption(page_context, source_image_url=None)
        if not events_data:
            logger.info(f"No events extracted from {url}")
            return
        for event_data in events_data:
            event_data["source_url"] = url
            # Remove id if present
            if "id" in event_data:
                del event_data["id"]

            # --- Ensure required fields for Events model ---
            # Ensure categories is always a non-empty list
            categories = event_data.get("categories")
            if not categories or not isinstance(categories, list) or not categories:
                event_data["categories"] = ["Uncategorized"]
            else:
                event_data["categories"] = categories

            club_type = event_data.get("club_type")
            if club_type is None:
                club_type = ""
            event_data["club_type"] = club_type

            if not event_data.get("title"):
                event_data["title"] = "Untitled Event"
            if not event_data.get("location"):
                event_data["location"] = ""
            if not event_data.get("description"):
                event_data["description"] = ""

            if not event_data.get("dtstart"):
                logger.warning(f"Missing dtstart for event at {url}, skipping.")
                # Still log to CSV as skipped
                await sync_to_async(append_event_to_csv)(
                    event_data, ig_handle="", source_url=url, added_to_db="skipped"
                )
                continue

            added_status = "unknown"
            try:
                result = await sync_to_async(insert_event_to_db)(
                    event_data, ig_handle="", source_url=url
                )
                added_status = "success" if result else "failed"
                logger.info(f"Added event: {event_data.get('title')} ({added_status})")
            except Exception as e:
                logger.error(f"Failed to insert event for {url}: {e}")
                added_status = "error"
            finally:
                await sync_to_async(append_event_to_csv)(
                    event_data, ig_handle="", source_url=url, added_to_db=added_status
                )
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")

async def main():
    # Step 1: Collect unique event links
    links = await collect_unique_event_links()
    logger.info(f"Collected {len(links)} unique event links.")
    # Step 2: Scrape each event link for details and add to DB
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        page = await browser.new_page()
        for url in sorted(links):
            logger.info(f"\n--- Scraping event: {url} ---")
            await scrape_event_details(page, url)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())