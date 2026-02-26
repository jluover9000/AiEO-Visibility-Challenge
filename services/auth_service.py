import streamlit as st
from config import APP_PASSWORD


def check_password() -> bool:
    """
    Simple password check using Streamlit session state.
    Returns True if authenticated, False otherwise.
    """
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("🔒 Authentication Required")
    st.write("Please enter the password to access the Multi-LLM Prompt Tester.")

    password = st.text_input("Password", type="password", key="password_input")
    
    if st.button("Login"):
        if password == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")
    
    return False
