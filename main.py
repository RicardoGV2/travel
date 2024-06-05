import streamlit as st
from time import sleep
from navigation import make_sidebar
from streamlit_cookies_manager import EncryptedCookieManager

# This should be on top of your app, for example in main.py
cookies = EncryptedCookieManager(prefix="myapp/")

# This should be inside your app
if not cookies.ready():
    # Wait for the component to load and send us current cookies.
    st.stop()

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
        cookies["logged_in"] = "true"
        cookies["username"] = username
        cookies.save()
        st.session_state.logged_in = True
        st.session_state.username = username  # Store the username in session state
        st.success("Logged in successfully!")
        sleep(0.5)
        st.switch_page("pages/page1.py")
    else:
        st.error("Incorrect username or password")

# Check if the user is already logged in
if cookies.get("logged_in") == "true":
    st.session_state.logged_in = True
    st.session_state.username = cookies.get("username")
    st.success(f"Welcome back, {st.session_state.username}!")
    sleep(0.5)
    st.switch_page("pages/page1.py")
