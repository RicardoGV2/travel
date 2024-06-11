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

# Function to add an item to a checklist
def add_item_to_checklist(user, item):
    if item not in [i["name"] for i in checklists["users"][user]]:
        checklists["users"][user].append({"name": item, "checked": False})
        save_data(checklists_file, checklists)
        st.experimental_rerun()

# Function to add a shared item to all checklists
def add_shared_item(item):
    for user in checklists["users"]:
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

# Function to delete an item from a checklist
def delete_item_from_checklist(user, item_name):
    checklists["users"][user] = [item for item in checklists["users"][user] if item["name"] != item_name]
    save_data(checklists_file, checklists)
    st.experimental_rerun()

# Function to delete a shared item from all checklists
def delete_shared_item(item_name):
    for user in checklists["users"]:
        checklists["users"][user] = [item for item in checklists["users"][user] if item["name"] != item_name]
    save_data(checklists_file, checklists)
    st.experimental_rerun()

# Page layout
st.title("Checklist")

# Section to add items to a checklist
st.header("Add an Item to a Checklist")
user = st.selectbox("Select User:", ["Shared"] + list(users.keys()), key="user")
item = st.text_input("Add an item:", key="item")
if st.button("Add Item"):
    if item:
        if user == "Shared":
            add_shared_item(item)
            st.success(f"Added '{item}' to shared checklist.")
        else:
            add_item_to_checklist(user, item)
            st.success(f"Added '{item}' to {user}'s checklist.")
    else:
        st.error("Please enter an item.")

# User selector for viewing checklists
selected_user = st.selectbox("View Checklist for User:", ["Shared"] + list(users.keys()), key="selected_user")

# Display checklists with checkboxes and delete buttons, including shared items
st.subheader(f"{selected_user}'s Checklist (including Shared)")
shared_items = checklists["users"]["Shared"]
user_items = checklists["users"][selected_user]

# Combine shared and user-specific items without duplicating shared items
all_items = {item["name"]: item for item in shared_items + user_items}.values()

# CSS to style the delete button as an icon and align it to the right
st.markdown("""
    <style>
    .delete-button {
        background: none;
        border: none;
        color: red;
        cursor: pointer;
        font-size: 1.2em;
        margin-left: 10px;
        float: right;
    }
    .item-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #ddd;
        padding: 5px 0;
    }
    </style>
    """, unsafe_allow_html=True)

for item in all_items:
    item_checked = item["checked"]
    item_name = item["name"]
    item_key = f"{selected_user}_{item_name}"
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        checked = st.checkbox(item_name, value=item_checked, key=item_key, on_change=update_item_state, args=(selected_user, item_name, not item_checked))
    with col2:
        delete_button_html = f"""
        <button class="delete-button" onclick="window.location.href = window.location.href + '&delete={selected_user}_{item_name}';">❌</button>
        """
        st.markdown(f'<div class="item-container">{delete_button_html}</div>', unsafe_allow_html=True)

if st.experimental_get_query_params().get('delete'):
    param = st.experimental_get_query_params().get('delete')[0]
    selected_user, item_name = param.split('_', 1)
    if item_name in [item["name"] for item in checklists["users"]["Shared"]]:
        delete_shared_item(item_name)
    else:
        delete_item_from_checklist(selected_user, item_name)

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
