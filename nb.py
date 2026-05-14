# %%
!cp -r /kaggle/input/datasets/rentoda/wiki-name-scraper /kaggle/working/wiki-japanese-name-crawler
!pip install /kaggle/working/wiki-japanese-name-crawler
# %%
import requests
from wiki_scrape.scripts.auth import get_wiki_headers

auth_headers = get_wiki_headers()
r = requests.get(
    "https://ja.wikipedia.org/w/api.php",
    params={"action": "query", "meta": "userinfo", "format": "json"},
    headers=auth_headers,
)

print(r.status_code,r.text)
# %%
!wiki-scrape --output /kaggle/working/data --lib-path /kaggle/working/wiki-japanese-name-crawler/wiki_scrape