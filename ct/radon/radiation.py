from skimage.draw import line
import numpy as np


class Radiation:
    def __init__(self, img, detectors_amount):
        self.img = img
        self.detectors_received_brightness = np.ndarray(shape=(detectors_amount,))

    def calculate(self, emiter: "(x, y)", detectors: "[(x, y) ...]"):
        """
            Averaging pixels values on the emitter-detector line for every detector.
        """
        for de_index, detector in enumerate(detectors):
            rr, cc = line(emiter[1], emiter[0], detector[1], detector[0])  # find pixels

            start = 0
            for i in range(len(rr)):  # find correct pixels start index
                if 0 <= rr[i] < self.img.shape[0] and 0 <= cc[i] < self.img.shape[1]:
                    start = i
                    break

            stop = 0
            for i in range(len(rr) - 1, start + 1, -1):  # find correct pixels stop index
                if 0 <= rr[i] < self.img.shape[0] and 0 <= cc[i] < self.img.shape[1]:
                    stop = i
                    break

            pixels_brightness = 0
            for i in range(start, stop + 1):  # correct pixels loop
                pixels_brightness += self.img[rr[i], cc[i]]

            self.detectors_received_brightness[de_index] = pixels_brightness / (stop - start + 1)

        return self.detectors_received_brightness
