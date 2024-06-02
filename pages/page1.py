from navigation import make_sidebar
import streamlit as st
import json
import os
from collections import OrderedDict
from streamlit_autorefresh import st_autorefresh
from time import sleep  # Import sleep function

make_sidebar()

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

# Function to save votes
def save_votes(votes):
    with open(votes_file, 'w') as file:
        json.dump(votes, file, indent=4)

# Load data and votes
data = load_data()
votes = load_votes()

# Initialize session state for tracking votes
if 'user_votes' not in st.session_state:
    st.session_state['user_votes'] = {date: {time: None for time in data[date]} for date in data}

# Function to update votes
def update_votes(selected_date, selected_time, selected_option):
    current_vote = st.session_state['user_votes'][selected_date][selected_time]
    if current_vote:
        votes[selected_date][selected_time][current_vote] -= 1
    votes[selected_date][selected_time][selected_option] += 1
    st.session_state['user_votes'][selected_date][selected_time] = selected_option
    save_votes(votes)
    sleep(2)  # Add a delay of 2 seconds after voting
    st.experimental_rerun()

# Add a setting to pause or continue autorefresh and to show/hide votes JSON and the add activity section
st.sidebar.title("Settings")
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
            save_data(data)
            save_votes(votes)
            st.experimental_rerun()
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
        current_vote = st.session_state['user_votes'][selected_date][time]
        if current_vote:
            vote_counts[current_vote] -= 1
        vote_counts[selected_option] += 1
        st.session_state['user_votes'][selected_date][time] = selected_option
        votes[selected_date][time][selected_option] += 1
        save_votes(votes)
        st.experimental_rerun()

# Display the current votes
if show_votes_json:
    st.write("## Current Votes")
    st.json(votes)
