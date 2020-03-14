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
    ct = InteractiveCT(img, rotate_angle=5, theta=0, detectors_number=100, far_detectors_distance=300, iterations=36)
    ct.interactive(img=True, sinogram=True, interval=0.0001)
    sinogram, ct_img = ct.run()

    showPlots([img, sinogram, ct_img])


if __name__ == '__main__':
    main(argv[1])
