from mainWindow import MainWindow
from PySide2.QtWidgets import QApplication
#from dicomWindow import *

def main():
    app = QApplication()
    app.setApplicationName("Computer Tomography Simulation")

    w = MainWindow()
    #w = DicomSaveDialog()
    w.show()

    exit(app.exec_())


if __name__ == '__main__':
    main()
