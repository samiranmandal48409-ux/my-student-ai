import streamlit as st
from groq import Groq
import time
import urllib.parse
import requests
from io import BytesIO

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

.hero {
    text-align: center; padding: 3rem 1rem 2rem; position: relative;
}
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
.dot-pink   { background: #ec4899; box-shadow: 0 0 6px #ec4899; }
</style>
""", unsafe_allow_html=True)

# ── Clients ───────────────────────────────────────────────────────────────────
client = Groq(api_key="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")
MODEL = "compound-beta"

SYSTEM_PROMPT = (
    "You are Nova AI — a smart, accurate, and friendly AI assistant with access to the internet. "
    "Always search the web for recent events, sports results, news, and current information. "
    "IMPORTANT: You can NOT generate images. If the user asks for an image, just say the image is being generated separately. "
    "Help with anything: coding, writing, math, science, general knowledge, creative tasks, advice, and more. "
    "Be clear and thorough. Format code with proper markdown code blocks."
)
MAX_HISTORY = 6

# ── Image detection — checks BEFORE sending to AI ─────────────────────────────
IMAGE_KEYWORDS = [
    "generate image", "generate an image", "generate a image",
    "create image", "create an image", "create a image",
    "make image", "make an image", "make a image",
    "draw", "draw me", "draw a", "draw an",
    "illustrate", "paint a", "paint an",
    "show me a picture", "show me an image", "show me a image",
    "image of", "picture of", "photo of",
    "generate a photo", "create a photo", "make a photo",
    "generate a picture", "create a picture", "make a picture",
]

def is_image_request(text: str) -> bool:
    t = text.lower().strip()
    return any(kw in t for kw in IMAGE_KEYWORDS)

def extract_image_prompt(user_text: str) -> str:
    """Pull out just the visual subject from the user's message."""
    t = user_text.lower()
    # Sort longest first so we match the most specific phrase
    for kw in sorted(IMAGE_KEYWORDS, key=len, reverse=True):
        if kw in t:
            idx = t.find(kw) + len(kw)
            subject = user_text[idx:].strip().lstrip(":-– of")
            return subject if subject else user_text
    return user_text

def generate_image(prompt: str):
    """Download a real image from Pollinations.ai and return bytes."""
    encoded = urllib.parse.quote(prompt)
    seed = int(time.time())
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=1024&height=768&nologo=true&seed={seed}&model=flux"
    )
    try:
        resp = requests.get(url, timeout=40)
        if resp.status_code == 200 and resp.headers.get("Content-Type", "").startswith("image"):
            return BytesIO(resp.content), url, None
        return None, url, f"Server returned status {resp.status_code}"
    except requests.exceptions.Timeout:
        return None, url, "Request timed out. Try again."
    except Exception as e:
        return None, url, str(e)

def get_trimmed_messages():
    return [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[-MAX_HISTORY:]
        if m.get("content")
    ]

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">LIVE &nbsp;·&nbsp; FREE TO USE</div>
    <h1>Nova<span> AI</span></h1>
    <p>Your personal AI assistant — chat, create, imagine, build.</p>
</div>
<div class="stats-row">
    <div class="stat-pill"><span class="dot dot-blue"></span> Live web search</div>
    <div class="stat-pill"><span class="dot dot-purple"></span> Accurate answers</div>
    <div class="stat-pill"><span class="dot dot-green"></span> All topics</div>
    <div class="stat-pill"><span class="dot dot-pink"></span> Real image generation</div>
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

# ── Render chat history ───────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem;color:var(--muted);">
        <div style="font-size:2.5rem;margin-bottom:1rem">✨</div>
        <p style="font-size:1rem;font-weight:500;color:#94a3b8;margin-bottom:.8rem">How can I help you today?</p>
        <p style="font-size:.875rem;line-height:2">
            🎨 <em>"Generate an image of a dragon"</em><br>
            🔍 <em>"Who won IPL 2023?"</em><br>
            💻 <em>"Write a Python web scraper"</em><br>
            🌍 <em>"Latest AI news today"</em>
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("type") == "image":
                st.markdown(f"🎨 **Generated image of:** _{msg['img_prompt']}_")
                if msg.get("img_bytes"):
                    st.image(msg["img_bytes"], use_container_width=True)
                else:
                    st.warning("Image could not be loaded.")
                st.markdown(
                    "<p style='font-size:11px;color:#64748b;margin-top:.4rem'>"
                    "🖼️ Real image · Pollinations.ai Flux model · Free & unlimited</p>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask anything, or say 'generate an image of a dragon'…"):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ══ Route: IMAGE ══════════════════════════════════════════════════════════
    if is_image_request(prompt):
        img_prompt = extract_image_prompt(prompt)
        if not img_prompt or len(img_prompt) < 2:
            img_prompt = prompt  # fallback: use full message

        with st.chat_message("assistant"):
            with st.spinner(f"🎨 Generating real image of '{img_prompt}'… (up to 20s)"):
                img_bytes, img_url, error = generate_image(img_prompt)

            if img_bytes:
                st.markdown(f"🎨 **Generated image of:** _{img_prompt}_")
                st.image(img_bytes, use_container_width=True)
                st.markdown(
                    "<p style='font-size:11px;color:#64748b;margin-top:.4rem'>"
                    "🖼️ Real image · Pollinations.ai Flux model · Free & unlimited</p>",
                    unsafe_allow_html=True
                )
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "image",
                    "img_prompt": img_prompt,
                    "img_url": img_url,
                    "img_bytes": img_bytes,
                    "content": f"[Image generated: {img_prompt}]"
                })
            else:
                st.error(f"❌ Image generation failed: {error}\n\nTry again or rephrase your prompt.")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Sorry, I couldn't generate the image. Error: {error}"
                })

    # ══ Route: CHAT (web-search powered) ═════════════════════════════════════
    else:
        with st.chat_message("assistant"):
            for attempt in range(3):
                try:
                    msg = "Thinking…" if attempt == 0 else "Rate limited — retrying in 60s ⏳"
                    with st.spinner(msg):
                        if attempt > 0:
                            time.sleep(60)
                        completion = client.chat.completions.create(
                            messages=[
                                {"role": "system", "content": SYSTEM_PROMPT},
                                *get_trimmed_messages()
                            ],
                            model=MODEL,
                            max_tokens=1024,
                        )
                    response = completion.choices[0].message.content
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    break
                except Exception as e:
                    if "rate_limit_exceeded" in str(e) and attempt < 2:
                        continue
                    else:
                        st.error(f"❌ Failed after 3 attempts: {e}")
