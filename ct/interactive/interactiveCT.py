import numpy as np
from typing import Tuple
from ct import CT


class InteractiveCT(CT):
    def __init__(self, img: np.ndarray, rotate_angle: int, start_angle: int, detectors_number: int, farthest_detectors_distance: int, use_filter: bool = False):
        """
            img: Image to simulate radon transform
            rotate_angle: Emiters and detectors_pos angle for next iteration in degrees
            start_angle: Initial degree in degrees
            detectors_amount: Amount of detectors_pos
            farthest_detectors_distance: Distance in pixels between farthest detectors_pos
        """
        super().__init__(img, rotate_angle, start_angle, detectors_number, farthest_detectors_distance, use_filter)

        self.iter = 0
        self.stopIter = 180 // rotate_angle
        self.step = 1
        self.rotate_angle = rotate_angle
        self.sinogram_plots = []
        self.result_plots = []

    def run(self) -> Tuple[np.ndarray, np.ndarray]:
        return super().run()

    def getFrames(self) -> Tuple[list, list]:
        return self.sinogram_plots, self.result_plots

    def saveRadonFrame(self, sinogram: np.ndarray) -> None:
        if not self.iter % self.step and self.iter < self.stopIter:
            sinogram = np.array(sinogram.T, copy=True)
            self.sinogram_plots.append(sinogram)
        self.iter += 1

    def resetIter(self) -> None:
        self.iter = 0

    def saveIradonFrame(self, img: np.ndarray, pixel_amount_lines: np.ndarray) -> None:
        if not self.iter % self.step and self.iter < self.stopIter:
            img_iradon = np.array(img, copy=True)
            x = img_iradon / pixel_amount_lines
            x = np.max(x)
            img_iradon /= x if x > 0 else 1
            self.result_plots.append(img_iradon)
        self.iter += 1
