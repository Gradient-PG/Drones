def calculate_focal(knownWidth: float, knownDistance: float, pixelWidth: int) -> float:
    """
    Calculate focal length of the camera
    focalLength = (pixelWidth * knownDistance) / knownWidth

    Parameters:
    ----------
    knownWidth: float
        measured width of the object (has to be known before running script)
    knownDistance: float
        measured distance between detected object and camera (has to be known before running script)
    pixelWidth: int
        width in pixels of detected object
        
    Returns:
    ----------
    focalLength: float
        calculated length of the focal

    Raises:
    ----------
        ZeroDivisionError: when nominator (knownWidth) is equal 0
    """
    try:
        focalLength = (pixelWidth * knownDistance) / knownWidth
    except ZeroDivisionError as err:
        raise ZeroDivisionError(err)

    return focalLength


def distance_to_camera(knownWidth: float, focalLength: float, pixelWidth: int) -> float:
    """
    Calculate distance between detected object and camera from equation
    distance = (knownWidth * focalLength) / pixelWidth

    Parameters:
    ----------
    knownWidth: float
        measured width of the object (has to be known before running script)
    focalLength: float
        length of the focal
    pixelWidth: int
        width in pixels of detected object

    Returns:
    ----------
    distance: float
        Calculated distance between detected object and camera

    Raises:
    ----------
        ZeroDivisionError: when nominator (pixelWidth) is equal 0
    """
    try:
        distance = (knownWidth * focalLength) / pixelWidth
    except ZeroDivisionError as err:
        raise ZeroDivisionError(err)

    return distance
