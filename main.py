from matplotlib import pyplot as plt
from skimage import io
from sys import argv
from radonTransform import *


def showPlots(plots: []):
    _, subplots = plt.subplots(1, 3)

    plt.set_cmap('gray')
    for plot, data in zip(subplots, plots):
        plot.imshow(data)
    plt.show()


def main(file):
    img = io.imread(file, as_gray=True)
    sinogram = radonTransform(img,
                              rotate_angle=1, theta=0,
                              detectors_number=100,
                              far_detectors_distance=100,
                              iterations=360)
    rev_img = reverseRadonTransform(sinogram)

    showPlots([img, sinogram, rev_img])


if __name__ == '__main__':
    main(argv[1])
