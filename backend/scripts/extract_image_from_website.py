import os
import sys
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.storage_service import upload_image_from_url


def find_main_image_url(soup):
    """
    Find the main event image URL, skipping logos, icons, etc.
    """
    # Remove tags that may contain tracking pixels or scripts
    for tag in soup(["noscript", "script", "meta", "link"]):
        tag.decompose()

    # Remove any <img> whose src contains known trackers
    for img in soup.find_all("img", src=True):
        if "facebook.com/tr" in img["src"] or "pixel" in img["src"].lower():
            img.decompose()

    skip_keywords = [
        "logo", "icon", "analytics", "ads",
        "google-analytics", "gstatic",
        "doubleclick", "adservice", "data:image"
    ]

    candidate_images = []

    for img in soup.find_all("img", src=True):
        src = img["src"].strip()

        # Skip any tracking or inline data images
        if any(k in src.lower() for k in skip_keywords):
            continue

        # Skip tiny images
        try:
            w = int(img.get("width", 0))
            h = int(img.get("height", 0))
            if w and h and (w < 80 or h < 80):
                continue
        except ValueError:
            pass

        # Skip URLs that are suspiciously short
        if len(src) < 10:
            continue

        candidate_images.append((w * h if w and h else 0, src))

    if not candidate_images:
        return None

    # Return the largest image candidate
    _, best_src = max(candidate_images, key=lambda x: x[0])
    return best_src


async def get_event_image_s3_url(event_url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(event_url, timeout=15000)
        await page.wait_for_load_state("domcontentloaded", timeout=10000)

        await page.evaluate("""
            document.querySelectorAll('img[src*="pixel"]').forEach(el => el.remove());
        """)

        content = await page.content()
        soup = BeautifulSoup(content, "lxml")
        image_url = find_main_image_url(soup)
        await page.close()
        await context.close()
        await browser.close()

        if not image_url:
            return None

        if image_url.startswith("/"):
            from urllib.parse import urljoin
            image_url = urljoin(event_url, image_url)

        s3_url = upload_image_from_url(image_url)
        return s3_url if s3_url else None


async def main():
    event_urls = [
        "https://uwaterloo.ca/theatres/events/allow-me-standup-comedy-show-rahul-dua",
        # Enter more URLs with images that need backfilling
    ]
    results = []

    async def fetch_and_store(url):
        s3_url = await get_event_image_s3_url(url)
        results.append((url, s3_url))

    await asyncio.gather(*(fetch_and_store(url) for url in event_urls))

    print("Event image results:")
    for url, s3_url in results:
        print(f"{url}\n{s3_url}\n")


def upload_manual_images_to_s3(image_urls):
    """
    Manually upload a list of image URLs to S3 and return their S3 URLs.
    """
    results = []
    for image_url in image_urls:
        # Resolve relative URLs if needed
        s3_url = upload_image_from_url(image_url)
        results.append((image_url, s3_url))
    print("Manual image upload results:")
    for image_url, s3_url in results:
        print(f"{image_url}\n{s3_url}\n")
    return results


if __name__ == "__main__":
    asyncio.run(main())
    manual_image_urls = [
        "https://wusa.ca/wp-content/uploads/2025/01/Board-Thumbnail-1-scaled.jpeg",
        # Enter image URLs to manually convert to S3 image links
    ]
    upload_manual_images_to_s3(manual_image_urls)
