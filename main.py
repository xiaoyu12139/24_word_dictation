import sys
from PyQt5.QtWidgets import QApplication
from MainWindow import MainWindow
from PyQt5.QtGui import QIcon

if __name__ == '__main__':
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("6666")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
