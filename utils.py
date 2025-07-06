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

def get_available_subjects():
    """Fetch list of available subjects from Firebase Realtime DB."""
    subjects_node = db.child("subjects").shallow().get()
    return list(subjects_node.val()) if subjects_node.val() else []

def join_subject(subject, email, joined_subjects):
    """Adds a subject to the user's joined subjects in the database, avoiding duplicates."""
    user_key = email.replace(".", "_")
    if subject not in joined_subjects:
        joined_subjects.append(subject)
        db.child("users").child(user_key).update({"joined_subjects": joined_subjects})

def init_user_node(email):
    """Ensures a user node exists in the database with default values."""
    user_key = email.replace(".", "_")
    existing = db.child("users").child(user_key).get().val()
    if not existing:
        db.child("users").child(user_key).set({"joined_subjects": []})


def get_joined_subjects(user_email):
    user_key = user_email.replace(".", "_")
    user_data = db.child("users").child(user_key).get().val()
    return user_data.get("joined_subjects", []) if user_data else []



def ensure_subject_access(subject, user_email):
    joined_subjects = get_joined_subjects(user_email)
    if subject not in joined_subjects:
        return False, joined_subjects
    return True, joined_subjects

def save_note_metadata(subject, user_email, note_data, is_private=False):
    """
    Save note metadata (title, summary, etc.) under global or private notes in Firebase
    """
    user_key = user_email.replace(".", "_")
    note_section = "private_notes" if is_private else "global_notes"
    
    db.child("subjects").child(subject).child("private_notes").child(user_key).push(note_data)

def fetch_notes(subject, is_private=False, user_email=None):
    """
    Fetch all notes for a subject. If private, filter by user.
    """
    note_section = "private_notes" if is_private else "global_notes"
    notes = db.child("subjects").child(subject).child(note_section).get().val()

    if not notes:
        return []

    if is_private and user_email:
        user_key = user_email.replace(".", "_")
        return [note for note in notes.values() if note.get("owner") == user_key]

    return list(notes.values())
