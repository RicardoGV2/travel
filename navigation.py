import streamlit as st
from time import sleep
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.source_util import get_pages
from streamlit_cookies_manager import EncryptedCookieManager
import os

# Paths to the debts files
debts_file = "debts.json"
debts_history_file = "debts_history.json"
checklist_file = "checklist.json"

# Create a cookie manager
cookies = EncryptedCookieManager(prefix="my_app", key="secret_key")

def get_current_page_name():
    ctx = get_script_run_ctx()
    if ctx is None:
        raise RuntimeError("Couldn't get script context")

    pages = get_pages("")

    return pages[ctx.page_script_hash]["page_name"]

def make_sidebar():
    if cookies.ready():
        cookies.load()
    else:
        st.stop()

    with st.sidebar:
        st.title("🛩️ Australia")
        st.write("")
        st.write("")

        if cookies.get("logged_in") == "True":
            st.write(f"Logged in as: {cookies.get('username')}")
            st.page_link("pages/page1.py", label="Voting", icon="⚖️")
            st.page_link("pages/page2.py", label="Time-Line", icon="⏲️")
            st.page_link("pages/page3.py", label="Debt Management", icon="💲")
            st.page_link("pages/page4.py", label="Checklist", icon="✅")

            st.write("")
            st.write("")

            # Delete all JSON files button (visible only to Ricardo)
            if cookies.get("username") == 'Ricardo':
                if st.button("Delete All JSON Files"):
                    delete_all_json_files()

            if st.button("Log out"):
                logout()

        elif get_current_page_name() != "main":
            st.switch_page("main.py")

def logout():
    cookies.set("logged_in", "False")
    cookies.set("username", "")
    cookies.save()
    st.info("Logged out successfully!")
    sleep(0.5)
    st.experimental_rerun()

def delete_all_json_files():
    if os.path.exists(debts_file):
        os.remove(debts_file)
    if os.path.exists(debts_history_file):
        os.remove(debts_history_file)
    if os.path.exists(checklist_file):
        os.remove(checklist_file)
    st.success("All JSON files have been deleted.")
    st.experimental_rerun()
