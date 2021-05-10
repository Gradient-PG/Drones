import numpy as np
import cv2 as cv
import imutils
import configparser
import typing
import drones.image_processing.normalization as normalization


def calculate_focal(known_width: float, known_distance: float, pixel_width: int) -> float:
    """Calculate focal length of the camera
    focal_length = (pixel_width * known_distance) / known_width

    Parameters:
    ----------
    known_width: float
        measured width of the object (has to be known before running script)
    known_distance: float
        measured distance between detected object and camera (has to be known before running script)
    pixel_width: int
        width in pixels of detected object

    Returns:
    ----------
    focal_length: float
        calculated length of the focal
    """
    focal_length = (pixel_width * known_distance) / known_width

    return focal_length


def distance_to_camera(known_width: float, focal_length: float, pixel_width: int) -> float:
    """Calculate distance between detected object and camera from equation
    distance = (known_width * focal_length) / pixel_width

    Parameters:
    ----------
    known_width: float
        measured width of the object (has to be known before running script)
    focal_length: float
        length of the focal
    pixel_width: int
        width in pixels of detected object

    Returns:
    ----------
    distance: float
        Calculated distance between detected object and camera
    """
    distance = (known_width * focal_length) / pixel_width

    return distance


def vector_to_centre(
    frame_width: int, frame_height: int, obj_coordinates: typing.Tuple[int, int], centre_height_coeff: float
) -> typing.Tuple[int, int]:
    """Calculate vector from tracked object to center of frame

    Parameters:
    ----------
    frame_width: int
        width of frame captured from camera
    frame_height: int
        height of frame captured from camera
    obj_coordinates: Tuple
        coordinates (x, y) of tracked object's center
    centre_height_coeff: float
        coefficient defining height of center where tracked object should be

    Returns:
    ----------
    vector_centre: typing.Tuple[int, int]
        vector (x, y) from tracked object to center of frame
    """

    x_centre = int(0.5 * frame_width)
    y_centre = int(centre_height_coeff * frame_height)

    x_component = x_centre - obj_coordinates[0]
    y_component = y_centre - obj_coordinates[1]
    vector_centre = (x_component, y_component)

    return vector_centre


def detect_object(image: np.ndarray) -> typing.Tuple[typing.Tuple[int, int], int]:
    """Detect object in the image.

    The detection is basicaly applying mask in specific color range
    and finding contour with best circularity and area combined.
    Next the minimal enclosing circle of the chosen contour is evaluated
    and its diameter and center returned.

    Parameters:
    ----------
    image: np.ndarray
        Image in which the object should be detected.

    Returns:
    -------
    center_and_diameter: typing.Tuple[typing.Tuple[int,int],int]
        The inside tuple is x and y coordinates on the picture
        of center of minimal enclosing circle of detected object.
        The other value is the diameter of minimal enclosing circle of detected object in pixels.
        If the object is not detected tuple ((-1,-1),-1) is returned
        (so center coordinates and diameter are -1).
        This returned format is insired by OpenCV minEnclosingCircle function returned format.
    """
    config_parser = configparser.ConfigParser()
    config_parser.read("image_processing/config.ini")
    config = config_parser["COLOR_RANGE"]

    # Image normalization to make colors more visious and less light vulnerable.
    image = normalization.normalization(image, minmax=True, clahe=True)

    # Convert colors of image to HSV for easier range selection.
    hsv_image = cv.cvtColor(image, cv.COLOR_BGR2HSV)

    # Mask in given color range.
    # The config stores everything as string,
    # so color bounds are splited, become array and they are converted to int.
    mask = cv.inRange(
        hsv_image,
        np.asarray(config["LOWER_BOUND"].split(" "), dtype=np.int32),
        np.asarray(config["UPPER_BOUND"].split(" "), dtype=np.int32),
    )

    # Remove tiny contours on the mask to make it more clear.
    mask = cv.erode(mask, None, iterations=2)
    mask = cv.dilate(mask, None, iterations=2)

    # Getting the list of contours from mask.
    contours_list = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contours_list = imutils.grab_contours(contours_list)

    if contours_list:
        selected_contour = choose_contour(contours_list)
        ((x, y), radius) = cv.minEnclosingCircle(selected_contour)

        # Times 2, because the diameter is returned
        return ((int(x), int(y)), int(2 * radius))
    return ((-1, -1), -1)


def choose_contour(contours_list: list) -> np.ndarray:
    """Choose apropriate contour, that is most likely the object to be detected.

    Contour with the greatest product of area and circularity will be selected.

    Parameters
    ----------
    contours_list: list
        List of contours, from which the contour of object to be detected, will be seleted.

    Returns
    -------
    selected_contour: np.ndarray
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
