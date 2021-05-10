import time
import typing
import configparser
import torch
import torch.backends.cudnn as cudnn
import numpy as np
from yolov5.models.experimental import attempt_load
from yolov5.utils.datasets import letterbox
from yolov5.utils.general import check_img_size, non_max_suppression, scale_coords, xyxy2xywh
from yolov5.utils.torch_utils import select_device
import logging


class YoloDetection:
    def __init__(self):
        # initialize config
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read("image_processing/config.ini")
        self.config = self.config_parser["YOLO"]

        # Parse classes from config
        config_classes = self.config["CLASSES"]
        if config_classes != "None":
            det_classes = config_classes.split(" ")
            self.classes = []
            for det_class in det_classes:
                self.classes.append(int(det_class))
        else:
            self.classes = None  # type: ignore

        self.device_type = self.config["DEVICE"]
        self.model = attempt_load(self.config["NETWORK_PATH"], map_location=self.device_type)  # load FP32 model
        self.stride = int(self.model.stride.max())  # model stride
        self.conf_tres = float(self.config["CONFIDENCE_THRESHOLD"])
        self.img_size = int(self.config["IMG_SIZE"])
        self.iou_thres = float(self.config["IOU_THRESHOLD"])

    def detect(self, img0: np.ndarray) -> list:
        """Detect object on image using provided weights. Objects are detected by YOLO neural network

        Parameters:
        ----------
            img0: np.ndarray
                image on which objects detection will be proceeded
        Returns:
        ----------
            It returns list of all detected objects on photo. Every element consist 5 values. First one is recognized
            class name. Others are central position of object(x,y) and size of object(width, height).
            All values are normalized in yolo norm.
            To have position and size on original photo you have to multiply this results by original photo size.
        """
        # Load model

        img_size = check_img_size(self.img_size, s=self.stride)  # check img_size
        img = img0.copy()

        img = letterbox(img, img_size, self.stride)[0]

        # Convert
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)

        # Get names and colors
        names = self.model.module.names if hasattr(self.model, "module") else self.model.names

        device = select_device(self.device_type)

        # Run inference
        if device.type != "cpu":
            self.model(
                torch.zeros(1, 3, img_size, img_size).to(device).type_as(next(self.model.parameters()))
            )  # run once
        t0 = time.time()
        result = []
        image = torch.from_numpy(img).to(device)
        image = image.float()  # uint8 to fp16/32
        image /= 255.0  # 0 - 255 to 0.0 - 1.0
        if image.ndimension() == 3:
            image = image.unsqueeze(0)

        # Inference
        pred = self.model(image)[0]

        # Apply NMS
        pred = non_max_suppression(pred, self.conf_tres, self.iou_thres, classes=self.classes)

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            gn = torch.tensor(img0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(image.shape[2:], det[:, :4], img0.shape).round()

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                    line = (names[int(cls)], *xywh)  # label format
                    result.append(line)

        logging.getLogger(__name__).info(f"Processed image, processing time: ({time.time() - t0:.3f}s)")
        return result

    def detect_object_yolo(self, image: np.ndarray) -> list:
        """Function will detect objects on given image and return position and width of object, which class is chosen
        in config file. Many parameters of detection such as weights, thresholds and others can be set inside config
        file. In case of many objects detected, all of them will be returned.

        Parameters:
        ----------
            img0: np.ndarray
                image on which objects detection will be proceeded

        Returns:
        ----------
            center_and_diameter: list of tuples(int, int, int)
                Every found instance of object defined in config file has it's own tuple. Every tuple have 3 values,
                which represent object center coordinates(x,y) and width.
                If the object is not detected list will be empty.
        """

        # Using yolo detect object on photo
        results = self.detect(image)

        image_width = image.shape[1]
        image_height = image.shape[0]

        result_list = []
        # Find proper class on photo. Should be only one represent of this class
        for line in results:
            classification, x_pos, y_pos, width, height = line
            if classification == self.config["CLASS"]:
                x_pos = int(x_pos * image_width)
                y_pos = int(y_pos * image_height)
                width = int(width * image_width)

                result_list.append((x_pos, y_pos, width))

        return result_list
