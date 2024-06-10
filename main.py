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
password = st_keyup(password_placeholder, key="password_input", type="password")

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
        top: -126px;  /* Adjust this value based on the position of your input field */
    }}
    #spacer {{
        visibility: hidden;
        position: absolute;
        top: 0;
        left: 0;
        white-space: pre;
    }}
    </style>
    <div class="arrow" id="arrow"></div>
    <span id="spacer"></span>
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        const passwordInput = document.querySelector('input[type="password"]');
        const arrow = document.getElementById('arrow');
        const spacer = document.getElementById('spacer');

        if (passwordInput) {{
            passwordInput.addEventListener('input', function() {{
                spacer.innerHTML = passwordInput.value.replace(/./g, '•');  // Use the bullet character to match password input
                const rect = passwordInput.getBoundingClientRect();
                const spacerRect = spacer.getBoundingClientRect();
                const lastCharPos = rect.left + spacerRect.width;
                arrow.style.left = `${{lastCharPos}}px`;  // Adjust to point correctly
                arrow.style.top = `${{rect.top - 40}}px`;
            }});
        }}
    }});
    </script>
""", unsafe_allow_html=True)

components.iframe("https://lottie.host/embed/b95a4da8-6ec1-40a4-96d2-dc049c1dfd22/sy5diXhx67.json")
