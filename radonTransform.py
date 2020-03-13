from math import sqrt, sin, cos, pi, asin, radians as degree2radians
from skimage.transform import iradon, radon as testRadon
from skimage.draw import line
import numpy as np


class Radiation:
    def __init__(self, img):
        self.img = img

    def calculate(self, emiter: "(x, y)", detectors: "[(x, y) ...]"):
        detectors_received_brightness = []
        for x, y in detectors:
            pixels = zip(*line(emiter[0], emiter[1], x, y))

            pixels_brightness = 0
            for pix_x, pix_y in pixels:
                if 0 <= pix_x < self.img.shape[0] and 0 <= pix_y < self.img.shape[1]:
                    pixels_brightness += self.img[pix_x, pix_y]

            detectors_received_brightness.append(pixels_brightness)
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


def radonTransform(img, *, rotate_angle, theta, detectors_number, far_detectors_distance, iterations):
    """
        img: Image to simulate radon transform
        rotate_angle: Emiters and detectors angle for next iteration in degree
        detectors_number: Amount of detectors
        far_detectors_distance: Distance in pixels between farthest detectors
    """

    diameter = sqrt(img.shape[0] ** 2 + img.shape[1] ** 2)
    angle_radians = degree2radians(rotate_angle)

    rad = Radiation(img)
    sinogram = np.ndarray(shape=(iterations, detectors_number))
    circle = Round((img.shape[0] / 2, img.shape[1] / 2), diameter / 2, detectors_number, far_detectors_distance, theta)

    for i in range(iterations):
        sinogram[i] = rad.calculate(circle.emiter, circle.detectors)
        circle.rotate(angle_radians)
        print(i)

    return np.rot90(sinogram.T, 2)

    #return testRadon(img, None, circle=True)


def reverseRadonTransform(sinogram):
    return iradon(sinogram, circle=False)