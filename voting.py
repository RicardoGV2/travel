import streamlit as st

# Redirect to login if no user is selected
if 'user' not in st.session_state:
    st.experimental_set_query_params(page="main")
    st.experimental_rerun()

st.title("Voting Page")

# To run the app, use the command: streamlit run voting.py
