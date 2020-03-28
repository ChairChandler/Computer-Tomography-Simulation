from typing import Tuple
import numpy as np
from PySide2.QtGui import QPixmap, QImage, QColor


class Conversion:
    def __init__(self, shape: Tuple[int, int] = None):
        if shape is not None:
            self.qimage = QImage(shape[1], shape[0], QImage.Format_RGB16)
            self.height, self.width = shape[:2]
            self.array_greyscale = np.ndarray(shape)
            self.array_rgb = np.ndarray((*shape, 3))
            self.is_init = True
        else:
            self.is_init = False

    def array2qpixmap(self, img: np.ndarray) -> QPixmap:
        img8 = img.astype(np.uint8)
        if self.is_init:
            height, width = self.height, self.width
            img = self.qimage
        else:
            height, width = img8.shape[:2]
            img = QImage(width, height, QImage.Format_RGB16)

        color = QColor()

        if len(img8.shape) == 2:
            for x in range(width):
                for y in range(height):
                    color.setHsv(0, 0, img8[y][x])
                    img.setPixel(x, y, color.rgb())
        else:
            for x in range(width):
                for y in range(height):
                    color.setRgb(*img8[y][x])
                    img.setPixel(x, y, color.rgb())

        return QPixmap(img)

    def rgb2greyscale(self, img: np.ndarray) -> np.ndarray:
        if len(img.shape) != 3:
            return img

        if self.is_init:
            array = self.array_greyscale
        else:
            array = np.ndarray(shape=(img.shape[0], img.shape[1]))

        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                array[i, j] = img[i, j, 0]

        return array

    def greyscale2rgb(self, img: np.ndarray) -> np.ndarray:
        if self.is_init:
            array = self.array_rgb
        else:
            array = np.ndarray(shape=(img.shape[0], img.shape[1], 3))

        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                array[i, j, :3] = img[i, j]

        return array
