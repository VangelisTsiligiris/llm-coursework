import streamlit as st
from lib.ui import inject_css
from lib.auth import login_view
from lib.clients import get_config
from lib.storage import get_student_dataframes

st.set_page_config(page_title="LLM Coursework Helper", layout="wide")

# Inject all global CSS styles
# Note: This will only style standard components now, not custom divs.
inject_css() 

cfg = get_config()

# Sidebar navigation
with st.sidebar:
    st.page_link("Home.py", label="🏠 Home", icon="🏠")
    st.page_link("pages/1_Student_Workspace.py", label="✍️ Student Workspace")
    st.page_link("pages/2_Academic_Dashboard.py", label="🎓 Academic Dashboard")

    st.divider()
    if st.session_state.get("__auth_ok"):
        st.caption(f"Signed in as: **{st.session_state.get('user_id','?')}**")
        if st.button("Sign out", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

# Not logged in → show login screen instead
if not st.session_state.get("__auth_ok"):
    login_view()
    st.stop()

# Role flag
is_academic = st.session_state.get("is_academic", False)

# --- Hero section (Simplified) ---
st.header("LLM Coursework Helper")
st.write(
    """
    This pilot helps students ideate & draft with an AI assistant while giving academics a transparent, 
    privacy-aware view of **process evidence** (chat turns & draft evolution).
    """
)
st.divider()

# --- Two-column landing layout (Simplified) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("For Students (pilot)")
    st.markdown(
        """
        * Brainstorm with the AI (all turns are logged).
        * Draft in the rich editor; autosave & resume anytime.
        * Run **similarity check** vs AI outputs to keep your own voice.
        * Export a **DOCX evidence pack** (chat + draft + similarity).
        * **Your responsibility:** follow assessment rules & cite sources.
        """
    )

with col2:
    st.subheader("For Academics")
    st.markdown(
        """
        * Dashboard to review students’ **turn-by-turn** interactions.
        * See **latest draft** and AI ↔ student exchanges.
        * Suggested writing-alignment check for oversight (not grading).
        * Data stored: timestamp, student ID (pseudonymous), assignment ID, prompt, response, latest draft snapshot.
        * Data minimisation: no personal identifiers beyond the provided ID.
        """
    )


with st.expander("Privacy & Ethics"):
    st.markdown(
        """
        We log **timestamps**, your **Student ID**, **Assignment ID**, each **prompt**, the **AI response**, and saved **draft snapshots**.  
        We do **not** log personal identifiers beyond the ID you enter. The AI output is advisory; you are responsible for citation and originality.
        """
    )

st.divider()

# --- Quick links & stats (No change needed here) ---
c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("Jump in")
    st.page_link("pages/1_Student_Workspace.py", label="Open Student Workspace", icon="✍️")
    if is_academic:
        st.page_link("pages/2_Academic_Dashboard.py", label="Open Academic Dashboard", icon="🎓")

with c2:
    st.subheader("Your context")
    st.write(f"**User ID:** {st.session_state.get('user_id','?')}")
    st.write(f"**Role:** {'Academic' if is_academic else 'Student'}")

with c3:
    st.subheader("Workbook health")
    try:
        drafts_df, events_df = get_student_dataframes()
        st.write(f"Draft records: **{len(drafts_df)}**")
        st.write(f"Event turns: **{len(events_df)}**")
    except Exception as e:
        st.warning(f"Could not fetch workbook stats: {e}")
