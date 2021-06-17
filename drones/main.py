"""Main project file.

It's where the API entrypoints are accessed and used for the purpose of the project.
"""

import logging
from connection import c  # Sample library import
import drones.image_processing as image_processing
import cv2 as cv


def setup_log():
    """Setup global log config."""

    logging.basicConfig(
        filename="logfile.log",
        filemode="w",
        level=logging.DEBUG,
        format="[%(filename)s] [%(levelname)s] : %(message)s",
    )
    logging.info("Log initialized")


if __name__ == "__main__":
    setup_log()
    c.connect()  # Sample entrypoint call
    # c.__track_errors()    # Sample invalid call - function inaccessible
    img_processor = image_processing.ImageProcessing()
