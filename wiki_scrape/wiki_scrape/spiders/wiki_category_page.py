import scrapy
import json
from urllib.parse import urlencode
from ..items import WikiPageItem
import pandas as pd


class WikiCategoryPageSpider(scrapy.Spider):
    name = "wiki_category_page"

    base_params = {
        "action": "query",
        "list": "categorymembers",
        "format": "json",
        "cmlimit": 500,
        "cmtype": "page",
        "cmprop": "ids|title|sortkeyprefix",
    }

    base_url = "https://ja.wikipedia.org/w/api.php"

    def start_requests(self):
        sub_categorys = pd.read_csv("data/wiki_sub_category.csv")

        for _, row in sub_categorys.iterrows():
            params = {**self.base_params, "cmpageid": row["pageid"]}
            url = f"{self.base_url}?{urlencode(params)}"
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={
                    "parent_id": row["pageid"],
                    "sex": row["sex"],
                },
            )

    def parse(self, response):
        data = json.loads(response.text)
        parent_id = response.meta["parent_id"]
        sex = response.meta["sex"]

        if "query" in data and "categorymembers" in data["query"]:
            for page in data["query"]["categorymembers"]:
                sortkey_prefix = page.get("sortkeyprefix", "")

                yield WikiPageItem(
                    title=page["title"],
                    pageid=page["pageid"],
                    parent_id=parent_id,
                    sortkeyprefix=sortkey_prefix,
                    sex=sex,
                )

        # continue処理
        if "continue" in data:
            params = {
                **self.base_params,
                "cmpageid": parent_id,
                "cmcontinue": data["continue"]["cmcontinue"],
            }
            url = f"{self.base_url}?{urlencode(params)}"
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={"parent_id": parent_id, "sex": sex},
            )
