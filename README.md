# Wikipedia Japanese Person Data Crawler
dataset available on kaggle  
 [japanese-names-with-gender](https://www.kaggle.com/datasets/rentoda/japanese-names-with-gender) : this wiki scraped dataset(79k)

## Quick Start
kaggle dataset for easier use:
[japanese-names-with-gender-extended](https://www.kaggle.com/datasets/rentoda/japanese-names-with-gender-extended) : 930k dataset(5 source meta dataset including this dataset)  

start with starter [notebook on kaggle](https://www.kaggle.com/code/rentoda/starter-japanese-names-with-gender-extended?scriptVersionId=320022647).
or do locally:

```sh
pip install kagglehub[pandas-datasets]
```

```sh
import kagglehub
from kagglehub import KaggleDatasetAdapter

# Set the path to the file you'd like to load
file_path = ""

df = kagglehub.load_dataset(
  KaggleDatasetAdapter.PANDAS,
  "rentoda/japanese-names-with-gender-extended",
  file_path,
)

print("First 5 records:", df.head())
```

## Overview

> Category:職業別の日本の女性 (pageid: 3248378)  
> Category:職業別の日本の男性 (pageid: 4051488)

Wikipediaから「職業別の日本人（男女別）」カテゴリを起点として、人物データを再帰的に収集・構造化するクローラー一式です。

日本語Wikipediaでは約10年前に[人物ページへの性別記載を廃止する方針](https://ja.wikipedia.org/wiki/Wikipedia%E2%80%90%E3%83%8E%E3%83%BC%E3%83%88:%E3%82%B9%E3%82%BF%E3%82%A4%E3%83%AB%E3%83%9E%E3%83%8B%E3%83%A5%E3%82%A2%E3%83%AB/%E4%BA%BA%E7%89%A9%E4%BC%9D/%E6%80%A7%E5%88%A5%E3%81%AE%E8%A1%A8%E8%A8%98%E3%81%AB%E3%81%A4%E3%81%84%E3%81%A6)が取られたため、性別別職業カテゴリ配下の人物ページをWikipedia APIで再帰的に探索することで性別を推定しています。

[wiki rate limit](https://www.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits#cite_note-exempt-1)


## 処理の流れ

1. **サブカテゴリ収集** (`wiki_sub_category`)  
   指定した親カテゴリ（日本の女性/男性・職業別）からサブカテゴリを再帰的に探索します。`items.py`の`WikiSubCategoryItem`に定義された`exclude`・`exclude_2`リストで人物カテゴリ以外（アルバム、ドラマ、大学など）を排除し、`white_list`で性別キーワードを含まなくても保持すべき例外カテゴリ（宝塚、歌舞伎役者など）を処理します。重複pageidはパイプライン内でDropItemします。

2. **人物ページID収集** (`wiki_category_page`)  
   残ったサブカテゴリに含まれる人物ページのIDをすべて取得します。

3. **人物情報収集** (`person_page`)  
   人物ページから氏名・誕生年・身長・体重・血液型などをWikipedia APIで取得します。Infoboxはmwparserfromhellで構造化します。

4. **フォーマット** (`format.py`)  
   `namedivider-python`を活用して氏名を「姓 名」の形式に分割し、数値・血液型などを正規化して最終CSV（`data.csv`）を出力します。

---

## Quick Start Run

### 1. 環境構築

```sh
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. クローラーの実行

```sh
cd wiki_scrape
scrapy crawl wiki_sub_category
scrapy crawl wiki_category_page
scrapy crawl person_page
python format.py
```


## 確認・デバッグ用スクリプト

### `data/data.py`

`wiki_sub_category.csv`をもとにサブカテゴリのツリー構造をplotly・treelibで可視化します。カテゴリの収集結果や親子関係を目視確認したいときに使います。`wiki_sub_category`クローリング後であればいつでも実行できます。

```sh
python data/data.py
```

### `data/wiki.py`

性別キーワード・white_listのいずれも含まないカテゴリを抽出し`has_no_sex_category.csv`に出力します。`exclude`・`white_list`の追加・修正が必要なカテゴリの洗い出しに使います。

```sh
python data/wiki.py
```

---

## 出力ファイル

`data.csv`

| カラム | 説明 | 欠損率 |
|---|---|---|
| sex | 性別 (male / female) | 0.50% |
| kanji | 氏名（漢字・姓名分割済み） | 0% |
| hiragana | 氏名（ひらがな） | 0% |
| pageid | Wikipedia page ID | 0% |
| birth_year | 生年 | 19.7% |
| blood_type | 血液型 (A / B / O / AB / 不明) | 94.7% |
| height | 身長 (cm) | 95.4% |
| weight | 体重 (kg) | 99.1% |
| occupation | 職業 | 84.9% |
| education | 学歴 | 90.3% |
| birth_place | 出生地 | 77.2% |
| birth_date | 生年月日 (YYYY-MM-DD) | 76.8% |
| nationality | 国籍 | 93.9% |

kanji・hiragana・pageidは欠損がある場合パイプライン内でDropItemされます。