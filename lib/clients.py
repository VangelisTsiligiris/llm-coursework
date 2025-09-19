# lib/clients.py
import os, json
from collections.abc import Mapping
import streamlit as st

# Optional libs (import here to fail fast if truly missing)
try:
    import gspread
    from gspread.exceptions import WorksheetNotFound
    from google.oauth2.service_account import Credentials
except Exception:
    gspread = None
    WorksheetNotFound = Exception
    Credentials = None

try:
    import google.generativeai as genai
except Exception:
    genai = None

def _as_plain(obj):
    if isinstance(obj, Mapping):
        return {k: _as_plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_as_plain(v) for v in obj]
    return obj

@st.cache_resource
def get_config():
    return {
        "APP_PASSCODE":      os.getenv("APP_PASSCODE")      or st.secrets.get("env", {}).get("APP_PASSCODE"),
        "ACADEMIC_PASSCODE": os.getenv("ACADEMIC_PASSCODE") or st.secrets.get("env", {}).get("ACADEMIC_PASSCODE"),
        "SPREADSHEET_KEY":   os.getenv("SPREADSHEET_KEY")   or st.secrets.get("env", {}).get("SPREADSHEET_KEY"),
        "ASSIGNMENT_DEFAULT": os.getenv("ASSIGNMENT_ID", "GENERIC"),
        "SIM_THRESHOLD": float(os.getenv("SIM_THRESHOLD", "0.85")),
        "AUTO_SAVE_SECONDS": int(os.getenv("AUTO_SAVE_SECONDS", "60")),
    }

@st.cache_resource
def get_spreadsheet():
    if gspread is None or Credentials is None:
        st.error("gspread/google-auth not installed.")
        st.stop()

    sa_raw = st.secrets.get("gcp_service_account", None)
    if sa_raw is None:
        sa_raw = os.getenv("GCP_SERVICE_ACCOUNT_JSON")

    if sa_raw is None:
        st.error("GCP Service Account credentials not found in secrets or env (GCP_SERVICE_ACCOUNT_JSON).")
        st.stop()

    if isinstance(sa_raw, str):
        try:
            sa_info = json.loads(sa_raw)
        except json.JSONDecodeError:
            st.error("GCP_SERVICE_ACCOUNT_JSON must be a valid JSON string.")
            st.stop()
    else:
        sa_info = _as_plain(sa_raw)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(sa_info, scopes=scopes)
    gc = gspread.authorize(creds)

    cfg = get_config()
    key = cfg["SPREADSHEET_KEY"]
    if not key:
        st.error("SPREADSHEET_KEY missing in env or secrets.")
        st.stop()
    return gc.open_by_key(key)

@st.cache_resource
def get_llm_client():
    if genai is None:
        st.error("google-generativeai not installed.")
        st.stop()
    gemini_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("google_api", {}).get("gemini_api_key")
    if not gemini_key:
        st.error("Gemini API key not found in secrets/env.")
        st.stop()
    genai.configure(api_key=gemini_key)
    return genai.GenerativeModel("gemini-1.5-flash")
