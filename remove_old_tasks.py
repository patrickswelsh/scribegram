from typing import Any
from procrastinate import builtin_tasks
from dotenv import load_dotenv
import os

from procrastinate import AiopgConnector, App


load_dotenv()

#Creds for Postgresql server:
DBHOST = os.getenv("DBHOST")
DBUSER = os.getenv("DBUSER")
DBPASSWORD = os.getenv("DBPASSWORD")
DBPORT = os.getenv("DBPORT")
DBNAME = os.getenv("DBNAME")

if DBPORT != '' and DBNAME != '':
    app = App(
        connector=AiopgConnector(dbname=DBNAME, host=DBHOST, user=DBUSER, password=DBPASSWORD, port=DBPORT )
    )
elif DBPORT == '' and DBNAME != '':
    app = App(
        connector=AiopgConnector(dbname=DBNAME, host=DBHOST, user=DBUSER, password=DBPASSWORD)
    )
elif DBNAME == '' and DBPORT != '':
    app = App(
        connector=AiopgConnector(host=DBHOST, user=DBUSER, password=DBPASSWORD, port=DBPORT )
    )
else:
    app = App(
        connector=AiopgConnector(host=DBHOST, user=DBUSER, password=DBPASSWORD)
    )
app.open()


builtin_tasks.remove_old_jobs.defer(max_hours=0)