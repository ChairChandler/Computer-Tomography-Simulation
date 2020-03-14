from math import sqrt, sin, cos, pi, asin, radians as degree2radians
from skimage.transform import iradon as skiradon
from skimage.draw import line
import numpy as np
from matplotlib import pyplot as plt


class Radiation:
    def __init__(self, img):
        self.img = img

    def calculate(self, emiter: "(x, y)", detectors: "[(x, y) ...]"):
        detectors_received_brightness = []
        for x, y in detectors:
            pixels = zip(*line(emiter[1], emiter[0], y, x))

            pixels_brightness = 0
            amount = 0
            for pix_x, pix_y in pixels:
                if 0 <= pix_x < self.img.shape[0] and 0 <= pix_y < self.img.shape[1]:
                    amount += 1
                    pixels_brightness += self.img[pix_x, pix_y]
            detectors_received_brightness.append(pixels_brightness / amount)
        return detectors_received_brightness


class Round:
    def __init__(self, center: "(x, y)", radius, detectors_number, far_detectors_distance, theta):
        self.center = center
        self.radius = radius
        self.theta = theta
        self.angle = 0

        self.detectors_number = detectors_number
        self.far_detectors_distance = far_detectors_distance

        self.emiter = self.calculateEmiterPosition()
        self.detectors = self.calculateDetectorsPositions()

    def calculateEmiterPosition(self):
        x = self.center[0] + self.radius * cos(self.theta + self.angle)
        y = self.center[1] - self.radius * sin(self.theta + self.angle)
        return int(x), int(y)

    def calculateDetectorsPositions(self):
        positions = []
        n = self.detectors_number
        fi = 2 * asin(self.far_detectors_distance / (2 * self.radius))
        for i in range(n):
            x = self.center[0] + self.radius * cos(self.theta + self.angle + pi - fi / 2 + i * fi / (n - 1))
            y = self.center[1] - self.radius * sin(self.theta + self.angle + pi - fi / 2 + i * fi / (n - 1))
            positions.append((int(x), int(y)))
        return positions

    def rotate(self, angle):
        self.angle += angle

        if self.angle > 2 * pi:
            self.angle -= 2 * pi

        self.emiter = self.calculateEmiterPosition()
        self.detectors = self.calculateDetectorsPositions()


class CT:
    def __init__(self, img, rotate_angle, theta, detectors_number, far_detectors_distance, iterations):
        """
                img: Image to simulate radon transform
                rotate_angle: Emiters and detectors angle for next iteration in degree
                detectors_number: Amount of detectors
                far_detectors_distance: Distance in pixels between farthest detectors
        """
        self.img = img
        self.rotate_angle = degree2radians(rotate_angle)
        self.theta = theta
        self.detectors_number = detectors_number
        self.far_detectors_distance = far_detectors_distance
        self.iterations = iterations

    def run(self):
        sinogram = self.radon()
        img = self.iradon(sinogram)
        return sinogram, img

    @staticmethod
    def rotateSinogram(sinogram):
        return np.rot90(sinogram.T, 2)[:, ::-1]

    def animate(self, *args, **kwargs):
        pass

    def radon(self):
        diameter = sqrt(self.img.shape[0] ** 2 + self.img.shape[1] ** 2)
        circle = Round((self.img.shape[0] / 2, self.img.shape[1] / 2), diameter / 2, self.detectors_number,
                       self.far_detectors_distance, degree2radians(self.theta))

        sinogram = np.zeros(shape=(self.iterations, self.detectors_number))
        rad = Radiation(self.img)

        for i in range(self.iterations):
            self.animate(circle, sinogram)
            sinogram[i] = rad.calculate(circle.emiter, circle.detectors)
            circle.rotate(self.rotate_angle)

        return self.rotateSinogram(sinogram)

    def iradon(self, sinogram):
        return skiradon(sinogram, circle=False)


class InteractiveCT(CT):
    def __init__(self, img, rotate_angle, theta, detectors_number, far_detectors_distance, iterations):
        super().__init__(img, rotate_angle, theta, detectors_number, far_detectors_distance, iterations)
        self.animation = False
        self.interactive_img = False
        self.interactive_sinogram = False
        self.interval = None

        self.cmap = None
        self.fig = None
        self.img_plot = None
        self.sinogram_plot = None

    def interactive(self, *, img, sinogram, interval=1):
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

        self.img_plot.imshow(img_radon, cmap=self.cmap)

    def drawSinogram(self, sinogram):
        self.sinogram_plot.imshow(super().rotateSinogram(sinogram), cmap=self.cmap)