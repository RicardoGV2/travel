from navigation import make_sidebar
import streamlit as st
import json
import os
from collections import defaultdict
from streamlit_autorefresh import st_autorefresh

make_sidebar()

# Redirigir a la página de inicio de sesión si no está logueado
if not st.session_state.get("logged_in", False) or st.session_state.get("username") != "Ricardo":
    st.warning("Please log in as Ricardo to access esta page.")
    st.stop()

# Paths to the data and votes files
data_file = "data.json"
votes_file = "votes.json"
debts_file = "debts.json"
debts_history_file = "debts_history.json"
checklists_file = "checklists.json"
users_file = "users.json"

# Load data
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        return {}

# Save data
def save_data(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Function to update votes.json based on data.json
def update_votes_based_on_data(data, votes):
    new_votes = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for date, times in data.items():
        for time, activities in times.items():
            for activity in activities:
                new_votes[date][time][activity] = votes.get(date, {}).get(time, {}).get(activity, 0)
    return new_votes

# Page layout
st.title("JSON Data Editor")

# Add a setting to pause or continue autorefresh
st.sidebar.title("Settings")
auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=True)
refresh_interval = st.sidebar.number_input("Refresh Interval (seconds)", min_value=1, max_value=60, value=7) if auto_refresh else None
view_mode = st.sidebar.radio("View Mode", ("Visual", "JSON"))

# Autorefresh every 'refresh_interval' seconds if enabled
if auto_refresh and refresh_interval:
    st_autorefresh(interval=refresh_interval * 1000, key="datarefresh")

# Function to display and edit JSON data
def display_and_edit_json(file_path, title):
    st.header(f"Edit {title}")
    data = load_data(file_path)
    
    if view_mode == "JSON":
        data_str = st.text_area(f"{title}", json.dumps(data, indent=4), height=300)
        if st.button(f"Save {title}"):
            try:
                data = json.loads(data_str)
                save_data(file_path, data)
                st.success(f"Saved {title} successfully")
                if title == "data.json":
                    update_votes_json(data)
            except json.JSONDecodeError as e:
                st.error(f"Error parsing JSON: {e}")
    else:
        if title == "data.json":
            if data:
                st.write("Activities per Date")
                visual_data = []
                for date, activities in data.items():
                    visual_data.append(f"{date}")
                    for time, acts in activities.items():
                        visual_data.append(f"  {time}: {', '.join(acts)}")
                visual_data_str = "\n".join(visual_data)
                updated_visual_data_str = st.text_area("Edit Activities", visual_data_str, height=300)
                if st.button(f"Save {title}"):
                    try:
                        new_data = {}
                        lines = updated_visual_data_str.split('\n')
                        current_date = ""
                        for line in lines:
                            if line.strip() and not line.startswith("  "):
                                current_date = line.strip()
                                new_data[current_date] = {}
                            elif line.strip() and line.startswith("  "):
                                time_activities = line.strip().split(": ", 1)
                                if len(time_activities) == 2:
                                    time = time_activities[0].strip()
                                    acts_str = time_activities[1].strip()
                                    acts = [act.strip() for act in acts_str.split(",")]
                                    new_data[current_date][time] = acts
                        save_data(file_path, new_data)
                        st.success(f"Saved {title} successfully")
                        update_votes_json(new_data)
                    except Exception as e:
                        st.error(f"Error updating data: {e}")
        elif title == "votes.json":
            if data:
                st.write("Votes per Activity")
                visual_data = []
                for date, times in data.items():
                    visual_data.append(f"{date}")
                    for time, options in times.items():
                        visual_data.append(f"  {time}: {', '.join([f'{option} {count} votes' for option, count in options.items()])}")
                visual_data_str = "\n".join(visual_data)
                updated_visual_data_str = st.text_area("Edit Votes", visual_data_str, height=300)
                if st.button(f"Save {title}"):
                    try:
                        new_data = {}
                        lines = updated_visual_data_str.split('\n')
                        current_date = ""
                        for line in lines:
                            if line.strip() and not line.startswith("  "):
                                current_date = line.strip()
                                new_data[current_date] = {}
                            elif line.strip() and line.startswith("  "):
                                time_options = line.strip().split(": ", 1)
                                if len(time_options) == 2:
                                    time = time_options[0].strip()
                                    options_str = time_options[1].strip()
                                    options = {opt.rsplit(" ", 2)[0]: int(opt.rsplit(" ", 2)[1]) for opt in options_str.split(",")}
                                    new_data[current_date][time] = options
                        save_data(file_path, new_data)
                        st.success(f"Saved {title} successfully")
                    except Exception as e:
                        st.error(f"Error updating data: {e}")
        elif title == "debts.json":
            if data:
                st.write("Debts between Users")
                visual_data = []
                for from_user, to_users in data.items():
                    for to_user, amount in to_users.items():
                        visual_data.append(f"{from_user} owes {to_user} {amount} AUD")
                visual_data_str = "\n".join(visual_data)
                updated_visual_data_str = st.text_area("Edit Debts", visual_data_str, height=300)
                if st.button(f"Save {title}"):
                    try:
                        new_data = defaultdict(lambda: defaultdict(int))
                        lines = updated_visual_data_str.split('\n')
                        for line in lines:
                            if " owes " in line:
                                parts = line.split(" owes ")
                                from_user = parts[0].strip()
                                to_user_amount = parts[1].rsplit(" ", 2)
                                to_user = to_user_amount[0].strip()
                                amount = int(to_user_amount[1])
                                new_data[from_user][to_user] = amount
                        save_data(file_path, new_data)
                        st.success(f"Saved {title} successfully")
                    except Exception as e:
                        st.error(f"Error updating data: {e}")
        elif title == "debts_history.json":
            if data:
                st.write("Debts History")
                visual_data = [f"{entry['from']} owes {entry['to']} {entry['amount']} AUD" for entry in data]
                visual_data_str = "\n".join(visual_data)
                updated_visual_data_str = st.text_area("Edit Debts History", visual_data_str, height=300)
                if st.button(f"Save {title}"):
                    try:
                        new_data = []
                        lines = updated_visual_data_str.split('\n')
                        for line in lines:
                            if " owes " in line:
                                parts = line.split(" owes ")
                                from_user = parts[0].strip()
                                to_user, amount = parts[1].rsplit(" ", 1)
                                to_user = to_user.strip()
                                amount = int(amount.split(" ")[0])
                                new_data.append({"from": from_user, "to": to_user, "amount": amount})
                        save_data(file_path, new_data)
                        st.success(f"Saved {title} successfully")
                    except Exception as e:
                        st.error(f"Error updating data: {e}")
        elif title == "checklists.json":
            if data:
                st.write("Checklists")
                visual_data = []
                for category, items in data['users'].items():
                    if items:
                        visual_data.append(f"{category}: {', '.join([item['name'] + ' (' + ('1' if item['checked'] else '0') + ')' for item in items])}")
                    else:
                        visual_data.append(f"{category}: ")
                visual_data_str = "\n".join(visual_data)
                updated_visual_data_str = st.text_area("Edit Checklists", visual_data_str, height=300)
                if st.button(f"Save {title}"):
                    try:
                        new_data = {'users': defaultdict(list)}
                        lines = updated_visual_data_str.split('\n')
                        for line in lines:
                            if ": " in line:
                                category, items_str = line.split(": ", 1)
                                if items_str:
                                    items = items_str.split(", ")
                                    new_items = [{'name': item.split(' (')[0], 'checked': item.split(' (')[1].strip(')') == '1'} for item in items]
                                else:
                                    new_items = []
                                new_data['users'][category.strip()] = new_items
                        save_data(file_path, new_data)
                        st.success(f"Saved {title} successfully")
                    except Exception as e:
                        st.error(f"Error updating data: {e}")
        elif title == "users.json":
            if data:
                st.write("Users")
                visual_data = []
                for user, details in data.items():
                    visual_data.append(f"{user}: {', '.join([f'{key}: {value}' for key, value in details.items()])}")
                visual_data_str = "\n".join(visual_data)
                updated_visual_data_str = st.text_area("Edit Users", visual_data_str, height=300)
                if st.button(f"Save {title}"):
                    try:
                        new_data = {}
                        lines = updated_visual_data_str.split('\n')
                        for line in lines:
                            if ": " in line:
                                user, details_str = line.split(": ", 1)
                                details = {kv.split(": ")[0]: kv.split(": ")[1] for kv in details_str.split(", ")}
                                new_data[user.strip()] = details
                        save_data(file_path, new_data)
                        st.success(f"Saved {title} successfully")
                    except Exception as e:
                        st.error(f"Error updating data: {e}")

# Function to update votes.json based on data.json
def update_votes_json(data):
    votes = load_data(votes_file)
    new_votes = update_votes_based_on_data(data, votes)
    save_data(votes_file, new_votes)

# Display and edit each JSON file
display_and_edit_json(data_file, "data.json")
display_and_edit_json(votes_file, "votes.json")
display_and_edit_json(debts_file, "debts.json")
display_and_edit_json(debts_history_file, "debts_history.json")
display_and_edit_json(checklists_file, "checklists.json")
display_and_edit_json(users_file, "users.json")
