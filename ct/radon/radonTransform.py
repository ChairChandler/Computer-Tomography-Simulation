from ct.radon.radiation import calculate_radiation
from math import sqrt, radians as degree2radians
from ct.round import Round
import numpy as np


def rotateSinogram(sinogram):
    return np.rot90(sinogram.T, 2)[:, ::-1]


def radonTransform(img, rotate_angle, theta, detectors_number, far_detectors_distance, animate_func=None):
    diameter = sqrt(img.shape[0] ** 2 + img.shape[1] ** 2)
    circle = Round((img.shape[0] / 2, img.shape[1] / 2), diameter / 2, detectors_number,
                   far_detectors_distance, degree2radians(theta))

    radian_rotate_angle = degree2radians(rotate_angle)
    sinogram = np.zeros(shape=(180, detectors_number))

    i = None
    for i in range(0, 180, rotate_angle):
        animate_func(circle, sinogram)
        sinogram[i] = calculate_radiation(img, circle.emiter, circle.detectors)
        # TODO: dodac polownicze usrednianie bo sa dziury

        if i - rotate_angle >= 0:  # averaging the nearest non-free data segments
            for j in range(i - rotate_angle + 1, i):
                sinogram[j] = (sinogram[i - rotate_angle] + sinogram[i]) / 2

        circle.rotate(radian_rotate_angle)

    if i >= 0:  # averaging the nearest non-free data segments
        for j in range(i + 1, 180):
            sinogram[j] = sinogram[i]

    return rotateSinogram(sinogram)
