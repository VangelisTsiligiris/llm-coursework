# pages/2_Academic_Dashboard.py
import pandas as pd
import streamlit as st
from streamlit.components.v1 import html as st_html

from lib.ui import inject_css, md_to_html
from lib.storage import get_student_dataframes

st.set_page_config(page_title="Academic Dashboard", layout="wide")
inject_css()

if not (st.session_state.get("__auth_ok") and st.session_state.get("is_academic")):
    st.error("Only academic users can access the dashboard. Please login from Home with the academic passcode.")
    st.stop()

st.title("🎓 Academic Dashboard")

@st.cache_data(ttl=300)
def _get_data():
    return get_student_dataframes()

drafts_df, events_df = _get_data()
if drafts_df.empty and events_df.empty:
    st.warning("No student data recorded yet.")
    st.stop()

# Choose student and optional assignment filter
all_ids = sorted(
    {*(drafts_df.get('user_id', pd.Series(dtype=str)).dropna().astype(str)),
     *(events_df.get('user_id', pd.Series(dtype=str)).dropna().astype(str))} - {"Academic"}
)

sid = st.selectbox("Select a Student ID", all_ids, index=None, placeholder="Search…")
if not sid:
    st.info("Select a student to begin.")
    st.stop()

assignments = sorted(events_df[events_df['user_id']==sid]['assignment_id'].dropna().unique().tolist())
aid = st.selectbox("Filter by Assignment (optional)", ["(All)"] + assignments, index=0)

st.header(f"Reviewing: {sid}")

s_events = events_df[events_df['user_id']==sid].sort_values("timestamp")
s_drafts = drafts_df[drafts_df['user_id']==sid]

if aid and aid!="(All)":
    s_events = s_events[s_events['assignment_id']==aid]
    s_drafts = s_drafts[s_drafts['assignment_id']==aid]

col1, col2 = st.columns(2)
with col1:
    st.subheader("Latest Draft")
    if not s_drafts.empty:
        latest = s_drafts.sort_values('last_updated', ascending=False).iloc[0]
        st.markdown(f"**Last Saved:** {latest['last_updated']}")
        st_html(f'<div class="chat-box">{latest["draft_html"]}</div>', height=600)
    else:
        st.info("No saved drafts for this student.")

with col2:
    st.subheader("Turns (Prompt → Response)")
    if not s_events.empty:
        bubbles = []
        for _, row in s_events.iterrows():
            bubbles.append(f'<div class="chat-bubble chat-user"><strong>Prompt (Turn {row.get("turn","?")}):</strong><br>{md_to_html(row["prompt"])}</div>')
            bubbles.append(f'<div class="chat-bubble chat-assistant"><strong>Response:</strong><br>{md_to_html(row["response"])}</div>')
        st_html(f'<div class="chat-box">{"".join(bubbles)}</div>', height=600)
    else:
        st.info("No chat history for this selection.")
