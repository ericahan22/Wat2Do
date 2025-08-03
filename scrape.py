import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import time

URL = 'https://clubs.wusa.ca/club_listings'
REQUEST_DELAY = 1

def get_soup(url):
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return BeautifulSoup(res.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {e}")

def find_club_links(soup):
    links = []
    for a in soup.find_all('a'):
        if 'learn more' in a.text.strip().lower():
            href = a.get('href')
            if href:
                links.append(urljoin(URL, href))
    return links

def find_instagram_link(soup):
    for tag in soup(['head', 'header']):
        tag.decompose()
    
    icon = soup.find_all('i', class_='fab fa-instagram')
    print(icon)
    if icon:
        icon = icon[0]
    else:
        return

    parent = icon.find_parent('a', href=True)
    if parent:
        href = parent['href'].strip()
        print(href)
        if 'instagram.com' in href:
            return href
        elif href and not href.startswith('http'):
            return urljoin('https://instagram.com/', href)
        
def scrape_all():
    page = 1
    results = []

    while True:
        page_url = f"{URL}?page={page}"
        print(f"Scraping page {page}, {page_url}")
        soup = get_soup(page_url)
        if not soup:
            print("Failed to load page")
            break

        club_links = find_club_links(soup)
        if not club_links:
            print("End of page. Stopping")
            break
        
        for link in club_links:
            print(f"Visiting {link}")
            sub_soup = get_soup(link)
            club_name = None
            insta_url = None
            if sub_soup:
                name_tag = sub_soup.find(class_='club-name-header')
                if name_tag:
                    club_name = name_tag.get_text(strip=True)
                insta_url = find_instagram_link(sub_soup)
            results.append({
                'club_name': club_name or 'Not found',
                'club_page': link,
                'insta_url': insta_url or 'Not found'
            })
            time.sleep(REQUEST_DELAY)
        
        page += 1
        time.sleep(REQUEST_DELAY)
    return results

def save_to_csv(data, filename='club_info.csv'):
    keys = ['club_name', 'club_page', 'insta_url']
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Saved {len(data)} entries to {filename}")

if __name__ == "__main__":
    data = scrape_all()
    save_to_csv(data)
