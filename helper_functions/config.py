import os
import streamlit as st
from dotenv import load_dotenv

# Load .env locally (ignored in HuggingFace)
load_dotenv()

def get_secret(key: str):
    """
    Loads a secret value in this priority order:
    1. Local .env environment variable (local development)
    2. HuggingFace environment variable (deployment)
    """
    value = os.environ.get(key)
    if value is None:
        raise KeyError(f"Secret '{key}' not found. Make sure it is set in .env (local) or HF Secrets.")
    return value

