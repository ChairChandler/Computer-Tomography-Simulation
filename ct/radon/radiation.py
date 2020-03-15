from skimage.draw import line


def calculate_radiation(img, emiter: "(x, y)", detectors: "[(x, y) ...]"):
    """
        Averaging pixels values on the emitter-detector line for every detector.
    """
    detectors_received_brightness = []
    for x, y in detectors:
        pixels = zip(*line(emiter[1], emiter[0], y, x))

        pixels_brightness = 0
        amount = 0
        for pix_x, pix_y in pixels:
            if 0 <= pix_x < img.shape[0] and 0 <= pix_y < img.shape[1]:
                amount += 1
                pixels_brightness += img[pix_x, pix_y]
        detectors_received_brightness.append(pixels_brightness / amount)
    return detectors_received_brightness
