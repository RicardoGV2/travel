import streamlit as st
import json
import os
from collections import defaultdict
from navigation import make_sidebar
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

make_sidebar()

components.iframe("https://lottie.host/embed/9baf20e0-746f-479c-ae84-db01663d2618/APnILAMrdN.json")

# Paths to the checklists and users files
checklists_file = "checklists.json"
users_file = "users.json"

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

# Load users
users = load_data(users_file, {})

# Initialize default data
default_checklists = {
    "shared": [],
    "users": {user: [] for user in users}
}
default_checklists["users"]["Shared"] = []

# Load checklists
checklists = load_data(checklists_file, default_checklists)

# Initialize session state for checklists if not present
if "checklists" not in st.session_state:
    st.session_state["checklists"] = checklists

# Function to add an item to a checklist
def add_item_to_checklist(user, item):
    if item not in [i["name"] for i in st.session_state["checklists"]["users"][user]]:
        st.session_state["checklists"]["users"][user].append({"name": item, "checked": False})
        save_data(checklists_file, st.session_state["checklists"])

# Function to update the checked state of an item
def update_item_state(user, item_name, checked):
    for item in st.session_state["checklists"]["users"][user]:
        if item["name"] == item_name:
            item["checked"] = checked
            break
    save_data(checklists_file, st.session_state["checklists"])

# Function to delete an item from a checklist
def delete_item_from_checklist(user, item_name):
    st.session_state["checklists"]["users"][user] = [item for item in st.session_state["checklists"]["users"][user] if item["name"] != item_name]
    save_data(checklists_file, st.session_state["checklists"])

# Function to delete a shared item
def delete_shared_item(item_name):
    for user in st.session_state["checklists"]["users"]:
        st.session_state["checklists"]["users"][user] = [item for item in st.session_state["checklists"]["users"][user] if item["name"] != item_name]
    save_data(checklists_file, st.session_state["checklists"])

# Page layout
st.title("Checklist")

# Section to add items to a checklist
st.header("Add an Item to a Checklist")
user = st.selectbox("Select User:", ["Shared"] + list(users.keys()), key="user")
item = st.text_input("Add an item:", key="item")
if st.button("Add Item"):
    if item:
        add_item_to_checklist(user, item)
        st.success(f"Added '{item}' to {user}'s checklist.")
    else:
        st.error("Please enter an item.")

# User selector for viewing checklists
selected_user = st.selectbox("View Checklist for User:", ["Shared"] + list(users.keys()), key="selected_user")

# Display checklists with checkboxes and delete buttons, including shared items
st.subheader(f"{selected_user}'s Checklist (including Shared)")
shared_items = st.session_state["checklists"]["users"]["Shared"]
user_items = st.session_state["checklists"]["users"][selected_user]

# Combine shared and user-specific items without duplicating shared items
all_items = {item["name"]: item for item in shared_items + user_items}.values()

# Add custom CSS for button alignment
st.markdown("""
    <style>
    .horizontal-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    .horizontal-container .checkbox {
        margin-right: 10px;
    }
    .horizontal-container .delete-button {
        border: none;
        background: none;
        cursor: pointer;
        color: red;
        font-size: 16px;
    }
    .horizontal-container .delete-button:disabled {
        color: gray;
        cursor: not-allowed;
    }
    </style>
    """, unsafe_allow_html=True)

for item in all_items:
    item_name = item["name"]
    checked = item["checked"]
    key_prefix = f"{selected_user}_{item_name}"

    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        st.checkbox(item_name, value=checked, key=f"{key_prefix}_checkbox", on_change=update_item_state, args=(selected_user, item_name, not checked))
    with col2:
        if selected_user == "Shared" or item in shared_items:
            if selected_user == "Shared":
                st.button('❌', key=f'{key_prefix}_button', on_click=delete_shared_item, args=(item_name,))
            else:
                st.button('❌', key=f'{key_prefix}_button', disabled=True)
        else:
            st.button('❌', key=f'{key_prefix}_button', on_click=delete_item_from_checklist, args=(selected_user, item_name))

# Option to show/hide checklists JSON, available only for user "Ricardo"
if st.session_state.get("username") == "Ricardo":
    show_checklists_json = st.sidebar.checkbox("Show Checklists JSON", value=False)
    if show_checklists_json:
        st.write("## Current Checklists JSON")
        st.json(st.session_state["checklists"])

# Auto refresh settings
st.sidebar.title("Settings")
auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=True)
refresh_interval = st.sidebar.number_input("Refresh Interval (seconds)", min_value=1, max_value=60, value=7) if auto_refresh else None

# Auto refresh
if auto_refresh and refresh_interval:
    st_autorefresh(interval=refresh_interval * 1000, key="datarefresh")
