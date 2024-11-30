import sys
import random
from PySide6 import QtWidgets

class VeepiaciMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("veepiaci")

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = VeepiaciMainWindow()
    widget.resize(800, 450)
    widget.show()

    sys.exit(app.exec())
