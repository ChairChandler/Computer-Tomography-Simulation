from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backend_bases import RendererBase
from matplotlib.figure import Figure
from PySide2.QtWidgets import *
from PySide2.QtCore import SIGNAL, QObject
from ct.interactive.interactiveCT import InteractiveCT as CT
from os import path
from skimage import io


class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.resize(800, 800)

        self.inputs = {
            "img": None,
            "animate_img": False,
            "animate_sinogram": False,
            "rotate_angle": 0,
            "theta_angle": 0,
            "detectors_number": 0,
            "detectors_distance": 0,
            "animation_interval": 0.001
        }

        self.ct = CT(self.inputs["img"], self.inputs["rotate_angle"], self.inputs["theta_angle"],
                     self.inputs["detectors_number"], self.inputs["detectors_distance"])

        self.iradon_fig = Figure()

        # First layout level
        self.plots_layout = {
            "object": QGridLayout(),
            "items": {
                "img_fig": {
                    "object": FigureCanvas(self.ct.img_fig),
                    "position": (1, 1)
                },
                "radon_fig": {
                    "object": FigureCanvas(self.ct.sinogram_fig),
                    "position": (1, 2)
                },
                "iradon_fig": {
                    "object": FigureCanvas(self.iradon_fig),
                    "position": (1, 3)
                },
                "animate_img": {
                    "object": QCheckBox("Animate Image"),
                    "position": (2, 1),
                    "signal": "stateChanged(int)",
                    "slot": lambda x:   self.setInputValue("animate_img", False if not x else True)  # on the linux for Qt 2 means True
                },
                "animate_sin": {
                    "object": QCheckBox("Animate Sinogram"),
                    "position": (2, 2),
                    "signal": "stateChanged(int)",
                    "slot": lambda x: self.setInputValue("animate_sinogram", False if not x else True)
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
                    "signal": "valueChanged()",
                    "slot": lambda x: self.setInputValue("rotate_angle", x)
                },
                "theta_label": {
                    "object": QLabel("Theta angle"),
                    "position": (2, 1)
                },
                "theta": {
                    "object": QSpinBox(),
                    "position": (2, 2),
                    "signal": "valueChanged()",
                    "slot": lambda x: self.setInputValue("theta_angle", x)
                },
                "detectors_num_label": {
                    "object": QLabel("Detectors amount"),
                    "position": (3, 1)
                },
                "detectors_num": {
                    "object": QSpinBox(),
                    "position": (3, 2),
                    "signal": "valueChanged()",
                    "slot": lambda x: self.setInputValue("detectors_number", x)
                },
                "detectors_distance_label": {
                    "object": QLabel("Distance"),
                    "position": (4, 1)
                },
                "detectors_distance": {
                    "object": QSpinBox(),
                    "position": (4, 2),
                    "signal": "valueChanged()",
                    "slot": lambda x: self.setInputValue("detectors_distance", x)
                },
                "animation_interval_label": {
                    "object": QLabel("Animation interval"),
                    "position": (5, 1)
                },
                "animation_interval": {
                    "object": QSpinBox(),
                    "position": (5, 2),
                    "signal": "valueChanged()",
                    "slot": lambda x: self.setInputValue("animation_interval", x)
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
        self.inputs["img"] = io.imread(path.expanduser(filename[0]), as_gray=True)
        ax = self.ct.img_fig.add_subplot(1, 1, 1)
        ax.imshow(self.inputs["img"], cmap="gray")
        self.ct.img_fig.canvas.draw()

    def start(self):
        try:
            self.ct.img = self.inputs["img"]
            self.ct.rotate_angle = self.inputs["rotate_angle"]
            self.ct.theta = self.inputs["theta_angle"]
            self.ct.detectors_number = self.inputs["detectors_number"]
            self.ct.far_detectors_distance = self.inputs["detectors_distance"]

            self.ct.interactive(self.inputs["animate_img"], self.inputs["animate_sinogram"], self.inputs["animation_interval"])  # set drawing image and sinogram every iteration
            self.ct.setCmap('gray')
            self.ct.run()
        except Exception as msg:
            QErrorMessage(self).showMessage(*msg.args)

    def setInputValue(self, key, value):
        print(key, value)
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
