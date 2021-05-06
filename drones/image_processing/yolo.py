import os
import configparser
import typing
import cv2 as cv
import numpy as np


def detect_object_yolo(path: str) -> typing.Tuple[int, int, int, int]:
    config_parser = configparser.ConfigParser()
    config_parser.read("image_processing/config.ini")
    config = config_parser["YOLO"]

    os.system(
        config["ENV_PATH"]
        + "python.exe "
        + config["YOLO_PATH"]
        + "detect.py --source "
        + path
        + " --weights D:/domik/Documents/yolo/yolov5/yolov5l.pt --conf 0.25 --save-txt"
    )

    result_path = "runs\\detect\\exp"
    if config["RUNS"] != "1":
        result_path = result_path + config["RUNS"]
    result_path += "\\labels\\"

    start = (-1, -1)
    width, height = 0.0, 0.0
    img = np.zeros((1, 1))
    for result in os.listdir(result_path):
        file = open(result_path + result)
        img = cv.imread(path + os.path.basename(file.name)[:-3] + "jpg")
        for line in file:
            classification, x_pos_str, y_pos_str, width_str, height_str = line.split(" ")
            x_pos, y_pos, width, height = float(x_pos_str), float(y_pos_str), float(width_str), float(height_str)
            start = (int((x_pos - (width / 2)) * img.shape[1]), int((y_pos - (height / 2)) * img.shape[0]))
            end = (int((x_pos + (width / 2)) * img.shape[1]), int((y_pos + (height / 2)) * img.shape[0]))
            color = (0, 255, 0)
            if classification == config["CLASS"]:
                img = cv.rectangle(img, start, end, color, 6)
                text_width, text_height = cv.getTextSize("piwo", 0, fontScale=1, thickness=1)[0]
                start_border = (start[0] + 5, start[1])
                end = (start[0] + text_width, start[1] + text_height)
                img = cv.rectangle(img, start_border, end, color, 6, cv.FILLED)
                img = cv.putText(img, "piwo", start, 0, 1, (0, 0, 0), 1)

        cv.imwrite(os.path.basename(file.name)[:-3] + "jpg", img)
    return start[0], start[1], int(width * img.shape[1]), int(height * img.shape[0])
