import streamlit as st
import json
import os

users_file = "users.json"

# Load existing users
def load_users():
    if os.path.exists(users_file):
        with open(users_file, 'r') as file:
            return json.load(file)
    else:
        return ["Jorge", "Raquel", "Karime", "Katia", "Janet", "Ricardo"]

# Save users
def save_users(users):
    with open(users_file, 'w') as file:
        json.dump(users, file, indent=4)

# Load users
users = load_users()

st.title("User Login")

# User selection or new user addition
selected_user = st.selectbox("Select User", users)
new_user = st.text_input("Add New User")

if st.button("Add User"):
    if new_user and new_user not in users:
        users.append(new_user)
        save_users(users)
        st.success(f"User {new_user} added!")
    elif new_user in users:
        st.warning("User already exists.")
    else:
        st.error("Please enter a valid name.")

# Button to proceed
if st.button("Proceed"):
    st.session_state['user'] = selected_user
    st.experimental_set_query_params(page="voting")

# Redirect to voting.py if user is selected
if 'user' in st.session_state:
    page = st.experimental_get_query_params().get("page", ["voting"])[0]
    if page == "voting":
        st.experimental_rerun()
    elif page == "timeline":
        st.experimental_rerun()

# Debug information
st.write(st.experimental_get_query_params())
