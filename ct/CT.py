import numpy as np
from typing import Tuple
from abc import abstractmethod
from ct.radon import radonTransform
from ct.iradon import iradonTransform
import logging


class CT:
    def __init__(self, img: np.ndarray, rotate_angle: int, start_angle: int, detectors_number: int,
                 farthest_detectors_distance: int, use_filter: bool = False):
        """
            img: Image to simulate radon transform
            rotate_angle: Emiters and detectors_pos angle for next iteration in degrees
            start_angle: Initial degree in degrees
            detectors_amount: Amount of detectors_pos
            farthest_detectors_distance: Distance in pixels between farthest detectors_pos
        """
        if rotate_angle <= 0 or rotate_angle >= 180:
            raise ArithmeticError("Rotate angle have to be in range (0, 180).")
        else:
            self.print = False
            self.img = img
            self.rotate_angle = rotate_angle
            self.theta = start_angle
            self.detectors_number = detectors_number
            self.far_detectors_distance = farthest_detectors_distance
            self.use_filter = use_filter
            self.logger = logging.getLogger(__name__)
            self.logger.addHandler(logging.StreamHandler())

    def setProcessInfo(self, value: bool) -> None:
        self.print = value

    def run(self) -> Tuple[np.ndarray, np.ndarray]:
        if self.print:
            self.logger.info('Radon transform starting.')

        sinogram = radonTransform(self.img, self.rotate_angle, self.theta,
                                  self.detectors_number, self.far_detectors_distance, self.saveRadonFrame)

        self.resetIter()

        if self.print:
            self.logger.info('Radon transform ended, inverse radon transform starting.')

        img = iradonTransform(self.img.shape, sinogram, self.rotate_angle, self.theta, self.far_detectors_distance,
                              self.use_filter, self.saveIradonFrame)

        if self.print:
            self.logger.info('Inverse radon transform ended.')

        sinogram /= np.max(sinogram)
        return sinogram.T, img

    @abstractmethod
    def saveRadonFrame(self, sinogram: np.ndarray) -> None:
        """
            Method to be overridden by derived class.
        """
        pass

    @abstractmethod
    def saveIradonFrame(self, img: np.ndarray, pixel_amount_lines: np.ndarray) -> None:
        """
            Method to be overridden by derived class.
        """
        pass

    @abstractmethod
    def resetIter(self) -> None:
        """
            Method to be overridden by derived class.
        """
        pass
