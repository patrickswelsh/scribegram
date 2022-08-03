import logging
logging.basicConfig(format='%(asctime)s %(message)s',filename='errors.log',level='ERROR')

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

app.run()