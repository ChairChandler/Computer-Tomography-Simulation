import numpy as np


def iradonFilter(sinogram: np.ndarray) -> np.ndarray:
    freq_mat = np.fft.fftfreq(sinogram.T.shape[0])
    freq_vec = freq_mat.reshape(-1, 1)  # convert to column vector

    filtered_freq = 2 * np.abs(freq_vec) * np.fft.fft(sinogram.T, axis=1)  # filtering
    sinogram = np.fft.ifft(filtered_freq, axis=1).real

    return sinogram.T
