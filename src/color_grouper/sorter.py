#!/usr/bin/env python

import base64

import cv2
import numpy as np
import os

from time import sleep
from color_grouper.message_queue import Messaging
from color_grouper import logger


class Sorter():
    COUNTER = 1
    
    def __init__(self):
        self.log = logger.setup_logger(__name__)
        self.messaging = Messaging("color_result")
        self.DEFAULT_PATH = "/output_folder/"

    def sort_image_from_queue(self):
        image_data = self.messaging.get_msg()
        if image_data is None:
            self.log.info("No new messages in the queue")
            return None
        color_name = image_data.get("color_name")
        image_encoded = base64.b64decode(bytes(image_data.get("image"), encoding="utf-8"))
        np_image = np.frombuffer(image_encoded, dtype=np.uint8)
        image = cv2.imdecode(np_image, flags=cv2.IMREAD_COLOR)
        self.create_dir(color_name)
        cv2.imwrite(f"/tmp/test/{color_name}/{self.COUNTER}.png", image)
        self.COUNTER += 1
        return True

    def create_dir(self, color, path_to_dir=None):
        try:
            os.makedirs(os.path.join(path_to_dir or self.DEFAULT_PATH, color))
        except FileExistsError:
            self.log.debug("Directory already exists")


def main():
    Sorter().sort_image_from_queue()


if __name__ == "__main__":
    main()
    