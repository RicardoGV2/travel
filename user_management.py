import json
import os

# Path to the user credentials file
users_file = "users.json"

# Function to load users
def load_users():
    if os.path.exists(users_file):
        with open(users_file, 'r') as file:
            return json.load(file)
    else:
        # Return a default user if the file does not exist
        default_users = {
            "Jorge": {"password": "australia"},
            "Raquel": {"password": "australia"},
            "Karime": {"password": "australia"},
            "Katia": {"password": "australia"},
            "Janet": {"password": "australia"},
            "Ricardo": {"password": "australia"}
        }
        save_users(default_users)
        return default_users

# Function to save users
def save_users(users):
    with open(users_file, 'w') as file:
        json.dump(users, file, indent=4)

# Function to authenticate user
def authenticate_user(username, password):
    users = load_users()
    if username in users and users[username]["password"] == password:
        return True
    return False