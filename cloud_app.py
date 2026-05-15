import streamlit as st
from groq import Groq
import time, requests, re, base64, json, math
from datetime import datetime
import urllib.parse
import xml.etree.ElementTree as ET
from PIL import Image
import io

st.set_page_config(
    page_title="Nova AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    --purple:   #7c3aed;
    --orange:   #f59e0b;
    --red:      #ef4444;
    --pink:     #ec4899;
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
    padding: 0 1.5rem 10rem !important;
    margin: 0 auto !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] .stSelectbox > div,
[data-testid="stSidebar"] .stTextInput > div > div {
    background: var(--surface2) !important;
    border-color: var(--border) !important;
}
[data-testid="stSidebar"] label { color: var(--muted) !important; font-size: 12px !important; }
[data-testid="stSidebar"] h3 {
    color: var(--accent) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 13px !important; margin: .8rem 0 .4rem !important;
}
[data-testid="stSidebar"] hr { border-color: var(--border) !important; }
[data-testid="stSidebar"] .stButton > button {
    width: 100% !important; background: var(--surface2) !important;
    border: 1px solid var(--border) !important; color: var(--muted) !important;
    border-radius: 8px !important; font-size: 12px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    border-color: var(--accent) !important; color: var(--accent) !important;
}
[data-testid="stSidebar"] .stDownloadButton > button {
    width: 100% !important; background: rgba(0,229,255,.08) !important;
    border: 1px solid rgba(0,229,255,.25) !important; color: var(--accent) !important;
    border-radius: 8px !important; font-size: 12px !important;
}
[data-testid="stSidebar"] .stExpander {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important; margin-bottom: .4rem !important;
}

/* ── Hero ── */
.hero { text-align: center; padding: 2.5rem 1rem 1.5rem; position: relative; }
.hero::before {
    content: ''; position: absolute; top: 0; left: 50%;
    transform: translateX(-50%); width: 600px; height: 300px;
    background: radial-gradient(ellipse at center, rgba(0,229,255,.07) 0%, transparent 70%);
    pointer-events: none;
}
.hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(0,229,255,.08); border: 1px solid rgba(0,229,255,.2);
    border-radius: 999px; padding: 4px 14px;
    font-family: 'Space Mono', monospace; font-size: 11px;
    color: var(--accent); letter-spacing: .05em; margin-bottom: 1rem;
}
.hero-badge::before { content: '●'; font-size: 8px; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }
.hero h1 {
    font-family: 'Space Mono', monospace !important;
    font-size: clamp(1.8rem,4vw,2.6rem) !important;
    font-weight: 700 !important; color: #fff !important;
    line-height: 1.15 !important; letter-spacing: -.02em; margin-bottom: .5rem !important;
}
.hero h1 span { color: var(--accent); }
.hero p { font-size: .95rem; color: var(--muted); font-weight: 300; max-width: 460px; margin: 0 auto; }
.divider { height:1px; background:linear-gradient(90deg,transparent,var(--border),transparent); margin:1.2rem 0; }

/* ── Stats ── */
.stats-row { display:flex; gap:.6rem; margin:1rem 0 1.5rem; justify-content:center; flex-wrap:wrap; }
.stat-pill {
    display:flex; align-items:center; gap:6px;
    background:var(--surface); border:1px solid var(--border);
    border-radius:999px; padding:5px 12px; font-size:12px; color:var(--muted);
}
.stat-pill .dot { width:6px; height:6px; border-radius:50%; }
.dot-green  { background:var(--green);  box-shadow:0 0 5px var(--green); }
.dot-blue   { background:var(--accent); box-shadow:0 0 5px var(--accent); }
.dot-purple { background:var(--purple); box-shadow:0 0 5px var(--purple); }
.dot-orange { background:var(--orange); box-shadow:0 0 5px var(--orange); }
.dot-pink   { background:var(--pink);   box-shadow:0 0 5px var(--pink); }

/* ── Chat messages ── */
[data-testid="stChatMessage"] { background:transparent !important; border:none !important; padding:0 !important; }
[data-testid="stChatMessage"] > div { background:transparent !important; }
[data-testid="stChatMessageContent"] { background:transparent !important; }
.stChatMessage {
    border-radius:var(--radius) !important; padding:1rem 1.2rem !important;
    border:1px solid var(--border) !important; margin-bottom:.6rem !important;
    background:var(--surface) !important; animation:fadeUp .25s ease;
}
@keyframes fadeUp { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) {
    background:var(--user-bg) !important; border-color:rgba(0,229,255,.15) !important;
}

/* ── Code ── */
pre, code { font-family:'Space Mono',monospace !important; font-size:13px !important; }
pre {
    background:#0d1117 !important; border:1px solid var(--border) !important;
    border-left:3px solid var(--accent) !important; border-radius:10px !important;
    padding:1rem 1.2rem !important; overflow-x:auto !important;
}
code:not(pre code) {
    background:rgba(0,229,255,.08) !important; color:var(--accent) !important;
    border-radius:5px !important; padding:2px 6px !important; font-size:12.5px !important;
}

/* ══════════════════════════════════════════════════════════
   CHAT INPUT AREA — fixed bottom with image upload button
══════════════════════════════════════════════════════════ */
[data-testid="stChatInputContainer"] {
    position: fixed !important; bottom: 0 !important; left: 50% !important;
    transform: translateX(-50%) !important; width: 100% !important;
    max-width: 860px !important; padding: 0.5rem 1.5rem 1.2rem !important;
    background: linear-gradient(to top, var(--bg) 80%, transparent) !important;
    backdrop-filter: blur(12px); z-index: 999 !important;
}
[data-testid="stChatInput"] {
    background: var(--surface2) !important; border: 1px solid var(--border) !important;
    border-radius: 12px !important; color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 15px !important;
}
[data-testid="stChatInput"]:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(0,229,255,.1) !important; outline: none !important;
}
[data-testid="stChatInputSubmitButton"] button {
    background: var(--accent) !important; border: none !important;
    border-radius: 8px !important; color: #000 !important; font-weight: 600 !important;
}

/* Upload toolbar above chat input */
.upload-toolbar {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 4px;
    margin-bottom: 4px;
    flex-wrap: wrap;
}
.upload-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 999px; padding: 5px 14px;
    font-size: 12px; color: var(--muted);
    cursor: pointer; transition: all .2s;
    font-family: 'DM Sans', sans-serif;
}
.upload-pill:hover { border-color: var(--accent); color: var(--accent); }
.upload-pill.active { 
    border-color: var(--pink); color: var(--pink);
    background: rgba(236,72,153,.08);
}

/* Pending image preview */
.pending-image-box {
    background: var(--surface2);
    border: 1px solid rgba(236,72,153,.4);
    border-radius: 12px;
    padding: 10px 14px;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
    animation: fadeUp .2s ease;
}
.pending-image-thumb {
    width: 48px; height: 48px;
    border-radius: 8px; object-fit: cover;
    border: 1px solid var(--border);
}
.pending-image-info { flex: 1; }
.pending-image-name { font-size: 13px; color: var(--text); font-weight: 500; }
.pending-image-hint { font-size: 11px; color: var(--muted); margin-top: 2px; }

/* Badges */
.badge {
    display:inline-flex; align-items:center; gap:5px;
    border-radius:6px; padding:3px 10px; font-size:11px;
    margin-bottom:.5rem; font-family:'DM Sans',sans-serif;
}
.badge-green  { background:rgba(16,185,129,.08);  border:1px solid rgba(16,185,129,.25); color:var(--green); }
.badge-red    { background:rgba(239,68,68,.08);   border:1px solid rgba(239,68,68,.3);   color:#fca5a5; }
.badge-purple { background:rgba(124,58,237,.08);  border:1px solid rgba(124,58,237,.3);  color:#a78bfa; }
.badge-orange { background:rgba(245,158,11,.08);  border:1px solid rgba(245,158,11,.3);  color:var(--orange); }
.badge-blue   { background:rgba(0,229,255,.08);   border:1px solid rgba(0,229,255,.25);  color:var(--accent); }
.badge-pink   { background:rgba(236,72,153,.08);  border:1px solid rgba(236,72,153,.3);  color:var(--pink); }

/* Result boxes */
.output-box {
    background:#0d1117; border:1px solid var(--border);
    border-left:3px solid var(--green); border-radius:10px;
    padding:.8rem 1.2rem; font-family:'Space Mono',monospace;
    font-size:13px; color:#a3e635; margin-top:.5rem; white-space:pre-wrap;
}
.error-box {
    background:#1a0a0a; border:1px solid #7f1d1d;
    border-left:3px solid var(--red); border-radius:10px;
    padding:.8rem 1.2rem; font-family:'Space Mono',monospace;
    font-size:13px; color:#fca5a5; margin-top:.5rem; white-space:pre-wrap;
}
.result-box {
    background:linear-gradient(135deg,#0d1117,#111827);
    border:1px solid var(--border); border-radius:10px;
    padding:.8rem 1.2rem; font-size:14px; color:var(--text); margin:.5rem 0;
}
.result-box.orange { border-left:3px solid var(--orange); }
.result-box.green  { border-left:3px solid var(--green); }

.btn-download {
    display:inline-flex; align-items:center; gap:5px;
    background:rgba(0,229,255,.1); border:1px solid rgba(0,229,255,.3);
    color:var(--accent); padding:6px 14px; border-radius:8px;
    text-decoration:none; font-size:12px; font-family:'DM Sans',sans-serif;
    font-weight:500; margin-top:.5rem;
}

.stButton > button {
    background:var(--surface2) !important; border:1px solid var(--border) !important;
    color:var(--muted) !important; border-radius:8px !important;
    font-family:'DM Sans',sans-serif !important; font-size:13px !important;
    font-weight:500 !important; padding:.4rem 1rem !important; transition:all .2s !important;
}
.stButton > button:hover {
    border-color:var(--accent) !important; color:var(--accent) !important;
    background:rgba(0,229,255,.06) !important;
}

/* Category grid */
.category-grid {
    display:grid; grid-template-columns:repeat(auto-fit,minmax(155px,1fr));
    gap:.8rem; margin:1.2rem 0;
}
.category-card {
    background:var(--surface); border:1px solid var(--border);
    border-radius:12px; padding:1rem; text-align:center;
    transition:border-color .2s,transform .2s;
}
.category-card:hover { border-color:var(--accent); transform:translateY(-2px); }
.category-icon  { font-size:1.6rem; margin-bottom:.4rem; }
.category-title { font-size:12.5px; font-weight:600; color:#94a3b8; margin-bottom:.2rem; }
.category-examples { font-size:11px; color:var(--muted); line-height:1.6; }

/* Image in chat */
.chat-image {
    max-width: 360px; max-height: 280px;
    border-radius: 12px; border: 1px solid var(--border);
    margin-bottom: 8px; display: block;
    object-fit: cover;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  CLIENT
# ══════════════════════════════════════════════════════════════════════════════
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_KEY = "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"

client       = Groq(api_key=GROQ_KEY)
MODEL        = "llama-3.3-70b-versatile"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
MAX_HISTORY  = 20

# ══════════════════════════════════════════════════════════════════════════════
#  IMAGE PROCESSING
# ══════════════════════════════════════════════════════════════════════════════
def image_to_base64(uploaded_file) -> tuple:
    """Convert uploaded image → base64. Returns (b64, mime, w, h)"""
    try:
        uploaded_file.seek(0)
        img  = Image.open(uploaded_file)
        fmt  = img.format or "PNG"
        mime = f"image/{fmt.lower()}"
        if mime == "image/jpg": mime = "image/jpeg"

        # Resize if too large
        max_size = 1568
        if max(img.size) > max_size:
            ratio    = max_size / max(img.size)
            new_size = (int(img.size[0]*ratio), int(img.size[1]*ratio))
            img      = img.resize(new_size, Image.LANCZOS)

        buf      = io.BytesIO()
        save_fmt = "JPEG" if fmt in ("JPEG","JPG") else "PNG"
        if img.mode in ("RGBA","P") and save_fmt == "JPEG":
            img = img.convert("RGB")
        img.save(buf, format=save_fmt, quality=85)
        buf.seek(0)

        b64  = base64.b64encode(buf.read()).decode()
        mime = f"image/{save_fmt.lower()}"
        return b64, mime, img.size[0], img.size[1]
    except Exception as e:
        return None, None, 0, 0

def get_image_thumbnail_html(b64: str, mime: str, name: str = "") -> str:
    """Return an <img> tag for inline display."""
    return (
        f'<img src="data:{mime};base64,{b64}" '
        f'class="chat-image" alt="{name}" />'
    )

# ══════════════════════════════════════════════════════════════════════════════
#  VISION ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
def get_vision_prompt(user_text: str) -> str:
    q = user_text.lower()
    if any(k in q for k in ["read","text","ocr","extract text","what does it say",
                              "what text","words","written","transcribe"]):
        return f"Read and transcribe ALL text visible in this image exactly as written. Then answer: {user_text}"
    elif any(k in q for k in ["solve","calculate","math","equation","problem","formula"]):
        return f"Solve the math problem shown in this image. Show step-by-step working. {user_text}"
    elif any(k in q for k in ["code","program","script","debug","error","fix","bug"]):
        return f"Read the code in this image exactly. Explain what it does and identify any issues. {user_text}"
    elif any(k in q for k in ["chart","graph","table","data","plot","diagram","statistics"]):
        return f"Analyze this chart/graph/table in detail. Extract all data, trends, and insights. {user_text}"
    elif any(k in q for k in ["ui","design","website","app","interface","layout"]):
        return f"Analyze this UI/UX design. Describe layout, design choices, and suggest improvements. {user_text}"
    elif any(k in q for k in ["translate","language","foreign","hindi","french","chinese"]):
        return f"Read all text in this image and translate it to English. {user_text}"
    elif any(k in q for k in ["document","invoice","receipt","form","certificate","id","card"]):
        return f"Extract all information from this document. Read every field and value carefully. {user_text}"
    elif any(k in q for k in ["food","recipe","ingredients","calories","dish","meal"]):
        return f"Identify this food/dish, describe it, estimate ingredients and calories. {user_text}"
    else:
        return (
            "Analyze this image comprehensively:\n"
            "1. Describe everything you see in detail\n"
            "2. Read any visible text\n"
            "3. Identify objects, colors, patterns\n"
            "4. Note any important details\n\n"
            f"Also answer this specific request: {user_text if user_text.strip() else 'What is in this image?'}"
        )

def analyze_image_stream(b64: str, mime: str, user_prompt: str) -> str:
    """Stream vision model response."""
    placeholder = st.empty()
    full        = ""
    try:
        stream = client.chat.completions.create(
            model    = VISION_MODEL,
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are Nova AI with powerful vision. Created by Samiran. "
                        "Analyze images with exceptional detail and accuracy. "
                        "Read text perfectly (OCR), identify objects, solve problems, "
                        "analyze data, review code, and answer any question about images. "
                        "Be thorough, accurate, and helpful."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime};base64,{b64}"}
                        },
                        {
                            "type": "text",
                            "text": user_prompt
                        }
                    ]
                }
            ],
            max_tokens  = 2048,
            temperature = 0.2,
            stream      = True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                full += delta
                placeholder.markdown(full + "▌")
        placeholder.markdown(full)
        return full
    except Exception as e:
        err = f"❌ Vision error: {e}"
        placeholder.error(err)
        return err

# ══════════════════════════════════════════════════════════════════════════════
#  STREAMING TEXT
# ══════════════════════════════════════════════════════════════════════════════
def stream_response(messages: list, max_tokens: int = 4096,
                    temperature: float = 0.25) -> str:
    full = ""
    box  = st.empty()
    try:
        stream = client.chat.completions.create(
            messages=messages, model=MODEL,
            max_tokens=max_tokens, temperature=temperature, stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                full += delta
                box.markdown(full + "▌")
        box.markdown(full)
        return full
    except Exception as e:
        box.error(f"❌ Error: {e}")
        return ""

# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS & HELPERS
# ══════════════════════════════════════════════════════════════════════════════
CURRENCIES = ["USD","EUR","GBP","INR","JPY","CAD","AUD","CHF","CNY","HKD",
              "SGD","NOK","SEK","DKK","NZD","MXN","BRL","ZAR","RUB","KRW",
              "TRY","AED","SAR","THB","IDR","MYR","PHP","VND","EGP","PKR"]

MODE_PROMPTS = {
    "🤖 Default":  "",
    "💻 Coder":    "CODER MODE: Focus on perfect production-ready code.",
    "🎨 Creative": "CREATIVE MODE: Be imaginative and expressive.",
    "📊 Analyst":  "ANALYST MODE: Be data-driven, precise, use tables.",
    "🎓 Teacher":  "TEACHER MODE: Explain step by step with examples.",
    "✍️ Writer":   "WRITER MODE: Clear, engaging, polished writing.",
}

GAME_KEYWORDS = ["game","snake game","tetris","pacman","flappy bird","2048",
    "tic tac toe","chess","checkers","sudoku","minesweeper","platformer",
    "shooter","puzzle game","card game","memory game","quiz game","breakout",
    "pong","asteroids","space invaders","racing game","rpg","tower defense",
    "clicker game","battle","dungeon","maze","arcade"]
APP_KEYWORDS  = ["app","application","dashboard","admin panel","landing page",
    "portfolio","website","web app","e-commerce","shop","store","blog",
    "chat app","todo app","calculator app","login page","signup","form",
    "expense tracker","budget","note app","kanban","timer","stopwatch",
    "music player","image gallery","calendar","analytics","chart","crm",
    "netflix clone","youtube clone","twitter clone","whatsapp ui"]
SOFTWARE_KEYWORDS = ["software","tool","utility","desktop app","file manager",
    "text editor","password manager","api tester","converter","automation","cli tool"]
DESIGN_KEYWORDS = ["design","ui","ux","mockup","prototype","wireframe",
    "beautiful","modern","stunning","animated","glassmorphism","neumorphism",
    "gradient","dark theme","light theme","component","ui kit","hero section",
    "navbar","sidebar","modal"]

STOCK_ALIASES = {
    "reliance":"RELIANCE.NS","tata":"TATAMOTORS.NS","tcs":"TCS.NS",
    "infosys":"INFY.NS","wipro":"WIPRO.NS","hdfc":"HDFCBANK.NS",
    "icici":"ICICIBANK.NS","sbi":"SBIN.NS","bajaj":"BAJFINANCE.NS",
    "adani":"ADANIENT.NS","nifty":"^NSEI","sensex":"^BSESN",
    "apple":"AAPL","microsoft":"MSFT","google":"GOOGL","amazon":"AMZN",
    "tesla":"TSLA","meta":"META","netflix":"NFLX","nvidia":"NVDA",
    "bitcoin":"BTC-USD","btc":"BTC-USD","ethereum":"ETH-USD","eth":"ETH-USD",
    "dogecoin":"DOGE-USD","doge":"DOGE-USD","solana":"SOL-USD",
    "dow jones":"^DJI","nasdaq":"^IXIC","s&p 500":"^GSPC",
}

SPORTS_MAP = {
    "cricket":"cricket","ipl":"IPL cricket","t20":"T20 cricket",
    "football":"football","soccer":"soccer","premier league":"Premier League",
    "champions league":"UEFA Champions League","world cup":"FIFA World Cup",
    "basketball":"basketball","nba":"NBA basketball","tennis":"tennis",
    "badminton":"badminton","hockey":"hockey","formula 1":"Formula 1",
    "f1":"F1 race","boxing":"boxing","mma":"MMA UFC","ufc":"UFC",
    "olympics":"Olympics","kabaddi":"kabaddi",
}
IPL_TEAMS = ["csk","mi","rcb","kkr","srh","pbks","dc","gt","lsg","rr",
             "chennai","mumbai","bangalore","kolkata","hyderabad",
             "punjab","delhi","gujarat","lucknow","rajasthan"]

LANGUAGE_MAP = {
    "python":("python","3.10.0"),
    "javascript":("javascript","18.15.0"),"js":("javascript","18.15.0"),
    "typescript":("typescript","5.0.3"),"java":("java","15.0.2"),
    "c++":("c++","10.2.0"),"cpp":("c++","10.2.0"),"c":("c","10.2.0"),
    "rust":("rust","1.68.2"),"go":("go","1.16.2"),"ruby":("ruby","3.0.1"),
    "php":("php","8.2.3"),"swift":("swift","5.3.3"),"kotlin":("kotlin","1.8.20"),
    "r":("r","4.1.1"),"bash":("bash","5.2.0"),"shell":("bash","5.2.0"),
    "sql":("sqlite3","3.36.0"),"lua":("lua","5.4.4"),"scala":("scala","3.2.2"),
}

SEARCH_TRIGGERS = [
    "who is","who was","who won","who are","what is","what was","what happened",
    "when is","when was","where is","current","latest","recent","today",
    "election","prime minister","president","chief minister","cm of",
    "winner","champion","result","2024","2025","2026",
]

def today_str(): return datetime.now().strftime("%B %d, %Y")

# ── Weather ───────────────────────────────────────────────────────────────────
def get_weather(city):
    try:
        r = requests.get(f"https://wttr.in/{requests.utils.quote(city)}?format=j1",
                         headers={"User-Agent":"Mozilla/5.0"}, timeout=8)
        d = r.json(); c = d["current_condition"][0]; a = d["nearest_area"][0]
        return (f"City: {a['areaName'][0]['value']}, {a['country'][0]['value']}\n"
                f"Temperature: {c['temp_C']}°C (Feels like {c['FeelsLikeC']}°C)\n"
                f"Condition: {c['weatherDesc'][0]['value']}\n"
                f"Humidity: {c['humidity']}%\nWind Speed: {c['windspeedKmph']} km/h\n"
                f"Visibility: {c['visibility']} km\nUV Index: {c['uvIndex']}")
    except Exception as e: return f"failed:{e}"

def extract_city(q):
    m = re.search(r"(?:weather|temperature|forecast|humidity|climate)\s+(?:report\s+)?(?:in|for|of|at)\s+([A-Za-z ,]+?)(?:\?|$)",q,re.IGNORECASE)
    if m: return m.group(1).strip().rstrip(",")
    sw = {"what","is","the","weather","report","temperature","forecast","today",
          "current","now","like","how","give","me","show","humidity","climate","condition","a","an"}
    return " ".join(w for w in q.replace("?","").split() if w.lower() not in sw).strip() or "Guwahati"

def is_weather_query(q):
    return any(k in q.lower() for k in ["weather","temperature","forecast","humidity","rain","sunny","cloudy","wind speed"])

# ── Stocks ────────────────────────────────────────────────────────────────────
def get_stock(symbol, dname):
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=2d",
                         headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"},timeout=8)
        m = r.json()["chart"]["result"][0]["meta"]
        price=m.get("regularMarketPrice",0); prev=m.get("chartPreviousClose",0)
        curr=m.get("currency","USD"); name=m.get("longName") or m.get("shortName") or dname
        chg=price-prev; pct=(chg/prev*100) if prev else 0
        arrow="🟢 ▲" if chg>=0 else "🔴 ▼"; sign="+" if chg>=0 else ""
        vol=m.get("regularMarketVolume","N/A")
        if isinstance(vol,int): vol=f"{vol:,}"
        return (f"Name: {name}\nExchange: {m.get('exchangeName','')}\nPrice: {curr} {price:,.2f}\n"
                f"Change: {arrow} {sign}{chg:.2f} ({sign}{pct:.2f}%)\n"
                f"Day High: {m.get('regularMarketDayHigh','N/A')}\nDay Low: {m.get('regularMarketDayLow','N/A')}\n"
                f"Volume: {vol}\nMarket: {m.get('marketState','')}")
    except Exception as e: return f"failed:{e}"

def extract_stock_symbol(q):
    ql=q.lower()
    for name,ticker in STOCK_ALIASES.items():
        if name in ql: return ticker,name.title()
    m=re.search(r"\b([A-Z]{2,5})\b",q)
    if m: return m.group(1),m.group(1)
    return None,None

def is_stock_query(q):
    ql=q.lower()
    return (any(a in ql for a in ["stock","share price","stock price","price of","market price",
                                   "trading at","crypto","bitcoin","ethereum","sensex","nifty",
                                   "nasdaq","dow jones","coin price"]) or
            any(k in ql for k in STOCK_ALIASES))

# ── Sports ────────────────────────────────────────────────────────────────────
def fetch_live_cricket():
    results=[]
    try:
        r=requests.get("https://api.cricapi.com/v1/currentMatches",
                       params={"apikey":"a52ea237-09e7-4d69-b7cc-e4f0e2a8c1f1","offset":0},timeout=6)
        data=r.json()
        if data.get("status")=="success" and data.get("data"):
            for m in data["data"][:5]:
                scores=""
                for s in m.get("score",[]):
                    if s.get("r"): scores+=f"\n  {s.get('inning','')}: {s.get('r','')}/{s.get('w','')} ({s.get('o','')} ov)"
                results.append(f"**{m.get('name','')}**\n  {m.get('status','')}{scores}")
    except: pass
    for sq in [f"IPL 2025 today match {datetime.now().strftime('%B %d')} live score","IPL 2025 match playing today"]:
        try:
            r=requests.get(f"https://news.google.com/rss/search?q={requests.utils.quote(sq)}&hl=en-IN&gl=IN&ceid=IN:en",
                           headers={"User-Agent":"Mozilla/5.0"},timeout=6)
            root=ET.fromstring(r.content); items=[]
            for item in root.findall(".//item")[:5]:
                title=item.findtext("title","").strip()
                pub=item.findtext("pubDate","")[:22] if item.findtext("pubDate","") else ""
                if title:
                    clean=title.split(" - ")[0].strip()
                    items.append(f"[{pub}] {clean}" if pub else clean)
            if items: results.append("📰 "+" \n".join(items))
        except: pass
    return "\n\n".join(results) if results else ""

def get_sports_news(term):
    try:
        r=requests.get(f"https://news.google.com/rss/search?q={requests.utils.quote(term+' score result today')}&hl=en&gl=US&ceid=US:en",
                       headers={"User-Agent":"Mozilla/5.0"},timeout=8)
        root=ET.fromstring(r.content); out=[]
        for item in root.findall(".//item")[:7]:
            title=item.findtext("title","").strip()
            if title:
                clean=title.split(" - ")[0].strip()
                src=title.split(" - ")[-1].strip() if " - " in title else ""
                out.append(f"• **{clean}**"+(f" _{src}_" if src else ""))
        return "\n".join(out) if out else "No recent updates."
    except Exception as e: return f"failed:{e}"

def is_sports_query(q):
    ql=q.lower()
    if any(p in ql for p in ["who made you","history of","rules of","how to play"]): return False
    if any(t in ql for t in IPL_TEAMS): return True
    actions=["score","result","match","game","live","standings","winner","champion",
             "playoff","final","tournament","who won","playing today","which team","schedule"]
    sports=list(SPORTS_MAP.keys())
    return (any(re.search(r"\b"+re.escape(a)+r"\b",ql) for a in actions) and
            any(re.search(r"\b"+re.escape(s)+r"\b",ql) for s in sports))

# ── News ──────────────────────────────────────────────────────────────────────
def get_news(topic="India"):
    try:
        r=requests.get(f"https://news.google.com/rss/search?q={requests.utils.quote(topic)}&hl=en-IN&gl=IN&ceid=IN:en",
                       headers={"User-Agent":"Mozilla/5.0"},timeout=8)
        root=ET.fromstring(r.content); out=[]
        for item in root.findall(".//item")[:6]:
            title=item.findtext("title","").strip()
            if title:
                clean=title.split(" - ")[0].strip()
                src=title.split(" - ")[-1].strip() if " - " in title else "News"
                out.append(f"• **{clean}** _{src}_")
        return "\n".join(out) if out else "No news found."
    except Exception as e: return f"failed:{e}"

def is_news_query(q):
    return any(k in q.lower() for k in ["news","headlines","latest news","today news","breaking","top news","what happened today"])

def extract_news_topic(q):
    sw={"news","latest","today","show","me","give","what","is","the","headlines","breaking","top","current","about","on"}
    return " ".join(w for w in q.replace("?","").split() if w.lower() not in sw).strip() or "India"

# ── Web search ────────────────────────────────────────────────────────────────
def web_search(q):
    try:
        r=requests.get(f"https://html.duckduckgo.com/html/?q={requests.utils.quote(q)}",
                       headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"},timeout=10)
        snips=re.findall(r'class="result__snippet"[^>]*>(.*?)</(?:a|span)>',r.text,re.DOTALL)
        titles=re.findall(r'class="result__title"[^>]*>.*?<a[^>]*>(.*?)</a>',r.text,re.DOTALL)
        cs=[re.sub(r"<[^>]+>","",s).strip() for s in snips[:5]]
        ct=[re.sub(r"<[^>]+>","",t).strip() for t in titles[:5]]
        results=[f"• {t}: {s}" for t,s in zip(ct,cs) if s]
        if results: return "\n".join(results)
        r2=requests.get("https://api.duckduckgo.com/",params={"q":q,"format":"json","no_html":"1","skip_disambig":"1"},timeout=8)
        data=r2.json(); parts=[]
        if data.get("Answer"): parts.append(data["Answer"])
        if data.get("Abstract"): parts.append(data["Abstract"][:500])
        for t in data.get("RelatedTopics",[])[:3]:
            if isinstance(t,dict) and t.get("Text"): parts.append(t["Text"][:200])
        return "\n".join(parts) if parts else "No results."
    except Exception as e: return f"Search failed:{e}"

def get_current_facts(q):
    try:
        r=requests.get(f"https://news.google.com/rss/search?q={requests.utils.quote(q)}&hl=en-IN&gl=IN&ceid=IN:en",
                       headers={"User-Agent":"Mozilla/5.0"},timeout=8)
        root=ET.fromstring(r.content); out=[]
        for item in root.findall(".//item")[:5]:
            title=item.findtext("title","").strip()
            pub=item.findtext("pubDate","")[:22] if item.findtext("pubDate","") else ""
            if title:
                clean=title.split(" - ")[0].strip()
                out.append(f"[{pub}] {clean}" if pub else clean)
        return "\n".join(out) if out else ""
    except: return ""

def needs_search(q):
    ql=q.lower()
    if any(k in ql for k in ["who made you","who created you","who are you"]): return False
    skip=GAME_KEYWORDS+APP_KEYWORDS+SOFTWARE_KEYWORDS+DESIGN_KEYWORDS
    if any(k in ql for k in skip): return False
    if is_sports_query(q): return False
    return any(t in ql for t in SEARCH_TRIGGERS)

# ── Math ──────────────────────────────────────────────────────────────────────
def solve_math(expr):
    try:
        e=re.sub(r"(calculate|compute|solve|evaluate|what is|how much is|=)","",expr,flags=re.IGNORECASE).strip()
        e=re.sub(r"[?!]","",e).replace("^","**").strip()
        safe={"sin":math.sin,"cos":math.cos,"tan":math.tan,"asin":math.asin,
              "acos":math.acos,"atan":math.atan,"log":math.log10,"ln":math.log,
              "log2":math.log2,"sqrt":math.sqrt,"exp":math.exp,"abs":abs,
              "pi":math.pi,"e":math.e,"ceil":math.ceil,"floor":math.floor,
              "round":round,"pow":math.pow,"factorial":math.factorial}
        result=eval(e,{"__builtins__":{}},safe)
        if isinstance(result,float): result=round(result,10)
        return str(result)
    except: return ""

def is_math_query(q):
    ql=q.lower()
    if any(k in ql for k in ["stock","weather","ipl","cricket","news","price","convert","currency"]): return False
    triggers=["calculate","compute","sqrt","factorial","sin","cos","tan","log"]
    return bool(re.search(r"\d",q)) and (bool(re.search(r"[+\-*/^%()]",q)) or any(t in ql for t in triggers))

# ── Currency ──────────────────────────────────────────────────────────────────
def get_exchange_rate(fc,tc,amount=1.0):
    try:
        r=requests.get(f"https://api.exchangerate-api.com/v4/latest/{fc.upper()}",timeout=6)
        data=r.json(); rates=data.get("rates",{})
        if tc.upper() not in rates: return f"❌ Currency '{tc}' not found."
        rate=rates[tc.upper()]; result=amount*rate
        return (f"**{amount:,.2f} {fc.upper()}** = **{result:,.4f} {tc.upper()}**\n\n"
                f"Rate: 1 {fc.upper()} = {rate:.6f} {tc.upper()}\n"
                f"_Updated: {data.get('date','today')} · ExchangeRate-API_")
    except Exception as e: return f"Currency fetch failed: {e}"

def is_currency_query(q):
    ql=q.lower(); curr=[c.lower() for c in CURRENCIES]
    trig=["convert","exchange rate","to inr","to usd","to eur","to gbp","in dollars","in rupees"]
    found=sum(1 for c in curr if re.search(r"\b"+c+r"\b",ql))
    return found>=2 or (any(t in ql for t in trig) and found>=1)

def extract_currency_params(q):
    ql=q.lower(); curr=[c.lower() for c in CURRENCIES]
    found=[c for c in curr if re.search(r"\b"+c+r"\b",ql)]
    am=re.search(r"(\d+(?:\.\d+)?)",q)
    amount=float(am.group(1)) if am else 1.0
    if len(found)>=2: return amount,found[0].upper(),found[1].upper()
    if len(found)==1:
        other="INR" if found[0]!="inr" else "USD"
        return amount,found[0].upper(),other
    return 1.0,"USD","INR"

# ── Unit converter ────────────────────────────────────────────────────────────
UNIT_MAP={
    ("celsius","fahrenheit"):lambda x:(x*9/5)+32,("fahrenheit","celsius"):lambda x:(x-32)*5/9,
    ("celsius","kelvin"):lambda x:x+273.15,("kelvin","celsius"):lambda x:x-273.15,
    ("km","miles"):lambda x:x*0.621371,("miles","km"):lambda x:x*1.60934,
    ("meters","feet"):lambda x:x*3.28084,("feet","meters"):lambda x:x/3.28084,
    ("cm","inches"):lambda x:x*0.393701,("inches","cm"):lambda x:x*2.54,
    ("kg","pounds"):lambda x:x*2.20462,("pounds","kg"):lambda x:x/2.20462,
    ("kg","grams"):lambda x:x*1000,("grams","kg"):lambda x:x/1000,
    ("kmh","mph"):lambda x:x*0.621371,("mph","kmh"):lambda x:x*1.60934,
    ("liters","gallons"):lambda x:x*0.264172,("gallons","liters"):lambda x:x*3.78541,
    ("gb","mb"):lambda x:x*1024,("mb","gb"):lambda x:x/1024,
    ("tb","gb"):lambda x:x*1024,("gb","tb"):lambda x:x/1024,
}

def convert_unit(q):
    ql=q.lower(); am=re.search(r"(\d+(?:\.\d+)?)",q)
    amount=float(am.group(1)) if am else 1.0
    for (fu,tu),fn in UNIT_MAP.items():
        if fu in ql and tu in ql: return f"**{amount} {fu}** = **{round(fn(amount),6)} {tu}**"
    return ""

def is_unit_query(q):
    ql=q.lower()
    units=["km","miles","meters","feet","cm","inches","kg","pounds","grams",
           "celsius","fahrenheit","kelvin","liters","gallons","mph","kmh","gb","mb","tb"]
    trig=["convert","how many","how much","to","equals"]
    return any(u in ql for u in units) and any(t in ql for t in trig) and bool(re.search(r"\d",q))

# ── QR ────────────────────────────────────────────────────────────────────────
def qr_url(text): return f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(text)}"
def is_qr_query(q): return any(k in q.lower() for k in ["qr code","qr for","generate qr","make qr","create qr"])
def extract_qr_content(q):
    m=re.search(r"https?://\S+",q)
    if m: return m.group(0)
    sw={"qr","code","generate","make","create","for","me","a","an","the","of","my"}
    return " ".join(w for w in q.replace("?","").split() if w.lower() not in sw).strip() or q

# ── File reader ───────────────────────────────────────────────────────────────
def read_uploaded_file(f):
    try:
        name=f.name.lower()
        if name.endswith((".txt",".md",".py",".js",".ts",".html",".css",".java",".cpp",".c",".rs",".go")):
            return f.read().decode("utf-8",errors="ignore")[:5000]
        elif name.endswith(".csv"):
            content=f.read().decode("utf-8",errors="ignore"); lines=content.split("\n")
            return f"CSV — {len(lines)} rows\n\nFirst 50 rows:\n"+"\n".join(lines[:50])
        elif name.endswith(".json"):
            content=f.read().decode("utf-8",errors="ignore")
            try: return "JSON:\n"+json.dumps(json.loads(content),indent=2)[:4000]
            except: return content[:4000]
        else: return f"File: {f.name}"
    except Exception as e: return f"File read error: {e}"

# ── URL reader ────────────────────────────────────────────────────────────────
def fetch_url_content(url):
    try:
        r=requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=10)
        text=r.text
        for tag in ["script","style","nav","footer","header","aside"]:
            text=re.sub(f"<{tag}[^>]*>[\\s\\S]*?</{tag}>","",text,flags=re.IGNORECASE)
        text=re.sub(r"<[^>]+>"," ",text); text=re.sub(r"\s+"," ",text).strip()
        return text[:4000] if len(text)>100 else "Could not extract content."
    except Exception as e: return f"URL fetch failed: {e}"

def is_url_query(q): return bool(re.search(r"https?://\S+",q))
def extract_url(q):
    m=re.search(r"https?://\S+",q)
    return m.group(0).rstrip(".,)>") if m else ""

# ── Export ────────────────────────────────────────────────────────────────────
def export_md():
    lines=["# Nova AI — Chat Export",f"_Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n---\n"]
    for m in st.session_state.messages:
        role="🧑 You" if m["role"]=="user" else "✨ Nova AI"
        content=re.sub(r"<[^>]+>","",m["content"]).strip()
        lines.append(f"### {role}\n{content}\n")
    return "\n".join(lines)

def export_json_chat():
    return json.dumps([{"role":m["role"],"content":re.sub(r"<[^>]+>","",m["content"]).strip()}
                       for m in st.session_state.messages],indent=2,ensure_ascii=False)

# ── Creation ──────────────────────────────────────────────────────────────────
def classify_creation(q):
    ql=q.lower()
    if any(k in ql for k in GAME_KEYWORDS): return "game"
    if any(k in ql for k in APP_KEYWORDS): return "app"
    if any(k in ql for k in SOFTWARE_KEYWORDS): return "software"
    if any(k in ql for k in DESIGN_KEYWORDS): return "design"
    if is_code_query(q): return "code"
    return "general"

def is_code_query(q):
    ql=q.lower()
    if is_stock_query(q) or is_weather_query(q): return False
    return any(t in ql for t in ["write","code","program","script","function","implement",
        "create","build","develop","make","generate","algorithm","sort","search","fibonacci",
        "factorial","prime","reverse","palindrome","linked list","binary tree","api","flask",
        "django","react","html","css","sql query","regex","class","oop","recursion","debug","fix","bug","solve"])

def get_badge(ct):
    return {"game":'<div class="badge badge-blue">🎮 World-class game</div>',
            "app":'<div class="badge badge-orange">🚀 Professional app</div>',
            "software":'<div class="badge badge-orange">⚙️ Production software</div>',
            "design":'<div class="badge badge-blue">✨ Stunning design</div>',
            "code":'<div class="badge badge-purple">💻 World-class code</div>',
            "general":""}.get(ct,"")

def get_spinner_text(ct):
    return {"game":"🎮 Building your game…","app":"🚀 Building your app…",
            "software":"⚙️ Engineering software…","design":"✨ Crafting design…",
            "code":"💻 Writing world-class code…","general":"✨ Thinking…"}.get(ct,"✨ Thinking…")

def get_system_prompt(ct):
    mode=st.session_state.get("ai_mode","🤖 Default")
    mode_extra=MODE_PROMPTS.get(mode,""); td=today_str()
    base=(f"You are Nova AI — world's BEST AI assistant with vision, created by Samiran. "
          f"Today: {td}. If asked who made you: 'Nova AI, created by Samiran.' "
          f"Never mention Meta, Llama, OpenAI, Groq. Full conversation memory. "
          f"NEVER write partial code. ALWAYS complete implementations. "
          f"Do NOT generate images — you can ANALYZE images but not create them. "
          f"{mode_extra}\n\n"
          f"LIVE DATA: When real-time data provided, use as ABSOLUTE TRUTH. "
          f"Answer directly. NEVER redirect to external sites. Today is {td}.\n\n")
    if ct=="game":
        return base+"GAME DEV: ONE COMPLETE HTML5 game in single ```html block. Canvas 60fps, score/highscore, start/gameover screens, Web Audio sounds, keyboard+touch controls, particles, neon dark theme."
    elif ct=="app":
        return base+"APP DEV: ONE COMPLETE app in single ```html block. Google Fonts, Font Awesome CDN, glassmorphism, full CRUD, localStorage, toast notifications, responsive."
    elif ct in ("software","design"):
        return base+"ONE COMPLETE stunning implementation in single ```html block. Aurora gradients, animations, glassmorphism, fully functional."
    else:
        return base+"COMPLETE working code always. Best practices. All languages. For facts: use provided search data as primary source."

def build_messages(user_query, search_results="", ct="general"):
    messages=[{"role":"system","content":get_system_prompt(ct)}]
    history=st.session_state.messages[:-1]
    if len(history)>MAX_HISTORY*2: history=history[-(MAX_HISTORY*2):]
    for msg in history:
        content=re.sub(r"<div[^>]*>.*?</div>","",msg["content"],flags=re.DOTALL)
        content=re.sub(r"<[^>]+>","",content).strip()
        if content: messages.append({"role":msg["role"],"content":content[:3000]})
    if search_results:
        user_content=(f"=== LIVE DATA ({today_str()}) ===\n{search_results}\n\n"
                      f"=== QUESTION ===\n{user_query}\nAnswer directly using live data.")
    else:
        user_content=user_query
    messages.append({"role":"user","content":user_content[:5000]})
    return messages

def run_code(code,lang):
    try:
        l,v=LANGUAGE_MAP.get(lang.lower(),("python","3.10.0"))
        r=requests.post("https://emkc.org/api/v2/piston/execute",
                        json={"language":l,"version":v,"files":[{"name":f"main.{lang[:3]}","content":code}],
                              "stdin":"","args":[],"compile_timeout":10000,"run_timeout":5000},timeout=15)
        result=r.json(); run=result.get("run",{})
        out=run.get("stdout","").strip(); err=run.get("stderr","").strip()
        comp=result.get("compile",{}).get("stderr","").strip()
        if comp: return f"❌ Compile Error:\n{comp}"
        if err:  return f"❌ Error:\n{err}"
        return out or "✅ Ran successfully (no output)"
    except Exception as e: return f"❌ Runner failed: {e}"

def extract_code_blocks(text):
    matches=re.findall(r"```(\w+)?\n([\s\S]*?)```",text)
    return [(lang.lower() if lang else "text",code.strip()) for lang,code in matches]

def build_html_preview(blocks):
    html_part=css_part=js_part=full_html=""
    for lang,code in blocks:
        if lang=="html":
            if "<!doctype" in code.lower() or "<html" in code.lower(): full_html=code
            else: html_part=code
        elif lang=="css": css_part=code
        elif lang in ("javascript","js"): js_part=code
    if full_html: return full_html
    if html_part or css_part or js_part:
        return (f"<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'>"
                f"<meta name='viewport' content='width=device-width,initial-scale=1.0'>"
                f"<title>Nova AI</title><style>{css_part}</style></head>"
                f"<body>{html_part}<script>{js_part}</script></body></html>")
    return ""

# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for key,default in [
    ("messages",[]),("temperature",0.25),("max_tokens",4096),
    ("ai_mode","🤖 Default"),("uploaded_file_content",None),
    ("uploaded_file_name",None),("pending_image_b64",None),
    ("pending_image_mime",None),("pending_image_name",None),
    ("show_image_uploader",False),("show_file_uploader",False),
]:
    if key not in st.session_state: st.session_state[key]=default

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR  (settings only — no file upload here)
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1.2rem 0 .8rem'>
        <div style='font-size:1.4rem;font-weight:700;font-family:Space Mono,monospace;color:#00e5ff'>✨ Nova AI</div>
        <div style='font-size:11px;color:#64748b;margin-top:.3rem'>Created by Samiran · v4.0</div>
    </div>""", unsafe_allow_html=True)
    st.divider()

    st.markdown("### ⚙️ Model Settings")
    st.session_state["temperature"]=st.slider("Temperature",0.0,1.0,
        value=st.session_state["temperature"],step=0.05,help="Low=factual | High=creative")
    st.session_state["max_tokens"]=st.select_slider("Max Length",
        options=[512,1024,2048,4096,8192],value=st.session_state["max_tokens"])
    st.divider()

    st.markdown("### 🎭 AI Mode")
    st.session_state["ai_mode"]=st.selectbox("Mode",list(MODE_PROMPTS.keys()),
        index=0,label_visibility="collapsed")
    st.divider()

    st.markdown("### 🛠️ Quick Tools")
    with st.expander("💱 Currency"):
        amt=st.number_input("Amount",value=1.0,min_value=0.0,key="sb_amt")
        c1,c2=st.columns(2)
        with c1: fc=st.selectbox("From",CURRENCIES,index=0,key="sb_fc")
        with c2: tc=st.selectbox("To",CURRENCIES,index=3,key="sb_tc")
        if st.button("Convert 💱",key="sb_conv"): st.markdown(get_exchange_rate(fc,tc,amt))

    with st.expander("📐 Units"):
        uin=st.text_input("e.g. 100 km to miles",key="sb_uin")
        if st.button("Convert 📐",key="sb_unit"):
            res=convert_unit(uin)
            st.markdown(res if res else "⚠️ Try: '100 km to miles'")

    with st.expander("🔢 Calculator"):
        cin=st.text_input("e.g. sqrt(144)",key="sb_cin")
        if st.button("Calculate 🔢",key="sb_calc"):
            res=solve_math(cin)
            if res: st.markdown(f"**= {res}**")
            else: st.warning("Could not evaluate.")

    with st.expander("📱 QR Code"):
        qin=st.text_input("Text or URL",key="sb_qin")
        if st.button("Generate QR",key="sb_qr") and qin:
            url=qr_url(qin)
            st.image(url,width=180)
            st.markdown(f"[⬇️ Download]({url})")

    st.divider()
    st.markdown("### 💾 Export")
    if st.session_state["messages"]:
        ca,cb=st.columns(2)
        ts=datetime.now().strftime("%Y%m%d_%H%M")
        with ca: st.download_button("📝 MD",data=export_md(),file_name=f"nova_{ts}.md",mime="text/markdown",use_container_width=True)
        with cb: st.download_button("📊 JSON",data=export_json_chat(),file_name=f"nova_{ts}.json",mime="application/json",use_container_width=True)
    else: st.caption("No messages yet.")
    st.divider()
    st.markdown(f"<div style='text-align:center;font-size:10px;color:#374151'>Nova AI · Samiran · v4.0<br>{datetime.now().strftime('%B %Y')}</div>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-badge">LIVE · FREE · UNLIMITED · VISION AI</div>
    <h1>Nova<span> AI</span></h1>
    <p>The world's smartest AI — sees images, builds apps, knows everything live.</p>
</div>
<div class="stats-row">
    <div class="stat-pill"><span class="dot dot-purple"></span>🧠 Memory</div>
    <div class="stat-pill"><span class="dot dot-pink"></span>👁️ Vision AI</div>
    <div class="stat-pill"><span class="dot dot-blue"></span>🏏 Live Sports</div>
    <div class="stat-pill"><span class="dot dot-orange"></span>🎮 Games & Apps</div>
    <div class="stat-pill"><span class="dot dot-green"></span>📁 Files & URLs</div>
    <div class="stat-pill"><span class="dot dot-green"></span>💱 Live Data</div>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

# Toolbar
col1,col2,col3=st.columns([5,1,1])
with col2:
    count=len([m for m in st.session_state.messages if m["role"]=="user"])
    st.markdown(f"<p style='text-align:right;color:var(--muted);font-size:12px;padding-top:.5rem'>{count} msg{'s' if count!=1 else ''}</p>",unsafe_allow_html=True)
with col3:
    if st.button("🗑️ Clear"): st.session_state.messages=[]; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  CHAT HISTORY
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center;padding:1rem 1rem .5rem">
        <div style="font-size:2rem;margin-bottom:.5rem">✨</div>
        <p style="font-size:.95rem;font-weight:600;color:#94a3b8;margin-bottom:1rem">What would you like to do today?</p>
    </div>
    <div class="category-grid">
        <div class="category-card"><div class="category-icon">👁️</div><div class="category-title">Vision AI</div><div class="category-examples">Click 📎 below<br>Upload any image<br>AI reads & analyzes</div></div>
        <div class="category-card"><div class="category-icon">🎮</div><div class="category-title">Games</div><div class="category-examples">Snake · Tetris<br>Chess · 2048<br>Pacman · RPG</div></div>
        <div class="category-card"><div class="category-icon">🚀</div><div class="category-title">Apps</div><div class="category-examples">Dashboard · Todo<br>E-commerce<br>Portfolio</div></div>
        <div class="category-card"><div class="category-icon">💻</div><div class="category-title">Code</div><div class="category-examples">Python · JS · Java<br>C++ · Go · Rust<br>SQL & more</div></div>
        <div class="category-card"><div class="category-icon">📁</div><div class="category-title">Files</div><div class="category-examples">Click 📄 below<br>CSV · JSON · Code<br>AI analyzes it</div></div>
        <div class="category-card"><div class="category-icon">🌐</div><div class="category-title">Live Data</div><div class="category-examples">Cricket · Stocks<br>Weather · News<br>Any URL</div></div>
    </div>
    <div class="divider"></div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("meta"):
                st.markdown(msg["meta"],unsafe_allow_html=True)
            # Show image inline if this message had one
            if msg.get("image_b64") and msg.get("image_mime"):
                try:
                    img_bytes=base64.b64decode(msg["image_b64"])
                    img=Image.open(io.BytesIO(img_bytes))
                    st.image(img,caption=msg.get("image_name","Uploaded image"),width=350)
                except: pass
            st.markdown(msg["content"])

# ══════════════════════════════════════════════════════════════════════════════
#  BOTTOM INPUT AREA  — image + file upload buttons ABOVE chat input
# ══════════════════════════════════════════════════════════════════════════════

# Show pending image preview above input
if st.session_state.get("pending_image_b64"):
    fname = st.session_state.get("pending_image_name","image")
    # Decode and show thumbnail
    try:
        img_bytes = base64.b64decode(st.session_state["pending_image_b64"])
        img       = Image.open(io.BytesIO(img_bytes))
        col_img, col_info, col_x = st.columns([1,5,1])
        with col_img:
            st.image(img, width=56)
        with col_info:
            st.markdown(
                f"<div style='padding-top:8px'>"
                f"<div style='font-size:13px;color:#e2e8f0;font-weight:500'>🖼️ {fname}</div>"
                f"<div style='font-size:11px;color:#64748b'>Ready · Type your question below ↓</div>"
                f"</div>",
                unsafe_allow_html=True
            )
        with col_x:
            if st.button("✕", key="clear_pending_img"):
                st.session_state["pending_image_b64"]  = None
                st.session_state["pending_image_mime"] = None
                st.session_state["pending_image_name"] = None
                st.rerun()
    except: pass

# Show pending file preview
if st.session_state.get("uploaded_file_content"):
    fname = st.session_state.get("uploaded_file_name","file")
    col_fi, col_fx = st.columns([8,1])
    with col_fi:
        st.markdown(
            f'<div class="badge badge-purple" style="margin:4px 0">📁 {fname} — Ask me anything about this file</div>',
            unsafe_allow_html=True
        )
    with col_fx:
        if st.button("✕", key="clear_pending_file"):
            st.session_state["uploaded_file_content"] = None
            st.session_state["uploaded_file_name"]    = None
            st.rerun()

# ── Upload toolbar row ─────────────────────────────────────────────────────────
st.markdown('<div class="upload-toolbar">', unsafe_allow_html=True)

tb_col1, tb_col2, tb_col3, tb_col4 = st.columns([1,1,1,6])

with tb_col1:
    img_btn_label = "🖼️ Image" if not st.session_state.get("pending_image_b64") else "🖼️ ✓"
    if st.button(img_btn_label, key="toggle_img_upload",
                 help="Upload an image for AI to analyze"):
        st.session_state["show_image_uploader"] = not st.session_state["show_image_uploader"]
        st.session_state["show_file_uploader"]  = False
        st.rerun()

with tb_col2:
    file_btn_label = "📄 File" if not st.session_state.get("uploaded_file_content") else "📄 ✓"
    if st.button(file_btn_label, key="toggle_file_upload",
                 help="Upload a file for AI to analyze"):
        st.session_state["show_file_uploader"]  = not st.session_state["show_file_uploader"]
        st.session_state["show_image_uploader"] = False
        st.rerun()

with tb_col3:
    if st.button("❓ Help", key="show_help", help="What can Nova AI do?"):
        st.session_state["show_image_uploader"] = False
        st.session_state["show_file_uploader"]  = False

st.markdown('</div>', unsafe_allow_html=True)

# ── Image uploader panel ───────────────────────────────────────────────────────
if st.session_state.get("show_image_uploader"):
    st.markdown("""
    <div style='background:#1a1d24;border:1px solid #232730;border-radius:14px;
                padding:1.2rem;margin-bottom:.5rem;'>
        <div style='font-size:13px;color:#00e5ff;font-weight:600;margin-bottom:.5rem'>
            👁️ Upload Image for Vision AI
        </div>
        <div style='font-size:11px;color:#64748b;margin-bottom:.8rem'>
            Supports: JPG, PNG, GIF, BMP, WebP, TIFF
        </div>
    </div>
    """, unsafe_allow_html=True)

    img_file = st.file_uploader(
        "Choose image",
        type=["jpg","jpeg","png","gif","bmp","webp","tiff"],
        key="main_img_upload",
        label_visibility="collapsed"
    )

    if img_file is not None:
        # Process immediately
        b64, mime, w, h = image_to_base64(img_file)
        if b64:
            st.session_state["pending_image_b64"]  = b64
            st.session_state["pending_image_mime"] = mime
            st.session_state["pending_image_name"] = img_file.name
            st.session_state["show_image_uploader"]= False

            # Show preview
            col_prev, col_info = st.columns([1,2])
            with col_prev:
                img_bytes = base64.b64decode(b64)
                preview   = Image.open(io.BytesIO(img_bytes))
                st.image(preview, width=120)
            with col_info:
                st.success(f"✅ {img_file.name}")
                st.caption(f"Size: {w}×{h}px · {mime}")
                st.info("Now type your question in the chat below!")
        else:
            st.error("❌ Could not process image. Try a different format.")

    # Example prompts
    st.markdown("""
    <div style='margin-top:.8rem'>
        <div style='font-size:11px;color:#64748b;margin-bottom:.4rem'>💡 Example questions:</div>
        <div style='display:flex;flex-wrap:wrap;gap:6px'>
            <span style='background:#1a1d24;border:1px solid #232730;border-radius:999px;
                         padding:3px 10px;font-size:11px;color:#94a3b8'>What is in this image?</span>
            <span style='background:#1a1d24;border:1px solid #232730;border-radius:999px;
                         padding:3px 10px;font-size:11px;color:#94a3b8'>Read the text</span>
            <span style='background:#1a1d24;border:1px solid #232730;border-radius:999px;
                         padding:3px 10px;font-size:11px;color:#94a3b8'>Solve this math</span>
            <span style='background:#1a1d24;border:1px solid #232730;border-radius:999px;
                         padding:3px 10px;font-size:11px;color:#94a3b8'>Explain this code</span>
            <span style='background:#1a1d24;border:1px solid #232730;border-radius:999px;
                         padding:3px 10px;font-size:11px;color:#94a3b8'>Analyze this chart</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── File uploader panel ────────────────────────────────────────────────────────
if st.session_state.get("show_file_uploader"):
    st.markdown("""
    <div style='background:#1a1d24;border:1px solid #232730;border-radius:14px;
                padding:1.2rem;margin-bottom:.5rem;'>
        <div style='font-size:13px;color:#a78bfa;font-weight:600;margin-bottom:.5rem'>
            📁 Upload File for Analysis
        </div>
        <div style='font-size:11px;color:#64748b;margin-bottom:.8rem'>
            Supports: TXT, CSV, JSON, Python, JS, HTML, CSS, Java, C++, Markdown
        </div>
    </div>
    """, unsafe_allow_html=True)

    doc_file = st.file_uploader(
        "Choose file",
        type=["txt","csv","json","py","js","ts","html","css","java","cpp","c","md","rs","go"],
        key="main_doc_upload",
        label_visibility="collapsed"
    )

    if doc_file is not None:
        content = read_uploaded_file(doc_file)
        st.session_state["uploaded_file_content"] = content
        st.session_state["uploaded_file_name"]    = doc_file.name
        st.session_state["show_file_uploader"]    = False
        st.success(f"✅ {doc_file.name} ready!")
        st.info("Now type your question in the chat below!")

# ══════════════════════════════════════════════════════════════════════════════
#  CHAT INPUT
# ══════════════════════════════════════════════════════════════════════════════
if prompt := st.chat_input("Ask anything — type here or click 🖼️ Image / 📄 File above…"):

    has_image = bool(st.session_state.get("pending_image_b64"))
    has_file  = bool(st.session_state.get("uploaded_file_content"))

    user_msg = {"role":"user","content":prompt,"meta":""}
    if has_image:
        user_msg["image_b64"]  = st.session_state["pending_image_b64"]
        user_msg["image_mime"] = st.session_state["pending_image_mime"]
        user_msg["image_name"] = st.session_state["pending_image_name"]

    st.session_state.messages.append(user_msg)

    with st.chat_message("user"):
        if has_image:
            try:
                img_bytes=base64.b64decode(st.session_state["pending_image_b64"])
                st.image(Image.open(io.BytesIO(img_bytes)),
                         caption=st.session_state.get("pending_image_name","Image"),width=350)
            except: pass
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response=""; meta=""

        # ── 🖼️ IMAGE ANALYSIS — TOP PRIORITY ─────────────────────────────────
        if has_image:
            b64  = st.session_state["pending_image_b64"]
            mime = st.session_state["pending_image_mime"]
            name = st.session_state.get("pending_image_name","image")
            meta = f'<div class="badge badge-pink">👁️ Vision AI · {name}</div>'
            st.markdown(meta, unsafe_allow_html=True)
            vision_prompt = get_vision_prompt(prompt)
            with st.spinner("👁️ Analyzing image…"):
                response = analyze_image_stream(b64, mime, vision_prompt)
            # Clear
            st.session_state["pending_image_b64"]  = None
            st.session_state["pending_image_mime"] = None
            st.session_state["pending_image_name"] = None

        # ── QR ────────────────────────────────────────────────────────────────
        elif is_qr_query(prompt):
            content=extract_qr_content(prompt); url=qr_url(content)
            meta='<div class="badge badge-green">📱 QR Code</div>'
            st.markdown(meta,unsafe_allow_html=True)
            st.markdown(f"**QR for:** `{content}`")
            st.image(url,width=260)
            st.markdown(f'<a href="{url}" class="btn-download" target="_blank">⬇️ Download QR</a>',unsafe_allow_html=True)
            response=f"✅ QR Code generated for: `{content}`"

        # ── CURRENCY ──────────────────────────────────────────────────────────
        elif is_currency_query(prompt):
            amount,fc,tc=extract_currency_params(prompt)
            with st.spinner("💱 Fetching rates…"): result=get_exchange_rate(fc,tc,amount)
            meta='<div class="badge badge-green">💱 Live rate</div>'
            st.markdown(meta,unsafe_allow_html=True)
            st.markdown(f'<div class="result-box green">{result}</div>',unsafe_allow_html=True)
            response=result

        # ── UNIT ──────────────────────────────────────────────────────────────
        elif is_unit_query(prompt):
            result=convert_unit(prompt)
            if result:
                meta='<div class="badge badge-orange">📐 Unit converted</div>'
                st.markdown(meta,unsafe_allow_html=True)
                st.markdown(f'<div class="result-box orange">{result}</div>',unsafe_allow_html=True)
                response=result

        # ── MATH ──────────────────────────────────────────────────────────────
        if not response and is_math_query(prompt):
            result=solve_math(prompt)
            if result:
                meta='<div class="badge badge-orange">🔢 Calculated</div>'
                st.markdown(meta,unsafe_allow_html=True)
                st.markdown(f'<div class="result-box orange" style="font-family:Space Mono,monospace;font-size:16px;color:#f59e0b">= {result}</div>',unsafe_allow_html=True)
                msgs=build_messages(f"The answer to '{prompt}' is {result}. Briefly explain in 2 lines.")
                explanation=stream_response(msgs,max_tokens=200,temperature=st.session_state["temperature"])
                response=f"= **{result}**\n\n{explanation}"

        # ── URL ───────────────────────────────────────────────────────────────
        if not response and is_url_query(prompt):
            url=extract_url(prompt)
            if url:
                with st.spinner(f"🌐 Reading {url[:50]}…"): page=fetch_url_content(url)
                meta=f'<div class="badge badge-green">🌐 URL read</div>'
                st.markdown(meta,unsafe_allow_html=True)
                msgs=build_messages(f"URL: {url}\nContent:\n{page}\n\nRequest: {prompt}")
                response=stream_response(msgs,max_tokens=st.session_state["max_tokens"],temperature=st.session_state["temperature"])

        # ── FILE ──────────────────────────────────────────────────────────────
        if not response and has_file:
            fname=st.session_state.get("uploaded_file_name","file")
            meta=f'<div class="badge badge-purple">📁 {fname}</div>'
            st.markdown(meta,unsafe_allow_html=True)
            msgs=build_messages(f"File: '{fname}'\nContent:\n{st.session_state['uploaded_file_content']}\n\nRequest: {prompt}")
            response=stream_response(msgs,max_tokens=st.session_state["max_tokens"],temperature=st.session_state["temperature"])
            st.session_state["uploaded_file_content"]=None; st.session_state["uploaded_file_name"]=None

        # ── STOCK ─────────────────────────────────────────────────────────────
        if not response and is_stock_query(prompt):
            symbol,dname=extract_stock_symbol(prompt)
            if symbol:
                with st.spinner(f"📈 Fetching {dname}…"): sd=get_stock(symbol,dname)
                if "failed" not in sd.lower():
                    L=dict(l.split(": ",1) for l in sd.strip().splitlines() if ": " in l)
                    meta='<div class="badge badge-green">📈 Live · Yahoo Finance</div>'
                    st.markdown(meta,unsafe_allow_html=True)
                    response=(f"### 📈 {L.get('Name',dname)}\n_{L.get('Exchange','')} · {L.get('Market','')}_\n\n"
                              f"| Detail | Value |\n|--------|-------|\n"
                              f"| 💰 Price | **{L.get('Price','N/A')}** |\n"
                              f"| 📊 Change | {L.get('Change','N/A')} |\n"
                              f"| 📈 Day High | {L.get('Day High','N/A')} |\n"
                              f"| 📉 Day Low | {L.get('Day Low','N/A')} |\n"
                              f"| 🔢 Volume | {L.get('Volume','N/A')} |\n\n_Delayed ~15 min_")
                    st.markdown(response)

        # ── SPORTS ────────────────────────────────────────────────────────────
        if not response and is_sports_query(prompt):
            with st.spinner("🏏 Fetching live sports data…"):
                cricket=fetch_live_cricket()
                sport_term="general"
                for k,v in SPORTS_MAP.items():
                    if k in prompt.lower(): sport_term=v; break
                extra=get_sports_news(sport_term) if sport_term!="general" else ""
                sports_data="\n\n".join(filter(None,[cricket,extra]))
            meta='<div class="badge badge-red">🔴 LIVE SPORTS</div>'
            st.markdown(meta,unsafe_allow_html=True)
            msgs=build_messages(prompt,search_results=sports_data)
            response=stream_response(msgs,max_tokens=1024,temperature=0.1)

        # ── NEWS ──────────────────────────────────────────────────────────────
        if not response and is_news_query(prompt):
            with st.spinner("📰 Fetching news…"):
                topic=extract_news_topic(prompt); news=get_news(topic)
            meta='<div class="badge badge-green">📰 Live news</div>'
            st.markdown(meta,unsafe_allow_html=True)
            response=f"### 📰 {topic.title()}\n\n{news}"
            st.markdown(response)

        # ── WEATHER ───────────────────────────────────────────────────────────
        if not response and is_weather_query(prompt):
            with st.spinner("🌤️ Fetching weather…"):
                city=extract_city(prompt); wd=get_weather(city)
            if "failed" not in wd.lower():
                L=dict(l.split(": ",1) for l in wd.strip().splitlines() if ": " in l)
                meta='<div class="badge badge-green">🌤️ Live weather</div>'
                st.markdown(meta,unsafe_allow_html=True)
                response=(f"### 🌍 {L.get('City',city)}\n\n"
                          f"| Detail | Value |\n|--------|-------|\n"
                          f"| 🌡️ Temperature | {L.get('Temperature','N/A')} |\n"
                          f"| 🌤️ Condition | {L.get('Condition','N/A')} |\n"
                          f"| 💧 Humidity | {L.get('Humidity','N/A')} |\n"
                          f"| 💨 Wind Speed | {L.get('Wind Speed','N/A')} |\n"
                          f"| 👁️ Visibility | {L.get('Visibility','N/A')} |\n"
                          f"| ☀️ UV Index | {L.get('UV Index','N/A')} |\n")
                st.markdown(response)
            else:
                response=f"❌ Could not fetch weather for **{city}**."
                st.markdown(response)

        # ── GENERAL / CODE / CREATION ─────────────────────────────────────────
        if not response:
            ct=classify_creation(prompt); search_results=""; searched=False
            if needs_search(prompt):
                with st.spinner("🔍 Searching…"):
                    search_results=web_search(prompt)
                    facts=get_current_facts(prompt)
                    if facts: search_results+="\n\nRecent headlines:\n"+facts
                    searched=True
            if searched:
                bm='<div class="badge badge-green">🔍 Web search</div>'
                st.markdown(bm,unsafe_allow_html=True); meta+=bm
            badge=get_badge(ct)
            if badge: st.markdown(badge,unsafe_allow_html=True); meta+=badge
            turns=len(st.session_state.messages)//2
            if turns>1:
                mem=f'<div class="badge badge-purple">🧠 {turns} turns remembered</div>'
                st.markdown(mem,unsafe_allow_html=True); meta+=mem

            for attempt in range(3):
                try:
                    with st.spinner(get_spinner_text(ct) if attempt==0 else "Retrying ⏳"):
                        if attempt>0: time.sleep(60)
                    msgs=build_messages(prompt,search_results,ct)
                    response=stream_response(msgs,max_tokens=st.session_state["max_tokens"],temperature=st.session_state["temperature"])

                    blocks=extract_code_blocks(response)
                    langs=[l for l,_ in blocks]
                    is_web=any(l in ("html","css","javascript","js") for l in langs)
                    code,lang=(blocks[0][1],blocks[0][0]) if blocks else (None,None)

                    if is_web:
                        html_src=build_html_preview(blocks)
                        if html_src:
                            st.markdown("---")
                            plabels={"game":"🎮 Live Game!","app":"🚀 Live App","software":"⚙️ Live Software","design":"✨ Live Design"}
                            st.markdown(f"### {plabels.get(ct,'🖥️ Preview')}")
                            h=650 if ct in ("game","app","software") else 520
                            st.components.v1.html(html_src,height=h,scrolling=True)
                            b64_html=base64.b64encode(html_src.encode()).decode()
                            fname={"game":"nova_game.html","app":"nova_app.html","software":"nova_software.html","design":"nova_design.html"}.get(ct,"nova_ai.html")
                            st.markdown(f'<a href="data:text/html;base64,{b64_html}" download="{fname}" class="btn-download">⬇️ Download {fname}</a>',unsafe_allow_html=True)
                    elif code and lang and lang not in ("html","css"):
                        rk=f"run_{len(st.session_state.messages)}"
                        if st.button(f"▶ Run {lang.title()}",key=rk):
                            with st.spinner(f"⚙️ Running {lang}…"): out=run_code(code,lang)
                            cls="error-box" if "❌" in out else "output-box"
                            st.markdown(f'<div class="{cls}">{out}</div>',unsafe_allow_html=True)
                    break
                except Exception as e:
                    if "rate_limit_exceeded" in str(e) and attempt<2: continue
                    st.error(f"❌ Error: {e}"); break

        if response:
            st.session_state.messages.append({"role":"assistant","content":response,"meta":meta})
