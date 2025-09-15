from PySide6 import QtWidgets, QtCore
import gfd.i18n as i18n

class GFDWidget(QtWidgets.QWidget):
    def __init__(self, tr):
        super().__init__()
        self.tr = tr
        self.setWindowTitle(self.tr("window_title"))
        self.resize(300, 100)

        label = QtWidgets.QLabel(self.tr("hello_world"), alignment=QtCore.Qt.AlignCenter)
        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(label)

def run(lang="es"):
    import sys
    app = QtWidgets.QApplication(sys.argv)

    tr = i18n.Translator(lang)
    w = GFDWidget(tr)
    w.show()

    sys.exit(app.exec())
