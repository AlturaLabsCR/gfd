from PySide6 import QtWidgets
from gfd.ui.main_window import GFDWidget
from gfd.i18n import Translator


def run(lang="es"):
    import sys

    app = QtWidgets.QApplication(sys.argv)
    tr = Translator(lang)
    window = GFDWidget(tr)
    window.show()
    sys.exit(app.exec())
