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

components.iframe("https://lottie.host/embed/b95a4da8-6ec1-40a4-96d2-dc049c1dfd22/sy5diXhx67.json")

st.title("Welcome to Australia")

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

# Initialize debounce state in session state
if 'debounce' not in st.session_state:
    st.session_state.debounce = state_data.get('debounce', False)

# Sidebar settings
with st.sidebar:
    disable_arrow_animation = st.checkbox("Disable Arrow Animation", value=st.session_state.disable_arrow_animation)
    debounce = st.checkbox("Add 0.1s debounce?", value=st.session_state.debounce)

# Save state when checkboxes change
if disable_arrow_animation != st.session_state.disable_arrow_animation:
    st.session_state.disable_arrow_animation = disable_arrow_animation
    state_data['disable_arrow_animation'] = disable_arrow_animation
    save_state(state_file, state_data)

if debounce != st.session_state.debounce:
    st.session_state.debounce = debounce
    state_data['debounce'] = debounce
    save_state(state_file, state_data)

# Login form
username = st.selectbox("Username", options=allowed_users)
password = st_keyup(password_placeholder, key="password_input", type="password", debounce=100 if st.session_state.debounce else None)

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
            top: -80px;  /* Adjust this value based on the position of your input field */
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

import streamlit as st
from pyvis.network import Network
import networkx as nx
import streamlit.components.v1 as components
import json
import os
from collections import OrderedDict
from streamlit_autorefresh import st_autorefresh

make_sidebar()

components.iframe("https://lottie.host/embed/d184c6c6-3f70-4986-858c-358a985a98cc/mgG3h5XqEX.json")

# Paths to the data and votes files
data_file = "data.json"
votes_file = "votes.json"

# Example initial data for multiple days
initial_data = {
    "14/06": {
        "06:00": ["Llegada al aeropuerto"],
        "07:00": ["Desayuno en el aeropuerto"],
        "08:00": ["Bus a Sydney"],
        "09:30": ["Bus al tour"],
        "10:00": ["Tour 1 20 AUD", "Tour 2 25 AUD"],
        "12:00": ["Bus a otra actividad"],
        "12:30": ["Actividad 1", "Actividad 2"],
        "18:00": ["Cena"]
    },
    "15/06": {
        "08:00": ["Desayuno en el hotel"],
        "09:00": ["Visita al parque"],
        "12:00": ["Almuerzo en el restaurante"],
        "15:00": ["Visita al museo"],
        "18:00": ["Cena en el centro"]
    },
    # Add more days as needed
}

# Function to load data
def load_data():
    if os.path.exists(data_file):
        with open(data_file, 'r') as file:
            return json.load(file)
    else:
        return initial_data

# Function to save data
def save_data(data):
    with open(data_file, 'w') as file:
        json.dump(data, file, indent=4)

# Function to load votes
def load_votes():
    if os.path.exists(votes_file):
        with open(votes_file, 'r') as file:
            return json.load(file)
    else:
        return {date: {time: {option: 0 for option in initial_data[date][time]} for time in initial_data[date]} for date in initial_data}

# Load data and votes
data = load_data()
votes = load_votes()

# Function to get top voted options
def get_top_voted_options(votes, selected_date=None):
    top_voted = {}
    for date in votes:
        if selected_date and date != selected_date:
            continue
        top_voted[date] = {}
        for time in votes[date]:
            options = votes[date][time]
            top_option = max(options, key=options.get)
            top_voted[date][time] = top_option
    return top_voted

# Function to create network with top voted options
def create_network_with_top_votes(data, top_voted):
    net = Network(height="1000px", width="100%", directed=True, bgcolor='#f0f2f6', font_color='black')
    G = nx.DiGraph()

    previous_node = None

    for date in data:
        if date not in top_voted:
            continue
        for time in data[date]:
            if date in top_voted and time in top_voted[date]:
                top_option = top_voted[date][time]
                time_node = f"{date}_{time}_{top_option}"
                G.add_node(time_node, label=f"{time}\n{top_option}", shape="box")
                if previous_node:
                    G.add_edge(previous_node, time_node)
                previous_node = time_node
    
    net.from_nx(G)
    net.set_options("""
    var options = {
        "layout": {
            "hierarchical": {
                "enabled": true,
                "direction": "UD",
                "sortMethod": "directed"
            }
        },
        "physics": {
            "hierarchicalRepulsion": {
                "centralGravity": 0,
                "springLength": 100,
                "springConstant": 0.01,
                "nodeDistance": 120,
                "damping": 0.09
            },
            "minVelocity": 0.75
        }
    }
    """)
    return net

# Add a setting to pause or continue autorefresh and to show/hide votes JSON
st.sidebar.title("Settings")
auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=True)
refresh_interval = st.sidebar.number_input("Refresh Interval (seconds)", min_value=1, max_value=60, value=7) if auto_refresh
