from pprint import pprint
import yaml
import pymysql
import mysql.connector
import logging.config
import logging
import connexion
from connexion import NoContent
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from base import Base
from employee_resume import EmployeeResume
from job_description import JobDescription
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from os.path import realpath, join
from json import loads
from time import sleep

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
    count = 1
    while count < app_config['service']['max_tries']:
        try:
            logger.info(f"Trying to connect to Kafka. Current try: {count}")
            client = KafkaClient(hosts=h_name)
            topic = client.topics[str.encode(app_config["events"]["topic"])]
        except:
            logger.error(f"Attemp to create Kafka connection failed.")
            sleep(app_config['service']['sleep_time'])
            count += 1
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


# Storage system GET method_1
def get_advertisement_description(start_timestamp, end_timestamp):
    """ Retrieve all the Job Description advertisement that are stored after certain timestamp"""
    logger.info(f"Hostname: {hostname}, port: {port}")
    session = DB_SESSION()
    start_timestamp_datetime = datetime.strptime(
        start_timestamp, "%Y-%m-%d %H:%M:%S")
    end_timestamp_datetime = datetime.strptime(
        end_timestamp, "%Y-%m-%d %H:%M:%S")

    readings = session.query(JobDescription).filter(and_(
        JobDescription.date_created >= start_timestamp_datetime,
        JobDescription.date_created < end_timestamp_datetime))
    results_list = [reading.to_dict() for reading in readings]
    session.close()

    logger.info(
        f"Query for Job advertisement description after {start_timestamp} and before {end_timestamp} returns {len(results_list)} results.")

    return results_list, 200


# Storage system GET method_2
def get_emp_resume(start_timestamp, end_timestamp):
    """ Retrieve all the Employee Resume that are stored after certain timestamp """
    logger.info(f"Hostname: {hostname}, port: {port}")
    session = DB_SESSION()
    start_timestamp_datetime = datetime.strptime(
        start_timestamp, "%Y-%m-%d %H:%M:%S")
    end_timestamp_datetime = datetime.strptime(
        end_timestamp, "%Y-%m-%d %H:%M:%S")
    readings = session.query(EmployeeResume).filter(and_(
        EmployeeResume.date_created >= start_timestamp_datetime,
        EmployeeResume.date_created < end_timestamp_datetime))
    results_list = [reading.to_dict() for reading in readings]
    session.close()
    logger.info(
        f"Query for employee resume after {start_timestamp} and before {end_timestamp} returns {len(results_list)} results.")
    return results_list, 200


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api(join(realpath("config"), 'openapi.yaml'),
            strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
