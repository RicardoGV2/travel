import streamlit as st
from time import sleep
import os
import json
from navigation import make_sidebar
from user_management import authenticate_user
import streamlit.components.v1 as components
from st_keyup import st_keyup

make_sidebar()

# Paths to jsons
users_file = "users.json"
state_file = "state.json"

# Load users
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        return {}

# Load and save state functions
def load_state(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        return {}

def save_state(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

users_data = load_data(users_file)
allowed_users = list(users_data.keys())
password_placeholder = "Password (use 'australia')"

# Load state
state_data = load_state(state_file)

# Initialize character count in session state
if 'char_count' not in st.session_state:
    st.session_state.char_count = 0

# Initialize arrow animation state in session state
if 'disable_arrow_animation' not in st.session_state:
    st.session_state.disable_arrow_animation = state_data.get('disable_arrow_animation', False)

# Login form
username = st.selectbox("Username", options=allowed_users)
password = st_keyup(password_placeholder, key="password_input", type="password")

# Update character count
st.session_state.char_count = len(password)

if st.button("Log in", type="primary"):
    if authenticate_user(username, password):
        st.session_state.logged_in = True
        st.session_state.username = username  # Store the username in session state
        st.success("Logged in successfully!")
        sleep(0.5)
        st.experimental_rerun()  # Reload the page after login to show new options
    else:
        st.error("Incorrect username or password")

# Disable Arrow Animation
with st.sidebar:
    disable_arrow_animation = st.checkbox("Disable Arrow Animation", value=st.session_state.disable_arrow_animation)

if disable_arrow_animation != st.session_state.disable_arrow_animation:
    st.session_state.disable_arrow_animation = disable_arrow_animation
    state_data['disable_arrow_animation'] = disable_arrow_animation
    save_state(state_file, state_data)

if not st.session_state.get('disable_arrow_animation', False):
    components.iframe("https://lottie.host/embed/b95a4da8-6ec1-40a4-96d2-dc049c1dfd22/sy5diXhx67.json")

# Initialize arrow position in session state
if "arrow_position" not in st.session_state:
    st.session_state.arrow_position = 0

if "arrow_position" in st.session_state:
    st.session_state.arrow_position = st.session_state.char_count * 8.7

if not st.session_state.get('disable_arrow_animation', False):
    # Custom HTML, CSS, and JavaScript for the arrow animation
    st.markdown(f"""
        <style>
        .arrow {{
            width: 0; 
            height: 0; 
            border-left: 7px solid transparent;
            border-right: 7px solid transparent;
            border-bottom: 17px solid red;
            position: absolute;
            animation: bounce 1s infinite;
            left: {st.session_state.arrow_position + 9}px;  /* Adjust to point correctly */
            top: -250px;  /* Adjust this value based on the position of your input field */
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
