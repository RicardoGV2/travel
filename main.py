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

# Function to set device type in session state
def set_device_type(device_type):
    st.session_state.device_type = device_type

# JavaScript to detect device type and send it to Streamlit
device_detection_script = """
<script>
    function detectDevice() {
        const userAgent = navigator.userAgent || navigator.vendor || window.opera;
        let deviceType = "desktop";

        if (/windows phone/i.test(userAgent)) {
            deviceType = "mobile";
        } else if (/android/i.test(userAgent)) {
            deviceType = "mobile";
        } else if (/iPad|iPhone|iPod/.test(userAgent) && !window.MSStream) {
            deviceType = "mobile";
        }

        const message = { type: "DEVICE_TYPE", device_type: deviceType };
        window.parent.postMessage(message, "*");
    }

    window.addEventListener("load", detectDevice);
</script>
"""

st.components.v1.html(device_detection_script, height=0)

# JavaScript to handle messages from the iframe
st.markdown("""
    <script>
        window.addEventListener("message", (event) => {
            const data = event.data;
            if (data.type === "DEVICE_TYPE") {
                const deviceType = data.device_type;
                window.streamlitEvent.send({
                    type: "STREAMLIT_SET_SESSION_STATE",
                    data: { device_type: deviceType }
                });
            }
        });
    </script>
""", unsafe_allow_html=True)

# Initialize device type in session state
if 'device_type' not in st.session_state:
    st.session_state.device_type = 'desktop'

# Adjust arrow position based on device type
if st.session_state.device_type == "mobile":
    st.session_state.arrow_position = st.session_state.char_count * 8.7
else:
    st.session_state.arrow_position = st.session_state.char_count * 5.3

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

with st.sidebar:
    st.session_state.disable_arrow_animation = st.checkbox("Disable Arrow Animation")

if not st.session_state.get('disable_arrow_animation', False):
    components.iframe("https://lottie.host/embed/b95a4da8-6ec1-40a4-96d2-dc049c1dfd22/sy5diXhx67.json")

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
