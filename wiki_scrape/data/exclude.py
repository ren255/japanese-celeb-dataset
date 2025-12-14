# %%
import pandas as pd
from pathlib import Path


def process_data(path):
    df = pd.read_csv(path)
    df["depth"] = df["depth"] + 1
    df = df.drop_duplicates(subset="pageid")

    exclude = ["アルバム", "曲", "作品", "ドラマ", "小説", "著作", "歌", "音楽", "集"]
    mask = ~df["title"].str.endswith(tuple(exclude))
    df = df[mask]

    return df


female_df = process_data(Path("wiki_sub_category_female.csv"))
female_df["sex"] = "female"

male_df = process_data(Path("wiki_sub_category_male.csv"))
male_df["sex"] = "male"

result = pd.concat([female_df, male_df], ignore_index=True)
result.to_csv("wiki_sub_category_processed.csv", index=False)

# %%
