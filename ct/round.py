from math import sin, cos, pi, asin


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

        self.emiter = self.calculateEmiterPosition()
        self.detectors = self.calculateDetectorsPositions()

    def calculateEmiterPosition(self):
        angle = self.theta + self.angle
        x = self.center[0] + self.radius * cos(angle)
        y = self.center[1] - self.radius * sin(angle)
        return round(x), round(y)

    def calculateDetectorsPositions(self):
        positions = []
        n = self.detectors_number
        fi = 2 * asin(self.far_detectors_distance / (2 * self.radius))
        for i in range(n):
            angle = self.theta + self.angle + pi - fi / 2 + i * fi / (n - 1)
            x = self.center[0] + self.radius * cos(angle)
            y = self.center[1] - self.radius * sin(angle)
            positions.append((round(x), round(y)))
        return positions

    def rotate(self, angle):
        """
            Rotate round by angle.
        """
        self.angle += angle

        if self.angle > 2 * pi:
            self.angle -= 2 * pi

        self.emiter = self.calculateEmiterPosition()
        self.detectors = self.calculateDetectorsPositions()
