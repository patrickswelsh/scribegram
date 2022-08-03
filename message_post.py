import logging
logging.basicConfig(format='%(asctime)s %(message)s',level='ERROR')
import time
from multiprocessing.spawn import import_main_path
from typing import Any
from procrastinate import JobContext, builtin_tasks
from dotenv import load_dotenv
import os
import gspread

from procrastinate import AiopgConnector, App

from googleapiclient import errors
from googleapiclient.discovery import build
from oauth2client import file as oauth_file, client as oauth_client, tools

logging.getLogger("root").setLevel('ERROR')
load_dotenv()

##Credentials and ID for the google sheet we're opening
GOOGLE_ACCOUNT = os.getenv("GOOGLE_ACCOUNT")
SHEET_ID = os.getenv("SHEET_ID")
gc = gspread.service_account(GOOGLE_ACCOUNT)    
sh = gc.open_by_key(SHEET_ID)
worksheet = sh.sheet1

## This is the ID of the appscript we're going to trigger when there's an update.
SCRIPT_ID = os.getenv("SCRIPT_ID")

#Creds for Postgresql server:
DBHOST = os.getenv("DBHOST")
DBUSER = os.getenv("DBUSER")
DBPASSWORD = os.getenv("DBPASSWORD")
DBPORT = os.getenv("DBPORT")
DBNAME = os.getenv("DBNAME")

IDFIELD = os.getenv("IDFIELD")

if DBPORT != '' and DBNAME != '':
    app = App(
        connector=AiopgConnector(dbname=DBNAME, host=DBHOST, user=DBUSER, password=DBPASSWORD, port=DBPORT ),
        worker_defaults={"delete_jobs": "always"}
    )
elif DBPORT == '' and DBNAME != '':
    app = App(
        connector=AiopgConnector(dbname=DBNAME, host=DBHOST, user=DBUSER, password=DBPASSWORD),
        worker_defaults={"delete_jobs": "always"}
    )
elif DBNAME == '' and DBPORT != '':
    app = App(
        connector=AiopgConnector(host=DBHOST, user=DBUSER, password=DBPASSWORD, port=DBPORT ),
        worker_defaults={"delete_jobs": "always"}
    )
else:
    app = App(
        connector=AiopgConnector(host=DBHOST, user=DBUSER, password=DBPASSWORD),
        worker_defaults={"delete_jobs": "always"}
    )

app.open()


@app.task(name="poster")
def message_post(each_file):
    message_ident = 'disabled'
    try:
        worksheet.append_row([each_file['date'],each_file['sender_chat']['id'],each_file['sender_chat']['type'],each_file['sender_chat']['title'],each_file[IDFIELD],each_file['text'],message_ident])
        logging.info('sent this to google: '+str([each_file['date'],each_file['sender_chat']['id'],each_file['sender_chat']['type'],each_file['sender_chat']['title'],each_file[IDFIELD],each_file['text'],message_ident]))
    except:
        worksheet.append_row([each_file['date'],each_file['sender_chat']['id'],each_file['sender_chat']['type'],each_file['sender_chat']['title'],each_file[IDFIELD],each_file['caption'],message_ident])
        logging.info('sent this to google: '+str([each_file['date'],each_file['sender_chat']['id'],each_file['sender_chat']['type'],each_file['sender_chat']['title'],each_file[IDFIELD],each_file['caption'],message_ident]))
    time.sleep(5) ## wait so that Sheets can process things for us
    # Set up the Apps Script API to trigger the outgoing post to telegram
    SCOPES = [
        'https://www.googleapis.com/auth/script.scriptapp',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/script.external_request',
    ]
    store = oauth_file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = oauth_client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('script', 'v1', credentials=creds)

    # Create an execution request object.
    logging.info('sending execution request to google')
    request = {"function": "postToTelgram"}
    ##Log for errors
    # Make the API request.
    response = service.scripts().run(body=request,
            scriptId=SCRIPT_ID).execute()
    logging.info('post request response: '+str(response))
    if 'error' in response:
        # The API executed, but the script returned an error.

        # Extract the first (and only) set of error details. The values of
        # this object are the script's 'errorMessage' and 'errorType', and
        # an list of stack trace elements.
        error = response['error']['details'][0]
        logging.error(str(error))
        if 'scriptStackTraceElements' in error:
            # There may not be a stacktrace if the script didn't start
            # executing.
            logging.error('Script error stacktrace:')
            for trace in error['scriptStackTraceElements']:
                logging.error("\t{0}: {1}".format(trace['function'],
                    trace['lineNumber']))
        else:
            # The structure of the result depends upon what the Apps Script
            # function returns. Here, the function returns an Apps Script Object
            # with String keys and values, and so the result is treated as a
            # Python dictionary (folderSet).
            folderSet = response['response'].get('result', {})
            if not folderSet:
                logging.error('No results returned!')