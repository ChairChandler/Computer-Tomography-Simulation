from ct.radon.radiation import Radiation
from ct.round import Round
import numpy as np


def radonTransform(img, rotate_angle, theta, detectors_number, far_detectors_distance, animate_func=None):
    diameter = np.sqrt(img.shape[0] ** 2 + img.shape[1] ** 2)
    circle = Round((img.shape[0] / 2, img.shape[1] / 2), diameter / 2, detectors_number,
                   far_detectors_distance, np.deg2rad(theta))

    radian_rotate_angle = np.deg2rad(rotate_angle)
    sinogram = np.zeros(shape=(360 // rotate_angle, detectors_number))

    rad = Radiation(img, detectors_number)

    for i in range(360 // rotate_angle):
        animate_func(circle, sinogram)
        sinogram[i] = rad.calculate(circle.emiter, circle.detectors)
        circle.rotate(radian_rotate_angle)

    return sinogram
