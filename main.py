import streamlit as st
from pyvis.network import Network
import networkx as nx
import streamlit.components.v1 as components
import json
import os
from streamlit_autorefresh import st_autorefresh
from collections import OrderedDict

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
        json.dump(votes, file, indent=4)

# Load votes
votes = load_votes()

# Initialize session state for tracking votes
if 'user_votes' not in st.session_state:
    st.session_state['user_votes'] = {date: {time: None for time in data[date]} for date in data}

# Function to get top voted options
def get_top_voted_options(votes):
    top_voted = {}
    for date in votes:
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
                "springConstant": 0.01,
                "nodeDistance": 120,
                "damping": 0.09
            },
            "minVelocity": 0.75
        }
    }
    """)
    return net

# Function to update votes
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
show_add_activity = st.sidebar.checkbox("Show Add Activity Section", value=True)

# Autorefresh every 5 seconds if enabled
if auto_refresh:
    st_autorefresh(interval=5000, key="datarefresh")

st.title("Itinerary Planner")

# Section to add new activities
if show_add_activity:
    st.write("## Propose a New Activity")
    new_date = st.selectbox("Select Date for New Activity:", options=list(data.keys()), key="new_date")
    new_time = st.text_input("Enter Time for New Activity (e.g., 14:00):", key="new_time")
    new_activity = st.text_input("Enter New Activity Description:", key="new_activity")
    new_cost = st.number_input("Enter Cost for New Activity (in AUD):", key="new_cost", min_value=0)

    if st.button("Add New Activity"):
        if new_date and new_time and new_activity:
            activity_entry = f"{new_activity} {new_cost} AUD"
            if new_time in data[new_date]:
                data[new_date][new_time].append(activity_entry)
            else:
                data[new_date][new_time] = [activity_entry]
            # Ensure the new activity is also added to the votes structure
            if new_time not in votes[new_date]:
                votes[new_date][new_time] = {}
            votes[new_date][new_time][activity_entry] = 0
            # Sort the times for the date
            data[new_date] = dict(OrderedDict(sorted(data[new_date].items())))
            votes[new_date] = dict(OrderedDict(sorted(votes[new_date].items())))
            save_votes(votes)  # Save the updated votes structure
            st.success(f"Added new activity: {activity_entry} on {new_date} at {new_time}")
            st.experimental_rerun()  # Rerun to update the voting section
        else:
            st.error("Please fill in all fields to add a new activity.")

# Date selection for voting
selected_date = st.selectbox("Select Date for Voting:", options=list(data.keys()), format_func=lambda x: x, disabled=False, label_visibility='collapsed')

# Voting section
st.write("## Vote for Preferences")
for time in sorted(data[selected_date]):
    st.write(f"**{time}**")
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
