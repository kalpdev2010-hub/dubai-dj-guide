import os
import json
import urllib.request
import urllib.parse
import time
import re
import html

MASTER_FEEDS = [
    "https://www.gearnews.com/zone/pro-audio/feed/",
    "https://www.gearnews.com/zone/electronic-music/feed/",
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
            raw_bytes = response.read()
            
            try:
                xml_data = raw_bytes.decode('utf-8')
            except UnicodeDecodeError:
                xml_data = raw_bytes.decode('iso-8859-1', errors='ignore')
            
            # UNBREAKABLE TEXT BLOCK EXTRACTOR: Skips strict parsing validation entirely
            raw_items = re.findall(r'<item>(.*?)</item>', xml_data, re.DOTALL)
            
            for item_str in raw_items:
                t_match = re.search(r'<title>(.*?)</title>', item_str, re.DOTALL)
                l_match = re.search(r'<link>(.*?)</link>', item_str, re.DOTALL)
                
                if t_match and l_match:
                    # Strip away CDATA envelopes cleanly
                    t_text = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', t_match.group(1), flags=re.DOTALL).strip()
                    l_text = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', l_match.group(1), flags=re.DOTALL).strip()
                    
                    # Remove hidden layout markers
                    t_text = re.sub(r'<[^>]+>', '', t_text)
                    l_text = re.sub(r'<[^>]+>', '', l_text)
                    
                    t_text = html.unescape(t_text)
                    l_text = html.unescape(l_text)
                    
                    if l_text not in seen_links:
                        seen_links.add(l_text)
                        all_articles.append({"title": t_text, "link": l_text})
    except Exception as e:
        print(f"⚠️ Channel skip warning: {e}")

print(f"🔍 Sorting {len(all_articles)} live industry updates into brand blueprints...")

brand_counts = {b: 0 for b in BRANDS}

for article in all_articles:
    title_lower = article["title"].lower()
    matched_any = False
    
    for brand in BRANDS:
        if brand_counts[brand] >= 3:
            continue
            
        keyword = brand.lower()
        if "denon" in keyword: keyword = "denon"
        if "akai" in keyword: keyword = "akai"
        if "allen" in keyword: keyword = "allen"
        if "pioneer" in keyword or "alphatheta" in keyword:
            if "pioneer" in title_lower or "alphatheta" in title_lower:
                create_github_issue(article["title"], article["link"], brand)
                brand_counts[brand] += 1
                matched_any = True
                time.sleep(1)
                continue
        
        if keyword in title_lower:
            create_github_issue(article["title"], article["link"], brand)
            brand_counts[brand] += 1
            matched_any = True
            time.sleep(1)
            
    if not matched_any:
        print(f"   ❌ Skipped (No brand match): {article['title']}")

print("🏁 Automation process concluded cleanly.")
