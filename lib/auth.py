# lib/auth.py
import streamlit as st
from lib.ui import inject_css
from lib.clients import get_config
from lib.storage import get_known_student_ids

def login_view():
    inject_css()
    cfg = get_config()

    st.markdown(
        """
<div class="hero">
  <h1>LLM Coursework Helper</h1>
  <p>Sign in with a <strong>Student ID</strong> or a passcode.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
<div class="card">
  <h3>For Students <span class="badge">pilot</span></h3>
  <ul>
    <li>Draft & chat with the AI. All turns are logged.</li>
    <li>Autosave & resume later with your Student ID.</li>
    <li>Run similarity check & export an evidence pack.</li>
  </ul>
</div>
"""
        )
    with col2:
        st.markdown(
            """
<div class="card">
  <h3>For Academics</h3>
  <ul>
    <li>Review turn-by-turn interactions and latest drafts.</li>
    <li>Optional writing-alignment view for oversight.</li>
    <li>Data minimisation: only pseudonymous IDs.</li>
  </ul>
</div>
"""
        )

    with st.expander("Privacy & Ethics"):
        st.markdown(
            """
We log **timestamps**, **Student ID**, **Assignment ID**, each **prompt**, the **AI response**, and saved **draft snapshots**.  
We do **not** log personal identifiers beyond the provided ID. You are responsible for citation, originality, and following assessment rules.
            """
        )

    st.divider()

    user_input = st.text_input(
        "Enter your **Student ID** or a **Passcode**",
        placeholder="Student ID, Student Passcode, or Academic Passcode",
    )

    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Login", use_container_width=True):
            ids = get_known_student_ids()
            inp = (user_input or "").strip().upper()
            if inp and cfg["ACADEMIC_PASSCODE"] and inp == cfg["ACADEMIC_PASSCODE"].upper():
                st.session_state.update({"__auth_ok": True, "is_academic": True, "user_id": "Academic", "show_landing_page": False})
                st.success("Logged in as Academic.")
                st.rerun()
            elif inp and cfg["APP_PASSCODE"] and inp == cfg["APP_PASSCODE"].upper():
                import random, string
                new_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
                st.session_state.update({"__auth_ok": True, "is_academic": False, "user_id": new_id, "show_landing_page": True})
                st.success(f"Your new Student ID is **{new_id}** — copy it to resume later.")
                st.rerun()
            elif inp in ids:
                st.session_state.update({"__auth_ok": True, "is_academic": False, "user_id": inp, "show_landing_page": False})
                st.success(f"Welcome back, {inp}!")
                st.rerun()
            else:
                st.error("Invalid ID or Passcode.")
    with c2:
        if st.button("Generate New Student ID", use_container_width=True):
            import random, string
            new_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
            st.session_state.update({"__auth_ok": True, "is_academic": False, "user_id": new_id, "show_landing_page": True})
            st.success(f"Your new Student ID is **{new_id}** — copy it to resume later.")
            st.rerun()
