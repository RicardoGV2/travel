import streamlit as st
from time import sleep
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.source_util import get_pages
import os
from user_management import authenticate_user, load_users

# Paths to the debts files
debts_file = "debts.json"
debts_history_file = "debts_history.json"
votes_file = "votes.json"
data_file = "data.json"
checklists_file = "checklists.json"

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

        if st.session_state.get("logged_in", False):
            st.write(f"Logged in as: {st.session_state.username}")  # Display the current user
            st.page_link("pages/page1.py", label="Voting", icon="⚖️")
            st.page_link("pages/page2.py", label="Time-Line", icon="⏲️")
            st.page_link("pages/page3.py", label="Debt Management", icon="💲")
            st.page_link("pages/page4.py", label="Checklist", icon="✅")

            st.write("")
            st.write("")

            # Delete all JSON files button (visible only to Ricardo)
            if st.session_state.username == 'Ricardo':
                if st.button("Delete All JSON Files"):
                    delete_all_json_files()
                if st.checkbox("Show Debts JSON"):
                    st.json(load_data(debts_file, {}))
                if st.checkbox("Show Debts History JSON"):
                    st.json(load_data(debts_history_file, []))
                if st.checkbox("Show Votes JSON"):
                    st.json(load_data(votes_file, {}))
                if st.checkbox("Show Data JSON"):
                    st.json(load_data(data_file, {}))
                if st.checkbox("Show Checklists JSON")):
                    st.json(load_data(checklists_file, {}))

            if st.button("Log out"):
                logout()

        elif get_current_page_name() != "main":
            # If anyone tries to access a secret page without being logged in,
            # redirect them to the login page
            st.switch_page("main.py")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""  # Clear the username
    st.info("Logged out successfully!")
    sleep(0.5)
    st.switch_page("main.py")

def delete_all_json_files():
    json_files = [debts_file, debts_history_file, votes_file, data_file, checklists_file]
    for file in json_files:
        if os.path.exists(file):
            os.remove(file)
    st.success("All JSON files have been deleted.")
    st.experimental_rerun()

def load_data(file_path, default_data):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        return default_data
