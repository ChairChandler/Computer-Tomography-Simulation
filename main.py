from ct.interactive.interactiveCT import InteractiveCT as CT
from matplotlib import pyplot as plt
from skimage import io
from sys import argv


def showPlots(plots: []):
    _, subplots = plt.subplots(1, len(plots))

    for plot, data in zip(subplots, plots):
        plot.imshow(data)
    plt.show()


def main(file):
    img = io.imread(file, as_gray=True)

    ct = CT(img, rotate_angle=2, theta=0, detectors_number=500, far_detectors_distance=1449)
    ct.setPrint(True)
    #ct.interactive(img=True, sinogram=True, interval=0.0001)  # set drawing image and sinogram every iteration
    ct.setCmap('gray')
    sinogram, ct_img = ct.run()

    showPlots([img, sinogram, ct_img])


if __name__ == '__main__':
    main(argv[1])
