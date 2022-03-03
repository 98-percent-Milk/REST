from os.path import join, realpath
import mysql.connector
import yaml
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

db_cursor.execute("""
    DROP TABLE employee_resume, job_description
""")

db_conn.commit()
db_conn.close()
