#main.py
import streamlit as st
from time import sleep
from navigation import make_sidebar

# Initialize session state for login if not already done
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

make_sidebar()

st.title("Welcome to Australia")

# List of allowed users
allowed_users = ["Jorge", "Raquel", "Karime", "Katia", "Janet", "Ricardo"]
password_placeholder = "Password (use 'australia')"

# Login form
username = st.selectbox("Username", options=allowed_users)
password = st.text_input(password_placeholder, type="password")

if st.button("Log in", type="primary"):
    if username in allowed_users and password == "australia":
        st.session_state.logged_in = True
        st.session_state.username = username  # Store the username in session state
        st.success("Logged in successfully!")
        sleep(0.5)
        st.experimental_rerun()  # Rerun the script to ensure state is updated
    else:
        st.error("Incorrect username or password")