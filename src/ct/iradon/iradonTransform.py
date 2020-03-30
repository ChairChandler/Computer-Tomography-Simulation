import numpy as np
from typing import Tuple, Callable
from .lineRadiation import LineRadiation
from ..round import Round
import skimage.exposure


def iradonTransform(shape: Tuple[int, int], sinogram: np.ndarray, rotate_angle: float, start_angle: float,
                    farthest_detectors_distance: int, animate_func: Callable[[np.ndarray, np.ndarray], None] = None) -> np.ndarray:
    """
    Construct sinogram from image.
    :param shape: original image shape
    :param rotate_angle: angle in degree to rotate every iteration
    :param start_angle: theta angle in degree
    :param sinogram: sinogram of original image
    :param farthest_detectors_distance: distance between farthest detectors
    :param animate_func: function for save reconstructed image frames
    :return: reconstructed image
    """
    diameter = np.sqrt(shape[0] ** 2 + shape[1] ** 2)
    circle = Round((shape[0] / 2, shape[1] / 2), diameter / 2, sinogram.shape[1],
                   farthest_detectors_distance, np.deg2rad(start_angle))

    img = np.zeros(shape)
    irad = LineRadiation(img, LineRadiation.Operation.MEAN)
    radian_rotate_angle = np.deg2rad(rotate_angle)

    for angle in range(sinogram.shape[0]):
        animate_func(irad.img, irad.amount)
        irad.next(sinogram[angle], circle.emiter, circle.detectors)
        circle.rotate(radian_rotate_angle)

    return skimage.exposure.rescale_intensity(irad.end().astype(np.uint8))
