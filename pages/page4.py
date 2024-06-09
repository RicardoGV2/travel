import streamlit as st
import json
import os

# Paths to the data and votes files
data_file = "data.json"
votes_file = "votes.json"
debts_file = "debts.json"
debts_history_file = "debts_history.json"

# Load data
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        return {}

# Page layout
st.title("JSON Data Viewer")

# Section to view data.json
st.header("Data JSON")
data = load_data(data_file)
st.json(data)

# Section to view votes.json
st.header("Votes JSON")
votes = load_data(votes_file)
st.json(votes)

# Section to view debts.json
st.header("Debts JSON")
debts = load_data(debts_file)
st.json(debts)

# Section to view debts_history.json
st.header("Debts History JSON")
debts_history = load_data(debts_history_file)
st.json(debts_history)
