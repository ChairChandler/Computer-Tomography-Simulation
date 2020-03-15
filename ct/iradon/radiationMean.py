from skimage.draw import line


def radiation_mean(img, detectors_values, emiter: "(x, y)", detectors: "[(x, y) ...]"):
    """
        Add emitter-detector line value to the intersected pixels.
    """
    for de_index, (x, y) in enumerate(detectors):
        pixels = zip(*line(emiter[1], emiter[0], y, x))

        for pix_x, pix_y in pixels:
            if 0 <= pix_x < img.shape[0] and 0 <= pix_y < img.shape[1]:
                img[pix_x, pix_y] += detectors_values[de_index]
