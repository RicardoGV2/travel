from navigation import make_sidebar
import streamlit as st
import json
import os
from collections import OrderedDict
from streamlit_autorefresh import st_autorefresh
from time import sleep  # Import sleep function
import streamlit.components.v1 as components


make_sidebar()

components.iframe("https://lottie.host/embed/89efecc0-ccec-423e-b237-16c5de971907/m5iscTBfB6.json")


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
    current_vote = st.session_state['user_votes'][selected_date].get(selected_time)
    if current_vote:
        votes[selected_date][selected_time][current_vote] -= 1
    votes[selected_date][selected_time][selected_option] += 1
    st.session_state['user_votes'][selected_date][selected_time] = selected_option
    save_votes(votes)
    sleep(2)  # Add a delay of 2 seconds after voting
    st.experimental_rerun()

# Function to delete an activity
def delete_activity(selected_date, selected_time, selected_activity):
    if selected_date in data and selected_time in data[selected_date]:
        if selected_activity in data[selected_date][selected_time]:
            data[selected_date][selected_time].remove(selected_activity)
            if not data[selected_date][selected_time]:
                del data[selected_date][selected_time]
            if selected_time in votes[selected_date]:
                if selected_activity in votes[selected_date][selected_time]:
                    del votes[selected_date][selected_time][selected_activity]
                if not votes[selected_date][selected_time]:
                    del votes[selected_date][selected_time]
            save_data(data)
            save_votes(votes)
            st.experimental_rerun()
        else:
            st.error("Activity not found.")
    else:
        st.error("Date or time not found.")

# Add a setting to pause or continue autorefresh and to show/hide votes JSON and the add activity section
st.sidebar.title("Settings")
auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=True)
refresh_interval = st.sidebar.number_input("Refresh Interval (seconds)", min_value=1, max_value=60, value=7) if auto_refresh else None
show_add_activity = st.sidebar.checkbox("Show Add Activity Section", value=True)
show_delete_activity = st.sidebar.checkbox("Show Delete Activity Section", value=True)

# Always declare the checkbox but only use it for Ricardo
show_votes_json = st.sidebar.checkbox("Show Votes JSON", value=False)
show_votes_json_visible = st.session_state.get('username') == "Ricardo"

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
            try:
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
            except Exception as e:
                st.error(f"Error adding new activity: {e}")
        else:
            st.error("Please fill in all fields to add a new activity.")

# Section to delete activities
if show_delete_activity:
    st.title("Delete an Activity")
    del_date = st.selectbox("Select Date for Deleting Activity:", options=list(data.keys()), key="del_date")
    if del_date:
        del_time = st.selectbox("Select Time for Deleting Activity:", options=list(data[del_date].keys()), key="del_time")
        if del_time:
            del_activity = st.selectbox("Select Activity to Delete:", options=data[del_date][del_time], key="del_activity")
            if st.button("Delete Selected Activity"):
                delete_activity(del_date, del_time, del_activity)

st.title("Itinerary Planner")

# Date selection for voting
selected_date = st.selectbox("Select Date for Voting:", options=list(data.keys()), format_func=lambda x: x, disabled=False, label_visibility='collapsed')

# Voting section
st.write("## Vote for Preferences")

# Style for making dates more visible
st.markdown("""
<style>
.date-section {
    font-size: 24px;
    font-weight: bold;
    color: #2E86C1;
    margin-top: 20px;
    border-left: 4px solid #2E86C1;
    padding-left: 10px;
}
.time-section {
    font-size: 18px;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

for time in sorted(data[selected_date]):
    st.markdown(f'<div class="date-section">{time}</div>', unsafe_allow_html=True)
    options = data[selected_date][time]
    if selected_date in votes and time in votes[selected_date]:
        vote_counts = {option: votes[selected_date][time].get(option, 0) for option in options}
    else:
        vote_counts = {option: 0 for option in options}
    vote_display = [f"{option} - {vote_counts[option]} ❤️" for option in options]
    
    # Check if the user has already voted
    current_vote = st.session_state['user_votes'][selected_date].get(time)
    if current_vote:
        st.info(f"You have already voted for {current_vote}. You can change your vote below.")
    
    selected_option_display = st.radio("", vote_display, key=f"display_{selected_date}_{time}")
    selected_option = selected_option_display.split(' - ')[0]
    if st.button(f"Vote for {selected_option}", key=f"button_{selected_date}_{time}"):
        if current_vote != selected_option:
            update_votes(selected_date, time, selected_option)
        else:
            st.warning("You have already voted for this option.")

# Display the current votes
if show_votes_json_visible and show_votes_json:
    st.write("## Current Votes")
    st.json(votes)