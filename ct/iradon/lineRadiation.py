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
        # local reference for speed up
        img_width, img_height = self.img.shape

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

            operation(rr[start:stop + 1], cc[start:stop + 1], detectors_values[de_index])  # correct pixels

    def next_mean(self, pixels_x, pixels_y, detector_value):
        """
            Add emitter-detector line value to the intersected pixels and calculate average.
        """
        self.img[pixels_x, pixels_y] += detector_value
        self.amount[pixels_x, pixels_y] += 1

    def end_mean(self):
        self.img /= self.amount

    def next_sum(self,  pixels_x, pixels_y, detector_value):
        """
            Add emitter-detector line value to the intersected pixels.
        """
        self.img[pixels_x, pixels_y] += detector_value

    def end_sum(self):
        pass
