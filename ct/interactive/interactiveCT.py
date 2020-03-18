from matplotlib import pyplot as plt
from matplotlib.figure import Figure
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
        self.img = img
        self.rotate_angle = rotate_angle
        self.theta = theta
        self.detectors_number = detectors_number
        self.far_detectors_distance = far_detectors_distance

        self.animation = False
        self.interactive_img = False
        self.interactive_sinogram = False
        self.interval = None

        self.cmap = None
        self.img_fig = Figure()
        self.sinogram_fig = Figure()
        self.img_plot = None
        self.sinogram_plot = None

    def interactive(self, img, sinogram, interval=1):
        """
            Switched animation state for image or sinogram.
            Have to used before run.
        """
        self.animation = img or sinogram
        self.interactive_img = img
        self.interactive_sinogram = sinogram
        self.interval = interval

        if self.interactive_img and self.interactive_sinogram:
            self.img_plot = self.img_fig.add_subplot(1, 1, 1)
            self.sinogram_plot = self.sinogram_fig.add_subplot(1, 1, 1)
        elif self.interactive_img:
            self.img_plot = self.img_fig.add_subplot(1, 1, 1)
        elif self.interactive_sinogram:
            self.sinogram_plot = self.sinogram_fig.add_subplot(1, 1, 1)

    def setCmap(self, value):
        self.cmap = value

    def run(self):
        super().__init__(self.img, self.rotate_angle, self.theta, self.detectors_number, self.far_detectors_distance)

        try:
            if self.animation:
                plt.ion()
                self.fig.show()
        except AttributeError:
            pass

        data = super().run()

        try:
            if self.animation:
                plt.close(self.fig)
                plt.ioff()
        except AttributeError:
            pass

        return data

    def animate(self, circle, sinogram):
        if self.animation:
            if self.interactive_img:
                self.drawImg(circle)

            if self.interactive_sinogram:
                self.drawSinogram(sinogram)

            plt.pause(self.interval)

    def drawImg(self, circle):
        img_radon = np.array(self.img, copy=True)

        for x, y in circle.detectors:
            pixels = zip(*line(circle.emiter[1], circle.emiter[0], y, x))

            # zoptymalizowac
            for pix_x, pix_y in pixels:
                if 0 <= pix_x < img_radon.shape[0] and 0 <= pix_y < img_radon.shape[1]:
                    img_radon[pix_x, pix_y] = 1

        self.img_plot.imshow(img_radon, cmap=self.cmap)

    def drawSinogram(self, sinogram):
        self.sinogram_plot.imshow(super().rotateSinogram(sinogram)[:, ::-1], cmap=self.cmap)
