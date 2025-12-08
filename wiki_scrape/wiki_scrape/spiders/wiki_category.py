import scrapy
import json
from ..items import WikiSubCategoryItem


class WikiCategorySpider(scrapy.Spider):
    name = "wiki_sub_category"

    def start_requests(self):
        url = "https://ja.wikipedia.org/w/api.php"
        categories = ["Category:職業別の日本の女性", "Category:職業別の日本の男性"]
        for category in categories:
            params = {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": f"Category:{category}",
                "format": "json",
                "cmlimit": 500,
                "cmtype": "subcat",  #  'subcat'/"page"
            }
            yield scrapy.Request(
                url=f"{url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}",
                callback=self.parse,
            )

    def parse(self, response):
        data = json.loads(response.text)
        for page in data["query"]["categorymembers"]:
            yield WikiSubCategoryItem(title=page["title"], pageid=page["pageid"])
