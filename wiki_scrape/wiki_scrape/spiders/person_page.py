import scrapy
import json
import re
from urllib.parse import urlencode
import pandas as pd
import mwparserfromhell
from ..items import WikiPersonItem


class WikiCategoryPageSpider(scrapy.Spider):
    name = "person_page"

    base_url = "https://ja.wikipedia.org/w/api.php"

    base_params = {
        "action": "query",
        "format": "json",
        "prop": "extracts|revisions|pageprops",
        "exintro": True,  # 冒頭のみ
        "redirects": 1,
        "explaintext": True,  # プレーンテキスト
        "rvprop": "content",  # ウィキテキスト取得
        "rvslots": "main",
    }

    def start_requests(self):
        persons = pd.read_csv("data/wiki_category_page.csv")

        batch_size = 50
        for i in range(0, len(persons), batch_size):
            batch = persons.iloc[i : i + batch_size]

            pageids = "|".join(batch["pageid"].astype(str))

            params = {
                **self.base_params,
                "pageids": pageids,
            }

            url = f"{self.base_url}?{urlencode(params)}"

            sex_mapping = dict(zip(batch["pageid"], batch["sex"]))

            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={"sex_mapping": sex_mapping},
            )

    def parse(self, response):
        data = json.loads(response.text)
        sex_mapping = response.meta["sex_mapping"]

        pages = data.get("query", {}).get("pages", {})
        for pageid, page_data in pages.items():
            sex = sex_mapping.get(int(pageid))

            # extractが空の場合、リトライ
            extract = page_data.get("extract", "")
            extract = re.sub(r"\s+", " ", extract).strip()

            retry_count = response.meta.get("retry_count", 0)

            if not extract and retry_count < 3:
                # 単独でリトライ
                params = {
                    **self.base_params,
                    "pageids": pageid,
                }
                url = f"{self.base_url}?{urlencode(params)}"

                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={
                        "sex_mapping": {int(pageid): sex},
                        "retry_count": retry_count + 1,
                    },
                    dont_filter=True,
                )
            else:
                yield self.process_page(page_data, sex)

    def process_page(self, page_data, sex):
        """人物ページ1件分の処理"""

        title = page_data.get("title")
        pageid = page_data.get("pageid")

        # 本文（冒頭）
        extract = page_data.get("extract", "")
        extract = re.sub(r"\s+", " ", extract).strip()

        # ウィキテキスト
        wikitext = (
            page_data.get("revisions", [{}])[0]
            .get("slots", {})
            .get("main", {})
            .get("*", "")
        )

        # Infoboxを構造化
        infobox = self.parse_infobox(wikitext)

        return WikiPersonItem(
            extract=extract,
            infobox=infobox,
            pageid=pageid,
            sex=sex,
            title=title,
        )

    def parse_infobox(self, wikitext):
        """
        mwparserfromhell を使って Infobox を構造化
        """
        infobox = {}
        if not wikitext:
            return infobox
        wikicode = mwparserfromhell.parse(wikitext)

        # テンプレートをすべて走査
        for template in wikicode.filter_templates():
            name = str(template.name).strip()

            # 日本語Wikiでは Infobox 人物 / Infobox 人物2 などが多い
            if not name.lower().startswith("infobox"):
                continue

            for param in template.params:
                key = str(param.name).strip().lower()
                value = str(param.value)
                value = re.sub(r"\s+", " ", value).strip()

                # Wikiリンク除去 [[A|B]] → B
                value = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", value)
                # 強調記法除去 '' '''
                value = re.sub(r"'{2,}", "", value)
                # HTMLタグ除去
                value = re.sub(r"<[^>]+>", "", value)

                value = value.strip()

                if value:
                    infobox[key] = value
            break

        return infobox
