#!/usr/bin/env python
import pika
import base64
import json

from pika import exceptions, spec

from color_grouper import logger

log = logger.setup_logger(__name__)

class Messaging():
    def __init__(self, queue_name=None):
        # create messagin connection, channel and queue, the name is irrelevant for us
        if queue_name is None:
            self.queue = 'pictures'
        else:
            self.queue = queue_name
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue)

    def send_msg(self, data):
        log.debug("Sending message to message queue")
        try:
            if isinstance(data, str):
                log.warning("Sending a string: ", data)
                self.channel.basic_publish(exchange='', routing_key=self.queue, body=data)
            else:
                self.channel.basic_publish(exchange='', routing_key=self.queue, body=base64.b64encode(data))
        except exceptions.AMQPError as ex:
            log.exception("Message queue exception raised while sendind a message: %s", ex)
            return
        log.debug("Message is sent")

    def send_json_msg(self, data):
        log.debug("Sending message to message queue")
        try:
            self.channel.basic_publish(exchange='', routing_key=self.queue, body=json.dumps(data),
            properties=spec.BasicProperties(content_type="json"))
        except exceptions.AMQPError as ex:
            log.exception("Message queue exception raised while sendind a message: %s", ex)
            return
        except TypeError as ex:
            log.exception("Error accured while json processing: %s", ex)
            return
        log.debug("Message is sent")

    def get_msg(self):
        method_frame, header_frame, body = self.channel.basic_get(self.queue)
        if method_frame:
            if header_frame.content_type == "json":
                data = json.loads(body)
            else:
                data = base64.b64decode(body)
            print(method_frame, header_frame, len(data))
            self.channel.basic_ack(method_frame.delivery_tag)
            return data
        else:
            print(f'No new messages in {self.queue} queue')
        return None


if __name__ == "__main__":
    messaging = Messaging()
    msg = messaging.get_msg()
    
