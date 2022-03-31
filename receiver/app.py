from http import client
import connexion
from connexion import NoContent
import requests
import yaml
import logging
import logging.config
from datetime import datetime
from json import dumps
from uuid import uuid1
from os.path import join, realpath
from os import environ
from pykafka import KafkaClient
from time import sleep

if "TARGET_ENV" in environ and environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
    advertisement = app_config['eventstore1']['url']
    resume = app_config['eventstore2']['url']
    hostname = app_config['events']['hostname']
    port = app_config['events']['port']
    count = 1
    while count < app_config['service']['max_tries']:
        try:
            logger.info(f"Trying to connect to Kafka. Current try: {count}")
            client = KafkaClient(
                hosts=f"{hostname}:{port}")
            topic = client.topics[str.encode(app_config["events"]["topic"])]
            break
        except:
            logger.error("Attempt to create Kafka connection failed")
            sleep(app_config['service']['sleep_time'])
            count += 1
    producer = topic.get_sync_producer()


logger.info(f"App Conf File: {app_conf_file}")
logger.info(f"App Log File: {log_conf_file}")


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
app.add_api(join(realpath("config"), 'openapi.yaml'), base_path="/receiver",
            strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=8080)
