from skimage.draw import line
from ct.CT import CT
import numpy as np


class InteractiveCT(CT):
    def __init__(self, img, rotate_angle, theta, detectors_number, far_detectors_distance):
        """
            img: Image to simulate radon transform
            rotate_angle: Emiters and detectors angle for next iteration in degrees
            theta: Initial degree in degrees
            detectors_number: Amount of detectors
            far_detectors_distance: Distance in pixels between farthest detectors
        """
        super().__init__(img, rotate_angle, theta, detectors_number, far_detectors_distance)

        self.iter = 0
        self.stopIter = 180 // rotate_angle
        self.step = 1
        self.rotate_angle = rotate_angle
        self.sinogram_plots = []
        self.result_plots = []

    def run(self):
        return super().run()

    def getIntermediatePlots(self):
        return self.sinogram_plots, self.result_plots

    def animate_radon(self, sinogram):
        if not self.iter % self.step and self.iter < self.stopIter:
            sinogram = np.array(sinogram.T, copy=True)
            self.sinogram_plots.append(sinogram)
        self.iter += 1

    def resetIter(self):
        self.iter = 0

    def animate_iradon(self, img, amount):
        if not self.iter % self.step and self.iter < self.stopIter:
            img_iradon = np.array(img, copy=True)
            x = img_iradon / amount
            x = np.max(x)
            img_iradon /= x if x > 0 else 1
            self.result_plots.append(img_iradon)
        self.iter += 1
