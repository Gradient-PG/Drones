import numpy as np
import cv2 as cv
import imutils
import configparser
import typing
import drones.image_processing.normalization as normalization
from drones.image_processing.yolo import YoloDetection
from drones.image_processing.utils import distance_to_camera, vector_to_centre


class ImageProcessing:
    def __init__(self):
        self.yolo = YoloDetection()

    def process_image(self, image: np.ndarray) -> list:
        """
        Detect object, count its distance from camera, pitch and yaw
        Parameters:
        ----------
        image: np.ndarray
            image to be processed

        Returns:
        ----------
            list of directions and distances of all objects: list and typing.Tuple[float,float,float] inside
            first two values are direction to object (yaw and pitch). They are counted from image position. Distance is
            counted from real width of object and focal length of camera. In case of no object detection list will be
            empty
        """
        config_parser = configparser.ConfigParser()
        config_parser.read("image_processing/config.ini")
        config = config_parser["OBJECT"]

        focal = int(config["FOCAL"])
        real_width = float(config["WIDTH"])
        detection_list = self.yolo.detect_object_yolo(image)
        image_width = image.shape[1]
        image_height = image.shape[0]
        result_list = []

        if len(detection_list) > 0:
            for detection in detection_list:
                x, y, width = detection
                distance = distance_to_camera(real_width, focal, width)
                vector = vector_to_centre(image_width, image_height, (x, y), 0.5)
                result_list.append(
                    (
                        -(vector[0] / image_width * float(config["FIELD_OF_VIEW"])),
                        vector[1] / image_height * float(config["FIELD_OF_VIEW"]),
                        distance,
                    )
                )

        return result_list
