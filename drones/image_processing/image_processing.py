import numpy as np
import cv2 as cv
import imutils
import configparser
import typing
import drones.image_processing.normalization as normalization
from drones.image_processing.yolo import YoloDetection
from drones.image_processing.utils import distance_to_camera, vector_to_centre
from typing import List, Tuple


class ImageProcessing:
    """
    This class is main class of image processing. It has only one field, which load and store all yolo data such as
    model and other stuff to increase performance. It has one main method, to process_image. All other method in this
    class are used by this method.
    """

    def __init__(self):
        """
        Creates instance of YOLO object, to perform detection using yolo. All parameters can be specified in config
        file.
        """
        self.yolo = YoloDetection()
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read("image_processing/config.ini")
        self.config = self.config_parser["OBJECT"]

        self.focal = int(self.config["FOCAL"])
        self.real_width = float(self.config["WIDTH"])

    def process_image(self, image: np.ndarray) -> List[Tuple[float, float, float]]:
        """
        Detect object, count its distance from camera, pitch and yaw.
        Parameters:
        ----------
        image: np.ndarray
            image to be processed

        Returns:
        ----------
            List of directions and distances of all objects: typing.List is made of typing.Tuple[float,float,float].
            First two values are directions to the object (yaw and pitch). They are counted from image position.
            Distance is counted from real width of the object and focal length of camera. In case of no object
            detection list will be empty.
        """

        detection_list = self.yolo.detect_object_yolo(image)
        image_width = image.shape[1]
        image_height = image.shape[0]
        result_list = []

        if detection_list:
            for x, y, width in detection_list:
                distance = distance_to_camera(self.real_width, self.focal, width)
                vector = vector_to_centre(image_width, image_height, (x, y), 0.5)
                result_list.append(
                    (
                        -vector[0] / image_width * float(self.config["FIELD_OF_VIEW"]),
                        vector[1] / image_height * float(self.config["FIELD_OF_VIEW"]),
                        distance,
                    )
                )

        return result_list
