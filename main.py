from ct.interactive.interactiveCT import InteractiveCT as CT
from matplotlib import pyplot as plt
from skimage import io
from sys import argv


def showPlots(plots: []):
    _, subplots = plt.subplots(1, 3)

    plt.set_cmap('gray')
    for plot, data in zip(subplots, plots):
        plot.imshow(data, interpolation='bessel')
    plt.show()


def main(file):
    img = io.imread(file, as_gray=True)
    ct = CT(img, rotate_angle=10, theta=0, detectors_number=100, far_detectors_distance=1000)
    ct.interactive(img=True, sinogram=True, interval=0.0001)  # set drawing image and sinogram every iteration
    ct.setCmap('gray')
    sinogram, ct_img = ct.run()

    showPlots([img, sinogram, ct_img])


if __name__ == '__main__':
    main(argv[1])
