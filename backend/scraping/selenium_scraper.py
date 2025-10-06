import random
import os
import sys
import traceback
import time
import logging
import argparse
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

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

USERNAME = os.getenv("INSTAGRAM_USERNAME")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")


# ----- Selenium setup -----

def get_driver():
    """Initializes Selenium WebDriver"""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    })
    user_data_dir = Path(__file__).resolve().parent / "chrome_profile"
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    # chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''
    })
    return driver


# ----- Helper functions -----
        
def typing(element, text):
    for char in text:
        element.send_keys(char)
        wait(0.1, 0.3)
        
def wait(min_time, max_time):
    time.sleep(random.uniform(min_time, max_time))

def login(driver):
    logger.info("Checking Instagram login status...")
    driver.get('https://www.instagram.com/')
    wait(2, 4)
    
    if "/accounts/login/" not in driver.current_url:
        logger.info("Session already active, skipping login...")
        return True

    logger.info("Logging in to Instagram...")
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
                    
        typing(username_field, USERNAME)
        wait(0.5, 1.5)
        typing(password_field, PASSWORD)
        wait(0.5, 1.5)

        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
            
        # Dismiss popups
        popups = [
            "//div[text()='Not Now']",
            "//button[text()='Not Now']",
            "//button[text()='Allow all cookies']",
            "//*[text()='Not now']",
        ]
        for xpath in popups:
            try:
                button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                button.click()
                logger.info(f"Dismissed popup: {xpath}")
                wait(1, 2)
            except TimeoutException:
                logger.debug(f"No popups found: {xpath}")
                pass
        
        # load homepage
        WebDriverWait(driver, 15).until_not(EC.url_contains("/accounts/login"))
        logger.info(f"Login successful, {driver.current_url} loaded!")
        return True
    except TimeoutException:
        logger.error("Login failed, timed out waiting for homepage :(")
        driver.save_screenshot(f"{LOG_DIR}/login_failed.png")
        return False
    except Exception as e:
        logger.error(f"An error occurred during login: {e}")
        logger.error(traceback.format_exc())
        return False
    
    
def extract_post_data(article):
    caption = ""
    raw_image_url = None

    # Extract caption
    try:
        caption_el = article.find_element(
            By.XPATH,
            ".//span[contains(@class,'_ap3a') and contains(@class,'_aaco') and contains(@class,'_aacu')]"
        )
        caption = caption_el.text.strip()
    except NoSuchElementException:
        logger.debug("Caption not found")
        pass

    # Extract image
    try:
        image_el = article.find_element(
            By.XPATH,
            ".//div[contains(@class,'_aagu')]/div[contains(@class,'_aagv')]/img"
        )
        raw_image_url = image_el.get_attribute("src")
    except NoSuchElementException:
        # Fallback: extract video thumbnail
        try:
            image_el = article.find_element(By.XPATH, ".//video")
            raw_image_url = image_el.get_attribute("poster") or image_el.get_attribute("src")
        except NoSuchElementException:
            logger.debug("Image not found")
            pass

    return caption, raw_image_url


def process_feed(driver, scroll_limit=50):
    cutoff = datetime.now(timezone.utc) - timedelta(days=CUTOFF_DAYS)
    events_added = 0
    posts_processed = 0
    consec_old_posts = 0
    
    seen_shortcodes = get_seen_shortcodes()
    processed_in_session = set()
    
    try:
        logger.info("Waiting for feed to load...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "article"))
        )
        logger.info("Feed loaded, starting feed processing...")
    except TimeoutException:
        logger.error("Feed not loaded, no posts found")
        driver.save_screenshot(f"{LOG_DIR}/feed_not_loaded.png")
        return 0, 0
    
    # Scroll and scrape
    for _ in range(scroll_limit):
        posts = driver.find_elements(By.TAG_NAME, "article")
        logger.info(f"Found {len(posts)} posts in feed")
        if len(posts) == 0:
            with open(f"{LOG_DIR}/debug_feed.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            logger.warning("Saved HTML snapshot to debug_feed.html for inspection")
        for p in posts:
            try:
                link_element = p.find_element(By.XPATH, ".//a[contains(@href, '/p/')]")
                post_url = link_element.get_attribute('href')
                shortcode = post_url.split('/')[-2]
                if shortcode in seen_shortcodes or shortcode in processed_in_session:
                    continue
                processed_in_session.add(shortcode)

                time_element = p.find_element(By.TAG_NAME, "time")
                post_time = datetime.fromisoformat(time_element.get_attribute("datetime").replace('Z', '+00:00'))
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
                    username = p.find_element(By.XPATH, ".//a[contains(@href, '/')]").text
                except NoSuchElementException:
                    username = "unknown"
                    
                logger.info(f"Processing post {shortcode} by {username}")
                
                caption, raw_image_url = extract_post_data(p)
                
                # Process data
                if raw_image_url:
                    wait(1, 3)
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
                wait(15, 45)
                
                if posts_processed >= MAX_POSTS:
                    logger.info(f"Reached max post limit of {MAX_POSTS}, stopping...")
                    return events_added, posts_processed
            except NoSuchElementException:
                logger.debug("Could not parse article element, likely not user post")
                continue
            except Exception as e:
                logger.error(f"Error processing post: {e}")
                logger.error(traceback.format_exc())
                continue
        logger.info("Scrolling... loading more posts...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        wait(5, 15)
        
    return events_added, posts_processed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape feed with Selenium")
    parser.add_argument(
        "--scroll-limit",
        type=int,
        default=50,
        help="Set max number of times to scroll the home feed"
    )
    args = parser.parse_args()
    
    driver = get_driver()
    if login(driver):
        time.sleep(5)
        events_added, posts_processed = process_feed(driver, scroll_limit=args.scroll_limit)
        logger.info("\n----------------------- SUMMARY -----------------------")
        logger.info(f"Processed {posts_processed} posts, added {events_added} events :D")
    else:
        logger.critical("Could not log in :( aborting...")
    driver.quit()
    