from navigation import make_sidebar
import streamlit as st
import json
import os
from collections import OrderedDict
from streamlit_autorefresh import st_autorefresh
from time import sleep
import streamlit.components.v1 as components
from datetime import datetime

make_sidebar()

components.iframe("https://lottie.host/embed/89efecc0-ccec-423e-b237-16c5de971907/m5iscTBfB6.json")

# Paths to the data and votes files
data_file = "data.json"
votes_file = "votes.json"

# Function to convert dates to "YYYY-MM-DD" format for internal processing
def convert_dates_to_2024(data):
    converted_data = {}
    for date, value in data.items():
        try:
            converted_date = datetime.strptime(date, "%d/%m").replace(year=2024).strftime("%Y-%m-%d")
            converted_data[converted_date] = value
        except ValueError:
            st.error(f"Date conversion error for {date}: {e}")
    return converted_data

# Function to convert date from "YYYY-MM-DD" to "dd/MM" format
def convert_date_to_ddmm(date):
    return datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m")

# Function to load data
def load_data():
    if os.path.exists(data_file):
        with open(data_file, 'r') as file:
            data = json.load(file)
            return convert_dates_to_2024(data)
    else:
        return {}

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
        data = load_data()
        return {date: {time: {option: 0 for option in data[date][time]} for time in data[date]} for date in data}

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

# Ensure the selected date exists in session state
def ensure_selected_date_in_session_state(selected_date):
    if selected_date not in st.session_state['user_votes']:
        st.session_state['user_votes'][selected_date] = {time: None for time in data[selected_date]}

# Function to update votes
def update_votes(selected_date, selected_time, selected_option):
    ensure_selected_date_in_session_state(selected_date)
    current_vote = st.session_state['user_votes'][selected_date].get(selected_time)
    
    # Reduce count of previous vote
    if current_vote and current_vote in votes[selected_date][selected_time]:
        votes[selected_date][selected_time][current_vote] -= 1

    # Increase count of new vote
    if selected_option not in votes[selected_date][selected_time]:
        votes[selected_date][selected_time][selected_option] = 0
    votes[selected_date][selected_time][selected_option] += 1

    # Update session state
    st.session_state['user_votes'][selected_date][selected_time] = selected_option

    # Save updated votes
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

# Always declare the checkbox but only use it for Ricardo
show_votes_json = st.sidebar.checkbox("Show Votes JSON", value=False)
show_votes_json_visible = st.session_state.get('username') == "Ricardo"

# Checkbox to show/hide debugging labels and JSON
show_debug = st.sidebar.checkbox("Show Debug Info", value=False)

# Autorefresh every 'refresh_interval' seconds if enabled
if auto_refresh and refresh_interval:
    st_autorefresh(interval=refresh_interval * 1000, key="datarefresh")

# Function to mark dates with data
def get_event_dates(data):
    event_dates = []
    for date in data:
        try:
            event_dates.append(datetime.strptime(date, "%Y-%m-%d").date())
        except ValueError:
            pass  # Silently ignore date parsing errors
    return event_dates

# Calendar for date selection
event_dates = get_event_dates(data)

# Section to add new activities
with st.expander("Propose a New Activity"):
    new_date = st.date_input("Select Date for New Activity:", value=event_dates[0] if event_dates else datetime.today().date(), key="new_date")
    new_date_ddmm = convert_date_to_ddmm(new_date.strftime("%Y-%m-%d"))
    new_time = st.text_input("Enter Time for New Activity (e.g., 14:00):", key="new_time")
    new_activity = st.text_input("Enter New Activity Description:", key="new_activity")
    new_cost = st.number_input("Enter Cost for New Activity (in AUD):", key="new_cost", min_value=0)

    if st.button("Add New Activity"):
        if new_date_ddmm and new_time and new_activity:
            try:
                activity_entry = f"{new_activity} {new_cost} AUD"
                if new_date_ddmm not in data:
                    data[new_date_ddmm] = {}
                if new_time in data[new_date_ddmm]:
                    data[new_date_ddmm][new_time].append(activity_entry)
                else:
                    data[new_date_ddmm][new_time] = [activity_entry]
                # Ensure the new activity is also added to the votes structure
                if new_date_ddmm not in votes:
                    votes[new_date_ddmm] = {}
                if new_time not in votes[new_date_ddmm]:
                    votes[new_date_ddmm][new_time] = {}
                votes[new_date_ddmm][new_time][activity_entry] = 0
                # Sort the times for the date
                data[new_date_ddmm] = dict(OrderedDict(sorted(data[new_date_ddmm].items())))
                votes[new_date_ddmm] = dict(OrderedDict(sorted(votes[new_date_ddmm].items())))
                save_data(data)
                save_votes(votes)
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error adding new activity: {e}")
        else:
            st.error("Please fill in all fields to add a new activity.")

# Section to delete activities
with st.expander("Delete an Activity"):
    del_date = st.date_input("Select Date for Deleting Activity:", value=event_dates[0] if event_dates else datetime.today().date(), key="del_date")
    del_date_ddmm = convert_date_to_ddmm(del_date.strftime("%Y-%m-%d"))
    if del_date_ddmm:
        del_time = st.selectbox("Select Time for Deleting Activity:", options=list(data[del_date_ddmm].keys()), key="del_time")
        if del_time:
            del_activity = st.selectbox("Select Activity to Delete:", options=data[del_date_ddmm][del_time], key="del_activity")
            if st.button("Delete Selected Activity"):
                delete_activity(del_date_ddmm, del_time, del_activity)

st.title("Itinerary Planner")

# Date selection for voting
selected_date = st.date_input("Select Date for Voting:", value=event_dates[0] if event_dates else datetime.today().date(), key="vote_date")
selected_date_ddmm = convert_date_to_ddmm(selected_date.strftime("%Y-%m-%d"))

# Ensure the selected date exists in session state
ensure_selected_date_in_session_state(selected_date_ddmm)

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

# Debug: Display selected date
if show_debug:
    st.write(f"### Debug: Selected Date {selected_date}")

if selected_date_ddmm in data:
    for time in sorted(data[selected_date_ddmm]):
        st.markdown(f'<div class="date-section">{time}</div>', unsafe_allow_html=True)
        options = data[selected_date_ddmm][time]
        if selected_date_ddmm in votes and time in votes[selected_date_ddmm]:
            vote_counts = {option: votes[selected_date_ddmm][time].get(option, 0) for option in options}
        else:
            vote_counts = {option: 0 for option in options}
        vote_display = [f"{option} - {vote_counts[option]} ❤️" for option in options]
        
        # Check if the user has already voted
        current_vote = st.session_state['user_votes'][selected_date_ddmm].get(time)
        if current_vote:
            st.info(f"You have already voted for {current_vote}. You can change your vote below.")
        
        selected_option_display = st.radio("", vote_display, key=f"display_{selected_date_ddmm}_{time}")
        selected_option = selected_option_display.split(' - ')[0]
        if st.button(f"Vote for {selected_option}", key=f"button_{selected_date_ddmm}_{time}"):
            if current_vote != selected_option:
                update_votes(selected_date_ddmm, time, selected_option)
            else:
                st.warning("You have already voted for this option.")
else:
    st.write("No data available for the selected date.")

# Display the current votes and debugging JSON
if show_votes_json_visible and show_votes_json or show_debug:
    st.write("## Current Votes")
    st.json(votes)

if show_debug:
    st.write("### Debug: Loaded Data")
    st.json(data)
