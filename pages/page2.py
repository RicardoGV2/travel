from navigation import make_sidebar
import streamlit as st
from pyvis.network import Network
import networkx as nx
import streamlit.components.v1 as components
import json
import os
from collections import OrderedDict
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta
import streamlit_calendar as stcal

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

# Convert initial_data keys to "YYYY-MM-DD" format
initial_data = {datetime.strptime(date, "%d/%m").strftime("2024-%m-%d"): value for date, value in initial_data.items()}

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
    net = Network(height="1000px", width="100%", directed=True)
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
refresh_interval = st.sidebar.number_input("Refresh Interval (seconds)", min_value=1, max_value=60, value=7) if auto_refresh else None

# Autorefresh every 'refresh_interval' seconds if enabled
if auto_refresh and refresh_interval:
    st_autorefresh(interval=refresh_interval * 1000, key="datarefresh")

# Function to mark dates with data
def get_event_dates(data):
    event_dates = []
    for date in data:
        try:
            event_dates.append(datetime.strptime(date, "%Y-%m-%d").date())
        except ValueError as e:
            st.write(f"Date parsing error for {date}: {e}")
    return event_dates

# Calendar for date selection
st.title("Timeline Viewer")
event_dates = get_event_dates(data)
selected_date = st.date_input("Select Date to View Timeline:", value=event_dates[0] if event_dates else datetime.today().date())

if selected_date:
    selected_date_str = selected_date.strftime("%Y-%m-%d")
    st.write(f"Selected Date: {selected_date_str}")

    if selected_date_str in data:
        # Get the top voted options for the selected date
        top_voted = get_top_voted_options(votes, selected_date_str)

        # Create and display the network with top voted options
        net = create_network_with_top_votes(data, top_voted)
        path = 'full_network.html'
        net.save_graph(path)

        with open(path, 'r', encoding='utf-8') as file:
            html_content = file.read()
            components.html(html_content, height=1000)
    else:
        st.write("No data available for the selected date.")
