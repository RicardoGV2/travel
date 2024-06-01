import streamlit as st

# Cargar usuarios desde st.secrets
users = st.secrets["users"]

st.title("User Login")

# Inputs de nombre de usuario y contraseña
username = st.text_input("Username")
password = st.text_input("Password", type="password")

# Función de autenticación
def authenticate(username, password):
    if username in users and users[username] == password:
        return True
    return False

# Botón de inicio de sesión
if st.button("Login"):
    if authenticate(username, password):
        st.session_state['user'] = username
        st.success("Login successful")
        st.experimental_set_query_params(page="2_Voting")
        st.rerun()
    else:
        st.error("Invalid username or password")

# Redirigir a la página de votación si el usuario ya está autenticado
if 'user' in st.session_state:
    st.experimental_set_query_params(page="2_Voting")
    st.rerun()
