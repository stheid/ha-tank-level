import logging

import numpy as np
from PIL import Image

_LOGGER = logging.getLogger(__name__)


def find_peaks(data, height=0, distance=100):
    # Identify points where the slope changes from positive to negative (peaks)
    gradient = np.diff(data)
    peaks = (np.hstack((0, gradient)) >= 0) & (np.hstack((gradient, 0)) <= 0)

    # Filter by threshold
    peaks = peaks & (data > height)

    # Get indices of the peaks
    peak_indices = np.where(peaks)[0]

    if distance > 1:
        selected_peaks = []
        last_peak = -distance  # Ensure first peak is always selected
        for peak in peak_indices:
            if peak - last_peak >= distance:
                selected_peaks.append(peak)
                last_peak = peak
        peak_indices = np.array(selected_peaks)

    return peak_indices


def process_image(image_path):
    img = np.array(Image.open(image_path))[:, :, 0]

    # extract fill level
    k25 = int(img.shape[0] * 0.45)
    k75 = img.shape[0] - k25
    data = np.partition(img, (k25, k75), axis=0)[k25:k75 + 1, :]
    levels = np.mean(data, axis=0)
    s = 64
    kernel = np.array([-1] * s + [0] + [1] * s)
    edge_filtered = np.convolve(levels, kernel, mode='valid')
    x = np.argmax(edge_filtered) + s

    # extract "horizontal" placement of the tank in the picture
    levels = np.mean(img, axis=1)
    s = 32
    kernel = np.array([-1] * s + [0] * (s + 1))
    edge_filtered = np.convolve(levels, kernel, mode='valid')
    try:
        y = find_peaks(edge_filtered, height=-800)[0] + s
    except ValueError:
        _LOGGER.warning("Could not detect edge of tank. Continuing with hard coded Reference values")
        y = 177

    # extract 1200 and 400 fill levels
    region = img[y + 570:y + 650]
    levels = np.mean(region, axis=0)
    kernel = np.array([1] * s + [0] + [-1] * s)
    edge_filtered = np.convolve(levels, kernel, mode='valid')
    try:
        up, low = find_peaks(edge_filtered[100:], height=150, distance=500)
        up, low = up + s + 100, low + s + 100
    except ValueError as e:
        _LOGGER.warning("Could not detect fill level stickers. Continuing with hard coded Reference values")
        _LOGGER.warning("Error: " + str(e))
        up, low = 230, 1190

    # 1200-400 fill level ratio
    l = (up - low) / 800

    # Compute the fill level
    tank_level = round(((x - low) / l + 400) * 3)
    return int(tank_level)
