import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

# Contains only the 21 links routed to the DJ Guide
FEEDS = {
    "Native Instruments": "https://www.google.com/alerts/feeds/17291303775024850829/9537452483107057677",
    "SSL": "https://www.google.com/alerts/feeds/17291303775024850829/7113639380508272407",
    "Teenage Engineering": "https://www.google.com/alerts/feeds/17291303775024850829/8457414191461055233",
    "Universal Audio": "https://www.google.com/alerts/feeds/17291303775024850829/7113639380508272946",
    "AlphaTheta": "https://www.google.com/alerts/feeds/17291303775024850829/2302414328451330321",
    "AIAIAI": "https://www.google.com/alerts/feeds/17291303775024850829/15689417266224105129",
    "Akai Pro": "https://www.google.com/alerts/feeds/17291303775024850829/10971714764224795617",
    "Allen & Heath": "https://www.google.com/alerts/feeds/17291303775024850829/1657006842736626489",
    "Arturia": "https://www.google.com/alerts/feeds/17291303775024850829/8457414191461056105",
    "Denon DJ": "https://www.google.com/alerts/feeds/17291303775024850829/10983863551238171227",
    "Ecler": "https://www.google.com/alerts/feeds/17291303775024850829/10971714764224794694",
    "Focusrite": "https://www.google.com/alerts/feeds/17291303775024850829/16537214002609777841",
    "Genelec": "https://www.google.com/alerts/feeds/17291303775024850829/16537214002609778634",
    "KRK": "https://www.google.com/alerts/feeds/17291303775024850829/16537214002609776865",
    "Mackie": "https://www.google.com/alerts/feeds/17291303775024850829/292043985323015668",
    "Rane": "https://www.google.com/alerts/feeds/17291303775024850829/1657006842736623864",
    "Reloop": "https://www.google.com/alerts/feeds/17291303775024850829/10971714764224797136",
    "Roland": "https://www.google.com/alerts/feeds/17291303775024850829/9537452483107059970",
    "Sennheiser": "https://www.google.com/alerts/feeds/17291303775024850829/292043985323012964",
    "Shure": "https://www.google.com/alerts/feeds/17291303775024850829/292043985323013067",
    "Technics": "https://www.google.com/alerts/feeds/17291303775024850829/1657006842736624497"
}

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
# Targeting the DJ repository
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
            
            entries = root.findall('{http://www.w3.org/2005/Atom}entry')
            print(f"   Found {len(entries)} raw items for {brand}.")
            
            # DIAGNOSTIC ADMISSION: If Google gives us 0 items, print the inner shell tags
            if len(entries) == 0:
                print("   🔍 Diagnostic Alert: Printing hidden feed elements:")
                for child in list(root)[:3]:
                    clean_tag = child.tag.split('}')[-1] # strip namespace
                    print(f"      ↳ Found Tag: <{clean_tag}> | Content: {child.text[:60] if child.text else 'None'}")
            
            for entry in entries[:5]:
                title = entry.find('{http://www.w3.org/2005/Atom}title').text
                raw_link = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']
                clean_link = raw_link.split('url=')[1].split('&ct=ga')[0] if 'url=' in raw_link else raw_link
                
                create_github_issue(title, clean_link, brand)
                
    except Exception as e:
        print(f"❌ Failed to read feed for {brand}. Reason: {e}")

