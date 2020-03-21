from pydicom import dcmread, dcmwrite
from pydicom.dataset import Dataset, FileDataset
from PySide2.QtWidgets import *
from datetime import date


class DicomSaveDialog(QDialog):
    def __init__(self):
        super().__init__()
        form = QFormLayout()
        name = QLabel('Name')

        self.inputs = {
            "PatientID": None,
            "PatientName": None,
            "PatientBirthDate": None,
            "PatientSex": None,
            "ContentDate": None
        }
        


        form.addWidget(name)
        self.setLayout(form)
