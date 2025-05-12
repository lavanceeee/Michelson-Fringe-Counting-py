from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

#启动main_window.py
if __name__ == "__main__":
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec()
