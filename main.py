from ct.interactive.interactiveCT import InteractiveCT, CT as FastCT
from PySide2.QtCore import SIGNAL, QObject, Qt
from PySide2.QtWidgets import *
from threading import Thread
from skimage import io
from math import sqrt
from os import path
from conversion import *


class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.resize(800, 800)

        self.inputs = {
            "img": None,
            "sinogram": None,
            "result": None,
            "fast_mode": False,
            "rotate_angle": 1,
            "theta_angle": 0,
            "detectors_number": 2,
            "detectors_distance": 1,
        }

        # First layout level
        self.plots_layout = {
            "object": QGridLayout(),
            "items": {
                "img_fig": {
                    "object": QLabel(self),
                    "position": (1, 1)
                },
                "radon_fig": {
                    "object": QLabel(self),
                    "position": (1, 2)
                },
                "iradon_fig": {
                    "object": QLabel(self),
                    "position": (1, 3),
                },
                "animation_img": {
                    "object": QSlider(Qt.Horizontal),
                    "position": (2, 1),
                    "signal": "valueChanged(int)",
                    "slot": lambda x: self.setInputValue("animation_img", False if not x else True)
                },
                "animation_sinogram": {
                    "object": QSlider(Qt.Horizontal),
                    "position": (2, 2),
                    "signal": "valueChanged(int)",
                    "slot": lambda x: self.setInputValue("animation_sinogram", False if not x else True)
                },
                "fast_mode": {
                    "object": QCheckBox("Fast mode"),
                    "position": (2, 3),
                    "signal": "stateChanged(int)",
                    "slot": lambda x: self.setInputValue("fast_mode", False if not x else True)  # in the linux, for Qt, 2 means True
                },
            }
        }
        self.buttons_layout = {
            "object": QVBoxLayout(),
            "items": {
                "load": {
                    "object": QPushButton("Load"),
                    "position": 1,
                    "signal": "clicked()",
                    "slot": self.load
                },
                "run": {
                    "object": QPushButton("Run"),
                    "position": 2,
                    "signal": "clicked()",
                    "slot": self.start
                },
                "dicom": {
                    "object": QPushButton("Dicom"),
                    "position": 3,
                    "signal": "clicked()",
                    "slot": self.saveDicom
                },
            }
        }
        self.inputs_layout = {
            "object": QGridLayout(),
            "items": {
                "rotate_angle_label": {
                    "object": QLabel("Rotate angle"),
                    "position": (1, 1)
                },
                "rotate_angle": {
                    "object": QSpinBox(),
                    "position": (1, 2),
                    "signal": "valueChanged(int)",
                    "slot": lambda x: self.setInputValue("rotate_angle", x)
                },
                "theta_label": {
                    "object": QLabel("Theta angle"),
                    "position": (2, 1)
                },
                "theta": {
                    "object": QSpinBox(),
                    "position": (2, 2),
                    "signal": "valueChanged(int)",
                    "slot": lambda x: self.setInputValue("theta_angle", x)
                },
                "detectors_num_label": {
                    "object": QLabel("Detectors amount"),
                    "position": (3, 1)
                },
                "detectors_num": {
                    "object": QSpinBox(),
                    "position": (3, 2),
                    "signal": "valueChanged(int)",
                    "slot": lambda x: self.setInputValue("detectors_number", x)
                },
                "detectors_distance_label": {
                    "object": QLabel("Distance"),
                    "position": (4, 1)
                },
                "detectors_distance": {
                    "object": QSpinBox(),
                    "position": (4, 2),
                    "signal": "valueChanged(int)",
                    "slot": lambda x: self.setInputValue("detectors_distance", x)
                }
            }
        }

        # Second layout level
        self.aggregated_layouts = {
            "object": QVBoxLayout(),
            "items": {
                "first": {
                    "reference": self.plots_layout,
                    "position": 1
                },
                "second": {
                    "object": QGridLayout(),
                    "position": 2,
                    "items": {
                        "left": {
                            "reference": self.inputs_layout,
                            "position": (1, 1)
                        },
                        "empty": {
                            "object": QWidget(),
                            "position": (1, 2)
                        },
                        "right": {
                            "reference": self.buttons_layout,
                            "position": (1, 3)
                        }
                    }
                }
            }
        }

        self.plots_layout["items"]["img_fig"]["object"].setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.plots_layout["items"]["img_fig"]["object"].setScaledContents(True)
        self.plots_layout["items"]["img_fig"]["object"].setFrameStyle(QFrame.Panel | QFrame.Plain)
        self.plots_layout["items"]["img_fig"]["object"].setLineWidth(1)

        self.plots_layout["items"]["radon_fig"]["object"].setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.plots_layout["items"]["radon_fig"]["object"].setScaledContents(True)
        self.plots_layout["items"]["radon_fig"]["object"].setFrameStyle(QFrame.Panel | QFrame.Plain)
        self.plots_layout["items"]["radon_fig"]["object"].setLineWidth(1)

        self.plots_layout["items"]["iradon_fig"]["object"].setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.plots_layout["items"]["iradon_fig"]["object"].setScaledContents(True)
        self.plots_layout["items"]["iradon_fig"]["object"].setFrameStyle(QFrame.Panel | QFrame.Plain)
        self.plots_layout["items"]["iradon_fig"]["object"].setLineWidth(1)

        self.plots_layout["items"]["animation_img"]["object"].setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.plots_layout["items"]["animation_sinogram"]["object"].setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.plots_layout["items"]["animation_img"]["object"].setDisabled(True)
        self.plots_layout["items"]["animation_sinogram"]["object"].setDisabled(True)

        self.inputs_layout["items"]["theta"]["object"].setMinimum(0)
        self.inputs_layout["items"]["theta"]["object"].setMaximum(360)
        self.inputs_layout["items"]["rotate_angle"]["object"].setMinimum(1)
        self.inputs_layout["items"]["rotate_angle"]["object"].setMaximum(179)
        self.inputs_layout["items"]["detectors_num"]["object"].setMinimum(2)
        self.inputs_layout["items"]["detectors_num"]["object"].setMaximum(1000)
        self.inputs_layout["items"]["detectors_distance"]["object"].setMinimum(1)
        self.inputs_layout["items"]["detectors_distance"]["object"].setDisabled(True)

        self.buttons_layout["items"]["run"]["object"].setDisabled(True)
        self.buttons_layout["items"]["dicom"]["object"].setDisabled(True)

        self.createLayout(self.aggregated_layouts)
        self.setLayout(self.aggregated_layouts["object"])

    def createLayout(self, layout):
        def addIf(operation, widget_dict, widget_object, position):
            if "position" in widget_dict:
                try:
                    operation(widget_object, *position)
                except:
                    operation(widget_object, position)
            else:
                operation(widget_object)

        # Python checks function argument, cannot pass undefined or unnecessary args ...
        for widget in layout["items"].values():
            if "items" in widget:
                self.createLayout(widget)
                addIf(layout["object"].addLayout, widget, widget["object"], widget["position"])
            elif "reference" in widget:
                self.createLayout(widget["reference"])
                addIf(layout["object"].addLayout, widget, widget["reference"]["object"], widget["position"])
            else:  # widget
                addIf(layout["object"].addWidget, widget, widget["object"], widget["position"])
                if "signal" and "slot" in widget:
                    QObject.connect(widget["object"], SIGNAL(widget["signal"]), widget["slot"])

    def load(self):
        filename = QFileDialog.getOpenFileName(self, "Open image", ".", "Image Files (*.png *.jpg *.bmp)", )
        img = io.imread(path.expanduser(filename[0]))  # rgb

        circle_inside_img_radius = sqrt(img.shape[0] ** 2 + img.shape[1] ** 2) // 2

        fig = self.plots_layout["items"]["img_fig"]["object"]
        fig.setPixmap(array2pixmap(img))

        self.inputs["img"] = rgb2greyscale(img)
        self.inputs_layout["items"]["detectors_distance"]["object"].setMaximum(2 * circle_inside_img_radius)
        self.inputs_layout["items"]["detectors_distance"]["object"].setEnabled(True)
        self.buttons_layout["items"]["run"]["object"].setEnabled(True)

    def start(self):
        runStatus = self.buttons_layout["items"]["run"]["object"].isEnabled()
        loadStauts = self.buttons_layout["items"]["load"]["object"].isEnabled()
        dicomStatus = self.buttons_layout["items"]["dicom"]["object"].isEnabled()

        self.buttons_layout["items"]["run"]["object"].setEnabled(False)
        self.buttons_layout["items"]["load"]["object"].setEnabled(False)
        self.buttons_layout["items"]["dicom"]["object"].setEnabled(False)

        def task():
            try:
                CT = FastCT if self.inputs["fast_mode"] else InteractiveCT

                ct = CT(self.inputs["img"], self.inputs["rotate_angle"], self.inputs["theta_angle"],
                        self.inputs["detectors_number"], self.inputs["detectors_distance"])

                ct.setPrint(True)

                self.inputs["sinogram"], self.inputs["result"] = ct.run()

                if not self.inputs["fast_mode"]:
                    self.inputs["animate_img"], self.inputs["animate_sinogram"] = ct.getIntermediatePlots()

                self.plots_layout["items"]["radon_fig"]["object"].setPixmap(
                    array2pixmap(greyscale2rgb(self.inputs["sinogram"])))
                self.plots_layout["items"]["iradon_fig"]["object"].setPixmap(
                    array2pixmap(greyscale2rgb(self.inputs["result"])))

                if self.inputs["fast_mode"]:
                    self.plots_layout["items"]["animation_img"]["object"].setEnabled(True)
                    self.plots_layout["items"]["animation_sinogram"]["object"].setEnabled(True)
                else:
                    self.plots_layout["items"]["animation_img"]["object"].setDisabled(True)
                    self.plots_layout["items"]["animation_sinogram"]["object"].setDisabled(True)

            except Exception as msg:
                QErrorMessage(self).showMessage(*msg.args)
            finally:
                self.buttons_layout["items"]["run"]["object"].setEnabled(runStatus)
                self.buttons_layout["items"]["load"]["object"].setEnabled(loadStauts)
                self.buttons_layout["items"]["dicom"]["object"].setEnabled(dicomStatus)

        thread = Thread(target=task)
        thread.start()

    def setInputValue(self, key, value):
        self.inputs[key] = value

    def saveDicom(self):
        pass


def main():
    app = QApplication()
    app.setApplicationName("Computer Tomography Simulation")
    w = Window()
    w.show()
    exit(app.exec_())


if __name__ == '__main__':
    main()
