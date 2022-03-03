from datetime import datetime
from os import times_result
from urllib import request
import connexion
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from stats import Stats
from apscheduler.schedulers.background import BackgroundScheduler
from connexion import NoContent
import swagger_ui_bundle
import requests
import yaml
import logging
import logging.config
from uuid import uuid1
from os.path import join, realpath

with open(join(realpath("config"), "app_conf.yml"), 'r') as f:
    app_config = yaml.safe_load(f.read())
    url = app_config['eventstore']['url']
    period_sec = app_config['scheduler']['period_sec']
    filename = app_config['datastore']["filename"]

with open(join(realpath("config"), "log_conf.yml"), 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine(f"sqlite:///{filename}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_stats():
    logger.info("Get stats event started")
    session = DB_SESSION()
    results = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    try:
        data = results.to_dict()
    except:
        logger.error("Statistics do not exist")
        return [], 404
    logger.debug(f"Last statistic {data}")
    logger.info("Get stats event succefully executed")
    return data, 200


def populate_stats():
    """ Periodically update stats """
    session = DB_SESSION()
    logger.info("Start Periodic Processing")
    results = session.query(Stats).order_by(Stats.last_updated.desc())
    new_stats = {}
    try:
        timestamp = str(results[0].last_updated)
        logger.info(f"Last timestamp {timestamp}")
    except KeyError:
        print("KEY ERROR! Invalid key input")
    except IndexError:
        logger.info("Stats database is empty")
        timestamp = "2021-10-29 09:12:33"

    headers = {"content-type": "application/json"}
    resume_res = requests.get(
        url + "/employee/resume?timestamp=" + timestamp, headers=headers)
    if resume_res.status_code != 200:
        logger.error("Invalid Resume Events Request!!!")
    else:
        new_stats['num_employees'] = len(resume_res.json())
        logger.info(
            f"Resume request retrieved {len(resume_res.json())} events.")

    job_res = requests.get(
        url + "/work/ad_description?timestamp=" + timestamp, headers=headers
    )
    if job_res.status_code != 200:
        logger.error("Invalid Resume Events Request!!!")
    else:
        logger.info(f"Job request retrieved {len(job_res.json())} events.")
        logger.debug(f"Populate stats trace id: {uuid1()}")
    calculate_statistics(resume_res, job_res, new_stats)
    stats = Stats(new_stats['num_employees'],
                  new_stats['popular_field'],
                  new_stats['unpopular_field'],
                  new_stats['desp_employer'],
                  new_stats['least_desp_employer'],
                  datetime.now().replace(microsecond=0))
    logger.debug(f"Event Statistics: {new_stats}")
    session.add(stats)
    session.commit()
    session.close()


def calculate_statistics(resumes, jobs, new_stats={}):
    field, employer = {}, {}
    if len(resumes.json()) != 0:
        for resume in resumes.json():
            try:
                field[resume['field']] += 1
            except KeyError:
                field[resume['field']] = 1
        for job in jobs.json():
            try:
                field[job['field']] += 1
            except KeyError:
                field[job['field']] = 1
        new_stats['popular_field'] = max(field)
        new_stats['unpopular_field'] = min(field)
    else:
        new_stats['popular_field'], new_stats['unpopular_field'] = 'Null', 'Null'
    if len(jobs.json()) != 0:
        for job in jobs.json():
            try:
                employer[job['employer']] += 1
            except KeyError:
                employer[job['employer']] = 1
        new_stats['desp_employer'] = max(employer)
        new_stats['least_desp_employer'] = min(employer)
    else:
        new_stats['desp_employer'], new_stats['least_desp_employer'] = "Null", 'Null'


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=period_sec)
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api(join(realpath("config"), 'openapi.yaml'),
            strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)
