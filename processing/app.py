from datetime import datetime
import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from stats import Stats
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin
import requests
import yaml
import logging
import logging.config
from uuid import uuid1
from os.path import join, realpath
from collections import Counter

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
    results = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    new_stats = {}
    try:
        last_updated = str(results.last_updated)
        logger.info(f"Last timestamp {last_updated}")
    except KeyError:
        print("KEY ERROR! Invalid key input")
    except IndexError:
        logger.info("Stats database is empty")
        last_updated = "2021-10-29 09:12:33"
    current_timestamp = datetime.now().replace(microsecond=0)

    headers = {"content-type": "application/json"}
    resume_res = requests.get(
        url + "/employee/resume?start_timestamp=" + last_updated + "&end_timestamp=" + current_timestamp, headers=headers)
    if resume_res.status_code != 200:
        logger.error("Invalid Resume Events Request!!!")
    else:
        new_stats['num_employees'] = len(
            resume_res.json()) + int(results.num_employees)
        logger.info(
            f"Resume request retrieved {len(resume_res.json())} events.")

    job_res = requests.get(
        url + "/work/ad_description?start_timestamp=" + last_updated + "&end_timestamp=" + current_timestamp, headers=headers
    )
    if job_res.status_code != 200:
        logger.error("Invalid Resume Events Request!!!")
    else:
        logger.info(f"Job request retrieved {len(job_res.json())} events.")

    if len(resume_res.json()) != 0 and len(job_res.json()) != 0:
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
    else:
        logger.info("No new events retrieved from GET requests.")
    session.close()


def calculate_statistics(res_res, job_res, new_stats={}):
    resumes = Counter([x['field'] for x in res_res.json()])
    jobs = Counter([x['field'] for x in job_res.json()])
    total = resumes + jobs
    new_stats['popular_field'] = max(total)
    new_stats['unpopular_field'] = min(total)

    jobs = Counter([x['employer'] for x in job_res.json()])
    new_stats['desp_employer'] = max(jobs)
    new_stats['least_desp_employer'] = min(jobs)


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=period_sec)
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api(join(realpath("config"), 'openapi.yaml'),
            strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)
