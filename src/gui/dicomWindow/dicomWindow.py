import sys

sys.path.append("..")

import numpy as np
from datetime import datetime
from typing import Dict
from conversion import Conversion
from PySide2.QtCore import Qt
import PySide2.QtWidgets as QtWidgets
import pydicom as pd
import pydicom.uid


class DicomSaveDialog(QtWidgets.QDialog):
    """
    Class for save patient informations to DICOM file.
    """

    def __init__(self, img: np.ndarray, date_time: datetime):
        """
        :param img: image to save
        :param date_time: ct operation start datetime
        """
        super().__init__(None)
        self.setWindowTitle('Save to DICOM file')
        self.img = img
        self.date_time = date_time

        self.input_data: Dict[str, None or str] = {
            'PatientID': None,
            'PatientName': None,
            'PatientSex': None,
            'ImageComments': None
        }

        self.name_input = None
        self.id_input = None
        self.sex_input = None
        self.comments_input = None

        self.createLayout()

    def createLayout(self) -> None:
        self.name_input = QtWidgets.QLineEdit()
        self.id_input = QtWidgets.QLineEdit()
        self.sex_input = QtWidgets.QComboBox()
        self.comments_input = QtWidgets.QPlainTextEdit()

        self.comments_input.setLineWrapMode(QtWidgets.QPlainTextEdit.WidgetWidth)
        self.sex_input.addItem('Male')
        self.sex_input.addItem('Female')

        cancel = QtWidgets.QPushButton('Cancel')
        save = QtWidgets.QPushButton('Save as')

        cancel.clicked.connect(self.close)
        save.clicked.connect(self.save)

        grid = QtWidgets.QGridLayout()
        grid.addWidget(cancel, 1, 1)
        grid.addWidget(save, 1, 2)

        form = QtWidgets.QFormLayout()
        form.addRow(QtWidgets.QLabel('Patient ID'), self.id_input)
        form.addRow(QtWidgets.QLabel('Patient name'), self.name_input)
        form.addRow(QtWidgets.QLabel('Patient sex'), self.sex_input)
        form.addRow(QtWidgets.QLabel('Comments'), self.comments_input)
        form.addRow(grid)
        self.setLayout(form)

    def validateInput(self) -> bool:
        mb = QtWidgets.QErrorMessage()
        mb.setModal(True)
        if self.id_input.text() == '':
            mb.showMessage('Patient ID cannot be empty.')
            mb.exec_()
            return False
        elif self.name_input.text() == '':
            mb.showMessage('Patient name cannot be empty.')
            mb.exec_()
            return False

        return True

    def parseInput(self) -> bool:
        if not self.validateInput():
            return False
        else:
            self.input_data["PatientID"] = self.id_input.text()
            self.input_data["PatientName"] = self.name_input.text()
            self.input_data["PatientSex"] = 'M' if self.sex_input.currentText() == 'Male' else 'F'
            self.input_data["ImageComments"] = self.comments_input.toPlainText()

            return True

    def save(self) -> None:
        """
        Save input data into DICOM file.
        :return: None
        """
        if not self.parseInput():
            return
        else:
            filename = QtWidgets.QFileDialog.getSaveFileName(self, "Save DICOM", "../../..", "*.dcm")[0]
            if filename == '':
                return
            else:
                fm = pd.Dataset()

                # CT Image Storage
                fm.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
                fm.MediaStorageSOPInstanceUID = pd.uid.generate_uid()
                fm.TransferSyntaxUID = pd.uid.ExplicitVRLittleEndian
                fm.ImplementationClassUID = pd.uid.generate_uid()

                ds = pd.FileDataset(None, {})

                ds.file_meta = fm

                # CT Image Storage
                ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
                ds.SOPInstanceUID = pd.uid.generate_uid()

                ds.ContentDate = f"{self.date_time.year:04}{self.date_time.month:02}{self.date_time.day:02}"
                ds.ContentTime = f"{self.date_time.hour:02}{self.date_time.minute:02}{self.date_time.second:02}"

                ds.StudyInstanceID = pd.uid.generate_uid()
                ds.SeriesInstanceID = pd.uid.generate_uid()

                ds.Modality = "CT"
                ds.ConversionType = 'WSD'  # workstation
                ds.ImageType = r"ORIGINAL\PRIMARY\AXIAL"

                ds.PatientName = self.input_data["PatientName"]
                ds.PatientID = self.input_data["PatientID"]
                ds.PatientSex = self.input_data["PatientSex"]
                ds.ImageComments = self.input_data["ImageComments"]

                ds.PixelData = self.img.astype(np.uint8).tobytes()
                ds.Rows, ds.Columns = self.img.shape
                ds.SamplesPerPixel = 1
                ds.PixelRepresentation = 0
                ds.PhotometricInterpretation = "MONOCHROME2"
                ds.BitsAllocated, ds.BitsStored = 8, 8
                ds.HighBit = 7

                ds.is_little_endian = True
                ds.is_implicit_VR = False

                ds.save_as(f"{filename}.dcm", write_like_original=False)
                self.close()


class DicomShowDialog(QtWidgets.QDialog):
    """
    Class for show DICOM file structure.
    """

    def __init__(self):
        super().__init__(None)
        self.setWindowTitle('Load DICOM file')

        self.img = None
        self.ct_date_time = None
        self.img_fig = None
        self.patient_ID = None
        self.patient_name = None
        self.patient_sex = None
        self.image_comments = None

        self.createLayout()

    def createLayout(self) -> None:
        self.ct_date_time = QtWidgets.QLabel()
        self.patient_ID = QtWidgets.QTextEdit()
        self.patient_name = QtWidgets.QTextEdit()
        self.patient_sex = QtWidgets.QTextEdit()

        form = QtWidgets.QFormLayout()
        form.addRow(self.ct_date_time)
        form.addRow(QtWidgets.QLabel('Patient ID'), self.patient_ID)
        form.addRow(QtWidgets.QLabel('Patient name'), self.patient_name)
        form.addRow(QtWidgets.QLabel('Patient sex'), self.patient_sex)

        self.img_fig = QtWidgets.QLabel(self)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setAlignment(Qt.AlignHCenter)
        hbox.addWidget(self.img_fig)

        self.image_comments = QtWidgets.QTextEdit()

        close = QtWidgets.QPushButton('Close')
        close.clicked.connect(self.close)

        grid = QtWidgets.QGridLayout()
        grid.addWidget(close, 1, 1)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(form)
        vbox.addLayout(hbox)
        vbox.addWidget(self.image_comments)
        vbox.addLayout(grid)

        self.setLayout(vbox)

    def exec_(self) -> None:
        if self.load():
            super().exec_()

    def load(self) -> bool:
        """
        Load DICOM file and insert file data into widgets.
        :return: bool
        """
        filename = QtWidgets.QFileDialog.getOpenFileName(self, "Open DICOM", "../../..", "DICOM File (*.dcm)")[0]
        if filename == '':
            self.close()
            return False
        else:
            ds = pydicom.dcmread(filename)
            ds.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
            self.img_fig.setPixmap(Conversion().array2qpixmap(ds.pixel_array))

            year, month, day = ds.ContentDate[:4], ds.ContentDate[4:6], ds.ContentDate[6:8]
            hour, minute, second = ds.ContentTime[:2], ds.ContentTime[2:4], ds.ContentTime[4:6]

            self.ct_date_time.setText(f"{year}/{month}/{day} {hour}:{minute}:{second}")
            self.patient_name.setText(str(ds.PatientName))
            self.patient_ID.setText(str(ds.PatientID))
            self.patient_sex.setText(str(ds.PatientSex))
            self.image_comments.setText(str(ds.ImageComments))

            return True
