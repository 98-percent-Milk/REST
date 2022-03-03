from http import client
import connexion
from connexion import NoContent
import requests
import yaml
import logging
import logging.config
from datetime import datetime
from json import dumps, loads
from uuid import uuid1
from os.path import join, realpath
from pykafka import KafkaClient


with open(join(realpath("config"), "app_conf.yml"), 'r') as f:
    app_config = yaml.safe_load(f.read())
    advertisement = app_config['eventstore1']['url']
    resume = app_config['eventstore2']['url']
    hostname = app_config['events']['hostname']
    port = app_config['events']['port']
    client = KafkaClient(
        hosts=f"{hostname}:{port}")
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    producer = topic.get_sync_producer()

with open(join(realpath("config"), "log_conf.yml"), 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')


def add_advertisement_description(body):
    """Add work add description event in to the system"""
    uid = uuid1()
    body['trace_id'] = str(uid)
    msg = {"type": "employers",
           "datetime": str(datetime.now().replace(microsecond=0)),
           "payload": body}
    msg_str = dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    return NoContent, 201


def emp_resume(body):
    """Add employee resume event in to the system"""
    uid = uuid1()
    body['trace_id'] = str(uid)
    msg = {"type": "employee",
           "datetime": str(datetime.now().replace(microsecond=0)),
           "payload": body}
    msg_str = dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api(join(realpath("config"), 'openapi.yaml'),
            strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=8080)
