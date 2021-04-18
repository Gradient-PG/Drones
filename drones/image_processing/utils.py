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

    Raises:
    ----------
        ZeroDivisionError: when nominator (known_width) is equal 0
    """
    try:
        focal_length = (pixel_width * known_distance) / known_width
    except ZeroDivisionError as err:
        raise ZeroDivisionError(err)

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

    Raises:
    ----------
        ZeroDivisionError: when nominator (pixel_width) is equal 0
    """
    try:
        distance = (known_width * focal_length) / pixel_width
    except ZeroDivisionError as err:
        raise ZeroDivisionError(err)

    return distance


def vector_to_centre(frame_width: int, frame_height: int, obj_coordinates: tuple, centre_height_coeff: float) -> tuple:
    """Calculate vector from tracked object to center of frame

    Parameters:
    ----------
    frame_width: int
        width of frame captured from camera
    frame_height: int
        height of frame captured from camera
    obj_coordinates: tuple
        coordinates (x, y) of tracked object's center
    centre_height_coeff: float
        coefficient defining height of center where tracked object should be

    Returns:
    ----------
    vector_to_centre: tuple
        vector (x, y) from tracked object to center of frame
    """

    x_centre = 0.5 * frame_width
    y_centre = centre_height_coeff * frame_height

    x_component = x_centre - obj_coordinates[0]
    y_component = y_centre - obj_coordinates[1]
    vector_to_centre = (x_component, y_component)

    return vector_to_centre