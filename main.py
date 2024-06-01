import streamlit as st
from pyvis.network import Network
import networkx as nx
import streamlit.components.v1 as components
import json
import os
from collections import OrderedDict
from streamlit_autorefresh import st_autorefresh

# Paths to the data and votes files
data_file = "data.json"
votes_file = "votes.json"
users_file = "users.json"

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

initial_users = ["Jorge", "Raquel", "Karime", "Katia", "Janet", "Ricardo"]

# Function to load data
def load_data(file_path, default_data):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        return default_data

# Function to save data
def save_data(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Load data, votes, and users
data = load_data(data_file, initial_data)
votes = load_data(votes_file, {date: {time: {option: 0 for option in initial_data[date][time]} for time in initial_data[date]} for date in initial_data})
users = load_data(users_file, initial_users)

# Initialize session state for tracking votes and user
if 'user_votes' not in st.session_state:
    st.session_state['user_votes'] = {user: {date: {time: None for time in data[date]} for date in data} for user in users}

if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None

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

# Function to update votes
def update_votes(user, selected_date, selected_time, selected_option):
    current_vote = st.session_state['user_votes'][user][selected_date][selected_time]
    if current_vote:
        votes[selected_date][selected_time][current_vote] -= 1
    votes[selected_date][selected_time][selected_option] += 1
    st.session_state['user_votes'][user][selected_date][selected_time] = selected_option
    save_data(votes_file, votes)  # Save votes to the file

# Page for user selection
if st.session_state['current_user'] is None:
    st.title("Select Your User")
    user = st.selectbox("Select Your Name", options=users, key="user_select")
    new_user = st.text_input("Add a New User", key="new_user_input")
    if st.button("Add User"):
        if new_user and new_user not in users:
            users.append(new_user)
            st.session_state['user_votes'][new_user] = {date: {time: None for time in data[date]} for date in data}
            save_data(users_file, users)
            st.experimental_rerun()
        else:
            st.error("Please enter a valid new user name.")
    if st.button("Continue"):
        st.session_state['current_user'] = user
        st.experimental_rerun()
else:
    st.sidebar.title("Settings")
    if st.sidebar.button("Change User"):
        st.session_state['current_user'] = None
        st.experimental_rerun()

    # Add a setting to pause or continue autorefresh and to show/hide votes JSON and the add activity section
    auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=True)
    refresh_interval = st.sidebar.number_input("Refresh Interval (seconds)", min_value=1, max_value=60, value=7) if auto_refresh else None
    show_votes_json = st.sidebar.checkbox("Show Votes JSON", value=False)
    show_add_activity = st.sidebar.checkbox("Show Add Activity Section", value=True)

    # Autorefresh every 'refresh_interval' seconds if enabled
    if auto_refresh and refresh_interval:
        st_autorefresh(interval=refresh_interval * 1000, key="datarefresh")

    # Section to add new activities
    if show_add_activity:
        st.title("Propose a New Activity")
        new_date = st.selectbox("Select Date for New Activity:", options=list(data.keys()), key="new_date")
        new_time = st.text_input("Enter Time for New Activity (e.g., 14:00):", key="new_time")
        new_activity = st.text_input("Enter New Activity Description:", key="new_activity")
        new_cost = st.number_input("Enter Cost for New Activity (in AUD):", key="new_cost", min_value=0)

        if st.button("Add New Activity"):
            if new_date and new_time and new_activity:
                activity_entry = f"{new_activity} {new_cost} AUD"
                if new_date not in data:
                    data[new_date] = {}
                if new_time in data[new_date]:
                    data[new_date][new_time].append(activity_entry)
                else:
                    data[new_date][new_time] = [activity_entry]
                # Ensure the new activity is also added to the votes structure
                if new_date not in votes:
                    votes[new_date] = {}
                if new_time not in votes[new_date]:
                    votes[new_date][new_time] = {}
                votes[new_date][new_time][activity_entry] = 0
                # Sort the times for the date
                data[new_date] = dict(OrderedDict(sorted(data[new_date].items())))
                votes[new_date] = dict(OrderedDict(sorted(votes[new_date].items())))
                save_data(data_file, data)  # Save the updated data structure
                save_data(votes_file, votes)  # Save the updated votes structure
                st.experimental_rerun()  # Rerun to update the voting section
            else:
                st.error("Please fill in all fields to add a new activity.")

    st.title("Itinerary Planner")

    # Date selection for voting
    selected_date = st.selectbox("Select Date for Voting:", options=list(data.keys()), format_func=lambda x: x, disabled=False, label_visibility='collapsed')

    # Voting section
    st.write("## Vote for Preferences")
    for time in sorted(data[selected_date]):
        st.write(f"**{time}**")
        options = data[selected_date][time]
        if selected_date in votes and time in votes[selected_date]:
            vote_counts = {option: votes[selected_date][time].get(option, 0) for option in options}
        else:
            vote_counts = {option: 0 for option in options}
        vote_display = [f"{option} - {vote_counts[option]} ❤️" for option in options]
        selected_option_display = st.radio("", vote_display, key=f"display_{selected_date}_{time}")
        selected_option = selected_option_display.split(' - ')[0]
        if st.button(f"Vote for {selected_option}", key=f"button_{selected_date}_{time}"):
            current_vote = st
