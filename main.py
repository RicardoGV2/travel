import streamlit as st
from st_pages import hide_pages

# Configurar la página principal
st.set_page_config(
    page_title="Travel Planner",
    page_icon="🌍",
)

# Ocultar páginas si el usuario no está logueado
if 'user' not in st.session_state:
    hide_pages(["2_Voting", "3_Timeline"])

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

# Si el usuario está logueado, redirigir a la página de votación
if 'user' in st.session_state:
    st.experimental_set_query_params(page="2_Voting")
    st.experimental_rerun()
