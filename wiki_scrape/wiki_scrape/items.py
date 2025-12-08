# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WikiSubCategoryItem(scrapy.Item):
    title = scrapy.Field()
    pageid = scrapy.Field()
