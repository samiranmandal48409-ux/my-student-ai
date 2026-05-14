import streamlit as st
from groq import Groq
import time

st.set_page_config(
    page_title="CodeMentor AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Root variables ── */
:root {
    --bg:        #0a0c10;
    --surface:   #111318;
    --surface2:  #1a1d24;
    --border:    #232730;
    --accent:    #00e5ff;
    --accent2:   #7c3aed;
    --text:      #e2e8f0;
    --muted:     #64748b;
    --user-bg:   #131b2e;
    --ai-bg:     #111318;
    --green:     #10b981;
    --radius:    14px;
}

/* ── Global reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Hide default Streamlit chrome */
[data-testid="stHeader"],
[data-testid="stToolbar"],
.stDeployButton,
#MainMenu,
footer { display: none !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

/* ── Main container ── */
[data-testid="stAppViewContainer"] > .main > .block-container {
    max-width: 860px !important;
    padding: 0 1.5rem 6rem !important;
    margin: 0 auto !important;
}

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 3rem 1rem 2rem;
    position: relative;
}
.hero::before {
    content: '';
    position: absolute;
    top: 0; left: 50%;
    transform: translateX(-50%);
    width: 600px; height: 300px;
    background: radial-gradient(ellipse at center, rgba(0,229,255,.07) 0%, transparent 70%);
    pointer-events: none;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(0,229,255,.08);
    border: 1px solid rgba(0,229,255,.2);
    border-radius: 999px;
    padding: 4px 14px;
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    color: var(--accent);
    letter-spacing: .05em;
    margin-bottom: 1.2rem;
}
.hero-badge::before { content: '●'; font-size: 8px; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }

.hero h1 {
    font-family: 'Space Mono', monospace !important;
    font-size: clamp(1.8rem, 4vw, 2.8rem) !important;
    font-weight: 700 !important;
    color: #fff !important;
    line-height: 1.15 !important;
    letter-spacing: -.02em;
    margin-bottom: .6rem !important;
}
.hero h1 span { color: var(--accent); }
.hero p {
    font-size: 1rem;
    color: var(--muted);
    font-weight: 300;
    max-width: 440px;
    margin: 0 auto;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 1.5rem 0;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin-bottom: .5rem !important;
}
[data-testid="stChatMessage"] > div {
    background: transparent !important;
}

/* User bubble */
[data-testid="stChatMessage"][data-testid*="user"],
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
    background: var(--user-bg) !important;
}

/* Message wrappers */
[data-testid="stChatMessageContent"] {
    background: transparent !important;
}
.stChatMessage {
    border-radius: var(--radius) !important;
    padding: 1rem 1.2rem !important;
    border: 1px solid var(--border) !important;
    margin-bottom: .75rem !important;
    background: var(--surface) !important;
    animation: fadeUp .25s ease;
}
@keyframes fadeUp {
    from { opacity:0; transform:translateY(8px); }
    to   { opacity:1; transform:translateY(0); }
}

/* User message accent */
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) {
    background: var(--user-bg) !important;
    border-color: rgba(0,229,255,.15) !important;
}

/* ── Code blocks ── */
pre, code {
    font-family: 'Space Mono', monospace !important;
    font-size: 13px !important;
}
pre {
    background: #0d1117 !important;
    border: 1px solid var(--border) !important;
    border-left: 3px solid var(--accent) !important;
    border-radius: 10px !important;
    padding: 1rem 1.2rem !important;
    overflow-x: auto !important;
}
code:not(pre code) {
    background: rgba(0,229,255,.08) !important;
    color: var(--accent) !important;
    border-radius: 5px !important;
    padding: 2px 6px !important;
    font-size: 12.5px !important;
}

/* ── Chat input ── */
[data-testid="stChatInputContainer"] {
    position: fixed !important;
    bottom: 0 !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: 100% !important;
    max-width: 860px !important;
    padding: 1rem 1.5rem 1.5rem !important;
    background: linear-gradient(to top, var(--bg) 70%, transparent) !important;
    backdrop-filter: blur(10px);
    z-index: 999 !important;
}
[data-testid="stChatInput"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
    padding: .8rem 1rem !important;
    box-shadow: 0 0 0 0 transparent;
    transition: border-color .2s, box-shadow .2s;
}
[data-testid="stChatInput"]:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(0,229,255,.1) !important;
    outline: none !important;
}
[data-testid="stChatInputSubmitButton"] button {
    background: var(--accent) !important;
    border: none !important;
    border-radius: 8px !important;
    color: #000 !important;
    font-weight: 600 !important;
}
[data-testid="stChatInputSubmitButton"] button:hover {
    background: #33ecff !important;
}

/* ── Buttons ── */
.stButton > button {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--muted) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: .4rem 1rem !important;
    transition: all .2s !important;
    letter-spacing: .01em;
}
.stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: rgba(0,229,255,.06) !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] {
    color: var(--accent) !important;
}

/* ── Stats row ── */
.stats-row {
    display: flex;
    gap: 1rem;
    margin: 1.2rem 0 1.8rem;
    justify-content: center;
}
.stat-pill {
    display: flex;
    align-items: center;
    gap: 7px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 6px 14px;
    font-size: 12.5px;
    color: var(--muted);
}
.stat-pill .dot { width:7px; height:7px; border-radius:50%; }
.dot-green  { background: var(--green); box-shadow: 0 0 6px var(--green); }
.dot-blue   { background: var(--accent); box-shadow: 0 0 6px var(--accent); }
.dot-purple { background: #7c3aed; box-shadow: 0 0 6px #7c3aed; }
</style>
""", unsafe_allow_html=True)

# ── Groq client ─────────────────────────────────────────────────────────────
client = Groq(api_key="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")

SYSTEM_PROMPT = (
    "You are CodeMentor AI — an expert coding partner for students. "
    "Help them learn and build real projects. Provide full, working code when asked "
    "and explain concepts simply and clearly. Format code with proper markdown code blocks."
)
MAX_HISTORY = 4

def get_trimmed_messages():
    return st.session_state.messages[-MAX_HISTORY:]

# ── Session state ────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Hero Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">LIVE &nbsp;·&nbsp; FREE TO USE</div>
    <h1>Code<span>Mentor</span> AI</h1>
    <p>Your personal AI coding partner — ask anything, build anything, learn everything.</p>
</div>

<div class="stats-row">
    <div class="stat-pill"><span class="dot dot-blue"></span> Instant responses</div>
    <div class="stat-pill"><span class="dot dot-purple"></span> Auto-retry on limits</div>
</div>

<div class="divider"></div>
""", unsafe_allow_html=True)

# ── Toolbar ──────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([5, 1, 1])
with col2:
    msg_count = len(st.session_state.messages)
    st.markdown(
        f"<p style='text-align:right;color:var(--muted);font-size:12.5px;padding-top:.5rem'>"
        f"{msg_count // 2} turn{'s' if msg_count // 2 != 1 else ''}</p>",
        unsafe_allow_html=True
    )
with col3:
    if st.button("🗑️ Clear"):
        st.session_state.messages = []
        st.rerun()

# ── Chat history ─────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem;color:var(--muted);">
        <div style="font-size:2.5rem;margin-bottom:1rem">⚡</div>
        <p style="font-size:1rem;font-weight:500;color:#94a3b8;margin-bottom:.5rem">
            Ready to help you code
        </p>
        <p style="font-size:.875rem">
            Try: <em>"Build a REST API in Python"</em> or <em>"Explain recursion with an example"</em>
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask me to write code, explain concepts, debug…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        for attempt in range(3):
            try:
                spinner_msg = "Thinking…" if attempt == 0 else f"Rate limited — retrying in 60s ⏳"
                with st.spinner(spinner_msg):
                    if attempt > 0:
                        time.sleep(60)
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            *get_trimmed_messages()
                        ],
                        model="llama-3.1-8b-instant",
                        max_tokens=512,
                    )
                    response = chat_completion.choices[0].message.content
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    break
            except Exception as e:
                if "rate_limit_exceeded" in str(e) and attempt < 2:
                    continue
                else:
                    st.error(f"❌ Failed after 3 attempts: {e}")
