# lib/storage.py
import datetime, time
import pandas as pd
import streamlit as st
from lib.clients import get_spreadsheet, get_config

EVENTS_HEADERS = ["timestamp", "user_id", "assignment_id", "turn", "prompt", "response"]
DRAFTS_HEADERS  = ["user_id", "assignment_id", "draft_html", "draft_text", "last_updated"]

@st.cache_resource
def get_or_create_worksheets():
    sh = get_spreadsheet()
    try:
        events_ws = sh.worksheet("events")
    except Exception:
        events_ws = sh.add_worksheet(title="events", rows=1, cols=len(EVENTS_HEADERS))
        events_ws.append_row(EVENTS_HEADERS, value_input_option="USER_ENTERED")
    try:
        drafts_ws = sh.worksheet("drafts")
    except Exception:
        drafts_ws = sh.add_worksheet(title="drafts", rows=1, cols=len(DRAFTS_HEADERS))
        drafts_ws.append_row(DRAFTS_HEADERS, value_input_option="USER_ENTERED")
    return events_ws, drafts_ws

def append_row_safe(ws, row):
    """Avoid 'Unable to parse range' by calculating next row and updating directly."""
    try:
        ws.append_row(row, value_input_option="USER_ENTERED")
        return
    except Exception:
        pass
    try:
        current = ws.get_all_values()
        next_row = len(current) + 1
        if next_row > ws.row_count:
            ws.add_rows(max(10, next_row - ws.row_count))
        ws.update(f"A{next_row}", [row], value_input_option="USER_ENTERED")
    except Exception as e2:
        st.warning(f"Append failed: {e2}")

def save_draft_row(drafts_ws, user_id, assignment_id, draft_html):
    from lib.ui import html_to_text
    draft_text = html_to_text(draft_html)
    append_row_safe(drafts_ws, [
        user_id, assignment_id, draft_html, draft_text, datetime.datetime.now().isoformat()
    ])
    st.session_state["last_saved_at"] = datetime.datetime.now()
    st.session_state["last_saved_html"] = draft_html

def load_last_draft(drafts_ws, user_id, assignment_id):
    try:
        recs = drafts_ws.get_all_records(expected_headers=DRAFTS_HEADERS, head=1, default_blank="")
        for r in reversed(recs):
            if str(r.get("user_id","")).strip().upper() == str(user_id).strip().upper() and \
               str(r.get("assignment_id","")).strip() == str(assignment_id).strip():
                return r.get("draft_html") or ""
    except Exception:
        return ""
    return ""

def log_turn_row(events_ws, user_id, assignment_id, prompt, response, turn):
    append_row_safe(events_ws, [
        datetime.datetime.now().isoformat(),
        user_id,
        assignment_id,
        turn,
        str(prompt)[:10000],
        str(response)[:10000],
    ])

@st.cache_data(ttl=60)
def get_known_student_ids():
    _, drafts_ws = get_or_create_worksheets()
    try:
        recs = drafts_ws.get_all_records(expected_headers=DRAFTS_HEADERS, head=1, default_blank="")
        if not recs: return set()
        return set(pd.DataFrame(recs)["user_id"].astype(str).unique())
    except Exception:
        return set()

@st.cache_data(ttl=300)
def get_student_dataframes():
    events_ws, drafts_ws = get_or_create_worksheets()
    drafts = pd.DataFrame(drafts_ws.get_all_records(expected_headers=DRAFTS_HEADERS, head=1, default_blank=""))
    events = pd.DataFrame(events_ws.get_all_records(expected_headers=EVENTS_HEADERS, head=1, default_blank=""))
    return drafts, events
