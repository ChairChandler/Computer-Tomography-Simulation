import numpy as np
from typing import Tuple


class Round:
    """
    Simulates rounding emitter and detectors around image.
    """
    def __init__(self, center: Tuple[float, float], radius: float, detectors_amount: int, farthest_detectors_distance: int, start_angle: float):
        """
        :param center: center point position
        :param radius: round radius
        :param detectors_amount: amount of detectors_pos
        :param farthest_detectors_distance: distance in pixels between farthest detectors_pos
        :param start_angle: initial degree in degrees
        """
        self.center = center
        self.radius = radius
        self.theta = start_angle
        self.angle = 0

        self.detectors_number = detectors_amount
        self.far_detectors_distance = farthest_detectors_distance

        self.emiter = None
        self.detectors = [None for i in range(detectors_amount)]

        if self.far_detectors_distance > 2 * radius:
            raise ArithmeticError(f"Distance between fartest detectors_pos have to be less or equal to {int(2 * radius)}.")
        else:
            self.fi = 2 * np.arcsin(self.far_detectors_distance / (2 * self.radius))

        # for performance reason it is done once
        self.angle_step_detectors = [self.theta + np.pi - self.fi / 2 + i * self.fi / (self.detectors_number - 1)
                                     for i in range(detectors_amount)]

        self.calculateEmiterPosition()
        self.calculateDetectorsPositions()

    def calculateEmiterPosition(self) -> None:
        angle = self.theta + self.angle
        x = self.center[0] + self.radius * np.cos(angle)
        y = self.center[1] - self.radius * np.sin(angle)
        self.emiter = int(np.round(x)), int(np.round(y))

    def calculateDetectorsPositions(self) -> None:
        for i in range(self.detectors_number):
            angle = self.angle + self.angle_step_detectors[i]
            x = self.center[0] + self.radius * np.cos(angle)
            y = self.center[1] - self.radius * np.sin(angle)
            self.detectors[i] = (int(np.round(x)), int(np.round(y)))

    def rotate(self, angle: float) -> None:
        """
        Rotate round by angle.
        :param angle: radian angle
        :return: None
        """
        self.angle += angle
        self.calculateEmiterPosition()
        self.calculateDetectorsPositions()
