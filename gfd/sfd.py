import re
import unicodedata
import requests
from bs4 import BeautifulSoup

SFD_URL = "https://soportefirmadigital.com/sfdj/dl.aspx"


def _normalize_text(text: str) -> str:
    """Internal: remove accents, extra spaces, and lowercase."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", text).strip().lower()


def fetchInstallerOptions(url: str = SFD_URL):
    """
    Fetch the list of installer options from the given Soporte Firma Digital page.

    Args:
        url (str, optional): Page URL to fetch. Defaults to SFD_URL.

    Returns:
        list[dict]: Each item is {'name': <str>, 'md5': <str or None>}
    """
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
    except requests.RequestException:
        return []

    soup = BeautifulSoup(r.text, "html.parser")

    installers = [
        opt.text.strip()
        for opt in soup.select("#ctl00_certContents_ddlInstaladores option")
    ]
    if not installers:
        return []

    # Extract valid MD5 hashes from embedded JavaScript
    md5s = {}
    for name, md5 in re.findall(
        r"text\s*==\s*'([^']+)'.*?MD5\s*[:=]\s*([A-Za-z0-9]+)",
        r.text,
        re.DOTALL,
    ):
        md5 = md5.lower()
        if re.fullmatch(r"[0-9a-f]{32}", md5):  # only valid 32-char hex hashes
            md5s[_normalize_text(name)] = md5

    results = []
    for inst in installers:
        n = _normalize_text(inst)
        md5 = md5s.get(n)
        if not md5:
            for key, val in md5s.items():
                if key in n or n in key:
                    md5 = val
                    break
        results.append({"name": inst, "md5": md5})

    return results


if __name__ == "__main__":
    for item in fetchInstallerOptions():
        print(f"{item['name']:<70}  MD5={item['md5'] or 'N/A'}")
