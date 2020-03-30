import numpy as np
from typing import Tuple, List, Callable, Union
from skimage.draw import line
from enum import Enum


class LineRadiation:
    """
    Reconstruct original image using sinogram.
    """
    class Operation(Enum):
        MEAN = 1
        SQRT = 2

    def __init__(self, img: np.ndarray, operation_type: Operation):
        self.img = img
        self.amount = np.ones(img.shape)

        if operation_type == LineRadiation.Operation.MEAN:
            self.operation = self.nextMean
            self.end_operation = self.endMean
        elif operation_type == LineRadiation.Operation.SQRT:
            self.operation = self.nextSqrt
            self.end_operation = self.endSqrt

    def next(self, detectors_values: np.ndarray, emiter_pos: Tuple[int, int], detectors_pos: List[Tuple[int, int]]) -> None:
        self.findLinesPixels(detectors_values, emiter_pos, detectors_pos, self.operation)

    def end(self) -> np.ndarray:
        self.end_operation()
        return self.img

    def findLinesPixels(self, detectors_values: np.ndarray, emiter_pos: Tuple[int, int], detectors_pos: List[Tuple[int, int]],
                        operation: Callable[[List[int], List[int], Union[int, float]], None]) -> None:
        # local reference for speed up
        img_width, img_height = self.img.shape

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

            operation(rr[start:stop + 1], cc[start:stop + 1], detectors_values[de_index])  # correct pixels

    def nextMean(self, pixels_x: List[int], pixels_y: List[int], detector_value: Union[int, float]) -> None:
        """
        Add emitter-detector line value to the intersected pixels and calculate average.
        :argument pixels_x: x position of pixels for corresponding y position
        :argument pixels_y: y position of pixels for corresponding x position
        :argument detector_value: pixels on the line value
        :return: None
        """
        self.img[pixels_x, pixels_y] += detector_value
        self.amount[pixels_x, pixels_y] += 1

    def endMean(self) -> None:
        x = self.img / self.amount
        x = np.max(x)
        self.img /= x if x > 0 else 1

    def nextSqrt(self, pixels_x: List[int], pixels_y: List[int], detector_value: Union[int, float]) -> None:
        """
        Add emitter-detector line value to the intersected pixels and calculate square root.
        :argument pixels_x: x position of pixels for corresponding y position
        :argument pixels_y: y position of pixels for corresponding x position
        :argument detector_value: pixels on the line value
        :return: None
        """
        self.img[pixels_x, pixels_y] += detector_value

    def endSqrt(self) -> None:
        self.img = np.sqrt(self.img)
