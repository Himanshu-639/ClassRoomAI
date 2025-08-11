def render_subject_page(subject):
    import streamlit as st
    from firebase_config import auth, storage, db
    from utils import get_joined_subjects
    from summarizers import youtube_summarizer, link_summarizer, pdf_summarizer, image_summarizer, text_summarizer, txt_summarizer
    import os, time
    from datetime import datetime

    st.title(subject)

    email = st.session_state.user_email
    joined_subjects = get_joined_subjects(email, st.session_state.id_token)

    if subject not in joined_subjects:
        st.error("🚫 Access denied: You haven't joined this class.")
        st.info("Go back to the Home page to join the class.")
        if st.button("⬅ Go to Home"):
            st.switch_page("Home.py")  # If using multipage app and Home.py is your main
        st.stop()

    # Tabs: Global Notes first, then Private Notes
    tabs = st.tabs(["🌐 Global Space", "🔒 Private Space"])

    #Global Notes
    with tabs[0]:
        try:
            user_key = email.replace(".", "_")
            notes = db.child("subjects").child(subject).child("global_notes").get(st.session_state.id_token)
            if notes.each():
                for item in notes.each():
                    note = item.val()
                    with st.container(border =True):
                        col1, col2 = st.columns([1, 2])
                        content = note.get("original_content", "")

                        with col1:
                            is_image = content.endswith((".jpg", ".png", ".jpeg"))

                            if is_image and os.path.exists(content):
                                with open(content, "rb") as f:
                                    st.image(f.read(), caption=os.path.basename(content), use_container_width=True)
                            elif content.endswith(".txt") and os.path.exists(content):
                                with open(content, "r", encoding="utf-8") as f:
                                    st.caption(f"📄 {os.path.basename(content)}")
                                    text_content = f.read()
                                    st.code(text_content, language="text", wrap_lines=True, height=200)
                                    st.download_button("Download File", f, file_name=os.path.basename(content), use_container_width=True, key=f"global-{content}-downloader")
                            elif content.endswith(".pdf") and os.path.exists(content):
                                st.caption(f"📄 {os.path.basename(content)}")
                                with open(content, "rb") as f:
                                    st.download_button("Download PDF", f, file_name=os.path.basename(content), use_container_width=True, key=f"global-{content}-downloader")
                            elif content.startswith("https://youtu.be") or content.startswith("https://youtube"):
                                st.video(content)
                            elif content.startswith("http"):
                                st.link_button("View Link", content, use_container_width=True)
                            else:
                                st.caption("Note")
                                st.code(content, language="text", wrap_lines=True, height=200)

                        with col2:
                            st.markdown("**Summary**")
                            summary = note.get("summary", "No summary available.")
                            st.write(summary)

            else:
                st.info("No global notes available.")
        except Exception as e:
            st.error(f"Failed to load global notes : {e}")

        if "show_input_box_global" not in st.session_state:
            st.session_state.show_input_box_global = False

        if st.button("➕ Add", use_container_width=True, key="show_global_add_btn"):
            st.session_state.show_input_box_global = True

        if st.session_state.show_input_box_global:
            with st.form("note_upload_form_global"):
                st.markdown("### Add New Global Note")
                col1, col2 = st.columns(2)
                with col1:
                    text_input = st.text_area("Type your note text here...")
                with col2:
                    file_input = st.file_uploader("Upload a file", type=["png", "jpg", "jpeg", "pdf", "txt"])

                col_submit, col_cancel = st.columns([1,1])
                submit = col_submit.form_submit_button("Submit")
                cancel = col_cancel.form_submit_button("Cancel")

                if submit:
                    if not file_input and not text_input.strip():
                        st.warning("Please upload a file or type a note.")
                        st.stop()

                    content_to_save = ""
                    title = "User Note"

                    if file_input:
                        safe_filename = file_input.name.replace(" ", "_")
                        folder_path = os.path.join("uploads", subject, "global")
                        os.makedirs(folder_path, exist_ok=True)

                        file_save_path = os.path.join(folder_path, safe_filename)
                        with open(file_save_path, "wb") as f:
                            f.write(file_input.getbuffer())

                        content_to_save = file_save_path
                        title = safe_filename

                        if safe_filename.endswith(".pdf"):
                            summary = pdf_summarizer(content_to_save)
                        elif safe_filename.endswith((".jpg", ".png", ".jpeg")):
                            summary = image_summarizer(content_to_save)
                        elif safe_filename.endswith(".txt"):
                            summary = txt_summarizer(content_to_save)

                    elif text_input.strip():
                        content_to_save = text_input.strip()
                        if content_to_save.startswith("https://youtu.be") or content_to_save.startswith("https://youtube.com"):
                            summary = youtube_summarizer(content_to_save)
                        elif content_to_save.startswith("https://"):
                            summary = link_summarizer(content_to_save)
                        else:
                            summary = text_summarizer(content_to_save)

                    note_data = {
                        "title" : title,
                        "summary" : summary,
                        "owner" : user_key,
                        "original_content" : content_to_save,
                        "timestamp": time.time()
                    }

                    db.child("subjects").child(subject).child("global_notes").push(note_data, st.session_state.id_token)
                    st.success("Note Submitted")
                    st.session_state.show_input_box_global = False
                    st.rerun()

                if cancel:
                    st.session_state.show_input_box_global = False
                    st.rerun()


    with tabs[1]:
        try:
            user_key = email.replace(".", "_")
            notes = db.child("subjects").child(subject).child("private_notes").child(user_key).get(st.session_state.id_token)
            if notes.each():
                for item in notes.each():
                    note = item.val()
                    with st.container(border =True):
                        col1, col2 = st.columns([1, 2])
                        content = note.get("original_content", "")
                        timestamp = note.get("timestamp")
                        if timestamp:
                            readable_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")


                        with col1:
                            is_image = content.endswith((".jpg", ".png", ".jpeg"))

                            if is_image and os.path.exists(content):
                                with open(content, "rb") as f:
                                    st.image(f.read(), caption=os.path.basename(content), use_container_width=True)
                                    st.write(timestamp)
                            elif content.endswith(".txt") and os.path.exists(content):
                                with open(content, "r", encoding="utf-8") as f:
                                    st.caption(f"📄 {os.path.basename(content)}")
                                    text_content = f.read()
                                    st.code(text_content, language="text", wrap_lines=True, height=200)
                                    st.write(timestamp)
                                    st.download_button("Download File", f, file_name=os.path.basename(content), use_container_width=True, key=f"private-{content}-downloader")
                            elif content.endswith(".pdf") and os.path.exists(content):
                                st.caption(f"📄 {os.path.basename(content)}")
                                with open(content, "rb") as f:
                                    st.download_button("Download PDF", f, file_name=os.path.basename(content), use_container_width=True, key=f"private-{content}-downloader")
                            elif content.startswith("https://youtu.be") or content.startswith("https://youtube"):
                                st.video(content)
                            elif content.startswith("http"):
                                st.link_button("View Link", content, use_container_width=True)
                            else:
                                st.caption("Note")
                                st.code(content, language="text", wrap_lines=True, height=200)

                        with col2:
                            st.markdown("**Summary**")
                            summary = note.get("summary", "No summary available.")
                            st.write(summary)
            else:
                st.info("You haven’t added any private notes yet.")

        except Exception as e:
            st.error(f"Failed to load private notes: {e}")

        if "show_input_box_private" not in st.session_state:
            st.session_state.show_input_box_private = False

        if st.button("➕ Add", use_container_width=True, key="show_private_add_btn"):
            st.session_state.show_input_box_private = True

        if st.session_state.show_input_box_private:
            with st.form("note_upload_form_private"):
                st.markdown("### Add New Private Note")
                col1, col2 = st.columns(2)
                with col1:
                    text_input = st.text_area("Type your note text here...")
                with col2:
                    file_input = st.file_uploader("Upload a file", type=["png", "jpg", "jpeg", "pdf", "txt"])

                col_submit, col_cancel = st.columns([1,1])
                submit = col_submit.form_submit_button("Submit")
                cancel = col_cancel.form_submit_button("Cancel")

                if submit:
                    if not file_input and not text_input.strip():
                        st.warning("Please upload a file or type a note.")
                        st.stop()

                    content_to_save = ""
                    title = "User Note"

                    if file_input:
                        safe_filename = file_input.name.replace(" ", "_")
                        folder_path = os.path.join("uploads", subject, "private", user_key)
                        os.makedirs(folder_path, exist_ok=True)

                        file_save_path = os.path.join(folder_path, safe_filename)
                        with open(file_save_path, "wb") as f:
                            f.write(file_input.getbuffer())

                        content_to_save = file_save_path
                        title = safe_filename

                        if safe_filename.endswith(".pdf"):
                            summary = pdf_summarizer(content_to_save)
                        elif safe_filename.endswith((".jpg", ".png", ".jpeg")):
                            summary = image_summarizer(content_to_save)
                        elif safe_filename.endswith(".txt"):
                            summary = txt_summarizer(content_to_save)

                    elif text_input.strip():
                        content_to_save = text_input.strip()
                        if content_to_save.startswith("https://youtu.be") or content_to_save.startswith("https://youtube.com"):
                            summary = youtube_summarizer(content_to_save)
                        elif content_to_save.startswith("https://"):
                            summary = link_summarizer(content_to_save)
                        else:
                            summary = text_summarizer(content_to_save)

                    note_data = {
                        "title" : title,
                        "summary" : summary,
                        "owner" : user_key,
                        "original_content" : content_to_save,
                        "timestamp": time.time()
                    }

                    db.child("subjects").child(subject).child("private_notes").child(user_key).push(note_data, st.session_state.id_token)
                    st.success("Note Submitted")
                    st.session_state.show_input_box_private = False
                    st.rerun()

                if cancel:
                    st.session_state.show_input_box_private = False
                    st.rerun()


