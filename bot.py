
import os
import telebot
import psycopg2
import schedule
import time
import threading
import datetime
import html
from google.cloud import firestore
from telegram.ext import Updater
import streamlit as st
import firebase_admin

from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import firestore


from telegram import Bot

bot = telebot.TeleBot('6719790897:AAHUKj8vphksgWvjfBEAvscLMfsCbDeu-tQ')

def initialize_firebase_app():
    try:
        firebase_admin.get_app()
    except ValueError:
        secrets = st.secrets["firebase-auth"]

        cred = credentials.Certificate({
            "type": secrets["type"],
            "project_id": secrets["project_id"],
            "private_key_id": secrets["private_key_id"],
            "private_key": secrets["private_key"],
            "client_email": secrets["client_email"],
            "client_id": secrets["client_id"],
            "auth_uri": secrets["auth_uri"],
            "token_uri": secrets["token_uri"],
            "auth_provider_x509_cert_url": secrets["auth_provider_x509_cert_url"],
            "client_x509_cert_url": secrets["client_x509_cert_url"]
        })

        # Initialize the Firebase app with the created credential
        firebase_admin.initialize_app(cred,
                                      {
                                          'storageBucket': 'gs://elmeto-12de0.appspot.com'
                                      }
                                      )

# Call the function to initialize the app
initialize_firebase_app()

# Initialize Firestore client
db = firestore.Client()

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

def check_for_new_users():
    try:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'{current_time} Scanning for new users...')

        one_minute_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)

        # Query Firestore for new users added in the last minute
        users_ref = db.collection('users')
        query = users_ref.where('timestamp', '>', one_minute_ago)
        results = query.stream()

        def escape_markdown(text):
            return html.escape(text)

        # Send alert for new users
        for user in results:
            user_data = user.to_dict()
            print(user_data)
            username = user_data.get('uid', 'N/A')
            email = user_data.get('email', 'N/A')
            escaped_username = escape_markdown(username)
            escaped_email = escape_markdown(email)

            message = f"✨ New user has registered:\nusername: {escaped_username}\nemail: {escaped_email}"
            bot.send_message(chat_id='-4218380287', text=message)

    except Exception as e:
        print(f"Connection Failed: {e}")


schedule.every(1).minutes.do(check_for_new_users)

# Define a function to run the bot's polling in a separate thread
def run_bot_polling():
    bot.polling()

# Run the bot's polling in a separate thread
bot_thread = threading.Thread(target=run_bot_polling)
bot_thread.start()

# Run the scheduled tasks in the main thread
while True:
    schedule.run_pending()
    time.sleep(1)

# Form to add a new user
with st.form(key='user_form'):
    st.write('I am some bot')
