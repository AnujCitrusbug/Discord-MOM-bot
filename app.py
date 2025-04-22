import discord
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import json  # Import the json library
import re  # Add this line
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

st.set_page_config(page_title="MOM-Bot", layout="centered")
st.title("🤖 MOM-Bot-Running")

# Replace with your bot token
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Replace with the IDs of the Discord channels you want to monitor
TARGET_CHANNEL_IDS = os.getenv("CHANNELS_IDS").split(",")

# Google Docs ID (optional, leave None to create a new doc)
GOOGLE_DOC_ID = os.getenv("GOOGLE_DOC_ID")

# Google Drive configuration
SERVICE_ACCOUNT_INFO = {
    "type": os.getenv("ACCOUNT_TYPE"),
    "project_id": os.getenv("PROJECT_ID"),
    "private_key_id": os.getenv("PRIVATE_KEY_ID"),
    "private_key": os.getenv("PRIVATE_KEY"),
    "client_email": os.getenv("CLIENT_EMAIL"),
    "client_id": os.getenv("CLIENT_ID"),
    "auth_uri": os.getenv("AUTH_URI"),
    "token_uri": os.getenv("TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("UNIVERSE_DOMAIN"),
}
with open("./credentials.json", "w") as e:
    e.write(json.dumps(SERVICE_ACCOUNT_INFO))

# Define the scopes needed for Google Docs and Drive API
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file'
]

# Authenticate with Google Sheets API using the embedded info
creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
service = build('docs', 'v1', credentials=creds)
drive_service = build('drive', 'v3', credentials=creds)

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        lower_content = message.content.lower()
        keywords = ["mom", "demo", "internal demo"]

        if any(keyword in lower_content for keyword in keywords):
            await self.append_to_google_doc(message.content)
            print(f"Appended message containing MOM/demo: {message.content}")

    async def append_to_google_doc(self, content):
        global GOOGLE_DOC_ID

        body = {
            'requests': [
                {
                    'insertText': {
                        'location': {
                            'index': 1  # Append to the end
                        },
                        'text': f"{content}\n\n"
                    }
                }
            ]
        }
        try:
            if GOOGLE_DOC_ID:
                result = service.documents().batchUpdate(documentId=GOOGLE_DOC_ID, body=body).execute()
            else:
                document = {'title': 'Meeting Minutes'}
                created_document = service.documents().create(body=document).execute()
                GOOGLE_DOC_ID = created_document.get('documentId')
                print(f"Created new Google Doc with ID: {GOOGLE_DOC_ID}")
                result = service.documents().batchUpdate(documentId=GOOGLE_DOC_ID, body=body).execute()
        except Exception as e:
            print(f"An error occurred while updating the Google Doc: {e}")

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(DISCORD_BOT_TOKEN)