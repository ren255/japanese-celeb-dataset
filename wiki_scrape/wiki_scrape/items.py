# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.exceptions import DropItem
import re
import datetime


class WikiSubCategoryItem(scrapy.Item):
    title = scrapy.Field()
    pageid = scrapy.Field()
    depth = scrapy.Field()
    parent_id = scrapy.Field()
    sex = scrapy.Field()
    drop = scrapy.Field()  # not in whitelist or duplicate
    sortkeyprefix = scrapy.Field()

    hiragana = [chr(i) for i in range(0x3041, 0x3097)]
    hiragana.append(" ")
    exclude = [
        "アルバム",
        "曲",
        "作品",
        "ドラマ",
        "小説",
        "著作",
        "歌",
        "音楽",
        "映画",
        "集",
        "テンプレート",
    ]
    exclude_2 = ["の選手", "大学", "番組"]
    contains = ["花譜", ""]
    pageids = []
    exclude_pageid = []

    def process(self, item):
        item["drop"] = False

        if item["parent_id"] in self.exclude_pageid:
            self.exclude_pageid.append(item["pageid"])
            item["drop"] = True
            raise DropItem("parent is in  exclude_ids")

        for exclude_word in self.exclude:
            if item["title"].endswith(exclude_word):
                item["drop"] = True
                self.exclude_pageid.append(item["pageid"])
                raise DropItem("title end with exclude")

        gender_list = [
            "男",
            "女",
            "ガール",
            "クイーン",
            "キング",
            "ボーイ",
            "レディ",
            "メンズ",
            "ウーマン",
            "紳士",
            "婦人",
            "夫人",
            "少年",
            "青年",
            "姫",
            "王子",
            "プリンス",
            "プリンセス",
        ]

        white_list = ["LPGA", "宝塚", "大相撲力士", "尼僧", "助産師", "NBA", "歌劇団"]
        white_list += [
            "芸妓",
            "芸者歌手",
            "島原太夫",
            "妓生",
            "日本のグラビアモデル",
            "グラビアアイドル",
            "ワンギャル",
            "ブランチリポーター",
            "日本のバレリーナ",
            "娘役",
            "日本のソプラノ歌手",
            "日本のメゾソプラノ歌手",
            "日本のアルト歌手",
            "ニコモ",
            "セブンティーンのモデル",
            "Non-noのモデル",
            "CanCamモデルズ",
            "ViViモデルズ",
            "JJモデル",
            "BAILAのモデル",
            "Rayの専属モデル",
            "Popteenモデル",
            "Popteen専属モデル",
            "ピチモ",
            "プチモ",
            "ラブベリーナ",
            "LARMEモデル",
            "小悪魔agehaモデル",
            "旭化成せんいキャンペーンモデル",
            "カネボウスイムウエアイメージモデル",
            "昭和シェル石油イメージパーソナリティ",
            "ユニチカアンバサダー",
        ]
        white_list += [
            "歌舞伎役者",
            "江戸時代の歌舞伎役者",
            "相撲記者",
            "大相撲力士",
            "日本のテノール歌手",
            "日本のバリトン歌手",
            "日本のバス歌手",
            "仮面ライダーシリーズ主演俳優",
            "スーパー戦隊シリーズ主演俳優",
            "ウルトラシリーズ主演俳優",
        ]

        sex_in_title = any(
            gender in item["title"] for gender in (gender_list + white_list)
        )
        if not sex_in_title:
            for exclude_word in self.exclude_2:
                if item["title"].endswith(exclude_word):
                    item["drop"] = True
                    self.exclude_pageid.append(item["pageid"])
                    raise DropItem("no sex and end with exclude2")

        if item["pageid"] in self.pageids:
            item["drop"] = True
            raise DropItem("duplicate pageid")

        if not sex_in_title:
            item["sortkeyprefix"] = re.sub(r"\s", " ", item["sortkeyprefix"])
            if all(char in self.hiragana for char in item["sortkeyprefix"]):
                if len(item["sortkeyprefix"].split(" ")) >= 2:
                    item["drop"] = True
                    self.exclude_pageid.append(item["pageid"])
                    raise DropItem("is name")

        if not sex_in_title:
            item["drop"] = True

        self.pageids.append(item["pageid"])
        return item


import re
from scrapy.exceptions import DropItem


class WikiPageItem(scrapy.Item):
    title = scrapy.Field()
    pageid = scrapy.Field()
    parent_id = scrapy.Field()
    sortkeyprefix = scrapy.Field()
    sex = scrapy.Field()
    drop = scrapy.Field()

    def process(self, item):
        item["drop"] = False

        # title に英字が含まれていたら除外
        if re.search(r"[A-Za-z]", item["title"]):
            item["drop"] = True
            raise DropItem("title contains english")

        # 日本語 + 許可記号 以外が含まれていたら除外
        if re.search(r"[^一-龯ぁ-ゖァ-ヺー\s(),]", item["title"]):
            item["drop"] = True
            raise DropItem("title contains non-japanese characters")

        # 名前がひらがな=漢字でない除外
        if len(item["sortkeyprefix"]) == 0:
            item["drop"] = True
            raise DropItem("no sortkeyprefix = title is hiragana?")

        # 空白正規化
        item["sortkeyprefix"] = re.sub(r"\s+", " ", item["sortkeyprefix"])
        # ひらがな＋スペース以外が含まれていたら除外
        if re.search(r"[^ぁ-ゖ ]", item["sortkeyprefix"]):
            item["drop"] = True
            raise DropItem("sortkeyprefix contains non hiragana")

        # sortkeyprefixがよみになるため、氏名分割できないものを除外
        if len(item["sortkeyprefix"].split(" ")) != 2:
            item["drop"] = True
            # 人名だが分割されていないものがあるためpass

        item["title"] = re.sub(r"・", " ", item["title"])

        return item


import ast


class WikiPersonItem(scrapy.Item):
    title = scrapy.Field()
    kanji = scrapy.Field()
    hiragana = scrapy.Field()
    pageid = scrapy.Field()
    extract = scrapy.Field()
    infobox = scrapy.Field()
    sex = scrapy.Field()
    drop = scrapy.Field()
    birth_year = scrapy.Field()
    birth_date = scrapy.Field()

    # ===== 正規化 infobox fields =====
    birth_date = scrapy.Field()
    birth_place = scrapy.Field()
    nationality = scrapy.Field()
    blood_type = scrapy.Field()
    height = scrapy.Field()
    weight = scrapy.Field()
    education = scrapy.Field()
    occupation = scrapy.Field()

    pageids = []

    INFOBOX_KEY_MAP: dict[str, list[str]] = {
        # ===== 基本 =====
        # "name": ["name", "名前", "氏名", "fullname", "本名", "birth_name", "出生名"],
        # "ruby": ["ふりがな", "ruby"],
        "birth_date": [
            "born",
            "birth_date",
            "出生",
            "生年月日",
            "誕生日",
            "dateofbirth",
            "birthdate",
        ],
        "birth_place": [
            "birth_place",
            "出生地",
            "生誕地",
            "出身地",
            "cityofbirth",
            "countryofbirth",
            "origin",
            "location",
        ],
        # ===== 属性 =====
        "nationality": ["nationality", "国籍", "country"],
        "blood_type": ["blood", "血液型"],
        "height": ["height", "身長"],
        "weight": ["weight", "体重"],
        # ===== 学歴・経歴 =====
        "education": [
            "education",
            "学歴",
            "school_background",
            "alma_mater",
            "出身校",
            "training",
        ],
        "occupation": ["occupation", "職業", "肩書き", "field", "role"],
    }

    def process(self, item):
        item["drop"] = False

        if item["pageid"] in self.pageids:
            raise DropItem("duplicate pageid")
        else:
            self.pageids.append(item["pageid"])

        hiragana, year, date, bracket_content = self.extract_birth_date(item["extract"])
        item["hiragana"] = hiragana
        item["birth_year"] = year
        item["birth_date"] = date
        item["extract"] = -1

        item = self.extract_infobox(item)
        item["infobox"] = -1

        kanji = item["title"]
        kanji = re.sub(r"\(.*", "", kanji)  # (の前まで抽出
        match = re.search(r"^([一-龯ぁ-んァ-ヶー]+)", kanji)
        if match:
            kanji = match.group(1)
            item["kanji"] = kanji

        if not item.get("kanji"):
            raise DropItem("title not japanese")

        if not hiragana:
            raise DropItem("no hiragana")
        if len(hiragana.split(" ")) != 2:
            raise DropItem("cannot split hiragana in 2")

        return item

    def extract_infobox(self, item):

        infobox = item.get("infobox")
        if not infobox:
            # infobox が無い場合は全て None
            for key in self.INFOBOX_KEY_MAP:
                item[key] = None
            return item

        # 文字列で来た場合（"{'name': 'xxx', ...}"）
        if isinstance(infobox, str):
            try:
                infobox = ast.literal_eval(infobox)
            except Exception:
                item["drop"] = True
                return item

        # 正規化
        for normalized_key, candidates in self.INFOBOX_KEY_MAP.items():
            value = None
            for cand in candidates:
                if cand in infobox:
                    value = infobox[cand]
                    break
            item[normalized_key] = value
        return item

    def extract_birth_date(self, text):
        bracket_match = re.search(r"（(.+)）", text)
        if not bracket_match:
            return None, None, None, None

        # 括弧内の全体を取得
        full_bracket_match = re.search(r"（(.+?)）", text)

        if not full_bracket_match:
            return None

        bracket_content = full_bracket_match.group(1)

        # 年・月・日を個別に抽出
        hiragana_match = re.search(
            r"^([ぁ-んァ-ヶー\s]+?)(?:、|,|$|\d)", bracket_content
        )
        # 先頭から"、",",","文字列の終端","数字"のいずれかまでのひらがな。
        year_match = re.search(r"(\d{4})年", bracket_content)

        month_match = re.search(r"(\d{1,2})月", bracket_content)
        day_match = re.search(r"(\d{1,2})日", bracket_content)

        # 結果を構築（見つからない要素はNone）
        hiragana = hiragana_match.group(1) if hiragana_match else None

        if year_match:
            year = int(year_match.group(1))
        else:
            year = None

        date = None
        if year_match and month_match and day_match:
            date = datetime.datetime(
                year,
                int(month_match.group(1)),
                int(day_match.group(1)),
            ).strftime("%Y-%m-%d")

        return hiragana, year, date, bracket_content
