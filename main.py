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

# Initialize character count and password value in session state
if 'char_count' not in st.session_state:
    st.session_state.char_count = 0
if 'real_password' not in st.session_state:
    st.session_state.real_password = ''

# Function to update character count and password value
def update_char_count():
    st.session_state.char_count = len(st.session_state.password_input)
    st.session_state.real_password = st.session_state.password_input

# Login form
username = st.selectbox("Username", options=allowed_users)
password_input = st.text_input(password_placeholder, type="password", autocomplete="off", key="password_input")

# Custom HTML, CSS, and JavaScript for the arrow animation and masking password input
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
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const passwordInput = document.querySelector('input[data-baseweb="input"]');
        const arrow = document.getElementById('arrow');

        if (passwordInput) {
            passwordInput.addEventListener('input', function() {
                const realPasswordInput = document.getElementById('real_password_input');
                const charWidth = 9;  // Approximate character width, you may need to adjust this
                const rect = passwordInput.getBoundingClientRect();
                const lastCharPos = rect.left + (realPasswordInput.value.length * charWidth);

                // Update the real password input
                realPasswordInput.value = passwordInput.value;

                // Mask the password input with asterisks
                passwordInput.value = '*'.repeat(realPasswordInput.value.length);

                // Adjust the arrow position
                arrow.style.left = `${lastCharPos}px`;  // Adjust to point correctly
                arrow.style.top = `${rect.top - 40}px`;
            });
        }
    });
    </script>
""", unsafe_allow_html=True)

# Hidden input field to store the real password value
components.html(f"""
    <input type="hidden" id="real_password_input" value="{st.session_state.real_password}">
""")

if st.button("Log in", type="primary"):
    if authenticate_user(username, st.session_state.real_password):
        st.session_state.logged_in = True
        st.session_state.username = username  # Store the username in session state
        st.success("Logged in successfully!")
        sleep(0.5)
        st.switch_page("pages/page1.py")
    else:
        st.error("Incorrect username or password")

st.write(f"Character Count: {st.session_state.char_count}")

components.iframe("https://lottie.host/embed/b95a4da8-6ec1-40a4-96d2-dc049c1dfd22/sy5diXhx67.json")
