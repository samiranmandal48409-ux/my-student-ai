import streamlit as st
from groq import Groq
import time
import requests

st.set_page_config(
    page_title="Nova AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:       #0a0c10;
    --surface:  #111318;
    --surface2: #1a1d24;
    --border:   #232730;
    --accent:   #00e5ff;
    --text:     #e2e8f0;
    --muted:    #64748b;
    --user-bg:  #131b2e;
    --green:    #10b981;
    --radius:   14px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stHeader"], [data-testid="stToolbar"],
.stDeployButton, #MainMenu, footer { display: none !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

[data-testid="stAppViewContainer"] > .main > .block-container {
    max-width: 860px !important;
    padding: 0 1.5rem 6rem !important;
    margin: 0 auto !important;
}

.hero { text-align: center; padding: 3rem 1rem 2rem; position: relative; }
.hero::before {
    content: ''; position: absolute; top: 0; left: 50%;
    transform: translateX(-50%);
    width: 600px; height: 300px;
    background: radial-gradient(ellipse at center, rgba(0,229,255,.07) 0%, transparent 70%);
    pointer-events: none;
}
.hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(0,229,255,.08); border: 1px solid rgba(0,229,255,.2);
    border-radius: 999px; padding: 4px 14px;
    font-family: 'Space Mono', monospace; font-size: 11px;
    color: var(--accent); letter-spacing: .05em; margin-bottom: 1.2rem;
}
.hero-badge::before { content: '●'; font-size: 8px; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }
.hero h1 {
    font-family: 'Space Mono', monospace !important;
    font-size: clamp(1.8rem, 4vw, 2.8rem) !important; font-weight: 700 !important;
    color: #fff !important; line-height: 1.15 !important;
    letter-spacing: -.02em; margin-bottom: .6rem !important;
}
.hero h1 span { color: var(--accent); }
.hero p { font-size: 1rem; color: var(--muted); font-weight: 300; max-width: 440px; margin: 0 auto; }
.divider { height: 1px; background: linear-gradient(90deg, transparent, var(--border), transparent); margin: 1.5rem 0; }

[data-testid="stChatMessage"] { background: transparent !important; border: none !important; padding: 0 !important; }
[data-testid="stChatMessage"] > div { background: transparent !important; }
[data-testid="stChatMessageContent"] { background: transparent !important; }
.stChatMessage {
    border-radius: var(--radius) !important; padding: 1rem 1.2rem !important;
    border: 1px solid var(--border) !important; margin-bottom: .75rem !important;
    background: var(--surface) !important; animation: fadeUp .25s ease;
}
@keyframes fadeUp { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) {
    background: var(--user-bg) !important; border-color: rgba(0,229,255,.15) !important;
}

pre, code { font-family: 'Space Mono', monospace !important; font-size: 13px !important; }
pre {
    background: #0d1117 !important; border: 1px solid var(--border) !important;
    border-left: 3px solid var(--accent) !important; border-radius: 10px !important;
    padding: 1rem 1.2rem !important; overflow-x: auto !important;
}
code:not(pre code) {
    background: rgba(0,229,255,.08) !important; color: var(--accent) !important;
    border-radius: 5px !important; padding: 2px 6px !important; font-size: 12.5px !important;
}

[data-testid="stChatInputContainer"] {
    position: fixed !important; bottom: 0 !important; left: 50% !important;
    transform: translateX(-50%) !important; width: 100% !important; max-width: 860px !important;
    padding: 1rem 1.5rem 1.5rem !important;
    background: linear-gradient(to top, var(--bg) 70%, transparent) !important;
    backdrop-filter: blur(10px); z-index: 999 !important;
}
[data-testid="stChatInput"] {
    background: var(--surface2) !important; border: 1px solid var(--border) !important;
    border-radius: 12px !important; color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 15px !important;
    transition: border-color .2s, box-shadow .2s;
}
[data-testid="stChatInput"]:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(0,229,255,.1) !important; outline: none !important;
}
[data-testid="stChatInputSubmitButton"] button {
    background: var(--accent) !important; border: none !important;
    border-radius: 8px !important; color: #000 !important; font-weight: 600 !important;
}
[data-testid="stChatInputSubmitButton"] button:hover { background: #33ecff !important; }
.stButton > button {
    background: var(--surface2) !important; border: 1px solid var(--border) !important;
    color: var(--muted) !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 13px !important;
    font-weight: 500 !important; padding: .4rem 1rem !important; transition: all .2s !important;
}
.stButton > button:hover {
    border-color: var(--accent) !important; color: var(--accent) !important;
    background: rgba(0,229,255,.06) !important;
}

.stats-row { display: flex; gap: 1rem; margin: 1.2rem 0 1.8rem; justify-content: center; flex-wrap: wrap; }
.stat-pill {
    display: flex; align-items: center; gap: 7px;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 999px; padding: 6px 14px; font-size: 12.5px; color: var(--muted);
}
.stat-pill .dot { width:7px; height:7px; border-radius:50%; }
.dot-green  { background: var(--green); box-shadow: 0 0 6px var(--green); }
.dot-blue   { background: var(--accent); box-shadow: 0 0 6px var(--accent); }
.dot-purple { background: #7c3aed; box-shadow: 0 0 6px #7c3aed; }

.search-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(16,185,129,.08); border: 1px solid rgba(16,185,129,.2);
    border-radius: 6px; padding: 3px 10px;
    font-size: 11px; color: var(--green); margin-bottom: .5rem;
}
</style>
""", unsafe_allow_html=True)

# ── Groq client ───────────────────────────────────────────────────────────────
client = Groq(api_key="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")
MODEL = "llama-3.3-70b-versatile"

# ── Web search via DuckDuckGo (free, no API key) ──────────────────────────────
def web_search(query: str, max_results: int = 4) -> str:
    """Search DuckDuckGo and return a clean text summary of results."""
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": "1",
            "skip_disambig": "1",
        }
        resp = requests.get(url, params=params, timeout=8)
        data = resp.json()

        results = []

        # Instant answer (best for factual questions)
        if data.get("Answer"):
            results.append(f"Answer: {data['Answer']}")

        # Abstract (Wikipedia-style summary)
        if data.get("Abstract"):
            results.append(f"Summary: {data['Abstract'][:400]}")

        # Related topics
        for topic in data.get("RelatedTopics", [])[:max_results]:
            if isinstance(topic, dict) and topic.get("Text"):
                results.append(topic["Text"][:200])

        if results:
            return "\n".join(results)

        # Fallback: DuckDuckGo HTML search scrape
        html_resp = requests.get(
            f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=8
        )
        import re
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html_resp.text)
        clean = [re.sub(r'<[^>]+>', '', s).strip() for s in snippets[:4]]
        return "\n".join(clean) if clean else "No results found."

    except Exception as e:
        return f"Search failed: {e}"


# ── Decide if query needs a web search ───────────────────────────────────────
SEARCH_TRIGGERS = [
    "who is", "who was", "who won", "who are", "who did",
    "what is", "what was", "what are", "what happened",
    "when is", "when was", "when did", "when will",
    "where is", "where was", "current", "latest", "recent",
    "today", "news", "ipl", "election", "prime minister", "president",
    "score", "match", "winner", "champion", "result",
    "price", "stock", "weather", "2023", "2024", "2025",
]

def needs_search(query: str) -> bool:
    q = query.lower()
    # Never search for identity questions about Nova AI itself
    identity_keywords = ["who made you", "who created you", "who built you", "who are you", "your creator", "your developer"]
    if any(k in q for k in identity_keywords):
        return False
    return any(trigger in q for trigger in SEARCH_TRIGGERS)


# ── Build prompt ──────────────────────────────────────────────────────────────
def build_messages(user_query: str, search_results: str = ""):
    system = (
        "You are Nova AI — a smart, accurate, and friendly AI assistant. "
        "You were created by Samiran. "
        "If anyone asks who made you, who created you, who built you, or who you are, "
        "always say: 'I am Nova AI, created by Samiran.' "
        "Never mention Meta, Llama, OpenAI, Groq, Anthropic, or any underlying model or company. "
        "Answer clearly and directly. Never hallucinate. "
        "If web search results are provided, use ONLY those to answer factual questions — do not guess. "
        "Format code with markdown code blocks. Be concise."
    )
    if search_results:
        user_content = (
            f"Web search results for '{user_query}':\n"
            f"{search_results}\n\n"
            f"Based on the above search results, answer this question accurately: {user_query}"
        )
    else:
        user_content = user_query

    return [
        {"role": "system", "content": system},
        {"role": "user",   "content": user_content[:2000]}
    ]


# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">LIVE &nbsp;·&nbsp; FREE TO USE</div>
    <h1>Nova<span> AI</span></h1>
    <p>Your personal AI assistant — accurate, fast, and always up to date.</p>
</div>
<div class="stats-row">
    <div class="stat-pill"><span class="dot dot-blue"></span> Live web search</div>
    <div class="stat-pill"><span class="dot dot-purple"></span> No hallucination</div>
    <div class="stat-pill"><span class="dot dot-green"></span> All topics</div>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

# ── Toolbar ───────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([5, 1, 1])
with col2:
    count = len([m for m in st.session_state.messages if m["role"] == "user"])
    st.markdown(
        f"<p style='text-align:right;color:var(--muted);font-size:12.5px;padding-top:.5rem'>"
        f"{count} message{'s' if count != 1 else ''}</p>",
        unsafe_allow_html=True
    )
with col3:
    if st.button("🗑️ Clear"):
        st.session_state.messages = []
        st.rerun()

# ── Chat history ──────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem;color:var(--muted);">
        <div style="font-size:2.5rem;margin-bottom:1rem">✨</div>
        <p style="font-size:1rem;font-weight:500;color:#94a3b8;margin-bottom:.8rem">How can I help you today?</p>
        <p style="font-size:.875rem;line-height:2.2">
            🔍 <em>"Who is the current Prime Minister of India?"</em><br>
            🏏 <em>"Who won IPL 2023?"</em><br>
            💻 <em>"Write a Python web scraper"</em><br>
            🌍 <em>"Latest AI news today"</em>
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("searched"):
                st.markdown(
                    '<div class="search-badge">🔍 Searched the web</div>',
                    unsafe_allow_html=True
                )
            st.markdown(msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask me anything…"):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        searched = False
        search_results = ""

        # Step 1: Search the web if needed
        if needs_search(prompt):
            with st.spinner("🔍 Searching the web…"):
                search_results = web_search(prompt)
                searched = True

        # Step 2: Ask the AI (grounded with search results)
        for attempt in range(3):
            try:
                spinner_msg = "✨ Thinking…" if attempt == 0 else "Rate limited — retrying in 60s ⏳"
                with st.spinner(spinner_msg):
                    if attempt > 0:
                        time.sleep(60)
                    completion = client.chat.completions.create(
                        messages=build_messages(prompt, search_results),
                        model=MODEL,
                        max_tokens=600,
                        temperature=0.3,
                    )
                response = completion.choices[0].message.content

                if searched:
                    st.markdown('<div class="search-badge">🔍 Searched the web</div>', unsafe_allow_html=True)
                st.markdown(response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "searched": searched
                })
                break

            except Exception as e:
                if "rate_limit_exceeded" in str(e) and attempt < 2:
                    continue
                else:
                    st.error(f"❌ Error: {e}")
