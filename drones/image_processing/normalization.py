import numpy as np
import cv2 as cv


def min_max_norm(image: np.ndarray) -> np.ndarray:
    image = cv.imread(r"D:\domik\Documents\photos\9_Moment.jpg")
    norm_image = np.zeros((image.shape[0], image.shape[1]))
    image = cv.normalize(image, norm_image, 0, 255, cv.NORM_MINMAX)
    return image
