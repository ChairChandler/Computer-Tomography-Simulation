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

        self.step = 10
        self.rotate_angle = rotate_angle
        self.img_plot = []
        self.sinogram_plot = []

    def run(self):
        return super().run()

    def getIntermediatePlots(self):
        return self.img_plot, self.sinogram_plot

    def animate(self, circle, sinogram):
        for i in range(360 // self.rotate_angle):
            if not i % self.step:
                self.drawImg(circle)
                self.drawSinogram(sinogram)
            yield

    def drawImg(self, circle):
        img_radon = np.array(self.img, copy=True)

        for x, y in circle.detectors:
            pixels = zip(*line(circle.emiter[1], circle.emiter[0], y, x))

            # zoptymalizowac
            for pix_x, pix_y in pixels:
                if 0 <= pix_x < img_radon.shape[0] and 0 <= pix_y < img_radon.shape[1]:
                    img_radon[pix_x, pix_y] = 1

        self.img_plot.append(img_radon)

    def drawSinogram(self, sinogram):
        sinogram = np.array(super().rotateSinogram(sinogram)[:, ::-1], copy=True)
        self.sinogram_plot.append(sinogram)
