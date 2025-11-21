# filename: utility.py
import streamlit as st  
import hmac  
import os
  
def check_password():  
    """Returns `True` if the user had the correct password."""  

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        correct_password = os.environ["APP_PASSWORD"]   # Secret from HF

        if hmac.compare_digest(st.session_state["password"], correct_password):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store plaintext password.
        else:
            st.session_state["password_correct"] = False

    # If user already logged in, no need to ask again
    if st.session_state.get("password_correct", False):
        return True

    # Show password input
    st.text_input(
        "Password",
        type="password",          
        on_change=password_entered,
        key="password"           
    )

    # If incorrect password was entered
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Password incorrect")

    return False

