import connexion
from connexion import NoContent
from pykafka import KafkaClient
from pykafka.common import OffsetType
from flask_cors import CORS, cross_origin
import logging
import logging.config
import yaml
from os.path import realpath, join
from os import environ
from json import loads, dumps

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
    hostname = f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}'
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

logger.info(f"App Conf File: {app_conf_file}")
logger.info(f"App Log File: {log_conf_file}")


def get_job_description(index):
    """ Get Job Description Reading in Queue """
    # hostname = f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}'
    # client = KafkaClient(hosts=hostname)
    # topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)

    logger.info(f"Retrieving Job Description at index {index}")
    c = -1
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = loads(msg_str)
            if msg['type'] == "employers":
                c += 1
                if c == index:
                    return msg, 200
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
    except:
        logger.error("No more messages found")

    logger.error(f"Could not find Job Description at index {index}")
    return {"message": "Not Found"}, 404


def get_emp_resume(index):
    """ Get Job Description Reading in Queue """
    hostname = f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}'
    # client = KafkaClient(hosts=hostname)
    # topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)

    logger.info(f"Retrieving Employee Resume at index {index}")
    c = -1
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = loads(msg_str)
            if msg['type'] == "employee":
                c += 1
                if c == index:
                    return msg, 200
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
    except:
        logger.error("No more messages found")

    logger.error(f"Could not find Employee Resume at index {index}")
    return {"message": "Not Found"}, 404


app = connexion.FlaskApp(__name__, specification_dir='')

if "TARGET_ENV" not in environ or environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'

app.add_api(join(realpath("config"), 'openapi.yaml'), base_path="/audit_log",
            strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110)
