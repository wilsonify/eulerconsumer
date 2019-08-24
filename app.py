import os
import sys
import logging
from logging.config import dictConfig
import pika

routing_key = "green"


def create_connection_channel():
    logging.info("create_connection_channel")
    cred = pika.PlainCredentials("guest", "guest")
    connection_parameters = pika.ConnectionParameters(
        host="172.17.0.2",
        port=5672,
        heartbeat=10000,
        blocked_connection_timeout=10001,
        credentials=cred,
    )

    connection = pika.BlockingConnection(connection_parameters)

    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)

    channel.exchange_declare(exchange="try_green", exchange_type="topic")
    channel.exchange_declare(exchange="done_green", exchange_type="topic")
    channel.exchange_declare(exchange="fail_green", exchange_type="topic")

    channel.queue_declare("try_green", exclusive=True)
    channel.queue_declare("done_green", exclusive=True)
    channel.queue_declare("fail_green", exclusive=True)

    channel.queue_bind(queue="try_green", exchange="try_green", routing_key="green")
    channel.queue_bind(queue="done_green", exchange="done_green", routing_key="green")
    channel.queue_bind(queue="fail_green", exchange="fail_green", routing_key="green")

    return channel


def route_callback(ch, method, properties, body):
    logging.info("route_callback")

    try:
        callback(ch, method, properties, body)
        logging.info("done")
        ch.basic_publish(exchange="done_green", routing_key=routing_key, body=body)

    except:
        logging.info("failed")
        ch.basic_publish(exchange="fail_green", routing_key=routing_key, body=body)


def callback(ch, method, properties, body):
    logging.info("callback")
    print(" [x] %r:%r" % (method.routing_key, body))


def main():
    logging.info("main")
    channel = create_connection_channel()
    print(" [*] Waiting for logs. To exit press CTRL+C")
    channel.basic_consume(
        queue="try_green", on_message_callback=route_callback, auto_ack=True
    )

    channel.start_consuming()


if __name__ == "__main__":
    logging_config_dict = dict(
        version=1,
        formatters={
            "simple": {
                "format": """%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s"""
            }
        },
        handlers={"console": {"class": "logging.StreamHandler", "formatter": "simple"}},
        root={"handlers": ["console"], "level": logging.DEBUG},
    )

    dictConfig(logging_config_dict)
    main()
