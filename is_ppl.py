# %%
import spacy

nlp = spacy.load("ja_ginza")


def is_person_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "Person":
            return True
    return False


# %%
# テスト例（Wikipediaリンク部分を除き名前のみ抽出）
examples = [
    "日本の男優一覧",
    "キネマ旬報20世紀の映画スター",
    "毎日映画コンクール男優助演賞",
    "毎日映画コンクール男優主演賞",
    "ARCHE",
    "R-指定 (ラッパー)",
    "アイ・ジョージ",
    "逢笠恵祐",
    "相ヶ瀬龍史",
    "愛川欽也",
    "相川裕滋",
    "愛甲猛",
    "あいざき進也",
    "相澤一成",
    "相沢治夫",
    "逢沢優",
]

for ex in examples:
    print(f"{ex}: {is_person_name(ex)}")

# %%
