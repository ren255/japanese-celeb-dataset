import scrapy
import json
from urllib.parse import urlencode
from ..items import WikiSubCategoryItem
from pathlib import Path


class WikiCategorySpider(scrapy.Spider):
    name = "wiki_sub_category"

    # ベースパラメータを定義
    base_params = {
        "action": "query",
        "list": "categorymembers",
        "format": "json",
        "cmlimit": 500,
        "cmtype": "subcat",
        "cmprop": "ids|title|sortkeyprefix",
    }

    base_url = "https://ja.wikipedia.org/w/api.php"

    custom_settings = {
        "DATA_DIR": "data",  # デフォルト
    }

    def start_requests(self):
        self.data_path = Path(self.settings.get("DATA_DIR"))
        # 女性カテゴリ (Category:職業別の日本の女性: 3248378)
        params = {**self.base_params, "cmpageid": 3248378}
        url = f"{self.base_url}?{urlencode(params)}"
        yield scrapy.Request(
            url=url,
            callback=self.parse,
            meta={"depth": 1, "parent_id": 3248378, "sex": "female"},
        )

        # 男性カテゴリ (Category:職業別の日本の男性: 4051488)
        params = {**self.base_params, "cmpageid": 4051488}
        url = f"{self.base_url}?{urlencode(params)}"
        yield scrapy.Request(
            url=url,
            callback=self.parse,
            meta={"depth": 1, "parent_id": 4051488, "sex": "male"},
        )

    def parse(self, response):
        data = json.loads(response.text)
        depth = response.meta["depth"]
        parent_id = response.meta["parent_id"]
        sex = response.meta["sex"]

        for page in data["query"]["categorymembers"]:
            sortkey_prefix = page.get("sortkeyprefix", "")
            yield WikiSubCategoryItem(
                title=page["title"],
                pageid=page["pageid"],
                depth=depth,
                parent_id=parent_id,
                sex=sex,
                sortkeyprefix=sortkey_prefix,
            )

            # 再帰的にサブカテゴリを取得
            params = {**self.base_params, "cmpageid": page["pageid"]}
            url = f"{self.base_url}?{urlencode(params)}"
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={"depth": depth + 1, "parent_id": page["pageid"], "sex": sex},
            )
