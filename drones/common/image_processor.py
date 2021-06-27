import multiprocessing
from drones.connection import Connector
import cv2 as cv
import time
from drones.image_processing import ImageProcessing
from drones.common.logger import setup_logger
import logging


class ImageProcessor(multiprocessing.Process):
    """Class to store all data needed to sync data between processes"""

    def __init__(self, frame_queue, result_queue, dump=False):
        multiprocessing.Process.__init__(self)
        self.frame_queue = frame_queue
        self.result_queue = result_queue
        self.dump = dump

    def run(self) -> None:
        """Get last frame from frame queue, process it and put result in result queue"""
        self.img_processor = ImageProcessing()
        i = 0
        next_frame = None
        while True:
            try:
                while True:
                    next_frame = self.frame_queue.get(False)
            except Exception:
                pass
            if next_frame is not None:
                if self.dump:
                    cv.imwrite(f"frame{i}.png", next_frame)
                self.img_processor.yolo.log.info(f"processing {i} frame")
                answer = self.img_processor.process_image(next_frame)
                self.result_queue.put(answer)
                i += 1
