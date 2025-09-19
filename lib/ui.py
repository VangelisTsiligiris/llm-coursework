# lib/ui.py
import html as _html
import re
import streamlit as st

def inject_css():
    st.markdown(
        """
<style>
:root {
  --ui-font: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, "Noto Sans", "Liberation Sans", sans-serif;
  --brand: #3558ff;
  --brand-2: #7c4dff;
  --bg-soft: #f6f8ff;
  --card: #ffffff;
  --muted: #6b7280;
  --border: #e6e9f2;
}
html, body, [data-testid="stAppViewContainer"] { font-family: var(--ui-font); }
.block-container { padding-top: 0.8rem; padding-bottom: 1rem; }

/* Chips & cards */
.header-bar {display:flex; gap:.6rem; flex-wrap:wrap; font-size:.95rem; color:#444; margin:.25rem 0 .5rem;}
.status-chip{background:#f5f7fb;border:1px solid var(--border);border-radius:999px;padding:.15rem .6rem}
.small-muted{color:#7a7f8a}
.hero { max-width: 1100px; margin:.6rem auto 1.2rem; padding:1.25rem 1.4rem; border-radius:16px; border:1px solid #dfe6ff;
        background: linear-gradient(135deg, #edf1ff 0%, #f7f4ff 100%); }
.hero h1 { margin:.1rem 0 .2rem; font-size:2.2rem; line-height:1.2; }
.card { background: var(--card); border:1px solid var(--border); border-radius:14px; padding:1rem 1.1rem; box-shadow:0 1px 0 rgba(17,24,39,.03);}
.badge { display:inline-block; padding:.2rem .5rem; font-size:.8rem; border-radius:999px; background:#eef2ff; color:#334155; border:1px solid #e5e7eb; margin-left:.5rem; }

/* Chat */
.chat-box { height: 560px; overflow-y:auto; border:1px solid #dcdfe6; border-radius:10px; background:#fff; padding:.5rem; }
.chat-empty{ border:1px dashed #e6e9f2; background:#fbfbfb; color:#708090; padding:.6rem .8rem; border-radius:10px; }
.chat-bubble { border-radius:12px; padding:.7rem .9rem; margin:.45rem .2rem; border:1px solid #eee; line-height:1.55; font-size:0.95rem;}
.chat-user{ background:#eef7ff; }
.chat-assistant{ background:#f6f6f6; }
.chat-bubble pre { background:#111827; color:#f9fafb; padding:.7rem .9rem; border-radius:10px; overflow:auto; font-size:.9rem; }

/* Editor */
.editor-wrap { border:1px solid var(--border); border-radius:10px; padding:.25rem .5rem; }
.ql-container.ql-snow {min-height:360px; border:none;}
.ql-toolbar.ql-snow {border:none; border-bottom:1px solid var(--border);}

/* Fix expander icon scribble issue by drawing our own */
[data-testid="stExpanderHeader"] [data-testid="stExpanderToggleIcon"]{ display:none !important; }
[data-testid="stExpanderHeader"]::before{
  content:"▸"; display:inline-block; margin-right:.35rem; color:#6b7280; transition: transform .18s ease;
}
[data-testid="stExpanderHeader"][aria-expanded="true"]::before{ content:"▾"; }
</style>
""",
        unsafe_allow_html=True,
    )

# --- Markdown/HTML helpers ---
try:
    import markdown as _md
except Exception:
    _md = None

def md_to_html(text: str) -> str:
    if not text:
        return ""
    if _md:
        try:
            return _md.markdown(text, extensions=["fenced_code", "tables", "sane_lists", "codehilite"])
        except Exception:
            pass
    t = _html.escape(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\\1</strong>", t)
    return t.replace("\n", "<br>")

try:
    from bs4 import BeautifulSoup
    def html_to_text(html: str) -> str:
        return BeautifulSoup(html or "", "html.parser").get_text("\n")
except Exception:
    def html_to_text(html: str) -> str:
        return (html or "").replace("<br>", "\n").replace("<br/>", "\n")
