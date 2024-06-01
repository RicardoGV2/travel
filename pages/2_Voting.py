import streamlit as st
import json
import os
from collections import OrderedDict

# Paths to the data and votes files
data_file = "data.json"
votes_file = "votes.json"

# Redirect to login if no user is selected
if 'user' not in st.session_state:
    st.warning("Please log in first.")
    st.experimental_set_query_params(page="1_Login")
    st.experimental_rerun()

# Function to load data
def load_data():
    if os.path.exists(data_file):
        with open(data_file, 'r') as file:
            return json.load(file)
    else:
        return initial_data

def save_data(data):
    with open(data_file, 'w') as file:
        json.dump(data, file, indent=4)

def load_votes():
    if os.path.exists(votes_file):
        with open(votes_file, 'r') as file:
            return json.load(file)
    else:
        return {date: {time: {option: 0 for option in initial_data[date][time]} for time in initial_data[date]} for date in initial_data}

def save_votes(votes):
    with open(votes_file, 'w') as file:
        json.dump(votes, file, indent=4)

# Initial data for multiple days
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
    save_votes(votes)  # Save votes to the file
    st.experimental_rerun()

st.title("Vote for Preferences")

# Date selection for voting
selected_date = st.selectbox("Select Date for Voting:", options=list(data.keys()), format_func=lambda x: x, disabled=False, label_visibility='collapsed')

# Voting section
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
