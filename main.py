import streamlit as st
from time import sleep
import os
import json
from navigation import make_sidebar
from user_management import authenticate_user
import streamlit.components.v1 as components
from st_keyup import st_keyup

make_sidebar()

st.title("Welcome to Australia")

# Paths to jsons
users_file = "users.json"

# Load users
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        return {}

users_data = load_data(users_file)
allowed_users = list(users_data.keys())
password_placeholder = "Password (use 'australia')"

# Initialize character count in session state
if 'char_count' not in st.session_state:
    st.session_state.char_count = 0

# Login form
username = st.selectbox("Username", options=allowed_users)
password = st_keyup(password_placeholder, key="password_input")

# Update character count
st.session_state.char_count = len(password)

if st.button("Log in", type="primary"):
    if authenticate_user(username, password):
        st.session_state.logged_in = True
        st.session_state.username = username  # Store the username in session state
        st.success("Logged in successfully!")
        sleep(0.5)
        st.switch_page("pages/page1.py")
    else:
        st.error("Incorrect username or password")

st.write(f"Character Count: {st.session_state.char_count}")

# Initialize arrow position in session state
if "arrow_position" not in st.session_state:
    st.session_state.arrow_position = 0

st.session_state.arrow_position = st.session_state.char_count

# Button to move arrow to the right
if st.button("Move Arrow Right"):
    st.session_state.arrow_position += 10

# Custom HTML, CSS, and JavaScript for the arrow animation
st.markdown(f"""
    <style>
    .arrow {{
        width: 0; 
        height: 0; 
        border-left: 10px solid transparent;
        border-right: 10px solid transparent;
        border-bottom: 20px solid red;
        position: absolute;
        animation: bounce 1s infinite;
        left: {st.session_state.arrow_position}px;  /* Adjust to point correctly */
        top: 120px;  /* Adjust this value based on the position of your input field */
    }}
    @keyframes bounce {{
        0%, 20%, 50%, 80%, 100% {{
            transform: translateY(0); 
        }}
        40% {{
            transform: translateY(-10px); 
        }}
        60% {{
            transform: translateY(-5px); 
        }}
    }}
    </style>
    <div class="arrow" id="arrow"></div>
""", unsafe_allow_html=True)

components.iframe("https://lottie.host/embed/b95a4da8-6ec1-40a4-96d2-dc049c1dfd22/sy5diXhx67.json")
