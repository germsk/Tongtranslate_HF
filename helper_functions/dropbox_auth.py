import requests
import streamlit as st

def get_fresh_access_token():
    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": st.secrets["DROPBOX_REFRESH_TOKEN"],
        "client_id": st.secrets["DROPBOX_APP_KEY"],
        "client_secret": st.secrets["DROPBOX_APP_SECRET"],
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]