# main.py
import streamlit as st
import pandas as pd
import re
from langdetect import detect, LangDetectException #added extra measure to detect Chinese text
from translation_pipeline.run_pipeline import translation_pipeline   # import translation pipeline
from openai_calls.translator import convert_markdown_to_word
from helper_functions.utility import check_password
from helper_functions.config import get_secret

import os
from pathlib import Path

BASE_DIR = Path(os.getcwd())
LOGO_PATH = BASE_DIR / "Images" / "logo.PNG"

# Streamlit Page Config
st.set_page_config(
    layout="centered",
    page_title="TongTranslate"
)

# Do not continue if check_password is not True.  
if not check_password():  
    st.stop()

#display logo and title 

col1, col2 = st.columns([1, 6])

with col1:
    st.image(str(LOGO_PATH), width=80)

with col2:
    st.title("TongTranslate")
    st.caption("Chinese → English Translation Prototype")

# Input form 
with st.form(key="form"):
    st.subheader("Enter Chinese text to translate")
    user_prompt = st.text_area("Input text", height=200)
    submitted = st.form_submit_button("Run Translation")

#identify mixed characters
def contains_chinese(text):
    """Return True if the text has at least one Chinese character."""
    return bool(re.search(r'[\u4e00-\u9fff]', text))

# Upon user input
if submitted:
    if not user_prompt.strip():
        st.warning("Please enter Chinese text before submitting.")
    
    # inspect if text is in Chinese
    else:
        try:
            lang = detect(user_prompt)
            if lang not in ["zh-cn", "zh-tw", "zh"] and not contains_chinese(user_prompt):
                st.warning ("⚠️ Please enter Chinese text.")
                st.stop()
        except LangDetectException:
            st.warning ("Unable to detect language.  Please check your input.")
            st.stop()

    # #run translation pipeline if Chinese input
    with st.spinner("Running translation pipeline... this may take a few minutes depending on length of Chinese text ⏳"):
        try:
            result, final_terms = translation_pipeline(user_prompt)
        except Exception as e:
            st.error(f"⚠️ An error occurred: {e}")
            st.stop()

        st.success("✨ Translation complete!")

        # Store result so we can show + download it
        st.session_state["translation_result"] = result
        st.session_state["final_terms"] = final_terms

    # If there is a translation result, display it and offer download
    if "translation_result" in st.session_state:
        result = st.session_state["translation_result"]
        final_terms = st.session_state.get("final_terms", [])

        if isinstance(result, dict):
            st.json(result)
        elif isinstance(result, pd.DataFrame):
            st.dataframe(result)
        else:
            st.write(result)

            # Prepare docx for download
            doc_path = convert_markdown_to_word(result)
            with open(doc_path, "rb") as f:
                file_bytes = f.read()

            st.download_button(
                label="⬇️ Download Word Document",
                data=file_bytes,
                file_name="translation.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                on_click="ignore"
            )
        # Display the final_terms glossary list
        if final_terms:
            st.subheader("Glossary Terms Used in Translation")

            # Convert list of dicts → DataFrame
            df_terms = pd.DataFrame(final_terms)

            # Make links readable (convert lists to line-separated strings)
            if "links" in df_terms.columns:
                df_terms["links"] = df_terms["links"].apply(
                    lambda x: "\n".join(x) if isinstance(x, list) else x
                )

            st.dataframe(df_terms)
        
        # if no glossary
        else:
            st.info("No glossary terms were used in this translation.")

    st.toast("💯 Translation completed!")

#Disclaimer
with st.expander("Disclaimer"):
    st.markdown("""

**IMPORTANT NOTICE**: This web application is a prototype developed for **educational purposes only**. 
The information provided here is NOT intended for **real-world usage** and should not be relied upon for making any decisions, especially those related to financial, legal, or healthcare matters.

**Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You assume full responsibility for how you use any generated output.**

Always consult with qualified professionals for accurate and personalised advice.
                
                """)

