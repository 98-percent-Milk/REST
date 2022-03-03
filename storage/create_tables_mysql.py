import mysql.connector
import yaml
from os.path import join, realpath

with open(join(realpath("config"), 'app_conf.yml'), 'r') as f:
    app_config = yaml.safe_load(f.read())
    user = app_config['datastore']['user']
    hostname = app_config['datastore']['hostname']
    password = app_config['datastore']['password']
    database = app_config['datastore']['db']
    port = app_config['datastore']['port']

db_conn = mysql.connector.connect(
    host=hostname, user=user, password=password, database=database)

db_cursor = db_conn.cursor()

db_cursor.execute('''
        CREATE TABLE job_description
        (id INT NOT NULL AUTO_INCREMENT,
         ad_id VARCHAR(250) NOT NULL,
         trace_id VARCHAR(250) NOT NULL,
         date_created VARCHAR(100) NOT NULL,
         description VARCHAR(250) NOT NULL,
         employer VARCHAR(100) NOT NULL,
         field VARCHAR(100) NOT NULL,
         position VARCHAR(100) NOT NULL,
         CONSTRAINT job_description_pk PRIMARY KEY (id))
        ''')

db_cursor.execute("""
        CREATE TABLE employee_resume
        (id INT NOT NULL AUTO_INCREMENT,
         resume_id VARCHAR(250) NOT NULL,
         trace_id VARCHAR(250) NOT NULL,
         date_created VARCHAR(100) NOT NULL,
         experience INTEGER NOT NULL,
         field VARCHAR(100) NOT NULL,
         position VARCHAR(100) NOT NULL,
         CONSTRAINT employee_resume_pk PRIMARY KEY (id))
""")

db_conn.commit()
db_conn.close()
