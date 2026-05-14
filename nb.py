#%%
!cp -r /kaggle/input/datasets/rentoda/wiki-name-scraper /kaggle/working/wiki-japanese-name-crawler
!pip install /kaggle/working/wiki-japanese-name-crawler
#%%
!wiki-scrape --output /kaggle/working/data.csv --lib-path /kaggle/working/wiki-japanese-name-crawler/wiki_scrape