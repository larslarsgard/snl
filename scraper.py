import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Define file paths
CURRENT_FILE = "data/current.json"
HISTORY_FILE = "data/history.json"

# Make sure data directory exists
os.makedirs("data", exist_ok=True)

# 1. Fetch and Parse Website
url = "https://snl.no"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) SNL-Tracker-Bot'}
response = requests.get(url, headers=headers)

if response.status_code != 200:
    print(f"Error fetching page: {response.status_code}")
    exit(1)

soup = BeautifulSoup(response.text, 'html.parser')
stats_container = soup.find('div', class_='l-front__read-stats')

if not stats_container:
    print("Could not find the stats block on the page.")
    exit(1)

today = datetime.now().strftime("%Y-%m-%d")
scraped_data = {
    "date": today,
    "categories": {}
}

# 2. Extract Data from HTML
lists = stats_container.find_all('article', class_='link-list')
for item_list in lists:
    heading = item_list.find('h2', class_='link-list__heading').text.strip()
    scraped_data["categories"][heading] = []
    
    items = item_list.find_all('li', class_='link-list__item')
    for item in items:
        category = item.find('div', class_='link-list__category').text.strip()
        link_tag = item.find('a', class_='link-list__link')
        title = link_tag.text.strip()
        link = link_tag['href']
        
        if link.startswith('/'):
            link = f"https://snl.no{link}"
            
        scraped_data["categories"][heading].append({
            "category": category,
            "title": title,
            "url": link
        })

# 3. Save "Current" file for the Widget
with open(CURRENT_FILE, "w", encoding="utf-8") as f:
    json.dump(scraped_data, f, ensure_ascii=False, indent=2)

# 4. Update "History" file (Append mode)
history = {}
if os.path.exists(HISTORY_FILE):
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    except json.JSONDecodeError:
        pass # Start fresh if empty/corrupted

# Add or overwrite today's entry in history
history[today] = scraped_data["categories"]

with open(HISTORY_FILE, "w", encoding="utf-8") as f:
    json.dump(history, f, ensure_ascii=False, indent=2)

print(f"Successfully tracked data for {today}!")
