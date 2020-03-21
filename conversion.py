from PySide2.QtGui import QPixmap, QImage, QColor
import numpy as np


def array2pixmap(image):
    image8 = image.astype(np.uint8)
    height, width = image8.shape[0:2]

    image = QImage(width, height, QImage.Format_RGB16)
    if len(image8.shape) == 2:
        for x in range(width):
            for y in range(height):
                color = QColor()
                color.setHsv(0, 0, image8[y][x])
                image.setPixel(x, y, color.rgb())
    else:
        for x in range(width):
            for y in range(height):
                color = QColor(*image8[y][x])
                image.setPixel(x, y, color.rgb())

    return QPixmap(image)


def rgb2greyscale(image):
    if len(image.shape) != 3:
        return image

    array = np.ndarray(shape=(image.shape[0], image.shape[1]))

    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            array[i, j] = image[i, j, 0]

    return array


def greyscale2rgb(image):
    array = np.ndarray(shape=(image.shape[0], image.shape[1], 3))

    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            array[i, j, :3] = image[i, j]

    return array
