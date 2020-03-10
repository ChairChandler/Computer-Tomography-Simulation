from skimage.transform import radon, iradon
from math import sqrt
from skimage import draw
import numpy as np
from scipy.ndimage import rotate


def radonTransform(img, *, alfa, detectors_number, far_detectors_distance):
    """
        img: Image to simulate radon transform
        alfa: Emiters and detectors angle for next iteration in degree
        detectors_number: Amount of detectors
        far_detectors_distance: Distance in pixels between farthest detectors
    """
    unit_distance = far_detectors_distance/detectors_number
    diameter = sqrt(img.shape[0]**2 + img.shape[1]**2)
    point = {
        'x': diameter/2,
        'y': diameter/2
    }

    rr, cc = draw.circle(point['x'], point['y'], diameter/2)
    img_circle = np.ndarray(shape=(int(diameter) + 1,) * 2)

    # create y list for every x
    points = {}
    for x, y in zip(rr, cc):
        if x in points:
            points[x].append(y)
        else:
            points[x] = []

    # find points alongs to the circumference
    circumference_points = {'x': [], 'y': []}
    for x, coords_y in points.items():
        for index_y, y in enumerate(coords_y):

            # if edge of the image
            if index_y - 1 < 0 or index_y + 1 == len(points[x]):
                circumference_points['x'].append(x)
                circumference_points['y'].append(y)
            else:
                req = [
                    coords_y[index_y - 1] == y - 1,  # (x, y - 1) in circle
                    coords_y[index_y + 1] == y + 1,  # (x, y + 1) in circle
                    x - 1 in points,  # (x - 1, y) in circle
                    x + 1 in points  # (x + 1, y) in circle
                ]

                # if not inside circle
                if not any(req):
                    circumference_points['x'].append(x)
                    circumference_points['y'].append(y)

    img_circle[:, :] = 0
    img_circle[circumference_points['x'], circumference_points['y']] = 1

    #img_circle = rotate(img_circle, 30, reshape=False)

    return radon(img_circle, theta=None, circle=True)


def reverseRadonTransform(sinogram):
    return iradon(sinogram, circle=True)