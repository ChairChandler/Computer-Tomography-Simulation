from skimage.draw import line


def radiation_mean(img, detectors_values, emiter: "(x, y)", detectors: "[(x, y) ...]"):
    """
        Add emitter-detector line value to the intersected pixels.
    """
    for de_index, detector in enumerate(detectors):
        rr, cc = line(emiter[1], emiter[0], detector[1], detector[0])  # find pixels

        start = 0
        for i in range(len(rr)):  # find correct pixels start index
            if 0 <= rr[i] < img.shape[0] and 0 <= cc[i] < img.shape[1]:
                start = i
                break

        stop = 0
        for i in range(len(rr) - 1, start + 1, -1):  # find correct pixels stop index
            if 0 <= rr[i] < img.shape[0] and 0 <= cc[i] < img.shape[1]:
                stop = i
                break

        for i in range(start, stop+1):  # correct pixels loop
            img[rr[i], cc[i]] += detectors_values[de_index]
