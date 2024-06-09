from navigation import make_sidebar
import streamlit as st
import json
import os
from streamlit_autorefresh import st_autorefresh

make_sidebar()

# Redirigir a la página de inicio de sesión si no está logueado
if not st.session_state.get("logged_in", False):
    st.warning("Please log in to access this page.")
    st.stop()

# Paths to the data and votes files
data_file = "data.json"
votes_file = "votes.json"
debts_file = "debts.json"
debts_history_file = "debts_history.json"

# Load data
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        return {}

# Page layout
st.title("JSON Data Viewer")

# Add a setting to pause or continue autorefresh
st.sidebar.title("Settings")
auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=True)
refresh_interval = st.sidebar.number_input("Refresh Interval (seconds)", min_value=1, max_value=60, value=7) if auto_refresh else None

# Autorefresh every 'refresh_interval' seconds if enabled
if auto_refresh and refresh_interval:
    st_autorefresh(interval=refresh_interval * 1000, key="datarefresh")

# Section to view data.json
st.header("Data JSON")
data = load_data(data_file)
st.json(data)

# Section to view votes.json
st.header("Votes JSON")
votes = load_data(votes_file)
st.json(votes)

# Section to view debts.json
st.header("Debts JSON")
debts = load_data(debts_file)
st.json(debts)

# Section to view debts_history.json
st.header("Debts History JSON")
debts_history = load_data(debts_history_file)
st.json(debts_history)
