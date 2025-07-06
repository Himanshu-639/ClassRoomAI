import streamlit as st
from firebase_config import auth, storage, db
from utils import get_joined_subjects, ensure_subject_access 

st.set_page_config(layout="wide")

#Ensure User is logged In 
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in first.")
    st.stop()

subject = "Maths"
st.title(f"Maths")

email = st.session_state.user_email
joined_subjects = get_joined_subjects(email)

if "Maths" not in joined_subjects:
    st.error("🚫 Access denied: You haven't joined this class.")
    st.info("Go back to the Home page to join the class.")
    if st.button("⬅ Go to Home"):
        st.switch_page("Home.py")  # If using multipage app and Home.py is your main
    st.stop()

# Tabs: Global Notes first, then Private Notes

tabs = st.tabs(["🌐 Global Notes", "🔒 Private Notes"])


#Global Notes
with tabs[0]:
    st.subheader("Global Space")
    try:
        notes = db.child("subjects").child(subject).child("global_notes").get()
        if notes.each():
            for item in notes.each():
                note = item.val()
                st.markdown(f"{note.get('title', 'Untitled')}")
                st.markdown(f"**Summary:** {note.get('summary', 'No summary')}\n")
                if note.get("file_url"):
                    st.markdown(f"[View File]({note['file_url']})", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("No global notes available.")
    except Exception as e:
        st.error(f"Failed to load global notes : {e}")

with tabs[1]:
    st.subheader("Your Private Space")
    try:
        user_key = email.replace(".", "_")  # Firebase keys can't contain '.'
        notes = db.child("subjects").child(subject).child("private_notes").child(user_key).get()
        if notes.each():
            for item in notes.each():
                note = item.val()
                st.markdown(f"{note.get('title', 'Untitled')}")
                st.markdown(f"**Summary : ** {note.get('summary', 'No summary')}\n")
                if note.get("file_url"):
                    st.markdown(f"[View File]({note['file_url']})", unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("You haven’t added any private notes yet.")

        
    except Exception as e:
        st.error(f"Failed to load private notes: {e}")









