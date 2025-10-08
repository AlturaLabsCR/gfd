import platform
import re
from pathlib import Path


def _read_os_release():
    """Read and parse /etc/os-release or /usr/lib/os-release if available."""
    paths = [Path("/etc/os-release"), Path("/usr/lib/os-release")]
    data = {}

    for path in paths:
        if path.exists():
            try:
                for line in path.read_text(encoding="utf-8").splitlines():
                    if "=" in line:
                        key, val = line.split("=", 1)
                        data[key.strip()] = val.strip().strip('"')
                break
            except Exception:
                pass
    return data


def get_os_type():
    """
    Detect and return a simple OS type string.

    Returns one of:
      'macos', 'windows', 'ubuntu24', 'ubuntu22', 'ubuntu20',
      'debian', 'arch', 'rpm', or None if unsupported.
    """
    system = platform.system().lower()
    os_type = None

    if system == "darwin":
        os_type = "macos"

    elif system == "windows":
        os_type = "windows"

    elif system == "linux":
        info = _read_os_release()
        id_name = info.get("ID", "").lower()
        version_id = info.get("VERSION_ID", "")

        # Ubuntu
        if id_name == "ubuntu":
            if version_id.startswith("24"):
                os_type = "ubuntu24"
            elif version_id.startswith("22"):
                os_type = "ubuntu22"
            elif version_id.startswith("20"):
                os_type = "ubuntu20"

        # Debian (11 or newer supported)
        elif id_name == "debian":
            try:
                version_num = int(re.findall(r"\d+", version_id or "0")[0])
            except IndexError:
                version_num = 0
            if version_num >= 11:
                os_type = "debian"

        # Arch / RPM-based
        elif "arch" in id_name:
            os_type = "arch"
        elif id_name in ["fedora", "rhel", "centos", "rocky", "alma", "opensuse"]:
            os_type = "rpm"

    return os_type


if __name__ == "__main__":
    print("Detected OS type:", get_os_type() or "NOT SUPPORTED")
