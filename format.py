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
from namedivider import BasicNameDivider, GBDTNameDivider

person = pd.read_csv("wiki_scrape/data/person_page.csv")

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
        "infobox",
    ]
]

person.to_csv("data.csv", index=False)

# %%
