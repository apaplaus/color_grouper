#!/usr/bin/env python
import os
import cv2

from color_grouper.message_queue import Messaging
from color_grouper import logger


class Reader():
    def __init__(self):
        self.log = logger.setup_logger(__name__)
        self.messaging = Messaging()

    def get_images(self):    
        """
        Read message and send them over message queue
        """
        # Folder with input images mounted inside a container
        image_dir = "/image_folder/"
        for file_name in os.listdir(image_dir):
            file_path = os.path.join(image_dir, file_name)
            # test if file is processable image
            cv2.imread(file_path)
            with open(file_path, 'rb') as img:
                if img is None:
                    self.log.error("Can't open the image '%s'", file_path)
                    continue
                retval =self.messaging.send_msg(img.read())
            

def main():
    Reader().get_images()

if __name__ == "__main__":
    main()
