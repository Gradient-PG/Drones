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


def detect(weights, img0, conf_tres=0.25, img_size=640, device="cpu", classes=None, iou_thres=0.45):
    # Load model
    model = attempt_load(weights, map_location=device)  # load FP32 model
    stride = int(model.stride.max())  # model stride
    img_size = check_img_size(img_size, s=stride)  # check img_size
    img = img0.copy()

    img = letterbox(img, img_size, stride)[0]

    # Convert
    img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
    img = np.ascontiguousarray(img)

    # Get names and colors
    names = model.module.names if hasattr(model, "module") else model.names

    device = select_device(device)

    # Run inference
    if device.type != "cpu":
        model(torch.zeros(1, 3, img_size, img_size).to(device).type_as(next(model.parameters())))  # run once
    t0 = time.time()
    result = []
    img = torch.from_numpy(img).to(device)
    img = img.float()  # uint8 to fp16/32
    img /= 255.0  # 0 - 255 to 0.0 - 1.0
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    # Inference
    pred = model(img)[0]

    # Apply NMS
    pred = non_max_suppression(pred, conf_tres, iou_thres, classes=classes)

    # Process detections
    for i, det in enumerate(pred):  # detections per image
        gn = torch.tensor(img0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
        if len(det):
            # Rescale boxes from img_size to im0 size
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], img0.shape).round()

            # Write results
            for *xyxy, conf, cls in reversed(det):
                xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                line = (names[int(cls)], *xywh)  # label format
                result.append(line)

    print(f"Done. ({time.time() - t0:.3f}s)")
    return result


def detect_object_yolo(image: np.ndarray) -> typing.Tuple[typing.Tuple[int, int], int]:
    config_parser = configparser.ConfigParser()
    config_parser.read("image_processing/config.ini")
    config = config_parser["YOLO"]

    results = detect(config["NETWORK_PATH"], image)

    image_width = image.shape[1]
    image_height = image.shape[0]
    for line in results:
        classification, x_pos, y_pos, width, height = line
        if classification == config["CLASS"]:
            x_pos = int(x_pos * image_width)
            y_pos = int(y_pos * image_height)
            width = int(width * image_width)

            return (x_pos, y_pos), width
    return (-1, -1), -1
