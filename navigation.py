import streamlit as st
from time import sleep
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.source_util import get_pages
from streamlit_cookies_manager import EncryptedCookieManager
import os

# Initialize the cookie manager
cookies = EncryptedCookieManager(prefix="my_app", key="your_secret_key")

# Load cookies (must be called in the main script)
if not cookies.ready():
    st.stop()

# Paths to the debts files
debts_file = "debts.json"
debts_history_file = "debts_history.json"

def get_current_page_name():
    ctx = get_script_run_ctx()
    if ctx is None:
        raise RuntimeError("Couldn't get script context")

    pages = get_pages("")

    return pages[ctx.page_script_hash]["page_name"]

def make_sidebar():
    with st.sidebar:
        st.title("🛩️ Australia")
        st.write("")
        st.write("")

        if cookies.get("logged_in", False):
            st.write(f"Logged in as: {cookies['username']}")  # Display the current user
            st.page_link("pages/page1.py", label="Voting", icon="⚖️")
            st.page_link("pages/page2.py", label="Time-Line", icon="⏲️")
            st.page_link("pages/page3.py", label="Debt Management", icon="💲")
            st.page_link("pages/page4.py", label="Checklist", icon="✅")

            st.write("")
            st.write("")

            # Delete all JSON files button (visible only to Ricardo)
            if cookies["username"] == 'Ricardo':
                if st.button("Delete All JSON Files"):
                    delete_all_json_files()

            if st.button("Log out"):
                logout()

        elif get_current_page_name() != "main":
            # If anyone tries to access a secret page without being logged in,
            # redirect them to the login page
            st.switch_page("main.py")

def logout():
    cookies["logged_in"] = False
    cookies["username"] = ""
    cookies.save()
    st.info("Logged out successfully!")
    sleep(0.5)
    st.switch_page("main.py")

def delete_all_json_files():
    if os.path.exists(debts_file):
        os.remove(debts_file)
    if os.path.exists(debts_history_file):
        os.remove(debts_history_file)
    st.success("All JSON files have been deleted.")
    st.experimental_rerun()
