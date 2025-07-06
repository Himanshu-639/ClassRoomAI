import streamlit as st
from firebase_config import auth, db
from utils import get_user_key, get_joined_subjects, get_available_subjects, join_subject, init_user_node, auto_login_from_refresh

# Page setup
st.set_page_config(page_title="ClassRoomAI", layout="centered")
st.title("Welcome to ClassRoomAI")

# Session state defaults
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.refresh_token = None

# Attempt session restore using refresh_token
auto_login_from_refresh()

# Login / Signup screen
def render_auth_ui():
    auth_mode = st.radio("Choose Action : ", ['LogIn', 'SignUp'], horizontal=True)
    email = st.text_input("Email : ")
    password = st.text_input("Password : ", type="password")

    if auth_mode == "SignUp":
        if st.button("Create Account"):
            try:
                auth.create_user_with_email_and_password(email, password)
                st.success("✅ Account created successfully! You can now log in.")
            except Exception as e:
                st.error(f"Signup error : {e}")

    elif auth_mode == "LogIn":
        if st.button("Log In"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.id_token = user["idToken"]
                st.session_state.refresh_token = user["refreshToken"]
                init_user_node(email)
                st.success("✅ Login successful!")
                st.rerun()
            except Exception as e:
                st.error(f"Login Error : {e}")

# Sidebar: Show joined subjects
def render_sidebar():
    st.sidebar.header("📚 Your Subjects")
    try:
        joined_subjects = get_joined_subjects(st.session_state.user_email)
        if joined_subjects:
            subject_files = {subj: f"pages/_{subj}.py" for subj in joined_subjects}

            for subj in joined_subjects:
                if st.sidebar.button(f"📘 {subj}", key=f"btn_{subj}"):
                    st.switch_page(subject_files[subj])
        else:
            st.sidebar.info("You haven't joined any subjects yet.")
    except Exception as e:
        st.sidebar.error(f"Error loading subjects: {e}")


# Main Area: Join a Class
def render_join_class():
    st.subheader("Join a Class")
    try:
        subject_list = get_available_subjects()
        if not subject_list:
            st.info("No subjects available. Please add subjects in Firebase.")
        else:
            selected_subject = st.selectbox("Available Subjects", subject_list, index=None, placeholder="Select a Subject")
            if selected_subject:
                joined_subjects = get_joined_subjects(st.session_state.user_email)
                if selected_subject in joined_subjects:
                    st.info(f"✅ You have already joined {selected_subject}")
                else:
                    if st.button("Join Selected Subject"):
                        join_subject(selected_subject, st.session_state.user_email, joined_subjects)
                        st.success(f"✅ Joined {selected_subject}")
                        st.rerun()
    except Exception as e:
        st.error(f"Error loading subjects: {e}")

# App logic
if not st.session_state.logged_in:
    render_auth_ui()
else:
    st.success(f"Logged In as {st.session_state.user_email}")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.id_token = None
        st.session_state.refresh_token = None
        st.rerun()

    st.markdown("---")
    st.write("📚 Go to the sidebar to select a subject and view your notes.")
    render_sidebar()
    st.markdown("---")
    render_join_class()
