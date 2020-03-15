from matplotlib import pyplot as plt
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
        self.animation = False
        self.interactive_img = False
        self.interactive_sinogram = False
        self.interval = None

        self.cmap = None
        self.fig = None
        self.img_plot = None
        self.sinogram_plot = None

    def interactive(self, *, img, sinogram, interval=1):
        """
            Switched animation state for image or sinogram.
            Have to used before run.
        """
        self.animation = img or sinogram
        self.interactive_img = img
        self.interactive_sinogram = sinogram
        self.interval = interval

        if self.interactive_img and self.interactive_sinogram:
            self.fig, (self.img_plot, self.sinogram_plot) = plt.subplots(1, 2)
        elif self.interactive_img:
            self.fig, self.img_plot = plt.subplots(1, 1)
        elif self.interactive_sinogram:
            self.fig, self.sinogram_plot = plt.subplots(1, 1)

        if self.fig:
            self.fig.canvas.set_window_title('CT')

    def setCmap(self, value):
        self.cmap = value

    def run(self):
        if self.animation:
            plt.ion()
            self.fig.show()

        data = super().run()

        if self.animation:
            plt.close(self.fig)
            plt.ioff()

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

            for pix_x, pix_y in pixels:
                if 0 <= pix_x < img_radon.shape[0] and 0 <= pix_y < img_radon.shape[1]:
                    img_radon[pix_x, pix_y] = 1

        self.img_plot.imshow(img_radon, cmap=self.cmap, interpolation='bessel')

    def drawSinogram(self, sinogram):
        self.sinogram_plot.imshow(self.rotateSinogram(sinogram), cmap=self.cmap, interpolation='bessel')

    @staticmethod
    def rotateSinogram(sinogram):
        return np.rot90(sinogram.T, 2)[:, ::-1]
