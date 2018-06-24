#!/usr/bin/env python3

# Jay Urbain
# jay.urbain@gmail.com

import requests
import time
import argparse
import os

from requests.compat import urljoin

from utils import *
from dialogue_manager import DialogueManager

from chatbot import chatbot

class BotHandler(object):

    def __init__(self, token, dialogue_manager):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)
        self.dialogue_manager = dialogue_manager

    def get_updates(self, offset=None, timeout=30):
        params = {"timeout": timeout, "offset": offset}
        resp = requests.get(urljoin(self.api_url, "getUpdates"), params).json()
        if "result" not in resp:
            return []
        return resp["result"]

    def send_message(self, chat_id, text):
        params = {"chat_id": chat_id, "text": text}
        return requests.post(urljoin(self.api_url, "sendMessage"), params)

    def get_answer(self, question):
        if question == '/start':
            return "Hi, I am your project bot. How can I help you today?"
        return self.dialogue_manager.generate_answer(question)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', type=str, default='')
    parser.add_argument('--modelTag', type=str, default='')
    parser.add_argument('--test', type=str, default='')
    return parser.parse_args()


def is_unicode(text):
    return len(text) == len(text.encode())


class QADialogueManager(object):
    """
    This is the awesome QA chatbot dialogue manager to test the telegram bot.
    """
    def __init__(self):

        # instantiate QA Chatbot
        self.chat = chatbot.Chatbot()
        self.chat.telecomChatBotSessionOpen()
    
    def generate_answer(self, question): 
        answer = self.chat.telecomChatBotSessionQuery(question)
        print("generate answer - question:", question, " answer: ", answer)
        
        return answer

class SimpleDialogueManager(object):
    """
    This is the simplest dialogue manager to test the telegram bot.
    Your task is to create a more advanced one in dialogue_manager.py."
    """
    
    def generate_answer(self, question): 
        return "Hello, world!" 
 
def main():
    args = parse_args()
    token = args.token

    if not token:
        if not "TELEGRAM_TOKEN" in os.environ:
            print("Please, set bot token through --token or TELEGRAM_TOKEN env variable")
            return
        token = os.environ["TELEGRAM_TOKEN"]

    #################################################################
    
    # Your task is to complete dialogue_manager.py and use your 
    # advanced DialogueManager instead of SimpleDialogueManager. 
    
    # This is the point where you plug it into the Telegram bot. 
    # Do not forget to import all needed dependendies when you do so.
    
    qa_manager = QADialogueManager()
    bot = BotHandler(token, qa_manager)
    
    ###############################################################

    print("Ready to talk!")
    offset = 0
    while True:
        updates = bot.get_updates(offset=offset)
        for update in updates:
            print("An update received.")
            if "message" in update:
                chat_id = update["message"]["chat"]["id"]
                if "text" in update["message"]:
                    text = update["message"]["text"]
                    if is_unicode(text):
                        print("Update content: {}".format(update))
                        bot.send_message(chat_id, bot.get_answer(update["message"]["text"]))
                    else:
                        bot.send_message(chat_id, "Hmm, you are sending some weird characters to me...")
            offset = max(offset, update['update_id'] + 1)
        time.sleep(1)

    chatbot.telecomChatBotSessionClose()

if __name__ == "__main__":
    main()
