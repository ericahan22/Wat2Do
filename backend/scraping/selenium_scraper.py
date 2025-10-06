import random
import os
import sys
import traceback
import logging
import argparse
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from pathlib import Path
import zendriver
import asyncio

load_dotenv()


# ----- Django setup -----

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")
django.setup()


# ----- Project imports -----

from scraping.scraping_utils import (
    get_seen_shortcodes,
    insert_event_to_db,
    append_event_to_csv,
    logger,
    MAX_POSTS,
    MAX_CONSEC_OLD_POSTS,
    CUTOFF_DAYS,
    LOG_DIR
)
from services.openai_service import extract_events_from_caption, generate_embedding
from services.storage_service import upload_image_from_url

logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('openai').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger("zendriver").setLevel(logging.WARNING)
logging.getLogger("uc.connection").setLevel(logging.WARNING)
logging.getLogger("websockets.client").setLevel(logging.WARNING)

IG_USERNAME = "xmdkjgjsjfj" # os.getenv("USERNAME")
IG_PASSWORD = os.getenv("PASSWORD")


# ----- Selenium setup -----

def get_driver():
    """Initializes Zendriver Chrome WebDriver"""
    chrome_options = [
        "--user-data-dir=" + str(Path(__file__).resolve().parent / "chrome_profile"),
        # "--headless=new",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        "--disable-blink-features=AutomationControlled"
    ]
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    return zendriver.start(options=chrome_options, prefs=prefs)


# ----- Helper functions -----
        
async def dismiss_popups(page):
    popups = [
        "Not Now",
        "Not now",
        "Allow all cookies",
        "Allow essential cookies only",
        "Accept All",
        "OK"
    ]
    for text in popups:
        try:
            button = await page.find(text, best_match=True)
            if button:
                print(f"Found popup button: {button.text_all}")
                await button.click()
                print(f"Clicked '{text}' button to dismiss popup.")
                await page.wait(0.5)
        except Exception:
            pass
        await asyncio.sleep(1)
        
        
async def login(page):
    logger.info("Checking Instagram login status...")
    await asyncio.sleep(3)
    logger.info("Logging in...")
    username_field = await page.query_selector('input[name="username"]')
    password_field = await page.query_selector('input[name="password"]')
    await username_field.send_keys(IG_USERNAME)
    await asyncio.sleep(1)
    await password_field.send_keys(IG_PASSWORD)
    await asyncio.sleep(1)

    login_button = await page.query_selector('button[type="submit"]')
    await login_button.click()
    await asyncio.sleep(10)
    
    await dismiss_popups(page)
    
    # load homepage
    new_post_icon = await page.query_selector('svg[aria-label="New post"]')
    if new_post_icon:
        logger.info(f"Login successful, home page loaded!")
        await page.save_screenshot(f"{LOG_DIR}/login_success.png")
        return True
    else:
        logger.error("Login failed or challenge encountered")
        await page.save_screenshot(f"{LOG_DIR}/login_error.png")
        return False
    
    
async def extract_post_data(article):
    caption = ""
    raw_image_url = None

    # Extract caption
    caption_el = await article.query_selector("span")
    if caption_el:
        caption = await caption_el.inner_text()
        
    # Extract image
    image_el = await article.query_selector("img")
    if image_el:
        raw_image_url = image_el.get("src")
    else:
        video_el = await article.query_selector("video")
        if video_el:
            raw_image_url = video_el.get("poster") or video_el.get("src")

    return caption, raw_image_url


async def process_feed(page, scroll_limit=50):
    cutoff = datetime.now(timezone.utc) - timedelta(days=CUTOFF_DAYS)
    events_added = 0
    posts_processed = 0
    consec_old_posts = 0
    
    seen_shortcodes = get_seen_shortcodes()
    processed_in_session = set()
    
    for _ in range(20):
        posts = await page.query_selector_all('article')
        if posts:
            break
        await asyncio.sleep(1)
    if not posts:
        logger.error("Feed not loaded, no posts found")
        await page.save_screenshot(f"{LOG_DIR}/feed_not_loaded.png")
        return 0, 0

    logger.info("Feed loaded, starting feed processing...")
    for _ in range(scroll_limit):
        posts = await page.query_selector_all('article')
        logger.info(f"Found {len(posts)} posts in feed")
        if len(posts) == 0:
            html = await page.content()
            with open(f"{LOG_DIR}/debug_feed.html", "w", encoding="utf-8") as f:
                f.write(html)
            logger.warning("Saved HTML snapshot to debug_feed.html for inspection")
        for p in posts:
            try:
                link_element = await p.query_selector('a[href*="/p/"]')
                post_url = link_element.get('href')
                shortcode = post_url.split('/')[-2]
                if shortcode in seen_shortcodes or shortcode in processed_in_session:
                    continue
                processed_in_session.add(shortcode)

                time_element = await p.query_selector('time')
                post_time = datetime.fromisoformat(time_element.get("datetime").replace('Z', '+00:00'))
                if post_time < cutoff:
                    consec_old_posts += 1
                    logger.debug(f"Post {shortcode} is older than cutoff, consecutive old posts: {consec_old_posts}")
                    if consec_old_posts >= MAX_CONSEC_OLD_POSTS:
                        logger.info(f"Reached {MAX_CONSEC_OLD_POSTS} consecutive old posts, stopping...")
                        return events_added, posts_processed
                    continue
                consec_old_posts = 0
                posts_processed += 1
                logger.info("\n" + "-" * 80)
                
                # Extract data
                try:
                    username_el = await p.query_selector('a[href^="/"]')
                    username = await username_el.inner_text()
                except Exception:
                    username = "unknown"
                    
                logger.info(f"Processing post {shortcode} by {username}")
                
                caption, raw_image_url = await extract_post_data(p)
                
                # Process data
                if raw_image_url:
                    await asyncio.sleep(2)
                    image_url = upload_image_from_url(raw_image_url)
                    logger.info(f"Uploaded image to S3: {image_url}")
                else:
                    image_url = None
                
                logger.info(f"Sending caption to AI for processing")
                events_data = extract_events_from_caption(caption, image_url)
                logger.info(f"Type of events data: {type(events_data)} | value: {events_data}")
                if not events_data:
                    logger.warning(f"Post {shortcode} is not an event")
                    continue
                
                for data in events_data:
                    logger.info(f"Raw event data: {data}")
                    status = "unknown"
                    required_fields = ["name", "date", "location", "start_time"]
                    has_required_fields = all(data.get(key) for key in required_fields)
                    
                    if has_required_fields:
                        if insert_event_to_db(data, username, post_url, image_url):
                            events_added += 1
                            status = "success"
                            logger.info(f"Successfully added event '{data.get('name')}'")
                        else:
                            status = "failed"
                            logger.error(f"Failed to insert event '{data.get('name')}'")
                    else:
                        missing_fields = [key for key in required_fields if not data.get(key)]
                        status = "missing_fields"
                        logger.warning(f"Missing {missing_fields} for event, skipping...") 
                    embedding = generate_embedding(data.get("description", ""))
                    append_event_to_csv(data, username, post_url, status=status, embedding=embedding)
                
                await asyncio.sleep(random.uniform(15, 45))
                
                if posts_processed >= MAX_POSTS:
                    logger.info(f"Reached max post limit of {MAX_POSTS}, stopping...")
                    return events_added, posts_processed
            except Exception as e:
                logger.error(f"Error processing post: {e}")
                logger.error(traceback.format_exc())
                continue
        logger.info("Scrolling... loading more posts...")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        await asyncio.sleep(random.uniform(5, 15))
        
    return events_added, posts_processed


async def main():
    parser = argparse.ArgumentParser(description="Scrape feed with Selenium")
    parser.add_argument(
        "--scroll-limit",
        type=int,
        default=50,
        help="Set max number of times to scroll the home feed"
    )
    args = parser.parse_args()
    
    browser = await get_driver()
    page = await browser.get('https://www.instagram.com/')
    if await login(page):
        await page.save_screenshot(f"{LOG_DIR}/post_login.png")       
        events_added, posts_processed = await process_feed(page, scroll_limit=args.scroll_limit)
        logger.info("\n----------------------- SUMMARY -----------------------")
        logger.info(f"Processed {posts_processed} posts, added {events_added} events :D")
    else:
        logger.critical("Could not log in :( aborting...")
    await browser.stop()
    
    
if __name__ == "__main__":
    asyncio.run(main())
    