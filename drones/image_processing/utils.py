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


def vector_to_centre(frameWidth: int, frameHeight: int, objectCoordinates: tuple, centreHeightCoeff: float) -> tuple:
    """
    Calculate vector from tracked object to center of frame

    Parameters:
    ----------
    frameWidth: int
        width of frame captured from camera
    frameHeight: int
        height of frame captured from camera
    objectCoordinates: tuple
        coordinates (x, y) of tracked object's center
    centreHeightCoeff: float
        coefficient defining height of center where tracked object should be

    Returns:
    ----------
    vector_to_centre: tuple
        vector (x, y) from tracked object to center of frame
    """

    xCentre = 0.5 * frameWidth
    yCentre = centreHeightCoeff * frameHeight

    xComponent = xCentre - objectCoordinates[0]
    yComponent = yCentre - objectCoordinates[1]
    vectorToCentre = (xComponent, yComponent)

    return vectorToCentre
