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

        # local reference for speed up
        img = self.img
        img_width, img_height = self.img.shape
        detectors_received_brightness = self.detectors_received_brightness

        for de_index, detector in enumerate(detectors):
            rr, cc = line(emiter[1], emiter[0], detector[1], detector[0])  # find pixels

            start = 0
            for i in range(len(rr)):  # find correct pixels start index
                if 0 <= rr[i] < img_width and 0 <= cc[i] < img_height:
                    start = i
                    break

            stop = 0
            for i in range(len(rr) - 1, start + 1, -1):  # find correct pixels stop index
                if 0 <= rr[i] < img_width and 0 <= cc[i] < img_height:
                    stop = i
                    break

            pixels_brightness = np.sum(img[rr[start:stop + 1], cc[start:stop + 1]])

            detectors_received_brightness[de_index] = pixels_brightness / (stop - start + 1)

        return self.detectors_received_brightness
