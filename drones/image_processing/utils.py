import numpy as np
import cv2 as cv
import imutils
import drones.image_processing.normalization as normalization

# These constants indicate color range in HSV of object to be detected.
LOWER_BOUND_COLOR = np.array([0, 220, 100])
UPPER_BOUND_COLOR = np.array([15, 255, 255])


def detect_object(image: np.ndarray) -> int:
    """Detect object in the image.

    The detection is basicaly applying mask in specific color range
    and finding contour with best circularity and area combined.
    Next the minimal enclosing circle of the chosen contour is evaluated
    and its diameter returned.

    Parameters
    ----------
    image : np.ndarray
        Image in which the object should be detected.

    Returns
    -------
    int
        Diameter of minimal enclosing circle of detected object in pixels.
        If the object is not detected 0 is returned.
    """
    # Image normalization to make colors more visious and less light vulnerable.
    image = normalization.normalization(image, minmax=True, clahe=True)

    # Convert colors of image to HSV for easier range selection.
    hsv_image = cv.cvtColor(image, cv.COLOR_BGR2HSV)

    # Mask in given color range.
    mask = cv.inRange(hsv_image, LOWER_BOUND_COLOR, UPPER_BOUND_COLOR)

    # Remove tiny contours on the mask to make it more clear.
    mask = cv.erode(mask, None, iterations=2)
    mask = cv.dilate(mask, None, iterations=2)

    # Getting the list of contours from mask.
    contours_list = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contours_list = imutils.grab_contours(contours_list)

    if len(contours_list) > 0:
        selected_contour = choose_contour(contours_list)
        ((_, _), radius) = cv.minEnclosingCircle(selected_contour)
        return int(radius)
    return 0


def choose_contour(contours_list: list) -> np.ndarray:
    """Choose apropriate contour, that is most likely the object to be detected.

    Contour with the greatest product of area and circularity will be selected.

    Parameters
    ----------
    contours_list : list
        List of contours, from which the contour of object to be detected, will be seleted.

    Returns
    -------
    np.ndarray
        Contour of detected object.
    """

    max_criteria = 0

    for contour in contours_list:
        # Calculate circularity and area of the contour.
        area = cv.contourArea(contour)
        arclength = cv.arcLength(contour, True)
        circularity = 4 * np.pi * area / (arclength * arclength)

        # Choose contour with the greatest product of area and circularity.
        if circularity * area > max_criteria:
            max_criteria = circularity * area
            selected_contour = contour
    return selected_contour
