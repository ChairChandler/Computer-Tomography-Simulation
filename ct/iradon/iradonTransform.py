from ct.round import Round
from ct.iradon.radiationMean import radiation_mean
import numpy as np
from skimage.transform import iradon


def iradonTransform(shape, sinogram, theta, far_detectors_distance):
    return iradon(sinogram, circle=False)

    diameter = np.sqrt(shape[0] ** 2 + shape[1] ** 2)
    circle = Round((shape[0] / 2, shape[1] / 2), diameter / 2, sinogram.shape[1],
                   far_detectors_distance, np.deg2rad(theta))

    img = np.zeros(shape)
    radian_rotate_angle = np.deg2rad(1)
    for angle in range(sinogram.shape[0]):
        radiation_mean(img, sinogram[angle], circle.emiter, circle.detectors)
        circle.rotate(radian_rotate_angle)

    return img
