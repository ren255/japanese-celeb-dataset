# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WikiSubCategoryItem(scrapy.Item):
    title = scrapy.Field()
    pageid = scrapy.Field()
    depth = scrapy.Field()
    parent = scrapy.Field()
    sex = scrapy.Field()

    exclude = ["アルバム", "曲", "作品", "ドラマ", "小説", "著作", "歌", "音楽", "集"]
    pageids = []

    def process(self, item):
        title = item.get("title", "")
        for exclude_word in self.exclude:
            if title.endswith(exclude_word):
                return None  # 除外対象

        pageid = item.get("pageid")
        if pageid in self.pageids:
            return None  # 重複

        self.pageids.append(pageid)

        return item
