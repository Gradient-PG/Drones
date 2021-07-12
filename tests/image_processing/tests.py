""" File containing unit tests for Image Processing module """

import unittest
import cv2
import drones.image_processing as image_processing
import configparser
import os


class YoloDetectionTest(unittest.TestCase):
    """Class containing test cases for YoloDetection class methods"""

    @classmethod
    def setUpClass(cls):
        """
        Method that is called once, before running the tests in the class
        Its main tasks are to create YoloDetection object and to read some images necessary in tests
        """
        cls.yolo_detection = image_processing.yolo.YoloDetection()

        cls.dog_img_width = 3072
        cls.dog_img_height = 2304
        cls.dog_img = cv2.imread("image_processing/resources/dog.JPG")

        cls.bottles_img = cv2.imread("image_processing/resources/bottles.jpeg")

        cls.orange_img_width = 1280
        cls.orange_img_height = 720
        cls.orange_img = cv2.imread("image_processing/resources/orange_indoor.png")

        cls.bottle_and_bed_img_width = 4624
        cls.bottle_and_bed_img_height = 1916
        cls.bottle_and_bed_img = cv2.imread("image_processing/resources/bottle_and_bed.jpg")

    def test_detect_one_dog(self):
        """
        Test that check if yolo can detect dog object in an image correctly
        and return its correct position in yolo format
        """
        results = self.yolo_detection.detect(self.dog_img)

        # In the test image there is only one class - dog
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], "dog")

        # Convert yolo format to pixel format
        x_pos = results[0][1] * self.dog_img_width
        y_pos = results[0][2] * self.dog_img_height
        width = results[0][3] * self.dog_img_width
        height = results[0][4] * self.dog_img_height

        # Check if object frame and its center are in relatively correct position in an image
        # The image is pretty large so I think that 100 pixels don't make much difference
        # Correct values were arbitrarily chosen using human eyes and some tool for labeling
        self.assertAlmostEqual(x_pos, 1100, delta=100)
        self.assertAlmostEqual(y_pos, 1650, delta=100)
        self.assertAlmostEqual(width, 2150, delta=100)
        self.assertAlmostEqual(height, 1300, delta=100)

    def test_detect_object_yolo_one_dog(self):
        """
        Test that check if yolo can detect dog object in an image correctly.
        Moreover conversion from yolo to pixel format is also checked
        and we specify to look only for dog object in an image
        """
        self.yolo_detection.config["CLASS"] = "dog"
        results = self.yolo_detection.detect_object_yolo(self.dog_img)

        # In test image there is only one dog
        self.assertEqual(len(results), 1)

        # Here results should be in pixel format
        x = results[0][0]
        y = results[0][1]
        width = results[0][2]

        # Checked if center of an object and width of its frame have relatively correct values
        # The image is pretty large, so I think that 100 pixels don't make much difference
        # Correct values were arbitrarily chosen using human eyes and some tool for labeling
        self.assertAlmostEqual(x, 1100, delta=100)
        self.assertAlmostEqual(y, 1650, delta=100)
        self.assertAlmostEqual(width, 2150, delta=100)

    def test_detect_bottle_and_bed(self):
        """
        Test that check if yolo can detect bottle and bed objects in an image correctly
        and return their correct positions in yolo format
        """
        results = self.yolo_detection.detect(self.bottle_and_bed_img)

        # The image presents two objects - bottle and bed
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0][0], "bed")
        self.assertEqual(results[1][0], "bottle")

        # Convert yolo format to pixel format
        bed_x_pos = results[0][1] * self.bottle_and_bed_img_width
        bed_y_pos = results[0][2] * self.bottle_and_bed_img_height
        bed_width = results[0][3] * self.bottle_and_bed_img_width
        bed_height = results[0][4] * self.bottle_and_bed_img_height

        bottle_x_pos = results[1][1] * self.bottle_and_bed_img_width
        bottle_y_pos = results[1][2] * self.bottle_and_bed_img_height
        bottle_width = results[1][3] * self.bottle_and_bed_img_width
        bottle_height = results[1][4] * self.bottle_and_bed_img_height

        # Check if object frame and its center are in relatively correct position in an image
        # The image is pretty large so I think that 100 pixels don't make much difference
        # Correct values were arbitrarily chosen using human eyes and some tool for labeling
        self.assertAlmostEqual(bed_x_pos, 4190, delta=100)
        self.assertAlmostEqual(bed_y_pos, 960, delta=100)
        self.assertAlmostEqual(bed_width, 900, delta=100)
        self.assertAlmostEqual(bed_height, 1900, delta=100)

        self.assertAlmostEqual(bottle_x_pos, 2470, delta=100)
        self.assertAlmostEqual(bottle_y_pos, 470, delta=100)
        self.assertAlmostEqual(bottle_width, 200, delta=100)
        self.assertAlmostEqual(bottle_height, 600, delta=100)

    def test_detect_object_yolo_bottle_and_bed(self):
        """
        Test that check if yolo can detect bottle object in an image correctly.
        Moreover conversion from yolo to pixel format is also checked
        and we specify to look only for bottle object in an image
        """
        self.yolo_detection.config["CLASS"] = "bottle"
        results = self.yolo_detection.detect_object_yolo(self.bottle_and_bed_img)

        # In the image there is only one bottle
        self.assertEqual(len(results), 1)

        # Here results should be in pixel format
        x_pos = results[0][0]
        y_pos = results[0][1]
        width = results[0][2]

        # Checked if center of an object and width of its frame have relatively correct values
        # The image is pretty large, so I think that 100 pixels don't make much difference
        # Correct values were arbitrarily chosen using human eyes and some tool for labeling
        self.assertAlmostEqual(x_pos, 2470, delta=100)
        self.assertAlmostEqual(y_pos, 470, delta=100)
        self.assertAlmostEqual(width, 200, delta=100)

    def test_detect_many_bottles(self):
        """
        Test that check if yolo is capable of detecting many objects of the same class in one image
        """
        results = self.yolo_detection.detect(self.bottles_img)

        # In the image there should be 13 bottles and one other objects
        self.assertEqual(len(results), 13)

        # And every object should be in bottle class
        for result in results:
            self.assertEqual(result[0], "bottle")

    def test_detect_object_yolo_many_bottles(self):
        """
        Test that check if yolo is capable of detecting many objects of the same class in the image.
        Here we also specify that the class should be bottle.
        """
        self.yolo_detection.config["CLASS"] = "bottle"
        results = self.yolo_detection.detect_object_yolo(self.bottles_img)

        # There should be 13 bottles in the image
        self.assertEqual(len(results), 13)

    def test_detect_object_yolo_orange(self):
        """
        Tests that check if yolo detect orange object in the image correctly.
        Here we specify that the class should be orange.
        """
        self.yolo_detection.config["CLASS"] = "orange"
        results = self.yolo_detection.detect_object_yolo(self.orange_img)

        # One orange in the image
        self.assertEqual(len(results), 1)

        # Here results should be in pixel format
        x_pos = results[0][0]
        y_pos = results[0][1]
        width = results[0][2]

        # Checked if center of an object and width of its frame have relatively correct values
        # The image and the object in it is quite small, so delta was chosen not to be very large
        # Correct values were arbitrarily chosen using human eyes and some tool for labeling
        self.assertAlmostEqual(x_pos, 690, delta=20)
        self.assertAlmostEqual(y_pos, 290, delta=20)
        self.assertAlmostEqual(width, 70, delta=20)

    def test_detect_orange(self):
        """
        Test that check if yolo detect orange object correctly.
        The algorithm should also detect bed, on which the orange lays
        """
        results = self.yolo_detection.detect(self.orange_img)

        # In the image there should be two objects - orange and bed
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0][0], "bed")
        self.assertEqual(results[1][0], "orange")

        # Convert yolo format to pixel format
        bed_x_pos = results[0][1] * self.orange_img_width
        bed_y_pos = results[0][2] * self.orange_img_height
        bed_width = results[0][3] * self.orange_img_width
        bed_height = results[0][4] * self.orange_img_height

        orange_x_pos = results[1][1] * self.orange_img_width
        orange_y_pos = results[1][2] * self.orange_img_height
        orange_width = results[1][3] * self.orange_img_width
        orange_height = results[1][4] * self.orange_img_height

        # The bed is the background of the image, so it should be detected as whole image
        # Delta was chosen appropriately to such large object
        self.assertAlmostEqual(bed_x_pos, 640, delta=50)
        self.assertAlmostEqual(bed_y_pos, 360, delta=50)
        self.assertAlmostEqual(bed_width, 1280, delta=50)
        self.assertAlmostEqual(bed_height, 720, delta=50)

        # Checked if center of an object and width of its frame have relatively correct values
        # The image and the object in it is quite small, so delta was chosen not to be very large
        # Correct values were arbitrarily chosen using human eyes and some tool for labeling
        self.assertAlmostEqual(orange_x_pos, 690, delta=20)
        self.assertAlmostEqual(orange_y_pos, 290, delta=20)
        self.assertAlmostEqual(orange_width, 70, delta=20)
        self.assertAlmostEqual(orange_height, 80, delta=20)


class UtilsTest(unittest.TestCase):
    """Class containing test cases for functions stored in utils.py file"""

    @classmethod
    def setUpClass(cls):
        """
        Method that is called once, before running the tests in the class
        Its main tasks are to read some images necessary in tests and to get focal length from config
        """
        cls.orange_outdoor_img = cv2.imread("image_processing/resources/orange_outdoor.png")
        cls.orange_indoor_img = cv2.imread("image_processing/resources/orange_indoor.png")

        config_parser = configparser.ConfigParser()
        config_parser.read("../drones/image_processing/config.ini")
        config = config_parser["OBJECT"]
        cls.focal = int(config["FOCAL"])

    def test_distance_to_camera(self):
        """
        Test that check if distance between camera is correctly calculated
        """
        # Distance calculated for black small square
        # Pixel width was defined using OpenCV by detecting the square and averaging its width and height
        # (because the square was not detected perfectly)
        distance_far = image_processing.utils.distance_to_camera(
            known_width=9.6, focal_length=self.focal, pixel_width=383
        )
        distance_close = image_processing.utils.distance_to_camera(
            known_width=9.6, focal_length=self.focal, pixel_width=881
        )

        # Correct distance was measured physically
        # Calculation has to be correct to unity
        self.assertAlmostEqual(distance_far, 45.5, delta=1)
        self.assertAlmostEqual(distance_close, 19, delta=1)

    def test_calculate_focal(self):
        """
        Test that check if focal length is calculated correctly
        """
        # Focal length calculated using black squares images
        # Pixel width was defined using OpenCV by detecting the square and averaging its width and height
        # (because the square was not detected perfectly)
        focal_far = image_processing.utils.calculate_focal(known_width=9.6, known_distance=45.5, pixel_width=383)
        focal_close = image_processing.utils.calculate_focal(known_width=9.6, known_distance=19, pixel_width=881)

        # Check if focal length is at least close to the one from config
        self.assertAlmostEqual(focal_far, self.focal, delta=60)
        self.assertAlmostEqual(focal_close, self.focal, delta=60)

    def test_vector_to_center(self):
        """
        Test that check if calculation of vector from some point to center of image is correct.
        """
        vector = image_processing.utils.vector_to_centre(
            frame_width=100, frame_height=100, obj_coordinates=(75, 75), centre_height_coeff=0.5
        )
        self.assertEqual(vector, (-25, -25))
        vector = image_processing.utils.vector_to_centre(
            frame_width=100, frame_height=100, obj_coordinates=(50, 50), centre_height_coeff=0.5
        )
        self.assertEqual(vector, (0, 0))
        vector = image_processing.utils.vector_to_centre(
            frame_width=100, frame_height=100, obj_coordinates=(50, 50), centre_height_coeff=0.1
        )
        self.assertEqual(vector, (0, -40))
        vector = image_processing.utils.vector_to_centre(
            frame_width=6, frame_height=10, obj_coordinates=(6, 10), centre_height_coeff=0.7
        )
        self.assertEqual(vector, (-3, -3))
        vector = image_processing.utils.vector_to_centre(
            frame_width=5, frame_height=10, obj_coordinates=(0, 0), centre_height_coeff=0.5
        )
        self.assertEqual(vector, (2, 5))
        vector = image_processing.utils.vector_to_centre(
            frame_width=6, frame_height=10, obj_coordinates=(6, 0), centre_height_coeff=0.4
        )
        self.assertEqual(vector, (-3, 4))
        vector = image_processing.utils.vector_to_centre(
            frame_width=6, frame_height=10, obj_coordinates=(0, 10), centre_height_coeff=0.9
        )
        self.assertEqual(vector, (3, -1))

    def test_detect_orange(self):
        """
        Test that check if OpenCV function for detection works correctly for indoor and outdoor orange images
        """
        ((outdoor_x, outdoor_y), outdoor_diameter) = image_processing.utils.detect_object(self.orange_outdoor_img)
        ((indoor_x, indoor_y), indoor_diameter) = image_processing.utils.detect_object(self.orange_indoor_img)

        # Checked if center of an object and diameter of minimal enclosing circle are in relatively correct positions
        # The image and the object in it is quite small, so delta was chosen not to be very large
        # Correct values were arbitrarily chosen using human eyes and some tool for labeling
        self.assertAlmostEqual(outdoor_x, 690, delta=20)
        self.assertAlmostEqual(outdoor_y, 450, delta=20)
        self.assertAlmostEqual(outdoor_diameter, 30, delta=20)

        self.assertAlmostEqual(indoor_x, 690, delta=20)
        self.assertAlmostEqual(indoor_y, 290, delta=20)
        self.assertAlmostEqual(indoor_diameter, 70, delta=20)
