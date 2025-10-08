"""
routines.py - OS-specific installer routines

Defines a registry of install routines by OS type.
If the current OS is supported and has an associated installer,
the matching routine can be executed to perform installation steps.
"""

from gfd.core.osinfo import get_os_type


def install_ubuntu24():
    """Simulated install routine for Ubuntu 24.04."""
    print("Running Ubuntu 24.04 (DEB) installation routine...")


def install_debian():
    """Simulated install routine for Debian."""
    print("Running Debian installation routine (using Ubuntu 24 package)...")


SUPPORTED_ROUTINES = {
    "ubuntu24": install_ubuntu24,
    "debian": install_debian,
}


def run_install_routine(os_type=None):
    """
    Run the appropriate install routine for the given OS type.

    Args:
        os_type (str | None): OS key (e.g. 'ubuntu24', 'macos').
            If None, automatically detects current OS.

    Returns:
        bool: True if the OS is supported and a routine was executed, else False.
    """
    os_type = os_type or get_os_type()
    if not os_type:
        return False

    routine = SUPPORTED_ROUTINES.get(os_type)
    if not routine:
        return False

    routine()
    return True


if __name__ == "__main__":
    run_install_routine()
