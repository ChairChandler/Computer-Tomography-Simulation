from skimage.draw import line
import numpy as np


class LineRadiation:
    def __init__(self, img, calcType: "mean | sum"):
        self.img = img
        self.amount = np.ones(img.shape)

        if calcType != "mean" and calcType != "sum":
            raise ValueError("Calculation type have to be mean or sum.")
        else:
            if calcType == "mean":
                self.operation = self.next_mean
                self.end_operation = self.end_mean
            elif calcType == "sum":
                self.operation = self.next_sum
                self.end_operation = self.end_sum

    def next(self, detectors_values, emiter: "(x, y)", detectors: "[(x, y) ...]"):
        self.find_lines_pixels(detectors_values, emiter, detectors, self.operation)

    def end(self):
        self.end_operation()
        return self.img

    def find_lines_pixels(self, detectors_values, emiter: "(x, y)", detectors: "[(x, y) ...]", operation):
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

            for i in range(start, stop + 1):  # correct pixels loop
                operation(rr[i], cc[i], detectors_values[de_index])

    def next_mean(self, pixel_x, pixel_y, detector_value):
        """
            Add emitter-detector line value to the intersected pixels and calculate average.
        """
        self.img[pixel_x, pixel_y] += detector_value
        self.amount[pixel_x, pixel_y] += 1

    def end_mean(self):
        self.img /= self.amount

    def next_sum(self,  pixel_x, pixel_y, detector_value):
        """
            Add emitter-detector line value to the intersected pixels.
        """
        self.img[pixel_x, pixel_y] += detector_value

    def end_sum(self):
        pass
