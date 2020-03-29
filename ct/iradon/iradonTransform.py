import numpy as np
from typing import Tuple, Callable
from ct.iradon.lineRadiation import LineRadiation
from ct.iradon.filter import iradonFilter
from ct.round import Round


def iradonTransform(shape: Tuple[int, int], sinogram: np.ndarray, rotate_angle: float, start_angle: float,
                    farthest_detectors_distance: int, use_filter: bool,
                    animate_func: Callable[[np.ndarray, np.ndarray], None] = None) -> np.ndarray:

    diameter = np.sqrt(shape[0] ** 2 + shape[1] ** 2)
    circle = Round((shape[0] / 2, shape[1] / 2), diameter / 2, sinogram.shape[1],
                   farthest_detectors_distance, np.deg2rad(start_angle))

    img = np.zeros(shape)
    irad = LineRadiation(img, LineRadiation.Operation.MEAN)
    radian_rotate_angle = np.deg2rad(rotate_angle)

    if use_filter:
        sinogram = iradonFilter(sinogram)

    for angle in range(sinogram.shape[0]):
        animate_func(irad.img, irad.amount)
        irad.next(sinogram[angle], circle.emiter, circle.detectors)
        circle.rotate(radian_rotate_angle)

    return irad.end()
