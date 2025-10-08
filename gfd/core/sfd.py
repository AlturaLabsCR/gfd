"""
sfd.py - Installer List Parser for Soporte Firma Digital

This module is responsible for fetching and parsing the list of available
digital signature installers from the official Soporte Firma Digital website.

It retrieves both the visible installer names (from the page’s <select> element)
and the associated MD5 hashes (embedded within inline JavaScript).

The parsed results are used by the UI layer to display which installers
are available and to match system OS types to the appropriate installer.
"""

import re
import unicodedata
import requests
from bs4 import BeautifulSoup

SFD_URL = "https://soportefirmadigital.com/sfdj/dl.aspx"


def _normalize_text(text: str) -> str:
    """
    Normalize text for consistent matching.

    Steps:
        1. Remove accents and diacritics using Unicode normalization.
        2. Replace consecutive spaces with a single space.
        3. Convert to lowercase and strip leading/trailing whitespace.

    Args:
        text (str): Raw string to normalize.

    Returns:
        str: Cleaned, normalized string suitable for fuzzy matching.
    """
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", text).strip().lower()


def fetchInstallerOptions(url: str = SFD_URL):
    """
    Fetch and parse the installer list from the Soporte Firma Digital website.

    Example output:
        [
            {"name": "Usuarios Linux - Ubuntu 24.04 LTS (DEB 64bits) - 78 MB",
             "md5": "bdc871e15f2096f930b285f0ed799aa0"},
            {"name": "Usuarios Windows JCOP3 - 189 MB",
             "md5": "596c347e409d00388c3c1ee0a72b96c0"},
            ...
        ]

    Args:
        url (str, optional): Target URL to fetch. Defaults to SFD_URL.

    Returns:
        list[dict]: Each dict contains:
            - "name" (str): Installer display name.
            - "md5" (str | None): MD5 checksum (if found), else None.
    """
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
    except requests.RequestException:
        # Network error, timeout, or unreachable server
        return []

    soup = BeautifulSoup(r.text, "html.parser")

    # Extract installer names from the dropdown list
    installers = [
        opt.text.strip()
        for opt in soup.select("#ctl00_certContents_ddlInstaladores option")
    ]
    if not installers:
        return []

    # Parse embedded JavaScript to extract name, MD5 mapping
    md5s = {}
    for name, md5 in re.findall(
        r"text\s*==\s*'([^']+)'.*?MD5\s*[:=]\s*([A-Za-z0-9]+)",
        r.text,
        re.DOTALL,
    ):
        md5 = md5.lower()
        if re.fullmatch(r"[0-9a-f]{32}", md5):  # Only valid 32-character MD5
            md5s[_normalize_text(name)] = md5

    # Merge name list with MD5 map
    results = []
    for inst in installers:
        n = _normalize_text(inst)
        md5 = md5s.get(n)

        # Try fuzzy match if exact normalization key not found
        if not md5:
            for key, val in md5s.items():
                if key in n or n in key:
                    md5 = val
                    break

        results.append({"name": inst, "md5": md5})

    return results


if __name__ == "__main__":
    """
    Fetch and print all installers to stdout.
    """
    installers = fetchInstallerOptions()
    print(f"Fetched {len(installers)} installers from {SFD_URL}\n")
    for item in installers:
        print(f"{item['name']:<70}  MD5={item['md5'] or 'N/A'}")
