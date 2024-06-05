import streamlit as st
from time import sleep
from navigation import make_sidebar
from streamlit_cookies_manager import EncryptedCookieManager

# Create a cookie manager
cookies = EncryptedCookieManager(prefix="my_app", key="secret_key")

# Load cookies
if cookies.ready():
    cookies.load()
else:
    st.stop()

make_sidebar()

st.title("Welcome to Australia")

# List of allowed users
allowed_users = ["Jorge", "Raquel", "Karime", "Katia", "Janet", "Ricardo"]
password_placeholder = "Password (use 'australia')"

# Check if the user is already logged in
if cookies.get("logged_in") == "True":
    st.session_state.logged_in = True
    st.session_state.username = cookies.get("username")
    st.success(f"Welcome back, {st.session_state.username}!")
    sleep(0.5)
    st.experimental_rerun()
else:
    # Login form
    username = st.selectbox("Username", options=allowed_users)
    password = st.text_input(password_placeholder, type="password")

    if st.button("Log in", type="primary"):
        if username in allowed_users and password == "australia":
            st.session_state.logged_in = True
            st.session_state.username = username
            cookies.set("logged_in", "True")
            cookies.set("username", username)
            cookies.save()
            st.success("Logged in successfully!")
            sleep(0.5)
            st.experimental_rerun()
        else:
            st.error("Incorrect username or password")
