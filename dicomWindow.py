from pydicom.dataset import Dataset, FileDataset
from pydicom import dcmread, uid
from PySide2.QtWidgets import *
from typing import Dict
from datetime import datetime
from conversion import *
from PySide2.QtCore import Qt


class DicomSaveDialog(QDialog):
    def __init__(self, img, date_time):
        super().__init__(None)
        self.setWindowTitle('Save to DICOM file')
        self.img = img
        self.date_time = date_time

        self.inputs_data: Dict[str, None or str] = {
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

    def createLayout(self):
        form = QFormLayout()

        self.name_input = QLineEdit()
        self.id_input = QLineEdit()
        self.sex_input = QComboBox()
        self.comments_input = QPlainTextEdit()
        cancel = QPushButton('Cancel')
        save = QPushButton('Save as')

        grid = QGridLayout()
        grid.addWidget(cancel, 1, 1)
        grid.addWidget(save, 1, 2)

        self.comments_input.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        self.sex_input.addItem('Male')
        self.sex_input.addItem('Female')
        cancel.clicked.connect(self.close)
        save.clicked.connect(self.save)

        form.addRow(QLabel('Patient ID'), self.id_input)
        form.addRow(QLabel('Patient name'), self.name_input)
        form.addRow(QLabel('Patient sex'), self.sex_input)
        form.addRow(QLabel('Comments'), self.comments_input)
        form.addRow(grid)
        self.setLayout(form)

    def checkInput(self):
        mb = QErrorMessage()
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

    def parseInput(self):
        if not self.checkInput():
            return False
        else:
            self.inputs_data["PatientID"] = self.id_input.text()
            self.inputs_data["PatientName"] = self.name_input.text()
            self.inputs_data["PatientSex"] = 'M' if self.sex_input.currentText() == 'Male' else 'F'
            self.inputs_data["ImageComments"] = self.comments_input.toPlainText()

            return True

    def save(self):
        if not self.parseInput():
            return
        else:
            filename = QFileDialog.getSaveFileName(self, "Save DICOM", ".", "*.dcm")[0]
            if filename == '':
                return
            else:
                file_meta = Dataset()
                file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
                file_meta.MediaStorageSOPInstanceUID = '1.2.3'
                file_meta.ImplementationClassUID = '1.2.3.4'

                ds = FileDataset(None, {}, file_meta=file_meta, preamble=b"\0" * 128)

                ds.ContentDate = f"{self.date_time.year}{self.date_time.month}{self.date_time.day}"
                ds.ContentTime = f"{self.date_time.hour}{self.date_time.minute}{self.date_time.second}"
                ds.PatientName = self.inputs_data["PatientName"]
                ds.PatientID = self.inputs_data["PatientID"]
                ds.PatientSex = self.inputs_data["PatientSex"]
                ds.ImageComments = self.inputs_data["ImageComments"]
                ds.PixelData = greyscale2rgb(self.img).tobytes()
                ds.BitsAllocated = 8
                ds.Rows = self.img.shape[0]
                ds.Columns = self.img.shape[1]
                ds.PixelRepresentation = 0
                ds.SamplesPerPixel = 1
                ds.PhotometricInterpretation = 'RGB'

                ds.is_little_endian = True
                ds.is_implicit_VR = True
                ds.save_as(f"{filename}.dcm")
                self.close()


class DicomShowDialog(QDialog):
    def __init__(self):
        super().__init__(None)
        self.setWindowTitle('Load DICOM file')
        self.setFixedSize(self.size())

        self.img = None
        self.date_time = None
        self.patientName = None
        self.patientID = None
        self.patientSex = None
        self.imageComments = None

        self.createLayout()

    def createLayout(self):
        form = QFormLayout()

        close = QPushButton('Close')
        close.clicked.connect(self.close)

        grid = QGridLayout()
        grid.addWidget(close, 1, 1)

        self.img_fig = QLabel(self)

        self.patientID_label = QTextEdit()
        self.patientName_label = QTextEdit()
        self.patientSex_label = QTextEdit()
        self.imageComments_label = QTextEdit()

        form.addRow(QLabel('Patient ID'), self.patientID_label)
        form.addRow(QLabel('Patient name'), self.patientName_label)
        form.addRow(QLabel('Patient sex'), self.patientSex_label)

        vbox = QVBoxLayout()

        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignHCenter)
        hbox.addWidget(self.img_fig)

        vbox.addLayout(form)
        vbox.addLayout(hbox)
        vbox.addWidget(self.imageComments_label)
        vbox.addLayout(grid)



        self.setLayout(vbox)

    def exec_(self):
        if self.load():
            super().exec_()

    def load(self):
        filename = QFileDialog.getOpenFileName(self, "Open DICOM", ".", "DICOM File (*.dcm)")[0]
        if filename == '':
            self.close()
            return False
        else:
            ds = dcmread(filename)
            ds.file_meta.TransferSyntaxUID = uid.ImplicitVRLittleEndian
            self.img_fig.setPixmap(array2pixmap(ds.pixel_array.copy()))
            self.date_time = datetime(int(ds.ContentDate[:4]), int(ds.ContentDate[4:5]), int(ds.ContentDate[5:7]),
                                      int(ds.ContentTime[:2]), int(ds.ContentTime[2:4]), int(ds.ContentTime[4:6]))

            self.patientName_label.setText(str(ds.PatientName))
            self.patientID_label.setText(str(ds.PatientID))
            self.patientSex_label.setText(str(ds.PatientSex))
            self.imageComments_label.setText(str(ds.ImageComments))

            return True
