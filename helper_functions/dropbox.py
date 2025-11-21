import dropbox
from io import BytesIO
import pandas as pd
import streamlit as st
from helper_functions.dropbox_auth import get_fresh_access_token


def get_dbx():
    """Initialize Dropbox client using a fresh access token."""
    access_token = get_fresh_access_token()   # NEW LINE
    return dropbox.Dropbox(access_token)


def read_csv_from_dropbox(path="/Apps/TongTranslate/Resources/glossary.csv"):
    """Read a CSV file from Dropbox and return a pandas DataFrame."""
    dbx = get_dbx()
    metadata, response = dbx.files_download(path)
    data = response.content
    df = pd.read_csv(BytesIO(data), encoding="utf-8-sig")
    return df


def write_csv_to_dropbox(df, path="/Apps/TongTranslate/Resources/glossary.csv"):
    """Write (overwrite) a pandas DataFrame to Dropbox as CSV."""
    dbx = get_dbx()
    buffer = BytesIO()
    df.to_csv(buffer, index=False, encoding="utf-8-sig")
    buffer.seek(0)
    dbx.files_upload(
        buffer.read(),
        path,
        mode=dropbox.files.WriteMode.overwrite
    )
