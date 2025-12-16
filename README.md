Category:職業別の日本の女性: 3248378
Category:職業別の日本の男性: 4051488


# person page
scrapy shell

from urllib.parse import urlencode
import json

base_url = "https://ja.wikipedia.org/w/api.php"
params = {
    "action": "query",
    "format": "json",
    "pageids": "3048253",
    "prop": "extracts|revisions|pageprops",  # 本文とInfobox
    "exintro": True,  # 冒頭のみ
    "explaintext": True,  # プレーンテキストで取得
    "rvprop": "content",  # ウィキテキストの生データ
    "rvslots": "main",
}

url = f"{base_url}?{urlencode(params)}"
fetch(url)

data = json.loads(response.text)
page_data = data["query"]["pages"]["3048253"]

# 本文（プレーンテキスト）
print("=== 本文 ===")
print(page_data.get("extract", "")[:500])  # 最初の500文字
from urllib.parse import urlencode
import json

base_url = "https://ja.wikipedia.org/w/api.php"

# 取得できていないpageidを1つずつテスト


test_pageids = ["3118994", "3221591", "3322909", "3369685", "3445719", "3495605"]

for pageid in test_pageids:
    params = {
        "action": "query",
        "format": "json",
        "pageids": pageid,
        "prop": "extracts|revisions|pageprops",
        "exintro": True,
        "explaintext": True,
        "rvprop": "content",
        "rvslots": "main",
        "redirects": 1,
    }
    
    url = f"{base_url}?{urlencode(params)}"
    fetch(url)
    
    data = json.loads(response.text)
    pages = data.get("query", {}).get("pages", {})
    
    print(f"\n{'='*60}")
    print(f"PageID: {pageid}")
    