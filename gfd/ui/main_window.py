from PySide6 import QtWidgets, QtCore
from gfd.core.osinfo import get_os_type
from gfd.core.installers import get_available_installers, get_installed_version


def check_installation_status():
    """
    Determine system support and installer availability.

    Returns:
        (installed: [version, md5] or [],
         available: list[[version, md5]],
         recommended: [version, md5] or None)
    """
    os_type = get_os_type()

    if not os_type:
        return [], [], None

    available = get_available_installers(os_type)
    installed = get_installed_version()

    if not available:
        return installed, [], None

    # Assume the first installer in the list is the recommended one
    recommended = available[0]

    return installed, available, recommended


class GFDWidget(QtWidgets.QWidget):
    def __init__(self, tr):
        super().__init__()
        self.tr = tr
        self.setWindowTitle(self.tr("window_title"))
        self.resize(600, 400)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # Card container
        self.card = QtWidgets.QFrame()
        self.card_layout = QtWidgets.QVBoxLayout(self.card)
        self.card_layout.setSpacing(12)

        # Title
        self.title = QtWidgets.QLabel(self.tr("window_title"))
        self.title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.card_layout.addWidget(self.title)

        # Content area
        self.content_area = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content_area)
        self.content_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.card_layout.addWidget(self.content_area)

        # Footer
        self.footer = QtWidgets.QHBoxLayout()
        self.footer.addStretch()
        self.refresh_btn = QtWidgets.QPushButton("⟳")
        self.refresh_btn.setFixedWidth(36)
        self.refresh_btn.clicked.connect(self.refresh_state)
        self.footer.addWidget(self.refresh_btn)
        self.card_layout.addLayout(self.footer)

        self.main_layout.addWidget(self.card)
        self.setStyleSheet("""
            QPushButton {
                border-radius: 8px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton[primary="true"] {
                background-color: #2f80ed;
                color: white;
            }
            QPushButton[primary="true"]:disabled {
                background-color: #a0c4ff;
            }
            QLabel, QComboBox {
                font-size: 16px;
            }
        """)

        self.states = ["not_installed", "installed", "update_available"]
        self.current_state = 0

        # Run initial refresh
        self.refresh_state()

    # --- LOGIC ---

    def refresh_state(self):
        """Fetch installer list and determine status."""
        self.refresh_btn.setEnabled(False)
        self.clear_content()
        loading_label = QtWidgets.QLabel(self.tr("loading_installers") + "…")
        loading_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(loading_label)

        QtCore.QTimer.singleShot(150, self._refresh_check)

    def _refresh_check(self):
        """Evaluate OS type, installed version, and available installers."""
        self.installed, self.available, self.recommended = check_installation_status()

        print("\n=== INSTALLER STATUS DEBUG ===")
        if not self.available:
            print("No available installers for this OS.")
        else:
            for i, (name, md5) in enumerate(self.available, start=1):
                print(f"{i:2d}. {name:<70}  MD5={md5 or 'N/A'}")
        print("==============================\n")

        # 🧩 Print simulated installed state
        if not self.installed:
            print("→ Status: NOT INSTALLED")
        else:
            print(f"→ Installed: {self.installed[0]}  MD5={self.installed[1]}")

        if not self.available:
            self.show_error()
        elif not self.recommended:
            print("→ Decision: OS NOT SUPPORTED")
            self.show_error()
        elif not self.installed:
            print(f"→ Decision: NOT INSTALLED (Recommended: {self.recommended[0]})")
            self.set_state("not_installed")
        else:
            installed_tuple = tuple(self.installed)
            available_tuples = [tuple(a) for a in self.available]

            if installed_tuple in available_tuples:
                print("→ Decision: INSTALLED (latest version matches)")
                self.set_state("installed")
            else:
                print("→ Decision: UPDATE AVAILABLE (installed not in available list)")
                self.set_state("update_available")

        self.refresh_btn.setEnabled(True)

    def clear_content(self):
        """Remove all widgets from content area."""
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    # --- UI STATES ---

    def update_state(self):
        """Render the current UI state."""
        self.clear_content()
        state = self.states[self.current_state]

        if state == "not_installed":
            self.show_not_installed()
        elif state == "installed":
            self.show_installed()
        elif state == "update_available":
            self.show_update_available()

    def show_error(self):
        """Shown when no installer data is available."""
        self.clear_content()
        lbl = QtWidgets.QLabel(self.tr("no_installers_found"))
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(lbl)

    def show_not_installed(self):
        recommended_name = self.recommended[0] if self.recommended else "?"
        lbl = QtWidgets.QLabel(
            f"{self.tr('no_install_message')}<br>"
            f"{self.tr('recommended_version')}<br><b>{recommended_name}</b>"
        )
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(lbl)

        btn = QtWidgets.QPushButton(self.tr("install"))
        btn.setProperty("primary", True)
        self.content_layout.addWidget(btn)

        combo = QtWidgets.QComboBox()
        for version, md5 in self.available:
            combo.addItem(f"{version} (MD5: {md5 or 'N/A'})")
        self.content_layout.addWidget(combo)

    def show_installed(self):
        version, md5 = self.installed
        lbl = QtWidgets.QLabel(
            f"{self.tr('installed_version')}<br><b>{version}</b><br>MD5: {md5 or 'N/A'}"
        )
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(lbl)

        btn = QtWidgets.QPushButton(self.tr("latest_version_installed"))
        btn.setEnabled(False)
        self.content_layout.addWidget(btn)

    def show_update_available(self):
        version, md5 = self.installed
        lbl = QtWidgets.QLabel(
            f"{self.tr('installed_version')}<br><b>{version}</b><br>MD5: {md5 or 'N/A'}"
        )
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(lbl)

        btn = QtWidgets.QPushButton(self.tr("update_digital_signature"))
        btn.setProperty("primary", True)
        self.content_layout.addWidget(btn)

        combo = QtWidgets.QComboBox()
        for version, md5 in self.available:
            combo.addItem(f"{version} (MD5: {md5 or 'N/A'})")
        self.content_layout.addWidget(combo)

    def set_state(self, state):
        if state in self.states:
            self.current_state = self.states.index(state)
            self.update_state()
