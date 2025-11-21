import streamlit as st
import pandas as pd
from datetime import datetime
from helper_functions.utility import check_password
from pathlib import Path
from helper_functions.dropbox import read_csv_from_dropbox, write_csv_to_dropbox
import os

# region <--------- Streamlit App Configuration --------->
st.set_page_config(
    layout="centered",
    page_title="TongTranslate_Glossary"
)
# endregion <--------- Streamlit App Configuration --------->

# project root = parent of /pages
BASE_DIR = Path(os.getcwd())
# Define folder
IMAGES_DIR = BASE_DIR / "Images"

# Do not continue if check_password is not True.  
if not check_password():  
    st.stop()

# Load Glossary
df = read_csv_from_dropbox("/Resources/glossary.csv")

# create additional columns - edited and last modified to track edits
for col in ["edited", "last_modified"]:
    if col not in df.columns:
        df[col] = "" if col == "last_modified" else False

# Subset shown to user
display_cols = ["chinese", "english", "status", "source", "links"]
df_clean = df[display_cols].copy()

#Title
st.title("✏️Glossary Editor")

#Page description
st.markdown(
    """
    If there are terms which are not translated correctly, you can click inside the table to edit the entry, then click Save Changes.
    """
)

# Editable table
edited_clean = st.data_editor(
    df_clean,
    num_rows="dynamic",
    use_container_width=True
)

# Save changes 
if st.button("💾 Save Changes"):
    df = read_csv_from_dropbox("/Resources/glossary.csv")
    
    for idx in edited_clean.index:

        # existing row
        if idx < len(df):
            old_row = df.loc[idx, display_cols]
            new_row = edited_clean.loc[idx, display_cols]

            if not old_row.equals(new_row):
                df.loc[idx, display_cols] = new_row
                df.at[idx, "edited"] = True
                df.at[idx, "last_modified"] = datetime.now().isoformat()

        # new row
        else:
            df.loc[idx, display_cols] = edited_clean.loc[idx, display_cols]
            df.at[idx, "edited"] = True
            df.at[idx, "last_modified"] = datetime.now().isoformat()

    write_csv_to_dropbox(df, "/Resources/glossary.csv")
    st.success("Changes saved ✔")

    # Reload the dataframe for display so updates show immediately
    df = read_csv_from_dropbox("/Resources/glossary.csv")
    df_clean = df[display_cols].copy()
    st.rerun()

#Instructions on how to edit the glossary
with st.expander("Glossary Features"):
    st.markdown("""
- **Delete entries:** Select one or more rows, then click the **delete** icon at the top of the table.  
- **Add a new entry:** Click the **“+”** icon to insert a new glossary record.  
- **Edit an entry:** Double-click any cell to modify it, then click **“Save Changes”** to update the glossary.  
- **Search or filter terms:** Use the **magnifying glass** icon to locate specific entries.
- **Hide columns**: Click on the **"eye"** icon to show or hide columns.  
- **Download the glossary:** Export the full glossary as a **CSV file** for offline review or backup.
""")
