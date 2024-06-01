import streamlit as st

st.set_page_config(
    page_title="Travel Planner",
    page_icon="🌍",
)

st.sidebar.success("Select a page above.")

st.write("# Welcome to the Travel Planner! 🌍")

st.markdown(
    """
    This is a travel planning application where you can:
    - Select or add users.
    - Vote for activities.
    - View the timeline of planned activities.
    
    **👈 Select a page from the sidebar** to get started!
    """
)

# Check if the user is logged in
if 'user' in st.session_state:
    st.experimental_set_query_params(page="2_Voting")
    st.experimental_rerun()
    