# 新順序
# sex            0.004979
# kanji          0.000000
# hiragana       0.000000
# pageid         0.000000
# birth_year     0.196680
# blood_type     0.946888
# height         0.953527
# weight         0.990595
# occupation     0.849516
# education      0.903458
# birth_place    0.772337
# birth_date     0.767635
# nationality    0.938589
# infobox        0.000000

# 消す
# drop           0.000000
# extract        0.000000
# title          0.000000

# %%
import pandas as pd
import numpy as np
import re
from pathlib import Path
from namedivider import BasicNameDivider, GBDTNameDivider
import argparse


def run(output_path=None):
    person = pd.read_csv("data/person_page.csv")

    person = person[~person["sex"].isna()]
    person["len"] = person["kanji"].str.len()
    person = person[(person["len"] >= 2) & (person["len"] <= 6)]

    divider = BasicNameDivider()
    # kanji列を分割し、姓 + 名の形式（"田中 太郎"）でkanji列に上書き保存
    person["kanji"] = person["kanji"].apply(
        lambda x: f"{divider.divide_name(x).family} {divider.divide_name(x).given}"
    )

    # 新順序に列を並べ替え
    person = person[
        [
            "sex",
            "kanji",
            "hiragana",
            "pageid",
            "birth_year",
            "blood_type",
            "height",
            "weight",
            "occupation",
            "education",
            "birth_place",
            "birth_date",
            "nationality",
        ]
    ]

    def normalize_blood_type(x):
        if pd.isna(x):
            return np.nan

        x = str(x)

        # wikiテンプレ・注釈・URL・括弧内を除去
        x = re.sub(r"\{\{.*?\}\}", "", x)
        x = re.sub(r"\[.*?\]", "", x)
        x = re.sub(r"\(.*?\)", "", x)
        x = re.sub(r"https?://\S+", "", x)

        # 全角・記号整理
        x = x.strip().upper()

        # 明示的な不明系
        if any(k in x for k in ["不明", "公式上不明", "型だけ", "型"]):
            return "不明"

        # 血液型判定（優先順が重要）
        if "AB" in x:
            return "AB"
        if "A" in x:
            return "A"
        if "B" in x:
            return "B"
        if "O" in x or "0" in x:
            return "O"

        return "不明"

    def normalize_numeric(x, min_val=None, max_val=None):
        if pd.isna(x):
            return np.nan

        x = str(x)

        # 右矢印があれば右側を採用（例: 170cm → 172cm）
        if "→" in x:
            x = x.split("→")[-1]

        # wikiテンプレ・注釈・URL・括弧を削除
        x = re.sub(r"\{\{.*?\}\}", "", x)
        x = re.sub(r"\[.*?\]", "", x)
        x = re.sub(r"\(.*?\)", "", x)
        x = re.sub(r"https?://\S+", "", x)

        # 数値抽出（整数 or 小数）
        m = re.search(r"\d+(\.\d+)?", x)
        if not m:
            return np.nan

        val = float(m.group())

        # 異常値フィルタ
        if min_val is not None and val < min_val:
            return np.nan
        if max_val is not None and val > max_val:
            return np.nan

        return val

    person["blood_type"] = person["blood_type"].apply(normalize_blood_type)
    person["weight"] = person["weight"].apply(
        normalize_numeric, min_val=20, max_val=300
    )
    person["height"] = person["height"].apply(
        normalize_numeric, min_val=100, max_val=250
    )
    person["birth_year"] = person["birth_year"].astype("Int64")

    output = Path(output_path) if output_path else Path(__file__).parent / "data.csv"
    person.to_csv(output, index=False)
    print(f"出力完了: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    run(output_path=args.output)

# %%
