import sys

def main():
    from PySide6.QtWidgets import QApplication
    from gui import Program2
    app = QApplication.instance() or QApplication(sys.argv)
    window = Program2()
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())