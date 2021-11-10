#!/usr/bin/env python

import base64
import cv2
import numpy as np

from webcolors import rgb_to_name
from time import sleep

from color_grouper import logger
from color_grouper.message_queue import Messaging

class Generator():
    def __init__(self):

        self.log = logger.setup_logger(__name__)
        self.input_messaging = Messaging("pictures")
        self.output_messaging = Messaging("color_result")

    def get_image_from_queue(self):
        image_data_decoded = self.input_messaging.get_msg()
        if image_data_decoded is None:
            return None
        # image_data = cv2.imdecode(image_data_encoded, )
        np_image = np.frombuffer(image_data_decoded, dtype=np.uint8)
        return cv2.imdecode(np_image, flags=cv2.IMREAD_COLOR)


    def process_image(self):
        img = self.get_image_from_queue()
        if img is None:
            self.log.info("No new messages in the queue")
            return None
        # get mean color of the image, and flip it back to RGB format
        mean_color = np.mean(img, axis=(0, 1))[::-1]
        mean_color = tuple(map(int, mean_color))
        # get name of the color
        try:
            color_name = rgb_to_name(mean_color)
        except ValueError as ex:
            self.log.exception("Can't find appropriate color: %s", ex)
            return None
        self.log.debug(f"Image mean color: {mean_color} with name: {color_name}")
        self.output_messaging.send_json_msg({"image": base64.b64encode(cv2.imencode(".PNG", img)[1]).decode(),
                                        "color_name": color_name})
        return True


def main():
    Generator().process_image()


if __name__ == "__main__":
    main()
    