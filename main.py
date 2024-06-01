import streamlit as st

st.title("User Login")

selected_user = st.text_input("Enter your name:")

if st.button("Login"):
    st.session_state['user'] = selected_user
    st.experimental_set_query_params(page="voting")
    st.experimental_rerun()

# Redirect to voting.py if user is selected
if 'user' in st.session_state:
    st.experimental_set_query_params(page="voting")
    st.experimental_rerun()

# Debug information
st.write(st.experimental_get_query_params())
