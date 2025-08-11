import streamlit as st
from firebase_config import db, auth
import os

def auto_login_from_refresh():
    """Attempt to auto-login the user using a saved refresh token."""
    if not st.session_state.logged_in and st.session_state.get("refresh_token"):
        try:
            user = auth.refresh(st.session_state.refresh_token)
            st.session_state.logged_in = True
            st.session_state.id_token = user['idToken']

            # Fetch user email again
            account_info = auth.get_account_info(user['idToken'])
            st.session_state.user_email = account_info['users'][0]['email']
        except Exception:
            st.warning("⚠️ Session expired or invalid. Please log in again.")
            st.session_state.logged_in = False

def get_user_key(email: str) -> str:
    """Convert user email to a valid Firebase key."""
    return email.replace(".", "_")

def get_available_subjects(id_token):
    """Fetch list of available subjects from Firebase Realtime DB."""
    subjects_node = db.child("subjects").shallow().get(id_token)
    return list(subjects_node.val()) if subjects_node.val() else []

def join_subject(subject, email, joined_subjects, id_token):
    """Adds a subject to the user's joined subjects in the database, avoiding duplicates."""
    user_key = email.replace(".", "_")
    if subject not in joined_subjects:
        joined_subjects.append(subject)
        db.child("users").child(user_key).update({"joined_subjects": joined_subjects}, id_token)

def init_user_node(email, id_token):
    """Ensures a user node exists in the database with default values."""
    user_key = email.replace(".", "_")
    existing = db.child("users").child(user_key).get(id_token).val()
    if not existing:
        db.child("users").child(user_key).set({"joined_subjects": []}, id_token)


def get_joined_subjects(user_email, id_token):
    user_key = user_email.replace(".", "_")
    user_data = db.child("users").child(user_key).get(id_token).val()
    return user_data.get("joined_subjects", []) if user_data else []

