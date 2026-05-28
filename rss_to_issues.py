import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time

# Corrected enterprise pro-audio channels with active endpoints
MASTER_FEEDS = [
    "https://www.musicradar.com/rss",
    "https://www.soundonsound.com/news/sosrssfeed.php"
]

BRANDS = [
    "Native Instruments", "SSL", "Teenage Engineering", "Universal Audio", 
    "AlphaTheta", "AIAIAI", "Akai Pro", "Allen & Heath", "Arturia", 
    "Denon DJ", "Ecler", "Focusrite", "Genelec", "KRK", "Mackie", 
    "Rane", "Reloop", "Roland", "Sennheiser", "Shure", "Technics"
]

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = "kalpdev2010-hub/dubai-dj-guide"

def create_github_issue(title, link, brand):
    url = f"https://api.github.com/repos/{REPO}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    check_url = f"{url}?labels={urllib.parse.quote(brand)}&state=all"
    try:
        with urllib.request.urlopen(urllib.request.Request(check_url, headers=headers)) as resp:
            existing = json.loads(resp.read().decode())
            if any(issue['title'] == title for issue in existing):
                return
    except Exception:
        pass

    data = json.dumps({"title": title, "body": link, "labels": [brand]}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        urllib.request.urlopen(req)
        print(f"✅ Posted to Radar [{brand}]: {title}")
    except Exception as e:
        print(f"❌ GitHub API Error: {e}")

seen_links = set()
all_articles = []

for url in MASTER_FEEDS:
    print(f"📡 Fetching open channel stream: {url}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_data = response.read().decode('utf-8', errors='ignore')
            root = ET.fromstring(xml_data)
            items = root.findall('.//item')
            
            for item in items:
                title_elem = item.find('title')
                link_elem = item.find('link')
                if title_elem is not None and link_elem is not None:
                    t_text = title_elem.text
                    l_text = link_elem.text
                    if l_text not in seen_links:
                        seen_links.add(l_text)
                        all_articles.append({"title": t_text, "link": l_text})
    except Exception as e:
        print(f"⚠️ Channel skip warning: {e}")

print(f"🔍 Sorting {len(all_articles)} live industry updates into brand blueprints...")

brand_counts = {b: 0 for b in BRANDS}

for article in all_articles:
    title_lower = article["title"].lower()
    
    for brand in BRANDS:
        if brand_counts[brand] >= 3:
            continue
            
        keyword = brand.lower()
        if "denon" in keyword: keyword = "denon"
        if "akai" in keyword: keyword = "akai"
        if "allen" in keyword: keyword = "allen"
        
        if keyword in title_lower:
            create_github_issue(article["title"], article["link"], brand)
            brand_counts[brand] += 1
            time.sleep(1)

print("🏁 Automation process concluded cleanly.")
