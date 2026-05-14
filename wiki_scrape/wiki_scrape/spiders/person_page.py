import scrapy
import json
import re
import time
from datetime import timedelta
from urllib.parse import urlencode
import pandas as pd
import mwparserfromhell
from pathlib import Path
from ..items import WikiPersonItem
from scripts.auth import get_wiki_headers


class WikiCategoryPageSpider(scrapy.Spider):
    name = "person_page"
    base_url = "https://ja.wikipedia.org/w/api.php"
    base_params = {
        "action": "query",
        "format": "json",
        "prop": "extracts|revisions|pageprops",
        "exintro": True,
        "redirects": 1,
        "explaintext": True,
        "rvprop": "content",
        "rvslots": "main",
    }

    custom_settings = {
        "DATA_DIR": "data",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_headers = get_wiki_headers()
        self.processed = 0
        self.total = 0
        self.start_time = None
        self.last_progress_print = 0
        # 10分
        self.progress_print_interval = 600

    async def start(self):
        self.start_time = time.time()
        self.data_path = Path(self.settings.get("DATA_DIR"))
        persons = pd.read_csv(self.data_path / "wiki_category_page.csv")
        drop_ctn = len(persons[persons["drop"]])
        total_before_drop = len(persons)
        print(
            f"[INFO] processing {total_before_drop} person pages "
            f"from data/wiki_category_page.csv. "
            f"{drop_ctn} ({drop_ctn/total_before_drop:.2%}) pages dropped"
        )
        persons = persons[~persons["drop"]]
        self.total = len(persons)
        print(f"[INFO] final target pages: {self.total}")

        batch_size = 50
        total_batches = (self.total + batch_size - 1) // batch_size
        print(f"[INFO] batch_size={batch_size}, " f"total_batches={total_batches}")

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
                headers=self.auth_headers,
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

            retry = response.meta.get("retry", False)

            if not extract and not retry:
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
                        "retry": True,
                    },
                    dont_filter=True,
                )
            else:
                self.processed += 1
                if not extract:
                    print(f"[WARN] pageid={pageid} " f"extract empty after retry")
                self.print_progress()

                yield self.process_page(page_data, sex)

    def print_progress(self):
        now = time.time()
        if now - self.last_progress_print < self.progress_print_interval:
            return
        self.last_progress_print = now
        elapsed = now - self.start_time
        if self.processed == 0:
            return
        overall_speed = self.processed / elapsed
        remaining = self.total - self.processed
        eta_seconds = remaining / overall_speed
        eta_td = timedelta(seconds=int(eta_seconds))
        elapsed_td = timedelta(seconds=int(elapsed))
        percent = (self.processed / self.total) * 100

        print(
            f"[PROGRESS] "
            f"{self.processed}/{self.total} "
            f"({percent:.2f}%) | "
            f"elapsed={elapsed_td} | "
            f"speed={overall_speed:.2f} pages/sec | "
            f"ETA={eta_td}"
        )

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

    def closed(self, reason):
        elapsed = time.time() - self.start_time

        elapsed_td = timedelta(seconds=int(elapsed))

        print("=" * 80)
        print("[FINISHED]")
        print(f"reason={reason}")
        print(f"processed={self.processed}/{self.total}")
        print(f"elapsed={elapsed_td}")

        if elapsed > 0:
            print(f"average_speed=" f"{self.processed / elapsed:.2f} pages/sec")

        print("=" * 80)
