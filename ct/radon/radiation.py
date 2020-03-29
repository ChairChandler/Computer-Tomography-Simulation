import numpy as np
from typing import Tuple, List
from skimage.draw import line


class Radiation:
    def __init__(self, img: np.ndarray, detectors_amount: int):
        self.img = img
        self.detectors_received_brightness = np.ndarray(shape=(detectors_amount,))

    def calculate(self, emiter_pos: Tuple[int, int], detectors_pos: List[Tuple[int, int]]) -> np.ndarray:
        """
            Averaging pixels values on the emitter-detector line for every detector.
        """

        # local reference for speed up
        img = self.img
        img_width, img_height = self.img.shape
        detectors_received_brightness = self.detectors_received_brightness

        for de_index, detector in enumerate(detectors_pos):
            rr, cc = line(emiter_pos[1], emiter_pos[0], detector[1], detector[0])  # find pixels

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
