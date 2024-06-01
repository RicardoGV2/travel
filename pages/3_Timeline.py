import streamlit as st
from pyvis.network import Network
import networkx as nx
import streamlit.components.v1 as components
import json
import os

# Paths to the data and votes files
data_file = "data.json"
votes_file = "votes.json"

# Function to load data
def load_data():
    if os.path.exists(data_file):
        with open(data_file, 'r') as file:
            return json.load(file)
    else:
        return initial_data

def load_votes():
    if os.path.exists(votes_file):
        with open(votes_file, 'r') as file:
            return json.load(file)
    else:
        return {date: {time: {option: 0 for option in initial_data[date][time]} for time in initial_data[date]} for date in initial_data}

# Function to get top voted options
def get_top_voted_options(votes):
    top_voted = {}
    for date in votes:
        top_voted[date] = {}
        for time in votes[date]:
            options = votes[date][time]
            top_option = max(options, key=options.get)
            top_voted[date][time] = top_option
    return top_voted

# Function to create network with top voted options
def create_network_with_top_votes(data, top_voted):
    net = Network(height="1000px", width="100%", directed=True)
    G = nx.DiGraph()

    previous_node = None

    for date in data:
        for time in data[date]]:
            if date in top_voted and time in top_voted[date]]:
                top_option = top_voted[date][time]
                time_node = f"{date}_{time}_{top_option}"
                G.add_node(time_node, label=f"{time}\n{top_option}", shape="box")
                if previous_node:
                    G.add_edge(previous_node, time_node)
                previous_node = time_node
    
    net.from_nx(G)
    net.set_options("""
    var options = {
        "layout": {
            "hierarchical": {
                "enabled": true,
                "direction": "UD",
                "sortMethod": "directed"
            }
        },
        "physics": {
            "hierarchicalRepulsion": {
                "centralGravity": 0,
                "springLength": 100,
                "springConstant": 0.01,
                "nodeDistance": 120,
                "damping": 0.09
            },
            "minVelocity": 0.75
        }
    }
    """)
    return net

# Load data and votes
data = load_data()
votes = load_votes()

# Get the top voted options
top_voted = get_top_voted_options(votes)

# Create and display the network with top voted options
net = create_network_with_top_votes(data, top_voted)
path = 'full_network.html'
net.save
