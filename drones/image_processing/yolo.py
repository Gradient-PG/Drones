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


def detect(
    weights: str,
    img0: np.ndarray,
    conf_tres: float = 0.25,
    img_size: int = 640,
    device_type: str = "cpu",
    classes: list = None,
    iou_thres: float = 0.45,
) -> list:
    """Detect object on image using provided weights. Objects are detected by YOLO neural network

    Parameters:
    ----------
        weights: str
            path to weights we want to use.
        img0: np.ndarray
            image on which objects detection will be proceeded
        conf_tres: float. Default is 0.25
            This parameter represent confidence level in which object should be detected.
        img_size:
            Size on which image should be rescaled. Larger image will provide better output, but it will take
            significant longer to proceed. Doubling img size will result 4 times longer processing time
        device_type: str. Default is cpu, Possible options are cuda devices i.e. 0 or 0, 1, 2, 3 or cpu
            Represents type of device on which we will proceed with predictions
        classes: Tuple of Ints. Default is None
            Classes we are interested to have results. Giving none means we want to have all classes
        iou_thres: float. Default is 0.45
            IOU threshold for NMS. It is responsible for bounding boxes and their size.

    Returns:
    ----------
        It returns list of all detected objects on photo. Every element consist 5 values. First one is recognized class
        name. Others are central position of object(x,y) and size of object(width, height).
        All values are normalized in yolo norm.
        To have position and size on original photo you have to multiply this results by original photo size.
    """
    # Load model
    model = attempt_load(weights, map_location=device_type)  # load FP32 model
    stride = int(model.stride.max())  # model stride
    img_size = check_img_size(img_size, s=stride)  # check img_size
    img = img0.copy()

    img = letterbox(img, img_size, stride)[0]

    # Convert
    img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
    img = np.ascontiguousarray(img)

    # Get names and colors
    names = model.module.names if hasattr(model, "module") else model.names

    device = select_device(device_type)

    # Run inference
    if device.type != "cpu":
        model(torch.zeros(1, 3, img_size, img_size).to(device).type_as(next(model.parameters())))  # run once
    t0 = time.time()
    result = []
    image = torch.from_numpy(img).to(device)
    image = image.float()  # uint8 to fp16/32
    image /= 255.0  # 0 - 255 to 0.0 - 1.0
    if image.ndimension() == 3:
        image = image.unsqueeze(0)

    # Inference
    pred = model(image)[0]

    # Apply NMS
    pred = non_max_suppression(pred, conf_tres, iou_thres, classes=classes)

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


def detect_object_yolo(image: np.ndarray) -> list:
    """Function will detect objects on given image and return position and width of object, which class is chosen in
    config file. Many parameters of detection such as weights, thresholds and others can be set inside config file. In
    case of many objects detected, all of them will be returned.

    Parameters:
    ----------
        img0: np.ndarray
            image on which objects detection will be proceeded

    Returns:
    ----------
        center_and_diameter: list of tuples(int, int, int)
            Every found instance of object defined in config file has it's own tuple. Every tuple have 3 values, which
            represent object center coordinates(x,y) and width
            If the object is not detected list will be empty.
    """
    config_parser = configparser.ConfigParser()
    config_parser.read("image_processing/config.ini")
    config = config_parser["YOLO"]

    # Parse classes from config
    config_classes = config["CLASSES"]
    if config_classes != "None":
        det_classes = config_classes.split(" ")
        classes = []
        for det_class in det_classes:
            classes.append(int(det_class))
    else:
        classes = None  # type: ignore

    # Using yolo detect object on photo
    results = detect(
        config["NETWORK_PATH"],
        image,
        conf_tres=float(config["CONFIDENCE_THRESHOLD"]),
        img_size=int(config["IMG_SIZE"]),
        device_type=config["DEVICE"],
        classes=classes,
        iou_thres=float(config["IOU_THRESHOLD"]),
    )

    # Gain image width and height
    image_width = image.shape[1]
    image_height = image.shape[0]

    result_list = []
    # Find proper class on photo. Should be only one represent of this class
    for line in results:
        classification, x_pos, y_pos, width, height = line
        if classification == config["CLASS"]:
            x_pos = int(x_pos * image_width)
            y_pos = int(y_pos * image_height)
            width = int(width * image_width)

            result_list.append((x_pos, y_pos, width))

    return result_list
