import time
import re
import unicodedata
from gfd.core import sfd

SUPPORTED_INSTALLERS = [
    {
        "os_type": "ubuntu24",
        "name": "Usuarios Linux - Ubuntu 24.04 LTS (DEB 64bits) - 78 MB",
        "md5": "bdc871e15f2096f930b285f0ed799aa0",
    },
    {
        "os_type": "debian",
        "name": "Usuarios Linux - Ubuntu 24.04 LTS (DEB 64bits) - 78 MB",
        "md5": "bdc871e15f2096f930b285f0ed799aa0",
    },
]


def _normalize(t):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKD", t).lower()).strip()


def _fetch(max_attempts=3, delay=2):
    for i in range(max_attempts):
        data = sfd.fetchInstallerOptions()

        if data:
            return data

        if i < max_attempts - 1:
            time.sleep(delay)

    return []


def get_available_installers(os_type, installers=None):
    """
    Return a list of confirmed available installers for the given OS type.

    If an installer is listed, it means that for a given OS type:
        - There is a supported installation routine.
        - There is a downloadable archive from Soporte Firma Digital.
    """
    src = installers or SUPPORTED_INSTALLERS
    locals_ = [i for i in src if i["os_type"] == os_type]

    if not locals_:
        return []

    remote = _fetch()

    if not remote:
        return []

    rmap = {_normalize(r["name"]): r.get("md5") for r in remote}
    confirmed = []

    for local in locals_:
        lname, lmd5 = (
            _normalize(local["name"]),
            (local.get("md5") or "").lower() or None,
        )
        rmd5 = rmap.get(lname)

        if (lmd5 == rmd5) or (lmd5 is None and rmd5 is None):
            confirmed.append((local["name"], lmd5))

    return confirmed


# TODO: Routine to check for installed version
def get_installed_version():
    """
    Return the current installed version data, or empty if not installed.
    """
    return []  # Return always empty for now


if __name__ == "__main__":
    os_type = "debian"
    print(f"=== TEST: {os_type.upper()} Installer Validation ===")
    confirmed = get_available_installers(os_type)
    print(
        f"{len(confirmed)} confirmed installer(s):"
        if confirmed
        else "No confirmed installers found."
    )

    for n, m in confirmed:
        print(f" - {n} (MD5={m or 'N/A'})")

    installed = get_installed_version()

    if not installed:
        print("Status: NOT INSTALLED")
    else:
        print(f"Installed: {installed[0]} MD5={installed[1]}")
