import numpy as np
from typing import Callable
from ct.radon.radiation import Radiation
from ct.round import Round


def radonTransform(img: np.ndarray, rotate_angle: int, start_angle: int, detectors_number: int, farthest_detectors_distance: int,
                   animate_func: Callable[[np.ndarray], None] = None) -> np.ndarray:

    diameter = np.sqrt(img.shape[0] ** 2 + img.shape[1] ** 2)
    circle = Round((img.shape[0] / 2, img.shape[1] / 2), diameter / 2, detectors_number,
                   farthest_detectors_distance, np.deg2rad(start_angle))

    radian_rotate_angle: float = np.deg2rad(rotate_angle)
    sinogram = np.zeros(shape=(180 // rotate_angle, detectors_number))

    rad = Radiation(img, detectors_number)

    for i in range(180 // rotate_angle):
        animate_func(sinogram)
        sinogram[i] = rad.calculate(circle.emiter, circle.detectors)
        circle.rotate(radian_rotate_angle)

    return sinogram
