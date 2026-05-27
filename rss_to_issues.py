import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

# Contains only the 21 links routed to the DJ Guide
FEEDS = {
    "Native Instruments": "https://www.gearnews.com/?s=Native+Instruments&feed=rss2",
    "SSL": "https://www.gearnews.com/?s=SSL&feed=rss2",
    "Teenage Engineering": "https://www.gearnews.com/?s=Teenage+Engineering&feed=rss2",
    "Universal Audio": "https://www.gearnews.com/?s=Universal+Audio&feed=rss2",
    "AlphaTheta": "https://www.gearnews.com/?s=AlphaTheta&feed=rss2",
    "AIAIAI": "https://www.gearnews.com/?s=AIAIAI&feed=rss2",
    "Akai Pro": "https://www.gearnews.com/?s=Akai+Pro&feed=rss2",
    "Allen & Heath": "https://www.gearnews.com/?s=Allen+%26+Heath&feed=rss2",
    "Arturia": "https://www.gearnews.com/?s=Arturia&feed=rss2",
    "Denon DJ": "https://www.gearnews.com/?s=Denon+DJ&feed=rss2",
    "Ecler": "https://www.gearnews.com/?s=Ecler&feed=rss2",
    "Focusrite": "https://www.gearnews.com/?s=Focusrite&feed=rss2",
    "Genelec": "https://www.gearnews.com/?s=Genelec&feed=rss2",
    "KRK": "https://www.gearnews.com/?s=KRK&feed=rss2",
    "Mackie": "https://www.gearnews.com/?s=Mackie&feed=rss2",
    "Rane": "https://www.gearnews.com/?s=Rane&feed=rss2",
    "Reloop": "https://www.gearnews.com/?s=Reloop&feed=rss2",
    "Roland": "https://www.gearnews.com/?s=Roland&feed=rss2",
    "Sennheiser": "https://www.gearnews.com/?s=Sennheiser&feed=rss2",
    "Shure": "https://www.gearnews.com/?s=Shure&feed=rss2",
    "Technics": "https://www.gearnews.com/?s=Technics&feed=rss2"
}

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
        print(f"✅ Posted to Radar: {title}")
    except Exception as e:
        print(f"❌ Error: {e}")

# Updated processing loop to parse open-access standard blog RSS structures
for brand, rss_url in FEEDS.items():
    print(f"📡 Fetching live radar feed for: {brand}...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml;q=0.9, text/xml;q=0.8, */*;q=0.7'
        }
        req = urllib.request.Request(rss_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            tree = ET.parse(response)
            root = tree.getroot()
            
            # Extracts items from standard RSS layout cleanly
            items = root.findall('.//item')
            print(f"   Found {len(items)} raw items for {brand}.")
            
            for item in items[:5]:
                title_elem = item.find('title')
                link_elem = item.find('link')
                
                if title_elem is not None and link_elem is not None:
                    title = title_elem.text
                    clean_link = link_elem.text
                    create_github_issue(title, clean_link, brand)
                    
    except Exception as e:
        print(f"❌ Error checking {brand}: {e}")


