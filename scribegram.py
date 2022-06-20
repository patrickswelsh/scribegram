import logging
logging.basicConfig(format='%(asctime)s %(message)s',filename='verbose.log',level='INFO')

import json
from pyrogram import Client


import os
from dotenv import load_dotenv

from deferer import message_post

load_dotenv()




##Credentials to access the Telegram API for downloading messages
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")



# Connection for Telegram
app = Client(SESSION, API_ID, API_HASH)


## This is the handler that is constantly running, listening for incoming messages
@app.on_message()
def scribe(client, message):
    each_file = json.loads(str(message))
    logging.info('new message: '+str(each_file))
    ## these jsons have different formats depending on the source. so, if/thens.
    ## first determining if its a channel or direct message
    if 'sender_chat' in each_file:
        logging.info('parsed as a chat')
        if 'poll' in each_file:
            logging.info('ignored because it was a poll')
            print('ignored a poll')
        try:
            foo =  each_file['via_bot']['first_name']
            logging.info('ignored because it was from a bot')
            print('ignored a bot')
        except:
            try:
                list = [each_file['date'],each_file['sender_chat']['id'],each_file['sender_chat']['type'],each_file['sender_chat']['title'],each_file['text']]
                logging.info('detected normal message')
                logging.info('activating posting script!')
                message_post.defer(each_file=each_file)
            except:
                try:
                    list = [each_file['date'],each_file['sender_chat']['id'],each_file['sender_chat']['type'],each_file['sender_chat']['title'],each_file['caption']]
                    logging.info('detected photo')
                    logging.info('activating posting script!')
                    message_post.defer(each_file=each_file)
                except:
                    logging.error('message not parsing properly, missing text key or caption key')            
    else:
        logging.error('did not contain chat information')
=======
import json
from pyrogram import Client
import gspread

import time
from googleapiclient import errors
from googleapiclient.discovery import build
from oauth2client import file as oauth_file, client as oauth_client, tools
import asyncio

##Credentials and ID for the google sheet we're opening
gc = gspread.service_account('/home/rhmeetslj/rhmeeetslj-ae10df125593.json')
sh = gc.open_by_key("1GlmGui4bc8Ygf6C3ck0pRTUP7Zz0y17DVfaqei_wit8")
sh2 = gc.open_by_key("1xQObzCsOrofa7gHv4UqRKPxIUSR8bHP6W-hoMQgri9E")
sh3 = gc.open_by_key("1_0sILnkq1YSgB56Tm-KqB6kow977F-vrgdEG8eACvSU")
sh5 = gc.open_by_key("1NtqTsCCQ9vDe4rp1gydEBjdosPogtyRPMR58iAqneM0")
worksheet = sh.sheet1
spamsheet = sh2.sheet1
dmsheet = sh3.sheet1
logsheet = sh5.sheet1

##Credentials to access the Telegram API for downloading messages
api_id = 5411482
api_hash = 'def95ebc957e199351d9080d3418a204'


## This is the ID of the appscript we're going to trigger when there's an update.
SCRIPT_ID = 'AKfycbx76-reNf2J0JCfFVnO15r4UOzd92fXGEhVzjUkVkuhex5n_OurHlCkOtABgiKY-Xgv'


# for some reason, I've had to spell out the api_id in this file instead of using the config.ini file.
app = Client("My_Crypto_Input", api_id, api_hash)
stuff_Lock = asyncio.Lock()

## This is the handler that is constantly running, listening for incoming messages
@app.on_message()
async def dev_my_handler(client, message):
    data = str(message)
    logsheet.append_row([data])
    ## this is how I get the script to split up the json when we get multiple messages in one update
    new_data = data.replace('}\n{', '}\n\n{')
    data_final = new_data.split('\n\n')
    ## this line tells the script to go through the process of creating a new entry in google fo each individual message in the json
    for i in data_final:
        each_file = json.loads(i)
        ## these jsons have different formats depending on the source. so, if/thens.
        ## first determining if its a channel or direct message
        if 'sender_chat' in each_file:
            ### load up the sub-json that is in the 'sender_chat' field
            senderchat = json.dumps(each_file['sender_chat'])
            chat = json.loads(senderchat)
            if 'via_bot' in each_file:
                botchat = json.dumps(each_file['via_bot'])
                bot = json.loads(botchat)
                botnamefield = json.dumps(bot['first_name'])
                botname = json.loads(botnamefield)
            ## Filter out scam and fake messages
            if chat['is_scam'] == True or chat['is_fake'] == True:
                spamsheet.append_row([each_file['date'],chat['id'],chat['type'],chat['title'],each_file['message_id'],each_file['text']])
            else:
                if 'poll' in each_file:
                    foo = 'bar'
                elif 'via_bot' in each_file:
                    if 'VoteBot' in botname:
                        foo = 'bar'
                else:
                    async with stuff_Lock:
                        message_ident = str(chat['id']) + str(each_file['message_id'])

                        worksheet.append_row([each_file['date'],chat['id'],chat['type'],chat['title'],each_file['message_id'],each_file['text'],message_ident])
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
                        request = {"function": "postToTelgram"}
                        ##Log for errors
                        logf = open("errors.log", "w")
                        try:
                            # Make the API request.
                            response = service.scripts().run(body=request,
                                    scriptId=SCRIPT_ID).execute()

                            if 'error' in response:
                                # The API executed, but the script returned an error.

                                # Extract the first (and only) set of error details. The values of
                                # this object are the script's 'errorMessage' and 'errorType', and
                                # an list of stack trace elements.
                                error = response['error']['details'][0]
                                logf.write(str(error))
                                if 'scriptStackTraceElements' in error:
                                    # There may not be a stacktrace if the script didn't start
                                    # executing.
                                    logf.write("Script error stacktrace:")
                                    for trace in error['scriptStackTraceElements']:
                                        logf.write("\t{0}: {1}".format(trace['function'],
                                            trace['lineNumber']))
                            else:
                                # The structure of the result depends upon what the Apps Script
                                # function returns. Here, the function returns an Apps Script Object
                                # with String keys and values, and so the result is treated as a
                                # Python dictionary (folderSet).
                                folderSet = response['response'].get('result', {})
                                if not folderSet:
                                    logf.write('No results returned!')
                        except errors.HttpError as e:
                            # The API encountered a problem before the script started executing.
                            logf.write(e.content)
                        store2 = oauth_file.Storage('token.json')
                        creds2 = store2.get()
                        if not creds2 or creds2.invalid:
                            flow2 = oauth_client.flow_from_clientsecrets('credentials2.json', SCOPES)
                            creds2 = tools.run_flow(flow2, store2)
                        service2 = build('script', 'v1', credentials=creds2)

                        # Create an execution request object.
                        request2 = {"function": "postToTelgram"}
                        ##Log for errors
                        logf = open("errors.log", "w")
                        time.sleep(15) #waiting again
        else:
            if 'from_user' in each_file:
                user = json.dumps(each_file['from_user'])
                user_json = json.loads(user)
                dmsheet.append_row([each_file['date'],each_file['message_id'],user_json['id'],user_json['first_name'],each_file['text']])
            else:
                dmsheet.append_row([each_file['date'],each_file['message_id'],"","",each_file['text']])
app.run()