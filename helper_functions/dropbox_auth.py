import requests
import streamlit as st
import os

def get_fresh_access_token():
    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": os.environ["DROPBOX_REFRESH_TOKEN"],
        "client_id": os.environ["DROPBOX_APP_KEY"],
        "client_secret": os.environ["DROPBOX_APP_SECRET"],
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]