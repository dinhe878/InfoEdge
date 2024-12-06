import streamlit as st
from pymongo.mongo_client import MongoClient
import os
# Local testing import
# from dotenv import load_dotenv
# load_dotenv(override=True)

# Welcome Page
st.title("Welcome to InfoEdge!")

# Connect to the DB.
@st.cache_resource
def connect_to_mongodb(username, password):
    if username and password is not None:
        # Construct the MongoDB connection URI
        mongo_uri = (
            "mongodb+srv://"
            + username
            + ":"
            + password
            + "@infoedge-cluster0.wrfbo.mongodb.net/"
        )
        client = MongoClient(mongo_uri)
        return client

# Initialize Session States.
if 'client' not in st.session_state:
       st.session_state.client = None
if 'username' not in st.session_state:
       st.session_state.username = ''
if 'form' not in st.session_state:
       st.session_state.form = ''
if 'selected_db' not in st.session_state:
       st.session_state.selected_db = None
if 'collections' not in st.session_state:
       st.session_state.collections = []
if 'selected_collection' not in st.session_state:
       st.session_state.selected_collection = None
if 'selected_region' not in st.session_state:
       st.session_state.selected_region = None

# Update username
def user_update(name):
    st.session_state.username = name

# Check if user is already logged in
if st.session_state.username != '':
    st.sidebar.write(f"You are logged in as {st.session_state.username}")

# Initialize login form
if st.session_state.username == '':
    login_form = st.sidebar.form(key='login_form', enter_to_submit=False, clear_on_submit=True)
    username = login_form.text_input(label='Enter Username')
    user_pas = login_form.text_input(label='Enter Password', type='password')
    login = login_form.form_submit_button(label='Log In', on_click=user_update(username))
    if login:
        st.sidebar.success(f"You are logged in as {username}")
        st.session_state.form = 'logged_in'
        st.session_state.client = connect_to_mongodb(username, user_pas)
        # Clear password
        del user_pas
        st.switch_page("pages/search.py")
    else:
        st.sidebar.warning("Please log in to continue")
else:    
    logout = st.sidebar.button(label='Log Out')
    if logout:
        user_update('')
        st.session_state.form = ''
        connect_to_mongodb.clear()
        st.session_state.client = None
        st.session_state.selected_db = None
        st.session_state.collections = []

# Sanity check for session state
#st.write(st.session_state)
