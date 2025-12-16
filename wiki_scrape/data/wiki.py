# %%
import pandas as pd

pages = pd.read_csv("wiki_category_page.csv")
pages["prefix"] = pages["sortkeyprefix"].str[0]

category = pd.read_csv("wiki_sub_category.csv")

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


# gender_listの各キーワードを含むかチェックするパターンを作成
pattern = "|".join(gender_list + white_list)

# gender_listのいずれかのキーワードを含まない行を抽出
filtered = category[~category["title"].str.contains(pattern, na=False)]
filtered = filtered[filtered["drop"] == False]

filtered.to_csv("has_no_sex_category.csv")

# %%
