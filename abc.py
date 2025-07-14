import streamlit as st
import os
from firebase_config import auth, storage, db  # Assumes you have this file
from utils import get_joined_subjects # Assumes you have this file

# --- Page Configuration ---
st.set_page_config(layout="wide")

# --- User Authentication Check ---
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in first. Login from the Home Page.")
    st.stop()

# --- Page Setup ---
subject = "Maths"
st.title(f"📚 {subject}")
email = st.session_state.user_email

# --- Access Control: Ensure user has joined the subject ---
try:
    joined_subjects = get_joined_subjects(email)
    if subject not in joined_subjects:
        st.error("🚫 Access denied: You haven't joined this class.")
        st.info("Go back to the Home page to join the class.")
        if st.button("⬅ Go to Home"):
            st.switch_page("Home.py")
        st.stop()
except Exception as e:
    st.error(f"Could not verify subject access: {e}")
    st.stop()


# --- Main Content with Tabs ---
tabs = st.tabs(["🌐 Global Notes", "🔒 Private Notes"])

# --- Tab 1: Global Notes ---
with tabs[0]:
    st.subheader("Shared Class Materials")
    try:
        notes = db.child("subjects").child(subject).child("global_notes").get()
        if notes.each():
            for item in notes.each():
                note = item.val()
                with st.container(border=True):
                    st.markdown(f"#### {note.get('title', 'Untitled')}")
                    st.markdown(f"**Summary:** {note.get('summary', 'No summary provided.')}")
                    if note.get("file_url"):
                        st.link_button("View File", note['file_url'])
        else:
            st.info("No global notes are available for this subject yet.")
    except Exception as e:
        st.error(f"Failed to load global notes: {e}")

# --- Tab 2: Private Notes (With Local File Handling) ---
with tabs[1]:
    st.subheader("Your Personal Space")
    user_key = email.replace(".", "_")

    # Display existing private notes
    try:
        notes = db.child("subjects").child(subject).child("private_notes").child(user_key).get()
        if notes.each():
            for item in notes.each():
                note = item.val()
                with st.container(border=True):
                    col1, col2 = st.columns([1, 2])
                    
                    # Column 1: Displaying the Original Content (Image or Text)
                    with col1:
                        content = note.get("original_content", "")
                        is_image = content.endswith((".jpg", ".png", ".jpeg"))

                        # **CRITICAL:** Check if the file path exists locally before trying to display it
                        if is_image and os.path.exists(content):
                            with open(content, "rb") as f:
                                st.image(f.read(), caption=os.path.basename(content), use_column_width=True)
                        elif content.startswith("http"):
                             st.link_button("View Link", content)
                        else:
                            st.write(content) # Display as plain text

                    # Column 2: Displaying the Summary
                    with col2:
                        st.markdown("**📝 Gemini Summary**")
                        summary = note.get("summary", "No summary available.")
                        st.write(summary)
        else:
            st.info("You haven’t added any private notes yet. Use the 'Add' button below.")
    except Exception as e:
        st.error(f"Failed to load private notes: {e}")

    st.markdown("---")

    # Form to add a new private note
    if "show_input_box_private" not in st.session_state:
        st.session_state.show_input_box_private = False

    if st.button("➕ Add New Private Note", use_container_width=True):
        st.session_state.show_input_box_private = True

    if st.session_state.show_input_box_private:
        with st.form("note_upload_form_private", clear_on_submit=True):
            st.markdown("### Add a New Note")
            file_input = st.file_uploader("Upload an image or document", type=["png", "jpg", "jpeg", "pdf", "txt"])
            text_input = st.text_area("Or type your note here...")
            
            submitted = st.form_submit_button("Submit Note")

            if submitted:
                if not file_input and not text_input.strip():
                    st.warning("Please upload a file or type a note.")
                    st.stop()
                
                content_to_save = ""
                title = "User Note"

                if file_input:
                    # Logic to save the file locally
                    safe_filename = file_input.name.replace(" ", "_")
                    folder_path = os.path.join("uploads", subject, "private", user_key)
                    os.makedirs(folder_path, exist_ok=True)
                    
                    file_save_path = os.path.join(folder_path, safe_filename)
                    with open(file_save_path, "wb") as f:
                        f.write(file_input.getbuffer())
                    
                    content_to_save = file_save_path # Save the local path to the database
                    title = safe_filename

                elif text_input.strip():
                    content_to_save = text_input.strip()

                # Replace with your actual Gemini summary logic
                summary = f"This is a summary for: '{content_to_save[:50]}...'"

                note_data = {
                    "title": title,
                    "summary": summary, 
                    "owner": user_key,
                    "original_content": content_to_save
                }

                # Push data to Firebase
                db.child("subjects").child(subject).child("private_notes").child(user_key).push(note_data)
                
                st.success("Note submitted successfully!")
                st.session_state.show_input_box_private = False
                st.rerun()











                
'''
                st.markdown(f"{note.get('title', 'Untitled')}")
                st.markdown(f"**Summary : ** {note.get('summary', 'No summary')}\n")
                if note.get("file_url"):
                    st.markdown(f"[View File]({note['file_url']})", unsafe_allow_html=True)
                st.markdown("---")
'''

