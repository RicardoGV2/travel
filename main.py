import streamlit as st

st.set_page_config(
    page_title="Travel Planner",
    page_icon="🌍",
)

# Si el usuario no está logueado, mostrar un mensaje para que inicie sesión
if 'user' not in st.session_state:
    st.sidebar.success("Select the login page above.")
    st.write("# Welcome to the Travel Planner! 🌍")

    st.markdown(
        """
        This is a travel planning application where you can:
        - Select or add users.
        - Vote for activities.
        - View the timeline of planned activities.
        
        **👈 Select the login page from the sidebar** to get started!
        """
    )
else:
    st.sidebar.success("Select a page above.")
    st.experimental_set_query_params(page="2_Voting")
    st.experimental_rerun()
