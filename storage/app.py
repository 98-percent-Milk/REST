import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from employee_resume import EmployeeResume
from job_description import JobDescription
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from os.path import realpath, join
from json import loads, dumps
import logging
import logging.config
import mysql.connector
import pymysql
import yaml

with open(join(realpath("config"), 'app_conf.yml'), 'r') as f:
    app_config = yaml.safe_load(f.read())
    user = app_config['datastore']['user']
    password = app_config['datastore']['password']
    hostname = app_config['datastore']['hostname']
    port = app_config['datastore']['port']
    db = app_config['datastore']['db']


with open(join(realpath("config"), "log_conf.yml"), 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine(
    f"mysql+pymysql://{user}:{password}@{hostname}:{port}/{db}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def process_messages():
    """ Process event messages """
    session = DB_SESSION()
    h_name = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    client = KafkaClient(hosts=h_name)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(consumer_group=b'event group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)

    for msg in consumer:
        msg_str = msg.value.decode()
        msg = loads(msg_str)
        logger.info(f"Message: {msg}")

        body = msg['payload']

        if msg["type"] == "employers":
            bp = JobDescription(body['ad_id'],
                                body['trace_id'],
                                body['description'],
                                body['employer'],
                                body['field'],
                                body['position'])
        elif msg["type"] == "employee":
            bp = EmployeeResume(body['resume_id'],
                                body['trace_id'],
                                body['experience'],
                                body['field'],
                                body['position'])
        logger.debug(
            f"Stored event {msg['type']} request with a trace id of {body['trace_id']}")
        session.add(bp)
        session.commit()
        consumer.commit_offsets()
    logger.info("Finished processing messages")
    session.close()
    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
# app.add_api(join(realpath("config"), 'openapi.yaml'),
#             strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
