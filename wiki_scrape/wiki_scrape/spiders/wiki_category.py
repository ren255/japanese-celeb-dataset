import scrapy
import json
from ..items import WikiSubCategoryItem


class WikiCategorySpider(scrapy.Spider):
    name = "wiki_sub_category"

    def __init__(self, page_id=None, *args, **kwargs):
        super(WikiCategorySpider, self).__init__(*args, **kwargs)
        self.page_id = page_id

    def start_requests(self):
        if not self.page_id:
            raise ValueError("page_id is required")

        url = "https://ja.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmpageid": self.page_id,
            "format": "json",
            "cmlimit": 500,
            "cmtype": "subcat",
        }
        yield scrapy.Request(
            url=f"{url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}",
            callback=self.parse,
            meta={"depth": 1, "parent_id": self.page_id},
        )

    def parse(self, response):
        data = json.loads(response.text)
        depth = response.meta["depth"]
        parent_id = response.meta["parent_id"]

        for page in data["query"]["categorymembers"]:
            yield WikiSubCategoryItem(
                title=page["title"],
                pageid=page["pageid"],
                depth=depth,
                parent=parent_id,
            )

            url = "https://ja.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "list": "categorymembers",
                "cmpageid": page["pageid"],
                "format": "json",
                "cmlimit": 500,
                "cmtype": "subcat",
            }
            yield scrapy.Request(
                url=f"{url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}",
                callback=self.parse,
                meta={"depth": depth + 1, "parent_id": page["pageid"]},
            )
