import numpy as np
from typing import Any, List, Union, Tuple, Callable
from src.ct import CT, InteractiveCT
from PySide2.QtGui import QPixmap
from PySide2.QtCore import SIGNAL, QObject, Qt
import PySide2.QtWidgets as QtWidgets
from threading import Thread
from skimage import io
from math import sqrt
from os import path
from ...conversion import Conversion
from datetime import datetime
from ..dicomWindow import *


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.resize(800, 800)
        self.ct_start_datetime: Union[None or datetime] = None

        self.inputs = {
            "img": None,
            "sinogram": None,
            "result": None,
            "fast_mode": False,
            "rotate_angle": 1,
            "theta_angle": 0,
            "detectors_amount": 2,
            "detectors_distance": 1,
            "animation_img_frames": None,
            "animation_sinogram_frames": None,
            "animation_result_frames": None,
            "animation_sinogram_actual_frame": None,
            "animation_img_actual_frame": None,
            "animation_result_actual_frame": None
        }

        # First layout level
        self.plots_layout = {
            "object": QtWidgets.QGridLayout(),
            "items": {
                "img_fig": {
                    "object": QtWidgets.QLabel(self),
                    "position": (1, 1)
                },
                "radon_fig": {
                    "object": QtWidgets.QLabel(self),
                    "position": (1, 2)
                },
                "iradon_fig": {
                    "object": QtWidgets.QLabel(self),
                    "position": (1, 3),
                },
                "animation_slider": {
                    "object": QtWidgets.QSlider(Qt.Horizontal),
                    "position": (2, 1),
                    "signal": "valueChanged(int)",
                    "slot": lambda x: self.setInputValue("animation_img_actual_frame", x / 100 if x < 99 else 1)
                                      or self.setInputValue("animation_sinogram_actual_frame", x / 100 if x < 99 else 1)
                                      or self.setInputValue("animation_result_actual_frame", x / 100 if x < 99 else 1)
                                      or self.changeFrame("radon_fig")
                                      or self.changeFrame("iradon_fig")
                },
                "fast_mode": {
                    "object": QtWidgets.QCheckBox("Fast mode"),
                    "position": (2, 3),
                    "signal": "stateChanged(int)",
                    "slot": lambda x: self.setInputValue("fast_mode", False if not x else True)
                    # in the linux, for Qt, 2 means True
                }
            }
        }
        self.buttons_layout = {
            "object": QtWidgets.QVBoxLayout(),
            "items": {
                "load": {
                    "object": QtWidgets.QPushButton("Load"),
                    "position": 1,
                    "signal": "clicked()",
                    "slot": self.loadImg
                },
                "run": {
                    "object": QtWidgets.QPushButton("Run"),
                    "position": 2,
                    "signal": "clicked()",
                    "slot": self.startComputerTomography
                },
                "save_dicom": {
                    "object": QtWidgets.QPushButton("Save Dicom"),
                    "position": 3,
                    "signal": "clicked()",
                    "slot": self.saveDicom
                },
                "show_dicom": {
                    "object": QtWidgets.QPushButton("Show Dicom"),
                    "position": 4,
                    "signal": "clicked()",
                    "slot": self.showDicom
                }
            }
        }
        self.inputs_layout = {
            "object": QtWidgets.QGridLayout(),
            "items": {
                "rotate_angle_label": {
                    "object": QtWidgets.QLabel("Rotate angle"),
                    "position": (1, 1)
                },
                "rotate_angle": {
                    "object": QtWidgets.QSpinBox(),
                    "position": (1, 2),
                    "signal": "valueChanged(int)",
                    "slot": lambda x: self.setInputValue("rotate_angle", x)
                },
                "theta_label": {
                    "object": QtWidgets.QLabel("Theta angle"),
                    "position": (2, 1)
                },
                "start_angle": {
                    "object": QtWidgets.QSpinBox(),
                    "position": (2, 2),
                    "signal": "valueChanged(int)",
                    "slot": lambda x: self.setInputValue("theta_angle", x)
                },
                "detectors_num_label": {
                    "object": QtWidgets.QLabel("Detectors amount"),
                    "position": (3, 1)
                },
                "detectors_num": {
                    "object": QtWidgets.QSpinBox(),
                    "position": (3, 2),
                    "signal": "valueChanged(int)",
                    "slot": lambda x: self.setInputValue("detectors_amount", x)
                },
                "detectors_distance_label": {
                    "object": QtWidgets.QLabel("Distance"),
                    "position": (4, 1)
                },
                "detectors_distance": {
                    "object": QtWidgets.QSpinBox(),
                    "position": (4, 2),
                    "signal": "valueChanged(int)",
                    "slot": lambda x: self.setInputValue("detectors_distance", x)
                }
            }
        }

        # Second layout level
        self.aggregated_layouts = {
            "object": QtWidgets.QVBoxLayout(),
            "items": {
                "first": {
                    "reference": self.plots_layout,
                    "position": 1
                },
                "second": {
                    "object": QtWidgets.QGridLayout(),
                    "position": 2,
                    "items": {
                        "left": {
                            "reference": self.inputs_layout,
                            "position": (1, 1)
                        },
                        "empty": {
                            "object": QtWidgets.QWidget(),
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

        self.plots_layout["items"]["img_fig"]["object"].setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.plots_layout["items"]["img_fig"]["object"].setScaledContents(True)
        self.plots_layout["items"]["img_fig"]["object"].setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Plain)
        self.plots_layout["items"]["img_fig"]["object"].setLineWidth(1)

        self.plots_layout["items"]["radon_fig"]["object"].setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.plots_layout["items"]["radon_fig"]["object"].setScaledContents(True)
        self.plots_layout["items"]["radon_fig"]["object"].setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Plain)
        self.plots_layout["items"]["radon_fig"]["object"].setLineWidth(1)

        self.plots_layout["items"]["iradon_fig"]["object"].setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.plots_layout["items"]["iradon_fig"]["object"].setScaledContents(True)
        self.plots_layout["items"]["iradon_fig"]["object"].setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Plain)
        self.plots_layout["items"]["iradon_fig"]["object"].setLineWidth(1)

        self.plots_layout["items"]["animation_slider"]["object"].setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self.plots_layout["items"]["animation_slider"]["object"].setDisabled(True)

        self.inputs_layout["items"]["start_angle"]["object"].setMinimum(0)
        self.inputs_layout["items"]["start_angle"]["object"].setMaximum(360)
        self.inputs_layout["items"]["rotate_angle"]["object"].setMinimum(1)
        self.inputs_layout["items"]["rotate_angle"]["object"].setMaximum(179)
        self.inputs_layout["items"]["detectors_num"]["object"].setMinimum(2)
        self.inputs_layout["items"]["detectors_num"]["object"].setMaximum(1000)
        self.inputs_layout["items"]["detectors_distance"]["object"].setMinimum(1)
        self.inputs_layout["items"]["detectors_distance"]["object"].setDisabled(True)

        self.buttons_layout["items"]["run"]["object"].setDisabled(True)
        self.buttons_layout["items"]["save_dicom"]["object"].setDisabled(True)

        self.createLayout(self.aggregated_layouts)
        self.setLayout(self.aggregated_layouts["object"])

    def createLayout(self, layout: Any) -> None:
        """
        Create layout via recursion.
        :param layout: layout object to create
        :return: None
        """
        def addIf(operation: Callable, widget_dict: dict, widget_object, position: Tuple[int]):
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

    def loadImg(self) -> None:
        """
        Load image to process by CT.
        :return: None
        """
        filename = QtWidgets.QFileDialog.getOpenFileName(self, "Open img", "../../..", "Image Files (*.png *.jpg *.bmp)")
        if filename[0] == '':
            return
        else:
            img = io.imread(path.expanduser(filename[0]))  # rgb

            circle_inside_img_radius = sqrt(img.shape[0] ** 2 + img.shape[1] ** 2) // 2

            fig = self.plots_layout["items"]["img_fig"]["object"]
            fig.setPixmap(Conversion().array2qpixmap(img))

            self.inputs["img"] = Conversion().rgb2greyscale(img)
            self.inputs_layout["items"]["detectors_distance"]["object"].setMaximum(2 * circle_inside_img_radius)
            self.inputs_layout["items"]["detectors_distance"]["object"].setEnabled(True)
            self.buttons_layout["items"]["run"]["object"].setEnabled(True)

            self.plots_layout["items"]["animation_slider"]["object"].setDisabled(True)

    def startComputerTomography(self) -> None:
        runStatus = self.buttons_layout["items"]["run"]["object"].isEnabled()
        loadStauts = self.buttons_layout["items"]["load"]["object"].isEnabled()

        self.buttons_layout["items"]["run"]["object"].setEnabled(False)
        self.buttons_layout["items"]["load"]["object"].setEnabled(False)
        self.buttons_layout["items"]["save_dicom"]["object"].setEnabled(False)

        # parallel task
        def task():
            try:
                selectedCT = CT if self.inputs["fast_mode"] else InteractiveCT

                ct = selectedCT(self.inputs["img"], self.inputs["rotate_angle"], self.inputs["theta_angle"],
                                self.inputs["detectors_amount"], self.inputs["detectors_distance"])

                self.ct_start_datetime = datetime.now()

                self.inputs["sinogram"], self.inputs["result"] = ct.run()
                self.normalizeImg(self.inputs["sinogram"])

                if not self.inputs["fast_mode"]:
                    frames = ct.getFrames()
                    self.inputs["animation_sinogram_frames"], self.inputs["animation_result_frames"] = frames

                    self.inputs["animation_sinogram_frames"].append(self.inputs["sinogram"])
                    self.inputs["animation_result_frames"].append(self.inputs["result"])

                    self.preprocessFrames(self.inputs["animation_sinogram_frames"])
                    self.preprocessFrames(self.inputs["animation_result_frames"])

                    self.plots_layout["items"]["animation_slider"]["object"].setEnabled(True)
                    self.plots_layout["items"]["animation_slider"]["object"].setValue(100)
                else:
                    self.plots_layout["items"]["animation_slider"]["object"].setDisabled(True)

                self.plots_layout["items"]["radon_fig"]["object"].setPixmap(
                    self.preprocessFrame(self.inputs["sinogram"]))
                self.plots_layout["items"]["iradon_fig"]["object"].setPixmap(
                    self.preprocessFrame(self.inputs["result"]))

            except Exception as msg:
                QtWidgets.QErrorMessage().showMessage(str(msg))
            finally:
                self.buttons_layout["items"]["run"]["object"].setEnabled(runStatus)
                self.buttons_layout["items"]["load"]["object"].setEnabled(loadStauts)
                self.buttons_layout["items"]["save_dicom"]["object"].setEnabled(True)

        thread = Thread(target=task)
        thread.start()

    @staticmethod
    def preprocessFrames(frames: List[np.ndarray]) -> None:
        """
        Convert greyscale frames into rgb QPixmap.
        :param frames: numpy greyscale ndarray list
        :return: None
        """
        conv = Conversion(frames[0].shape)
        for index, img in enumerate(frames):
            frames[index] = conv.array2qpixmap(conv.greyscale2rgb(img))

    @staticmethod
    def preprocessFrame(frame: np.ndarray) -> QPixmap:
        """
        Convert greyscale frame into rgb QPixmap.
        :param frame: numpy greyscale ndarray
        :return: QPixmap
        """
        conv = Conversion()
        return conv.array2qpixmap(conv.greyscale2rgb(frame))

    @staticmethod
    def normalizeImg(img: np.ndarray) -> None:
        """
        Extends image pixel value range from [0-1] to [0-255].
        :param img: image to normalize
        :return: None
        """
        img *= 255

    def setInputValue(self, key: str, value: Any) -> None:
        self.inputs[key] = value

    def changeFrame(self, label_type: str) -> None:
        """
        Load image from frames list into selected label.
        :param label_type: selected label
        :return: None
        """
        if label_type == "radon_fig":
            frame_id = self.inputs["animation_sinogram_actual_frame"] * (len(self.inputs["animation_sinogram_frames"]) - 1)
            frame_id = round(frame_id)
            frame = self.inputs["animation_sinogram_frames"][frame_id]

            fig = self.plots_layout["items"]["radon_fig"]["object"]
            fig.setPixmap(frame)
        elif label_type == "iradon_fig":
            frame_id = self.inputs["animation_result_actual_frame"] * (len(self.inputs["animation_result_frames"]) - 1)
            frame_id = round(frame_id)
            frame = self.inputs["animation_result_frames"][frame_id]

            fig = self.plots_layout["items"]["iradon_fig"]["object"]
            fig.setPixmap(frame)

    @staticmethod
    def showDicom() -> None:
        DicomShowDialog().exec_()

    def saveDicom(self) -> None:
        DicomSaveDialog(self.inputs["result"], self.ct_start_datetime).exec_()
