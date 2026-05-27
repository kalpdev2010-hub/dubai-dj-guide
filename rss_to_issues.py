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

# Process feeds via the API broker to bypass data center blocks
for brand, rss_url in FEEDS.items():
    print(f"📡 Requesting broker connection for: {brand}...")
    try:
        # Encodes the target link cleanly inside the broker API line
        broker_url = f"https://api.rss2json.com/v1/api.json?rss_url={urllib.parse.quote_plus(rss_url)}"
        
        req = urllib.request.Request(broker_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if data.get('status') == 'ok':
                items = data.get('items', [])
                print(f"   Success! Broker returned {len(items)} items for {brand}.")
                
                for item in items[:3]:
                    title = item.get('title')
                    link = item.get('link')
                    if title and link:
                        create_github_issue(title, link, brand)
            else:
                print(f"   ⚠️ Broker could not parse feed for {brand}")
                    
    except Exception as e:
        print(f"❌ Core link exception for {brand}: {e}")


