import streamlit as st
from subject_page import render_subject_page

st.set_page_config(layout="wide")

#Ensure User is logged In 
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in first.")
    st.stop()

render_subject_page("DM")