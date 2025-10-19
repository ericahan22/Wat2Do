import csv
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

URL = "https://clubs.wusa.ca/club_listings"
REQUEST_DELAY = 1


def get_soup(url):
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return BeautifulSoup(res.text, "html.parser")
        else:
            print(f"Error: Status code {res.status_code} for URL: {url}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")


def get_categories():
    soup = get_soup(URL)
    cats = []
    cat_section = soup.find(class_="mt-3 list-group border-0 bg-transparent")
    if cat_section:
        for a in cat_section.find_all("a", href=True):
            cat_name = a.get_text(strip=True)
            cat_url = urljoin(URL, a["href"])
            if cat_name and cat_url != URL:
                cats.append({"name": cat_name, "url": cat_url})
    return cats


def find_club_links(soup):
    links = []
    for a in soup.find_all("a"):
        if "learn more" in a.text.strip().lower():
            href = a.get("href")
            if href:
                links.append(urljoin(URL, href))
    return links


def find_instagram_handle(soup):
    for tag in soup(["head", "header"]):
        tag.decompose()

    icon = soup.find_all("i", class_="fab fa-instagram")
    if icon:
        icon = icon[0]
    else:
        return

    parent = icon.find_parent("a", href=True)
    if parent:
        href = parent["href"].strip()
        if "instagram.com" in href:
            handle = href.split("/")[-1]
            return handle if handle else None
        elif href:
            return href
    return None


def scrape_category(cat_name, cat_url):
    page = 1
    results = []

    while True:
        page_url = f"{cat_url}?page={page}"
        print(f"Scraping page {cat_name}, page {page}")
        soup = get_soup(page_url)
        if not soup:
            print("Failed to load page")
            break

        club_links = find_club_links(soup)
        if not club_links:
            print(f"End of {cat_name} category")
            break

        for link in club_links:
            print(f"Visiting {link}")
            sub_soup = get_soup(link)
            club_name = None
            ig_handle = None
            if sub_soup:
                name_tag = sub_soup.find(class_="club-name-header")
                if name_tag:
                    club_name = name_tag.get_text(strip=True)
                ig_handle = find_instagram_handle(sub_soup)
            results.append(
                {
                    "club_name": club_name or "Not found",
                    "categories": cat_name,
                    "club_page": link.split("/")[-1],
                    "ig": ig_handle or "Not found",
                    "discord": "NULL",
                }
            )
            time.sleep(REQUEST_DELAY)

        page += 1
        time.sleep(REQUEST_DELAY)
    return results


def scrape_all():
    club_data = {}
    cats = get_categories()
    for cat in cats:
        cat_results = scrape_category(cat["name"], cat["url"])
        for club in cat_results:
            club_id = club["club_page"]
            if club_id in club_data:
                existing_cats = club_data[club_id]["categories"]
                if cat["name"] not in existing_cats:
                    existing_cats.append(cat["name"])
            else:
                club_data[club_id] = {
                    "club_name": club["club_name"],
                    "categories": [cat["name"]],
                    "club_page": club["club_page"],
                    "ig": club["ig"],
                    "discord": club["discord"],
                }
        time.sleep(REQUEST_DELAY)

    res = []
    for club_url, club_info in club_data.items():
        res.append(
            {
                "club_name": club_info["club_name"],
                "categories": club_info["categories"],  
                "club_page": club_info["club_page"],
                "ig": club_info["ig"],
                "discord": club_info["discord"],
            }
        )
    return res


def save_to_csv(data, filename="club_info.csv"):
    keys = (
        data[0].keys()
        if data
        else ["club_name", "categories", "club_page", "ig", "discord"]
    )

    existing_data = []
    try:
        with open(filename, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            existing_data = list(reader)
    except FileNotFoundError:
        pass
    combined_data = existing_data + data
    unique_data = list(
        {
            entry["club_page"]: {k.strip(): v for k, v in entry.items()}
            for entry in combined_data
        }.values()
    )

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(unique_data)
    print(f"Saved {len(unique_data)} entries to {filename}")


def sort_csv_alphabetically(filename="club_info.csv"):
    """Sort existing CSV file alphabetically by club name"""
    # Read the CSV
    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        data = list(reader)

    # Sort by club name (case-insensitive)
    data.sort(key=lambda x: x["club_name"].lower())

    # Write back to CSV
    keys = (
        data[0].keys()
        if data
        else ["club_name", "categories", "club_page", "ig", "discord"]
    )
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

    print(f"Sorted {len(data)} entries alphabetically in {filename}")


if __name__ == "__main__":
    # data = scrape_all()
    # save_to_csv(data)
    sort_csv_alphabetically()
