# monitor/main.py
# Cross-platform Qt Application Window
#
# @author n1ghts4kura
# @date 2026-03-20
#

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow


def main():
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("SenseReAct Monitor")
    window.resize(1280, 720)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
