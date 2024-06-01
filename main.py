import streamlit as st
from pyvis.network import Network
import networkx as nx
import streamlit.components.v1 as components
import json
import os
from streamlit_autorefresh import st_autorefresh

# Path to the votes file
votes_file = "votes.json"

# Example data for multiple days
data = {
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

# Function to load votes
def load_votes():
    if os.path.exists(votes_file):
        with open(votes_file, 'r') as file:
            return json.load(file)
    else:
        return {date: {time: {option: 0 for option in data[date][time]} for time in data[date]} for date in data}

# Function to save votes
def save_votes(votes):
    with open(votes_file, 'w') as file:
        json.dump(votes, file)

# Load votes
votes = load_votes()

# Initialize session state for tracking votes
if 'user_votes' not in st.session_state:
    st.session_state['user_votes'] = {date: {time: None for time in data[date]} for date in data}

def get_top_voted_options(votes):
    top_voted = {}
    for date in votes:
        top_voted[date] = {}
        for time in votes[date]:
            options = votes[date][time]
            top_option = max(options, key=options.get)
            top_voted[date][time] = top_option
    return top_voted

def create_network_with_top_votes(data, top_voted):
    net = Network(height="1000px", width="100%", directed=True)
    G = nx.DiGraph()

    previous_node = None

    for date in data:
        for time in data[date]:
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
                "springConstant": 01,
                "nodeDistance": 120,
                "damping": 0.09
            },
            "minVelocity": 0.75
        }
    }
    """)
    return net

def update_votes(selected_date, selected_time, selected_option):
    current_vote = st.session_state['user_votes'][selected_date][selected_time]
    if current_vote:
        votes[selected_date][selected_time][current_vote] -= 1
    votes[selected_date][selected_time][selected_option] += 1
    st.session_state['user_votes'][selected_date][selected_time] = selected_option
    save_votes(votes)  # Save votes to the file
    st.success(f"Voted for {selected_option} in {selected_time}")

# Add a setting to pause or continue autorefresh and to show/hide votes JSON
st.sidebar.title("Settings")
auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=True)
show_votes_json = st.sidebar.checkbox("Show Votes JSON", value=False)

# Autorefresh every 5 seconds if enabled
if auto_refresh:
    st_autorefresh(interval=5000, key="datarefresh")

st.title("Itinerary Planner")

# Date selection for voting
selected_date = st.selectbox("Select Date for Voting:", options=list(data.keys()), format_func=lambda x: x, disabled=False, label_visibility='collapsed')

# Voting section
st.write("## Vote for Preferences")
for time in data[selected_date]:
    options = data[selected_date][time]
    selected_option = st.radio("", options, key=f"{selected_date}_{time}")
    if st.button(f"Vote for {selected_option}", key=f"button_{selected_date}_{time}"):
        update_votes(selected_date, time, selected_option)

# Get the top voted options
top_voted = get_top_voted_options(votes)

# Create and display the network with top voted options
net = create_network_with_top_votes(data, top_voted)
path = 'full_network.html'
net.save_graph(path)

with open(path, 'r', encoding='utf-8') as file:
    html_content = file.read()
    components.html(html_content, height=1000)

# Display the current votes
if show_votes_json:
    st.write("## Current Votes")
    st.json(votes)

# To run the app, use the command: streamlit run filename.py
