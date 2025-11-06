import streamlit as st
from lib.ui import inject_css
from lib.auth import login_view
from lib.clients import get_config
from lib.storage import get_student_dataframes

st.set_page_config(page_title="LLM Coursework Helper", layout="wide")

# Inject all global CSS styles
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

# Hero section
st.markdown(
    """
<div class="hero">
  <h1>LLM Coursework Helper</h1>
  <p>This pilot helps students ideate & draft with an AI assistant while giving academics a transparent, 
  privacy-aware view of <strong>process evidence</strong> (chat turns & draft evolution).</p>
</div>
""",
    unsafe_allow_html=True,
)

# Two-column landing layout
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
<div class="card">
  <h3>For Students <span class="badge">pilot</span></h3>
  <ul>
    <li>Brainstorm with the AI (all turns are logged).</li>
    <li>Draft in the rich editor; autosave & resume anytime.</li>
    <li>Run <strong>similarity check</strong> vs AI outputs to keep your own voice.</li>
    <li>Export a <strong>DOCX evidence pack</strong> (chat + draft + similarity).</li>
    <li><strong>Your responsibility:</strong> follow assessment rules & cite sources.</li>
  </ul>
</div>
""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
<div class="card">
  <h3>For Academics</h3>
  <ul>
    <li>Dashboard to review students’ <strong>turn-by-turn</strong> interactions.</li>
    <li>See <strong>latest draft</strong> and AI ↔ student exchanges.</li>
    <li>Suggested writing-alignment check for oversight (not grading).</li>
    <li>Data stored: timestamp, student ID (pseudonymous), assignment ID, prompt, response, latest draft snapshot.</li>
    <li>Data minimisation: no personal identifiers beyond the provided ID.</li>
  </ul>
</div>
""",
        unsafe_allow_html=True,
    )

with st.expander("Privacy & Ethics"):
    st.markdown(
        """
We log **timestamps**, your **Student ID**, **Assignment ID**, each **prompt**, the **AI response**, and saved **draft snapshots**.  
We do **not** log personal identifiers beyond the ID you enter. The AI output is advisory; you are responsible for citation and originality.
        """
    )

st.divider()

# Quick links & stats
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