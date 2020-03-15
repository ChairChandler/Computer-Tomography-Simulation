import numpy as np


class Round:
    """
        Helps simulates rounding emitter and detectors around image.
    """
    def __init__(self, center: "(x, y)", radius, detectors_number, far_detectors_distance, theta):
        self.center = center
        self.radius = radius
        self.theta = theta
        self.angle = 0

        self.detectors_number = detectors_number
        self.far_detectors_distance = far_detectors_distance

        self.emiter = None
        self.detectors = [0 for i in range(detectors_number)]

        self.fi = 2 * np.arcsin(self.far_detectors_distance / (2 * self.radius))
        if np.isnan(self.fi):
            raise ArithmeticError("Distance between fartest detectors too much.")

        # for performance reason it is done once
        self.angle_step_detectors = [self.theta + np.pi - self.fi / 2 + i * self.fi / (self.detectors_number - 1)
                                     for i in range(detectors_number)]

        self.calculateEmiterPosition()
        self.calculateDetectorsPositions()

    def calculateEmiterPosition(self):
        angle = self.theta + self.angle
        x = self.center[0] + self.radius * np.cos(angle)
        y = self.center[1] - self.radius * np.sin(angle)
        self.emiter = int(np.round(x)), int(np.round(y))

    def calculateDetectorsPositions(self):
        for i in range(self.detectors_number):
            angle = self.angle + self.angle_step_detectors[i]
            x = self.center[0] + self.radius * np.cos(angle)
            y = self.center[1] - self.radius * np.sin(angle)
            self.detectors[i] = (int(np.round(x)), int(np.round(y)))

    def rotate(self, angle):
        """
            Rotate round by angle.
        """
        self.angle += angle
        self.calculateEmiterPosition()
        self.calculateDetectorsPositions()
