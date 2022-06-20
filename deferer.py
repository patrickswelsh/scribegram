import os
from dotenv import load_dotenv
import logging

from procrastinate import Psycopg2Connector, App

load_dotenv()



#Creds for Postgresql server:
DBHOST = os.getenv("DBHOST")
DBUSER = os.getenv("DBUSER")
DBPASSWORD = os.getenv("DBPASSWORD")
DBPORT = os.getenv("DBPORT")
DBNAME = os.getenv("DBNAME")

if DBPORT != '' and DBNAME != '':
    app = App(
        connector=Psycopg2Connector(dbname=DBNAME, host=DBHOST, user=DBUSER, password=DBPASSWORD, port=DBPORT ), worker_defaults={"delete_jobs": "always"}
    )
elif DBPORT == '' and DBNAME != '':
    app = App(
        connector=Psycopg2Connector(dbname=DBNAME, host=DBHOST, user=DBUSER, password=DBPASSWORD), worker_defaults={"delete_jobs": "always"}
    )
elif DBNAME == '' and DBPORT != '':
    app = App(
        connector=Psycopg2Connector(host=DBHOST, user=DBUSER, password=DBPASSWORD, port=DBPORT ), worker_defaults={"delete_jobs": "always"}
    )
else:
    app = App(
        connector=Psycopg2Connector(host=DBHOST, user=DBUSER, password=DBPASSWORD), worker_defaults={"delete_jobs": "always"}
    )
app.open()



#This is the post job
@app.task(name="poster")
def message_post(each_file):
    foo = each_file