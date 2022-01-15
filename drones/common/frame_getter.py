import multiprocessing
from drones.connection import Connector
import cv2 as cv
import time
from drones.image_processing import ImageProcessing
from drones.common.logger import setup_logger
import logging


class FrameGetterProcess(multiprocessing.Process):
    """Class to store all data needed to sync data between main process, frame processing and this one"""

    def __init__(self, frame_queue: multiprocessing.Queue, stream_address: str):
        multiprocessing.Process.__init__(self)
        self.frame_queue = frame_queue
        self.stream_address = stream_address

    def run(self) -> None:
        """Recieve stream from tello drone using OpenCv video capture. Last frame is stored in self.frame"""

        tello_video = cv.VideoCapture(self.stream_address)
        tello_video.set(cv.CAP_PROP_BUFFERSIZE, 2)
        iterator = 0
        while True:
            # Capture frame-by-framestreamon
            ret, frame = tello_video.read()
            cv.imshow("stream", frame)
            cv.waitKey(1)
            # if frame is read correctly ret is True
            if not ret:
                break
            # No need to take every frame from stream, also it will block taking last available frame
            try:
                if not self.frame_queue.empty():
                    self.frame_queue.get(False)
            except Exception:
                pass
            self.frame_queue.put(frame, False)
            iterator += 1
