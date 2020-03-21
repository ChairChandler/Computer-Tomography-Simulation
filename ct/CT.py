from ct.radon.radonTransform import radonTransform
from ct.iradon.iradonTransform import iradonTransform
from abc import abstractmethod
import numpy as np

class CT:
    def __init__(self, img, rotate_angle, theta, detectors_number, far_detectors_distance):
        """
            img: Image to simulate radon transform
            rotate_angle: Emiters and detectors angle for next iteration in degrees
            theta: Initial degree in degrees
            detectors_number: Amount of detectors
            far_detectors_distance: Distance in pixels between farthest detectors
        """
        if rotate_angle <= 0 or rotate_angle >= 180:
            raise ArithmeticError("Rotate angle have to be in range (0, 180).")
        else:
            self.print = False
            self.img = img
            self.rotate_angle = rotate_angle
            self.theta = theta
            self.detectors_number = detectors_number
            self.far_detectors_distance = far_detectors_distance

    def setPrint(self, value):
        self.print = value

    def run(self):
        if self.print:
            print('Radon transform starting.')

        sinogram = radonTransform(self.img, self.rotate_angle, self.theta,
                                  self.detectors_number, self.far_detectors_distance, self.animate_radon)

        self.resetIter()

        if self.print:
            print('Radon transform ended, inverse radon transform starting.')

        img = iradonTransform(self.img.shape, sinogram, self.rotate_angle, self.theta, self.far_detectors_distance, self.animate_iradon)

        if self.print:
            print('Inverse radon transform ended.')

        sinogram /= np.max(sinogram)
        return sinogram.T, img

    @abstractmethod
    def animate_radon(self, *args, **kwargs):
        """
            Method to be overridden by derived class.
        """
        pass

    @abstractmethod
    def animate_iradon(self, *args, **kwargs):
        """
            Method to be overridden by derived class.
        """
        pass

    @abstractmethod
    def resetIter(self):
        """
            Method to be overridden by derived class.
        """
        pass
