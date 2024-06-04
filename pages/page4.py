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
        "Shared": [],
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
def add_item_to_checklist(user, item):
    if item not in [i["name"] for i in checklists["users"][user]]:
        checklists["users"][user].append({"name": item, "checked": False})
        save_data(checklists_file, checklists)
        st.experimental_rerun()

# Function to update the checked state of an item
def update_item_state(user, item_name, checked):
    for item in checklists["users"][user]:
        if item["name"] == item_name:
            item["checked"] = checked
            break
    save_data(checklists_file, checklists)

# Page layout
st.title("Checklist")

# Section to add items to a checklist
st.header("Add an Item to a Checklist")
user = st.selectbox("Select User:", ["Shared", "Jorge", "Raquel", "Karime", "Katia", "Janet", "Ricardo"], key="user")
item = st.text_input("Add an item:", key="item")
if st.button("Add Item"):
    if item:
        add_item_to_checklist(user, item)
        st.success(f"Added '{item}' to {user}'s checklist.")
    else:
        st.error("Please enter an item.")

# Display checklists with checkboxes
st.subheader("Checklist Items")
for user, items in checklists["users"].items():
    st.write(f"**{user}'s Checklist:**")
    for item in items:
        checked = st.checkbox(item["name"], value=item["checked"], key=f"{user}_{item['name']}")
        update_item_state(user, item["name"], checked)

# Option to show/hide checklists JSON, available only for user "Ricardo"
if st.session_state.get("username") == "Ricardo":
    show_checklists_json = st.sidebar.checkbox("Show Checklists JSON", value=False)
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
