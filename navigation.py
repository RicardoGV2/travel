import streamlit as st
from time import sleep
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.source_util import get_pages
import os
import json

# Paths to the users file
users_file = "users.json"

# Function to load users
def load_users(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        return {}

# Load users
users_data = load_users(users_file)

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

            # Show page4 if the user is Ricardo
            if st.session_state.username == "Ricardo":
                st.page_link("pages/page5.py", label="JSONS", icon="📄")

            st.write("")
            st.write("")

            # Change password button
            if st.button("Change Password"):
                st.session_state.show_change_password = True

            # Delete all JSON files button (visible only to Ricardo)
            if st.session_state.username == 'Ricardo':
                if st.button("Delete All JSON Files"):
                    delete_all_json_files()

            if st.button("Log out"):
                logout()

            # Change Password Popover
            if 'show_change_password' in st.session_state and st.session_state.show_change_password:
                with st.sidebar.expander("Change Password", expanded=True):
                    new_password = st.text_input("New Password", type="password")
                    confirm_password = st.text_input("Confirm New Password", type="password")

                    if st.button("Submit"):
                        if new_password == confirm_password:
                            users_data[st.session_state.username]['password'] = new_password
                            with open(users_file, 'w') as file:
                                json.dump(users_data, file, indent=4)
                            st.success("Password changed successfully!")
                            sleep(2)  # Wait for 3 seconds before closing the popover
                            st.session_state.show_change_password = False
                            st.experimental_rerun()  # Hide the popover after successful submission
                        else:
                            st.error("Passwords do not match.")

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
    if os.path.exists(debts_file):
        os.remove(debts_file)
    if os.path.exists(debts_history_file):
        os.remove(debts_history_file)
    if os.path.exists(checklist_file):
        os.remove(checklist_file)
    st.success("All JSON files have been deleted.")
    st.experimental_rerun()
