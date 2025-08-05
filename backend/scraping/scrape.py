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

def get_categories():
    soup = get_soup(URL)
    cats = []
    cat_section = soup.find(class_='mt-3 list-group border-0 bg-transparent')
    if cat_section:
        for a in cat_section.find_all('a', href=True):
            cat_name = a.get_text(strip=True)
            cat_url = urljoin(URL, a['href'])
            if cat_name and cat_url != URL:
                cats.append({
                    'name': cat_name,
                    'url': cat_url
                })
    return cats

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
    if icon:
        icon = icon[0]
    else:
        return

    parent = icon.find_parent('a', href=True)
    if parent:
        href = parent['href'].strip()
        if 'instagram.com' in href:
            return href
        elif href and not href.startswith('http'):
            return urljoin('https://instagram.com/', href)
        
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
            insta_url = None
            if sub_soup:
                name_tag = sub_soup.find(class_='club-name-header')
                if name_tag:
                    club_name = name_tag.get_text(strip=True)
                insta_url = find_instagram_link(sub_soup)
            results.append({
                'club_name': club_name or 'Not found',
                'category': cat_name,
                'club_page': link,
                'insta_url': insta_url or 'Not found'
            })
            time.sleep(REQUEST_DELAY)
        
        page += 1
        time.sleep(REQUEST_DELAY)
    return results

def scrape_all():
    club_data = {}
    cats = get_categories()
    for cat in cats:
        cat_results = scrape_category(cat['name'], cat['url'])
        for club in cat_results:
            club_url = club['club_page']
            if club_url in club_data:
                existing_cats = club_data[club_url]['categories']
                if cat['name'] not in existing_cats:
                    existing_cats.append(cat['name'])
            else:
                club_data[club_url] = {
                    'club_name': club['club_name'],
                    'categories': [cat['name']],
                    'club_page': club['club_page'],
                    'insta_url': club['insta_url']
                }
        time.sleep(REQUEST_DELAY)

    res = []
    for club_url, club_info in club_data.items():
        res.append({
            'club_name': club_info['club_name'],
            'categories': '; '.join(club_info['categories']),
            'club_page': club_info['club_page'],
            'insta_url': club_info['insta_url']
        })
    return res

def save_to_csv(data, filename='club_info.csv'):
    keys = ['club_name', 'categories', 'club_page', 'insta_url']
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Saved {len(data)} entries to {filename}")

def sort_csv_alphabetically(filename='club_info.csv'):
    """Sort existing CSV file alphabetically by club name"""
    # Read the CSV
    with open(filename, 'r', newline='') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    # Sort by club name (case-insensitive)
    data.sort(key=lambda x: x['club_name'].lower())
    
    # Write back to CSV
    keys = ['club_name', 'categories', 'club_page', 'insta_url']
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Sorted {len(data)} entries alphabetically in {filename}")

if __name__ == "__main__":
    # data = scrape_all()
    # save_to_csv(data)
    sort_csv_alphabetically()