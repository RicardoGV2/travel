import streamlit as st
import json
import os
from collections import defaultdict
from navigation import make_sidebar
from streamlit_autorefresh import st_autorefresh

make_sidebar()

# Paths to the checklists file
checklists_file = "checklists.json"

# Load data
def load_data(file_path, default_data):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        return default_data

# Save data
def save_data(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Initialize default data
default_checklists = {
    "shared": [],
    "users": {
        "Jorge": [],
        "Raquel": [],
        "Karime": [],
        "Katia": [],
        "Janet": [],
        "Ricardo": []
    }
}

# Load checklists
checklists = load_data(checklists_file, default_checklists)

# Function to add an item to a checklist
def add_item_to_checklist(checklist, item):
    if item not in checklist:
        checklist.append(item)
        save_data(checklists_file, checklists)
        st.experimental_rerun()

# Page layout
st.title("Checklist")

# Section to add items to the shared checklist
st.header("Shared Checklist")
shared_item = st.text_input("Add an item to the shared checklist:", key="shared_item")
if st.button("Add to Shared Checklist"):
    if shared_item:
        add_item_to_checklist(checklists["shared"], shared_item)
        st.success(f"Added '{shared_item}' to the shared checklist.")
    else:
        st.error("Please enter an item.")

# Display shared checklist
st.subheader("Shared Checklist Items")
for item in checklists["shared"]:
    st.write(f"- {item}")

# Section to add items to individual checklists
st.header("Individual Checklists")
user = st.selectbox("Select User:", ["Jorge", "Raquel", "Karime", "Katia", "Janet", "Ricardo"], key="user")
user_item = st.text_input(f"Add an item to {user}'s checklist:", key="user_item")
if st.button(f"Add to {user}'s Checklist"):
    if user_item:
        add_item_to_checklist(checklists["users"][user], user_item)
        st.success(f"Added '{user_item}' to {user}'s checklist.")
    else:
        st.error("Please enter an item.")

# Display individual checklists
st.subheader("Individual Checklist Items")
for user, items in checklists["users"].items():
    st.write(f"**{user}'s Checklist:**")
    for item in items:
        st.write(f"- {item}")

# Option to show/hide checklists JSON
show_checklists_json = st.sidebar.checkbox("Show Checklists JSON", value=False)

# Display the current checklists JSON
if show_checklists_json:
    st.write("## Current Checklists JSON")
    st.json(checklists)

# Auto refresh settings
st.sidebar.title("Settings")
auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=True)
refresh_interval = st.sidebar.number_input("Refresh Interval (seconds)", min_value=1, max_value=60, value=7) if auto_refresh else None

# Auto refresh
if auto_refresh and refresh_interval:
    st_autorefresh(interval=refresh_interval * 1000, key="datarefresh")
