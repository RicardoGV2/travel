import streamlit as st
from time import sleep
from navigation import make_sidebar

make_sidebar()

st.title("Welcome to Australia")

# List of allowed users
allowed_users = ["Jorge", "Raquel", "Karime", "Katia", "Janet", "Ricardo"]
password_placeholder = "Password (use 'australia')"

# Check if the user is already logged in
if 'logged_in' in st.session_state and st.session_state.logged_in:
    st.success(f"Welcome back, {st.session_state.username}!")
    sleep(0.5)
    st.switch_page("pages/page1.py")
else:
    # Login form
    username = st.selectbox("Username", options=allowed_users)
    password = st.text_input(password_placeholder, type="password")

    if st.button("Log in", type="primary"):
        if username in allowed_users and password == "australia":
            st.session_state.logged_in = True
            st.session_state.username = username  # Store the username in session state
            st.success("Logged in successfully!")
            sleep(0.5)
            st.switch_page("pages/page1.py")
        else:
            st.error("Incorrect username or password")
