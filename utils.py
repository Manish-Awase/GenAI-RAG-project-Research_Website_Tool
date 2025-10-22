import os
import shutil
from pathlib import Path
import requests


def reset_vectorstore(vectorstore_path: Path):
    """
    Deletes and recreates the vectorstore directory to reset ChromaDB.
    """

    try:

        if vectorstore_path.exists():
            shutil.rmtree(vectorstore_path)
            print(f"🧹 Cleared contents of: {vectorstore_path}")
        else:
            print(f"ℹ️ No existing vectorstore found at: {vectorstore_path}")

        vectorstore_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 Recreated vectorstore directory at: {vectorstore_path}")

    except Exception as e:
        print(f"❌ Error resetting vectorstore: {e}")


def is_valid_url(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
    }
    try:
        response = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
        return response.status_code < 400
    except requests.RequestException:
        return False



def validate_urls(url_list):
    valid = []
    for url in url_list:
        if not url.strip():
            continue
        if is_valid_url(url):
            valid.append(url)
        else:
            print(f"Invalid or unreachable: {url}")
    return valid
