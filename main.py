import streamlit as st
from time import sleep
import os
import json
from navigation import make_sidebar
from user_management import authenticate_user
import streamlit.components.v1 as components

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

# Login form
username = st.selectbox("Username", options=allowed_users)
password = st.text_input(password_placeholder, type="password", autocomplete="off", key="password_input")

if st.button("Log in", type="primary"):
    if authenticate_user(username, password):
        st.session_state.logged_in = True
        st.session_state.username = username  # Store the username in session state
        st.success("Logged in successfully!")
        sleep(0.5)
        st.switch_page("pages/page1.py")
    else:
        st.error("Incorrect username or password")

# Custom HTML, CSS, and JavaScript for the arrow animation
st.markdown("""
    <style>
    .arrow {
        width: 0; 
        height: 0; 
        border-left: 10px solid transparent;
        border-right: 10px solid transparent;
        border-bottom: 20px solid red;
        position: absolute;
        animation: bounce 1s infinite;
    }
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {
            transform: translateY(0); 
        }
        40% {
            transform: translateY(-10px); 
        }
        60% {
            transform: translateY(-5px); 
        }
    }
    </style>
    <div class="arrow" id="arrow"></div>
    <div id="char-count">Character Count: 0</div>
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const passwordInput = document.querySelector('input[data-testid="stTextInput"]');
        const arrow = document.getElementById('arrow');
        const charCount = document.getElementById('char-count');

        if (passwordInput) {
            passwordInput.addEventListener('input', function() {
                const charWidth = 9;  // Approximate character width, you may need to adjust this
                const rect = passwordInput.getBoundingClientRect();
                const lastCharPos = rect.left + (passwordInput.value.length * charWidth);
                arrow.style.left = `${lastCharPos}px`;  // Adjust to point correctly
                arrow.style.top = `${rect.top - 40}px`;
                charCount.textContent = `Character Count: ${passwordInput.value.length}`;
            });
        }
    });
    </script>
""", unsafe_allow_html=True)

components.iframe("https://lottie.host/embed/b95a4da8-6ec1-40a4-96d2-dc049c1dfd22/sy5diXhx67.json")
