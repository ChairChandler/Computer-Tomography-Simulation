from ct.round import Round
from ct.iradon.lineRadiation import LineRadiation
import numpy as np


def iradonTransform(shape, sinogram, rotate_angle, theta, far_detectors_distance):
    diameter = np.sqrt(shape[0] ** 2 + shape[1] ** 2)
    circle = Round((shape[0] / 2, shape[1] / 2), diameter / 2, sinogram.shape[1],
                   far_detectors_distance, np.deg2rad(theta))

    img = np.zeros(shape)
    irad = LineRadiation(img, calcType="mean")
    radian_rotate_angle = np.deg2rad(rotate_angle)
    for angle in range(sinogram.shape[0]):
        irad.next(sinogram[angle], circle.emiter, circle.detectors)
        circle.rotate(radian_rotate_angle)

    return irad.end()
