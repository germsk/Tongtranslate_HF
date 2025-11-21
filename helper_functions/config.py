import os
import streamlit as st
from dotenv import load_dotenv

# Load .env locally (ignored on Streamlit Cloud)
load_dotenv()

def get_secret(key: str):
    """
    Loads a secret value in this priority order:
    1. Local .env environment variable (local development)
    2. Streamlit Cloud st.secrets (deployment)
    """
    return os.getenv(key) or st.secrets.get(key)
