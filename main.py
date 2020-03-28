from PySide2.QtWidgets import QApplication
from gui import MainWindow


def main() -> None:
    app = QApplication()
    app.setApplicationName("Computer Tomography Simulation")

    w = MainWindow()
    w.show()

    exit(app.exec_())


if __name__ == '__main__':
    main()
