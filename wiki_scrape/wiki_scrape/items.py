# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.exceptions import DropItem
import re


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

    hiragana = [chr(i) for i in range(0x3041, 0x3097)]
    hiragana.append(" ")

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
