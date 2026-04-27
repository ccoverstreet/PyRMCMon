import sys
from PyQt6.QtWidgets import QApplication
import pyrmcmon.gui as prm




def main():
    app = QApplication(sys.argv)
    window = prm.MainWindow()

    window.show()

    app.exec()


if __name__ == "__main__":
    main()
