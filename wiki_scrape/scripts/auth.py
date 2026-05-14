import os
from typing import Optional


def get_wiki_headers() -> dict:
    KAGGLER = os.environ.get("KAGGLE_KERNEL_RUN_TYPE", "") != ""
    if KAGGLER:
        token = _from_kaggle()
    else:
        token = _from_dotenv()

    headers = {
        "User-Agent": "WikiResearchBot/1.0 (+https://rentoda.com)",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"
        print("[AUTH] 認証済みヘッダーを使用")
    else:
        print("[AUTH] 未認証モードで実行（rate limit: 200 req/min）")

    return headers


def _from_kaggle() -> Optional[str]:
    try:
        from kaggle_secrets import UserSecretsClient

        token = UserSecretsClient().get_secret("WIKI_ACCESS_TOKEN")
        print("[AUTH] Kaggle Secretsからトークン取得")
        return token
    except Exception:
        return None


def _from_dotenv() -> Optional[str]:
    try:
        from dotenv import load_dotenv

        load_dotenv()
        token = os.environ.get("WIKI_ACCESS_TOKEN")
        if token:
            print("[AUTH] .envからトークン取得")
            return token
    except ImportError:
        pass
    return None
