import streamlit as st
import json
import os
from collections import defaultdict
from navigation import make_sidebar
from streamlit_autorefresh import st_autorefresh

make_sidebar()

# Paths to the debts files
debts_file = "debts.json"
debts_history_file = "debts_history.json"

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

# Convert loaded data to defaultdict
def convert_to_defaultdict(data):
    if isinstance(data, dict):
        return defaultdict(lambda: defaultdict(int), {k: convert_to_defaultdict(v) for k, v in data.items()})
    return data

# Load debts and convert to defaultdict
loaded_debts = load_data(debts_file, {})
debts = convert_to_defaultdict(loaded_debts)
debts_history = load_data(debts_history_file, [])

# Function to add a debt
def add_debt(from_user, to_user, amount):
    if from_user not in debts:
        debts[from_user] = defaultdict(int)
    if to_user not in debts[from_user]:
        debts[from_user][to_user] = 0
    debts[from_user][to_user] += amount
    debts_history.append({"from": from_user, "to": to_user, "amount": amount})
    save_data(debts_file, debts)
    save_data(debts_history_file, debts_history)

# Function to recalculate debts from history
def recalculate_debts_from_history():
    new_debts = defaultdict(lambda: defaultdict(int))
    for debt in debts_history:
        from_user = debt['from']
        to_user = debt['to']
        amount = debt['amount']
        if from_user not in new_debts:
            new_debts[from_user] = defaultdict(int)
        if to_user not in new_debts[from_user]:
            new_debts[from_user][to_user] = 0
        new_debts[from_user][to_user] += amount
    return new_debts

# Function to delete a debt
def delete_debt(index):
    del debts_history[index]
    save_data(debts_history_file, debts_history)
    st.success("Debt deleted from history.")
    # Recalculate debts from history after deletion
    global debts
    debts = recalculate_debts_from_history()
    save_data(debts_file, debts)
    st.experimental_rerun()

# Function to simplify debts
def simplify_debts(debts):
    simplified_debts = defaultdict(lambda: defaultdict(int))

    # Simplify mutual debts first
    for from_user in list(debts.keys()):
        for to_user in list(debts[from_user].keys()):
            if from_user != to_user and debts[to_user].get(from_user, 0) > 0:
                if debts[from_user][to_user] > debts[to_user][from_user]:
                    simplified_debts[from_user][to_user] = debts[from_user][to_user] - debts[to_user][from_user]
                    del debts[to_user][from_user]
                elif debts[from_user][to_user] < debts[to_user][from_user]:
                    simplified_debts[to_user][from_user] = debts[to_user][from_user] - debts[from_user][to_user]
                    del debts[from_user][to_user]
                else:
                    del debts[from_user][to_user]
                    del debts[to_user][from_user]

    # Simplify chains of debts
    for _ in range(len(debts)):
        for from_user in list(debts.keys()):
            for to_user in list(debts[from_user].keys()):
                if debts[from_user][to_user] > 0:
                    for to_user_2 in list(debts[to_user].keys()):
                        if from_user != to_user_2 and debts[to_user][to_user_2] > 0:  # Ensure valid chain
                            min_debt = min(debts[from_user][to_user], debts[to_user][to_user_2])
                            debts[from_user][to_user] -= min_debt
                            debts[to_user][to_user_2] -= min_debt
                            if debts[from_user][to_user] == 0:
                                del debts[from_user][to_user]
                            if debts[to_user][to_user_2] == 0:
                                del debts[to_user][to_user_2]
                            if from_user not in debts:
                                debts[from_user] = defaultdict(int)
                            if to_user_2 not in debts[from_user]:
                                debts[from_user][to_user_2] = 0
                            debts[from_user][to_user_2] += min_debt

    for from_user in debts:
        for to_user in debts[from_user]:
            if debts[from_user][to_user] > 0:
                simplified_debts[from_user][to_user] += debts[from_user][to_user]

    return simplified_debts

# Page layout
st.title("Debt Management")

# Section to add a new debt
st.header("Add a New Debt")
from_user = st.selectbox("From:", ["Jorge", "Raquel", "Karime", "Katia", "Janet", "Ricardo"], key="from_user")
to_user = st.selectbox("To:", ["Jorge", "Raquel", "Karime", "Katia", "Janet", "Ricardo"], key="to_user")
amount = st.number_input("Amount (in AUD):", min_value=1, key="amount")

if st.button("Add Debt"):
    if from_user and to_user and amount > 0:
        if from_user != to_user:
            add_debt(from_user, to_user, amount)
            st.success(f"Added debt: {from_user} owes {to_user} {amount} AUD")
            st.experimental_rerun()
        else:
            st.error("The same user cannot owe to themselves.")
    else:
        st.error("Please fill in all fields")

# Section to simplify debts
st.header("Debts")
simplified_debts = simplify_debts(debts)

if simplified_debts:
    for from_user in simplified_debts:
        for to_user in simplified_debts[from_user]:
            st.write(f"{from_user} owes {to_user} {simplified_debts[from_user][to_user]} AUD")
else:
    st.write("No debts to display.")

# Option to show/hide debt history and deletion
show_deletion_section = st.checkbox("Show Debt History and Deletion Section", value=False)

if show_deletion_section:
    # Section to display and delete debts
    st.header("Debt History and Deletion")
    selected_debt = st.radio("Select a debt to delete:", [f"{debt['from']} owes {debt['to']} {debt['amount']} AUD" for debt in debts_history], key="selected_debt")
    selected_index = next((i for i, debt in enumerate(debts_history) if f"{debt['from']} owes {debt['to']} {debt['amount']} AUD" == selected_debt), None)
    
    if st.button("Delete Selected Debt"):
        if selected_index is not None:
            delete_debt(selected_index)
        else:
            st.error("No debt selected for deletion.")

# Auto refresh settings
st.sidebar.title("Settings")
auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=True)
refresh_interval = st.sidebar.number_input("Refresh Interval (seconds)", min_value=1, max_value=60, value=7) if auto_refresh else None

# Auto refresh
if auto_refresh and refresh_interval:
    st_autorefresh(interval=refresh_interval * 1000, key="datarefresh")

# Option to show/hide JSON files, only available for user "Ricardo"
if st.session_state.get('username') == "Ricardo":
    show_debts_json = st.sidebar.checkbox("Show Debts JSON", value=False)
    show_debts_history_json = st.sidebar.checkbox("Show Debts History JSON", value=False)

    # Display JSON files
    if show_debts_json:
        st.write("### Debts JSON")
        st.json(load_data(debts_file, {}))

    if show_debts_history_json:
        st.write("### Debts History JSON")
        st.json(load_data(debts_history_file, []))
