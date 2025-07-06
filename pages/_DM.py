import streamlit as st
from firebase_config import db
from utils import get_joined_subjects

st.set_page_config(page_title="DM", layout="centered")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in first.")
    st.stop()

email = st.session_state.user_email
joined_subjects = get_joined_subjects(email)

st.title("📘 DM Notes")

if "DM" not in joined_subjects:
    st.error("🚫 Access denied: You haven't joined this class.")
    st.info("Go back to the Home page to join the class.")
    if st.button("⬅ Go to Home"):
        st.switch_page("Home.py")  # If using multipage app and Home.py is your main

    st.stop()


st.info("You can now upload, summarize or ask questions related to DM.")
