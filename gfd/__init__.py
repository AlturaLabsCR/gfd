from PySide6 import QtWidgets, QtCore
import gfd.i18n as i18n
from gfd import sfd


class GFDWidget(QtWidgets.QWidget):
    def __init__(self, tr):
        super().__init__()
        self.tr = tr
        self.setWindowTitle(self.tr("window_title"))
        self.resize(400, 220)

        self.label = QtWidgets.QLabel(
            self.tr("hello_world"),
            alignment=QtCore.Qt.AlignmentFlag.AlignCenter,
        )

        self.combo = QtWidgets.QComboBox()
        self.combo.addItem(self.tr("loading_installers") + "…")

        self.refresh_btn = QtWidgets.QPushButton("⟳ " + self.tr("refresh"))
        self.refresh_btn.clicked.connect(self.reload_installers)

        combo_layout = QtWidgets.QHBoxLayout()
        combo_layout.addWidget(self.combo)
        combo_layout.addWidget(self.refresh_btn)

        self.md5_label = QtWidgets.QLabel(
            "", alignment=QtCore.Qt.AlignmentFlag.AlignCenter
        )

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addLayout(combo_layout)
        layout.addWidget(self.md5_label)

        self.combo.currentIndexChanged.connect(self.on_selection_changed)

        QtCore.QTimer.singleShot(0, self.load_installers_async)

    def reload_installers(self):
        """Triggered by the refresh button."""
        self.refresh_btn.setEnabled(False)
        self.combo.clear()
        self.combo.addItem(self.tr("loading_installers") + "…")
        self.load_installers_async()

    def load_installers_async(self):
        """Fetch installer options without freezing the UI."""
        self.thread = QtCore.QThread()
        self.worker = SFDWorker()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.result_ready.connect(self.populate_installers)

        self.thread.start()

    @QtCore.Slot(list)
    def populate_installers(self, installers):
        self.refresh_btn.setEnabled(True)
        self.combo.clear()

        if not installers:
            self.combo.addItem(self.tr("no_installers_found"))
            self.md5_label.setText("")
            return

        self.installers = installers
        for item in installers:
            self.combo.addItem(item["name"], item["md5"])

        self.combo.setCurrentIndex(0)
        self.on_selection_changed(0)

    @QtCore.Slot(int)
    def on_selection_changed(self, index):
        if not hasattr(self, "installers") or not self.installers:
            return
        md5 = self.combo.currentData()
        name = self.combo.currentText()
        self.md5_label.setText(f"<b>{name}</b><br>MD5: <code>{md5 or 'N/A'}</code>")


class SFDWorker(QtCore.QObject):
    """Background worker to fetch installers safely."""

    finished = QtCore.Signal()
    result_ready = QtCore.Signal(list)

    @QtCore.Slot()
    def run(self):
        data = sfd.fetchInstallerOptions()
        self.result_ready.emit(data)
        self.finished.emit()


def run(lang="es"):
    import sys

    app = QtWidgets.QApplication(sys.argv)
    tr = i18n.Translator(lang)
    w = GFDWidget(tr)
    w.show()
    sys.exit(app.exec())
