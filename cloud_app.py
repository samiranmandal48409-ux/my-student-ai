import streamlit as st
from groq import Groq
import time, requests, re, base64, json, math
from datetime import datetime
import urllib.parse
import xml.etree.ElementTree as ET

st.set_page_config(
    page_title="Nova AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════════════════════
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
    color: var(--text) !important;
}
[data-testid="stSidebar"] label {
    color: var(--muted) !important;
    font-size: 12px !important;
}
[data-testid="stSidebar"] h3 {
    color: var(--accent) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 13px !important;
    margin: .8rem 0 .4rem !important;
}
[data-testid="stSidebar"] hr { border-color: var(--border) !important; }
[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--muted) !important;
    border-radius: 8px !important;
    font-size: 12px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}
[data-testid="stSidebar"] .stDownloadButton > button {
    width: 100% !important;
    background: rgba(0,229,255,.08) !important;
    border: 1px solid rgba(0,229,255,.25) !important;
    color: var(--accent) !important;
    border-radius: 8px !important;
    font-size: 12px !important;
}
[data-testid="stSidebar"] .stExpander {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    margin-bottom: .4rem !important;
}

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    position: relative;
}
.hero::before {
    content: '';
    position: absolute; top: 0; left: 50%;
    transform: translateX(-50%);
    width: 600px; height: 300px;
    background: radial-gradient(ellipse at center,
        rgba(0,229,255,.07) 0%, transparent 70%);
    pointer-events: none;
}
.hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(0,229,255,.08);
    border: 1px solid rgba(0,229,255,.2);
    border-radius: 999px; padding: 4px 14px;
    font-family: 'Space Mono', monospace;
    font-size: 11px; color: var(--accent);
    letter-spacing: .05em; margin-bottom: 1rem;
}
.hero-badge::before {
    content: '●'; font-size: 8px;
    animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }
.hero h1 {
    font-family: 'Space Mono', monospace !important;
    font-size: clamp(1.8rem,4vw,2.6rem) !important;
    font-weight: 700 !important; color: #fff !important;
    line-height: 1.15 !important; letter-spacing: -.02em;
    margin-bottom: .5rem !important;
}
.hero h1 span { color: var(--accent); }
.hero p {
    font-size: .95rem; color: var(--muted);
    font-weight: 300; max-width: 460px; margin: 0 auto;
}
.divider {
    height: 1px;
    background: linear-gradient(90deg,transparent,var(--border),transparent);
    margin: 1.2rem 0;
}

/* ── Stats ── */
.stats-row {
    display: flex; gap: .6rem;
    margin: 1rem 0 1.5rem;
    justify-content: center; flex-wrap: wrap;
}
.stat-pill {
    display: flex; align-items: center; gap: 6px;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 999px; padding: 5px 12px;
    font-size: 12px; color: var(--muted);
}
.stat-pill .dot { width:6px; height:6px; border-radius:50%; }
.dot-green  { background:var(--green);  box-shadow:0 0 5px var(--green); }
.dot-blue   { background:var(--accent); box-shadow:0 0 5px var(--accent); }
.dot-purple { background:var(--purple); box-shadow:0 0 5px var(--purple); }
.dot-orange { background:var(--orange); box-shadow:0 0 5px var(--orange); }

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important; padding: 0 !important;
}
[data-testid="stChatMessage"] > div { background: transparent !important; }
[data-testid="stChatMessageContent"] { background: transparent !important; }
.stChatMessage {
    border-radius: var(--radius) !important;
    padding: 1rem 1.2rem !important;
    border: 1px solid var(--border) !important;
    margin-bottom: .6rem !important;
    background: var(--surface) !important;
    animation: fadeUp .25s ease;
}
@keyframes fadeUp {
    from{opacity:0;transform:translateY(8px)}
    to{opacity:1;transform:translateY(0)}
}
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) {
    background: var(--user-bg) !important;
    border-color: rgba(0,229,255,.15) !important;
}

/* ── Code ── */
pre, code { font-family:'Space Mono',monospace !important; font-size:13px !important; }
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
    position: fixed !important; bottom: 0 !important;
    left: 50% !important; transform: translateX(-50%) !important;
    width: 100% !important; max-width: 860px !important;
    padding: 1rem 1.5rem 1.5rem !important;
    background: linear-gradient(to top,var(--bg) 70%,transparent) !important;
    backdrop-filter: blur(10px); z-index: 999 !important;
}
[data-testid="stChatInput"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important; color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
}
[data-testid="stChatInput"]:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(0,229,255,.1) !important;
    outline: none !important;
}
[data-testid="stChatInputSubmitButton"] button {
    background: var(--accent) !important; border: none !important;
    border-radius: 8px !important; color: #000 !important;
    font-weight: 600 !important;
}
.stButton > button {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--muted) !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important; font-weight: 500 !important;
    padding: .4rem 1rem !important; transition: all .2s !important;
}
.stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: rgba(0,229,255,.06) !important;
}

/* ── Badges ── */
.badge {
    display: inline-flex; align-items: center; gap: 5px;
    border-radius: 6px; padding: 3px 10px;
    font-size: 11px; margin-bottom: .5rem;
    font-family: 'DM Sans', sans-serif;
}
.badge-green  { background:rgba(16,185,129,.08);  border:1px solid rgba(16,185,129,.25); color:var(--green); }
.badge-red    { background:rgba(239,68,68,.08);   border:1px solid rgba(239,68,68,.3);   color:#fca5a5; }
.badge-purple { background:rgba(124,58,237,.08);  border:1px solid rgba(124,58,237,.3);  color:#a78bfa; }
.badge-orange { background:rgba(245,158,11,.08);  border:1px solid rgba(245,158,11,.3);  color:var(--orange); }
.badge-blue   { background:rgba(0,229,255,.08);   border:1px solid rgba(0,229,255,.25);  color:var(--accent); }

/* ── Result boxes ── */
.output-box {
    background: #0d1117; border: 1px solid var(--border);
    border-left: 3px solid var(--green); border-radius: 10px;
    padding: .8rem 1.2rem; font-family: 'Space Mono', monospace;
    font-size: 13px; color: #a3e635;
    margin-top: .5rem; white-space: pre-wrap;
}
.error-box {
    background: #1a0a0a; border: 1px solid #7f1d1d;
    border-left: 3px solid var(--red); border-radius: 10px;
    padding: .8rem 1.2rem; font-family: 'Space Mono', monospace;
    font-size: 13px; color: #fca5a5;
    margin-top: .5rem; white-space: pre-wrap;
}
.result-box {
    background: linear-gradient(135deg,#0d1117,#111827);
    border: 1px solid var(--border);
    border-radius: 10px; padding: .8rem 1.2rem;
    font-size: 14px; color: var(--text); margin: .5rem 0;
}
.result-box.orange { border-left: 3px solid var(--orange); }
.result-box.green  { border-left: 3px solid var(--green); }

/* ── Download button ── */
.btn-download {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(0,229,255,.1);
    border: 1px solid rgba(0,229,255,.3);
    color: var(--accent); padding: 6px 14px;
    border-radius: 8px; text-decoration: none;
    font-size: 12px; font-family: 'DM Sans',sans-serif;
    font-weight: 500; margin-top: .5rem;
    transition: all .2s;
}
.btn-download:hover {
    background: rgba(0,229,255,.18);
    color: var(--accent);
}

/* ── Category grid ── */
.category-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px,1fr));
    gap: .8rem; margin: 1.2rem 0;
}
.category-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 1rem; text-align: center;
    transition: border-color .2s, transform .2s;
}
.category-card:hover {
    border-color: var(--accent); transform: translateY(-2px);
}
.category-icon  { font-size: 1.6rem; margin-bottom: .4rem; }
.category-title { font-size: 12.5px; font-weight:600; color:#94a3b8; margin-bottom:.2rem; }
.category-examples { font-size: 11px; color: var(--muted); line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  GROQ CLIENT
# ══════════════════════════════════════════════════════════════════════════════
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_KEY = "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"

client = Groq(api_key=GROQ_KEY)
MODEL  = "llama-3.3-70b-versatile"
MAX_HISTORY_TURNS = 20

# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
CURRENCIES = [
    "USD","EUR","GBP","INR","JPY","CAD","AUD","CHF","CNY","HKD",
    "SGD","NOK","SEK","DKK","NZD","MXN","BRL","ZAR","RUB","KRW",
    "TRY","AED","SAR","THB","IDR","MYR","PHP","VND","EGP","PKR",
]

MODE_PROMPTS = {
    "🤖 Default":  "",
    "💻 Coder":    "CODER MODE: Focus exclusively on writing perfect production-ready code with error handling, type hints, and comments. Prefer code over explanation.",
    "🎨 Creative": "CREATIVE MODE: Be imaginative and expressive. Think outside the box.",
    "📊 Analyst":  "ANALYST MODE: Be data-driven and precise. Use bullet points, tables, structured formats.",
    "🎓 Teacher":  "TEACHER MODE: Explain everything simply, step by step, with examples and analogies.",
    "✍️ Writer":   "WRITER MODE: Focus on clear, engaging writing. Polish grammar, style, and content.",
}

GAME_KEYWORDS = [
    "game","snake game","tetris","pacman","flappy bird","2048","tic tac toe",
    "chess","checkers","sudoku","minesweeper","platformer","shooter",
    "puzzle game","card game","memory game","quiz game","breakout","pong",
    "asteroids","space invaders","racing game","rpg","tower defense",
    "clicker game","battle","dungeon","maze","arcade","word game",
]
APP_KEYWORDS = [
    "app","application","dashboard","admin panel","landing page","portfolio",
    "website","web app","e-commerce","shop","store","blog","chat app",
    "todo app","weather app","calculator app","login page","signup","form",
    "expense tracker","budget","note app","kanban","timer","stopwatch","clock",
    "music player","image gallery","calendar","booking","analytics","chart",
    "crm","netflix clone","youtube clone","twitter clone","whatsapp ui",
    "instagram clone","responsive","animated",
]
SOFTWARE_KEYWORDS = [
    "software","tool","utility","desktop app","file manager","text editor",
    "password manager","api tester","converter","downloader","scraper",
    "automation","cli tool",
]
DESIGN_KEYWORDS = [
    "design","ui","ux","mockup","prototype","wireframe","beautiful","modern",
    "stunning","animated","glassmorphism","neumorphism","gradient","dark theme",
    "light theme","component","ui kit","hero section","navbar","sidebar","modal",
    "dropdown","footer","header","banner","carousel",
]

STOCK_ALIASES = {
    "reliance":"RELIANCE.NS","tata":"TATAMOTORS.NS","tcs":"TCS.NS",
    "infosys":"INFY.NS","wipro":"WIPRO.NS","hdfc":"HDFCBANK.NS",
    "icici":"ICICIBANK.NS","sbi":"SBIN.NS","bajaj":"BAJFINANCE.NS",
    "adani":"ADANIENT.NS","ongc":"ONGC.NS","itc":"ITC.NS",
    "maruti":"MARUTI.NS","mahindra":"M&M.NS","kotak":"KOTAKBANK.NS",
    "axis bank":"AXISBANK.NS","titan":"TITAN.NS","nifty":"^NSEI",
    "sensex":"^BSESN","bank nifty":"^NSEBANK",
    "apple":"AAPL","microsoft":"MSFT","google":"GOOGL","alphabet":"GOOGL",
    "amazon":"AMZN","tesla":"TSLA","meta":"META","facebook":"META",
    "netflix":"NFLX","nvidia":"NVDA","intel":"INTC","amd":"AMD","uber":"UBER",
    "bitcoin":"BTC-USD","btc":"BTC-USD","ethereum":"ETH-USD","eth":"ETH-USD",
    "dogecoin":"DOGE-USD","doge":"DOGE-USD","solana":"SOL-USD",
    "bnb":"BNB-USD","xrp":"XRP-USD",
    "dow jones":"^DJI","nasdaq":"^IXIC","s&p 500":"^GSPC","s&p":"^GSPC",
}

SPORTS_MAP = {
    "cricket":"cricket","ipl":"IPL cricket","t20":"T20 cricket",
    "odi":"ODI cricket","test match":"test cricket",
    "football":"football","soccer":"soccer",
    "premier league":"Premier League",
    "champions league":"UEFA Champions League",
    "la liga":"La Liga","bundesliga":"Bundesliga",
    "world cup":"FIFA World Cup","basketball":"basketball",
    "nba":"NBA basketball","tennis":"tennis",
    "wimbledon":"Wimbledon tennis","badminton":"badminton",
    "hockey":"hockey","baseball":"baseball",
    "formula 1":"Formula 1","f1":"F1 race","motogp":"MotoGP",
    "rugby":"rugby","golf":"golf","boxing":"boxing",
    "mma":"MMA UFC","ufc":"UFC","olympics":"Olympics",
    "table tennis":"table tennis","volleyball":"volleyball",
    "kabaddi":"kabaddi",
}

IPL_TEAMS = [
    "csk","mi","rcb","kkr","srh","pbks","dc","gt","lsg","rr",
    "chennai","mumbai","bangalore","kolkata","hyderabad",
    "punjab","delhi","gujarat","lucknow","rajasthan",
]

LANGUAGE_MAP = {
    "python":("python","3.10.0"),
    "javascript":("javascript","18.15.0"),"js":("javascript","18.15.0"),
    "typescript":("typescript","5.0.3"),"ts":("typescript","5.0.3"),
    "java":("java","15.0.2"),
    "c++":("c++","10.2.0"),"cpp":("c++","10.2.0"),
    "c":("c","10.2.0"),"rust":("rust","1.68.2"),"go":("go","1.16.2"),
    "ruby":("ruby","3.0.1"),"php":("php","8.2.3"),
    "swift":("swift","5.3.3"),"kotlin":("kotlin","1.8.20"),
    "r":("r","4.1.1"),"bash":("bash","5.2.0"),"shell":("bash","5.2.0"),
    "sql":("sqlite3","3.36.0"),"lua":("lua","5.4.4"),
    "perl":("perl","5.36.0"),"scala":("scala","3.2.2"),
}

SEARCH_TRIGGERS = [
    "who is","who was","who won","who are","who did",
    "what is","what was","what are","what happened",
    "when is","when was","when did","when will",
    "where is","where was","current","latest","recent","today",
    "election","prime minister","president","chief minister",
    "cm of","minister of","winner","champion","result",
    "2023","2024","2025","2026",
]

# ══════════════════════════════════════════════════════════════════════════════
#  HELPER — TODAY
# ══════════════════════════════════════════════════════════════════════════════
def today_str() -> str:
    return datetime.now().strftime("%B %d, %Y")

# ══════════════════════════════════════════════════════════════════════════════
#  STREAMING
# ══════════════════════════════════════════════════════════════════════════════
def stream_response(messages: list, max_tokens: int = 4096,
                    temperature: float = 0.25) -> str:
    full = ""
    box  = st.empty()
    try:
        stream = client.chat.completions.create(
            messages=messages, model=MODEL,
            max_tokens=max_tokens, temperature=temperature,
            stream=True,
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
#  URL READER
# ══════════════════════════════════════════════════════════════════════════════
def fetch_url_content(url: str) -> str:
    try:
        resp = requests.get(
            url,
            headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                  "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"},
            timeout=10
        )
        text = resp.text
        for tag in ["script","style","nav","footer","header","aside"]:
            text = re.sub(f"<{tag}[^>]*>[\\s\\S]*?</{tag}>","",text,flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>"," ",text)
        text = re.sub(r"\s+"," ",text).strip()
        return text[:4000] if len(text) > 100 else "Could not extract content."
    except Exception as e:
        return f"URL fetch failed: {e}"

def is_url_query(q: str) -> bool:
    return bool(re.search(r"https?://\S+", q))

def extract_url(q: str) -> str:
    m = re.search(r"https?://\S+", q)
    return m.group(0).rstrip(".,)>") if m else ""

# ══════════════════════════════════════════════════════════════════════════════
#  MATH ENGINE
# ══════════════════════════════════════════════════════════════════════════════
def solve_math(expression: str) -> str:
    try:
        expr = re.sub(
            r"(calculate|compute|solve|evaluate|what is|how much is|=)",
            "", expression, flags=re.IGNORECASE
        ).strip()
        expr = re.sub(r"[?!]","",expr).replace("^","**").strip()
        safe = {
            "sin":math.sin,"cos":math.cos,"tan":math.tan,
            "asin":math.asin,"acos":math.acos,"atan":math.atan,
            "log":math.log10,"ln":math.log,"log2":math.log2,
            "sqrt":math.sqrt,"exp":math.exp,"abs":abs,
            "pi":math.pi,"e":math.e,"ceil":math.ceil,
            "floor":math.floor,"round":round,"pow":math.pow,
            "factorial":math.factorial,
        }
        result = eval(expr, {"__builtins__":{}}, safe)
        if isinstance(result, float): result = round(result,10)
        return str(result)
    except:
        return ""

def is_math_query(q: str) -> bool:
    ql = q.lower()
    if any(k in ql for k in ["stock","weather","ipl","cricket","news",
                               "price","convert","currency"]): return False
    triggers = ["calculate","compute","sqrt","factorial","sin","cos",
                "tan","log","integrate","derivative"]
    has_num  = bool(re.search(r"\d", q))
    has_ops  = bool(re.search(r"[+\-*/^%()]", q))
    has_trig = any(t in ql for t in triggers)
    return has_num and (has_ops or has_trig)

# ══════════════════════════════════════════════════════════════════════════════
#  CURRENCY
# ══════════════════════════════════════════════════════════════════════════════
def get_exchange_rate(from_c: str, to_c: str, amount: float = 1.0) -> str:
    try:
        resp  = requests.get(
            f"https://api.exchangerate-api.com/v4/latest/{from_c.upper()}",
            timeout=6
        )
        data  = resp.json()
        rates = data.get("rates", {})
        tc    = to_c.upper()
        if tc not in rates: return f"❌ Currency '{tc}' not found."
        rate   = rates[tc]
        result = amount * rate
        return (
            f"**{amount:,.2f} {from_c.upper()}** = **{result:,.4f} {tc}**\n\n"
            f"Rate: 1 {from_c.upper()} = {rate:.6f} {tc}\n"
            f"_Updated: {data.get('date','today')} · ExchangeRate-API_"
        )
    except Exception as e:
        return f"Currency fetch failed: {e}"

def is_currency_query(q: str) -> bool:
    ql   = q.lower()
    curr = [c.lower() for c in CURRENCIES]
    trig = ["convert","exchange rate","to inr","to usd","to eur","to gbp",
            "in dollars","in rupees","in euros","in pounds"]
    found = sum(1 for c in curr if re.search(r"\b"+c+r"\b", ql))
    return found >= 2 or (any(t in ql for t in trig) and found >= 1)

def extract_currency_params(q: str) -> tuple:
    ql    = q.lower()
    curr  = [c.lower() for c in CURRENCIES]
    found = [c for c in curr if re.search(r"\b"+c+r"\b", ql)]
    am    = re.search(r"(\d+(?:\.\d+)?)", q)
    amount = float(am.group(1)) if am else 1.0
    if len(found) >= 2: return amount, found[0].upper(), found[1].upper()
    if len(found) == 1:
        other = "INR" if found[0] != "inr" else "USD"
        return amount, found[0].upper(), other
    return 1.0, "USD", "INR"

# ══════════════════════════════════════════════════════════════════════════════
#  UNIT CONVERTER
# ══════════════════════════════════════════════════════════════════════════════
UNIT_MAP = {
    ("celsius","fahrenheit"):    lambda x:(x*9/5)+32,
    ("fahrenheit","celsius"):    lambda x:(x-32)*5/9,
    ("celsius","kelvin"):        lambda x:x+273.15,
    ("kelvin","celsius"):        lambda x:x-273.15,
    ("fahrenheit","kelvin"):     lambda x:((x-32)*5/9)+273.15,
    ("km","miles"):              lambda x:x*0.621371,
    ("miles","km"):              lambda x:x*1.60934,
    ("meters","feet"):           lambda x:x*3.28084,
    ("feet","meters"):           lambda x:x/3.28084,
    ("cm","inches"):             lambda x:x*0.393701,
    ("inches","cm"):             lambda x:x*2.54,
    ("km","meters"):             lambda x:x*1000,
    ("meters","km"):             lambda x:x/1000,
    ("kg","pounds"):             lambda x:x*2.20462,
    ("pounds","kg"):             lambda x:x/2.20462,
    ("kg","grams"):              lambda x:x*1000,
    ("grams","kg"):              lambda x:x/1000,
    ("tons","kg"):               lambda x:x*1000,
    ("kg","tons"):               lambda x:x/1000,
    ("kmh","mph"):               lambda x:x*0.621371,
    ("mph","kmh"):               lambda x:x*1.60934,
    ("ms","kmh"):                lambda x:x*3.6,
    ("kmh","ms"):                lambda x:x/3.6,
    ("sqm","sqft"):              lambda x:x*10.7639,
    ("sqft","sqm"):              lambda x:x/10.7639,
    ("acres","sqm"):             lambda x:x*4046.86,
    ("hectares","acres"):        lambda x:x*2.47105,
    ("liters","gallons"):        lambda x:x*0.264172,
    ("gallons","liters"):        lambda x:x*3.78541,
    ("ml","liters"):             lambda x:x/1000,
    ("liters","ml"):             lambda x:x*1000,
    ("gb","mb"):                 lambda x:x*1024,
    ("mb","gb"):                 lambda x:x/1024,
    ("tb","gb"):                 lambda x:x*1024,
    ("gb","tb"):                 lambda x:x/1024,
    ("mb","kb"):                 lambda x:x*1024,
    ("kb","mb"):                 lambda x:x/1024,
}

def convert_unit(q: str) -> str:
    ql = q.lower()
    am = re.search(r"(\d+(?:\.\d+)?)", q)
    amount = float(am.group(1)) if am else 1.0
    for (fu, tu), fn in UNIT_MAP.items():
        if fu in ql and tu in ql:
            return f"**{amount} {fu}** = **{round(fn(amount),6)} {tu}**"
    return ""

def is_unit_query(q: str) -> bool:
    ql    = q.lower()
    units = ["km","miles","meters","feet","cm","inches","kg","pounds","grams",
             "celsius","fahrenheit","kelvin","liters","gallons","mph","kmh",
             "acres","hectares","gb","mb","tb","kb","sqm","sqft","ms","tons"]
    trig  = ["convert","how many","how much","to","equals","in"]
    return (any(u in ql for u in units) and
            any(t in ql for t in trig) and
            bool(re.search(r"\d", q)))

# ══════════════════════════════════════════════════════════════════════════════
#  QR CODE
# ══════════════════════════════════════════════════════════════════════════════
def qr_url(text: str) -> str:
    return (f"https://api.qrserver.com/v1/create-qr-code/"
            f"?size=300x300&data={urllib.parse.quote(text)}")

def is_qr_query(q: str) -> bool:
    return any(k in q.lower() for k in
               ["qr code","qr for","generate qr","make qr",
                "create qr","qr generator"])

def extract_qr_content(q: str) -> str:
    m = re.search(r"https?://\S+", q)
    if m: return m.group(0)
    sw = {"qr","code","generate","make","create","for","me","a","an","the","of","my"}
    return " ".join(w for w in q.replace("?","").split()
                    if w.lower() not in sw).strip() or q

# ══════════════════════════════════════════════════════════════════════════════
#  FILE READER
# ══════════════════════════════════════════════════════════════════════════════
def read_uploaded_file(f) -> str:
    try:
        name = f.name.lower()
        if name.endswith((".txt",".md",".py",".js",".ts",".html",
                          ".css",".java",".cpp",".c",".rs",".go")):
            return f.read().decode("utf-8", errors="ignore")[:5000]
        elif name.endswith(".csv"):
            content = f.read().decode("utf-8", errors="ignore")
            lines   = content.split("\n")
            return (f"CSV — {len(lines)} rows\n\nFirst 50 rows:\n"
                    + "\n".join(lines[:50]))
        elif name.endswith(".json"):
            content = f.read().decode("utf-8", errors="ignore")
            try:
                parsed = json.loads(content)
                return "JSON:\n" + json.dumps(parsed, indent=2)[:4000]
            except:
                return content[:4000]
        else:
            return f"File: {f.name} — describe what you need help with."
    except Exception as e:
        return f"File read error: {e}"

# ══════════════════════════════════════════════════════════════════════════════
#  CHAT EXPORT
# ══════════════════════════════════════════════════════════════════════════════
def export_md() -> str:
    lines = [
        "# Nova AI — Conversation Export",
        f"_Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n---\n"
    ]
    for m in st.session_state.messages:
        role    = "🧑 You" if m["role"]=="user" else "✨ Nova AI"
        content = re.sub(r"<[^>]+>","",m["content"]).strip()
        lines.append(f"### {role}\n{content}\n")
    return "\n".join(lines)

def export_json_chat() -> str:
    return json.dumps(
        [{"role":m["role"],
          "content":re.sub(r"<[^>]+>","",m["content"]).strip()}
         for m in st.session_state.messages],
        indent=2, ensure_ascii=False
    )

# ══════════════════════════════════════════════════════════════════════════════
#  WEATHER
# ══════════════════════════════════════════════════════════════════════════════
def get_weather(city: str) -> str:
    try:
        resp = requests.get(
            f"https://wttr.in/{requests.utils.quote(city)}?format=j1",
            headers={"User-Agent":"Mozilla/5.0"}, timeout=8
        )
        d    = resp.json()
        c    = d["current_condition"][0]
        area = d["nearest_area"][0]
        return (
            f"City: {area['areaName'][0]['value']}, {area['country'][0]['value']}\n"
            f"Temperature: {c['temp_C']}°C (Feels like {c['FeelsLikeC']}°C)\n"
            f"Condition: {c['weatherDesc'][0]['value']}\n"
            f"Humidity: {c['humidity']}%\n"
            f"Wind Speed: {c['windspeedKmph']} km/h\n"
            f"Visibility: {c['visibility']} km\n"
            f"UV Index: {c['uvIndex']}"
        )
    except Exception as e:
        return f"failed: {e}"

def extract_city(q: str) -> str:
    m = re.search(
        r"(?:weather|temperature|forecast|humidity|climate)"
        r"\s+(?:report\s+)?(?:in|for|of|at)\s+([A-Za-z ,]+?)(?:\?|$)",
        q, re.IGNORECASE
    )
    if m: return m.group(1).strip().rstrip(",")
    sw = {"what","is","the","weather","report","temperature","forecast",
          "today","current","now","like","how","give","me","show",
          "humidity","climate","condition","conditions","a","an"}
    return " ".join(w for w in q.replace("?","").split()
                    if w.lower() not in sw).strip() or "Guwahati"

def is_weather_query(q: str) -> bool:
    return any(k in q.lower() for k in
               ["weather","temperature","forecast","humidity",
                "rain","sunny","cloudy","wind speed","climate today"])

# ══════════════════════════════════════════════════════════════════════════════
#  STOCKS
# ══════════════════════════════════════════════════════════════════════════════
def get_stock(symbol: str, dname: str) -> str:
    try:
        resp = requests.get(
            f"https://query1.finance.yahoo.com/v8/finance/chart/"
            f"{symbol}?interval=1d&range=2d",
            headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"},
            timeout=8
        )
        meta  = resp.json()["chart"]["result"][0]["meta"]
        price = meta.get("regularMarketPrice",0)
        prev  = meta.get("chartPreviousClose",0)
        curr  = meta.get("currency","USD")
        name  = meta.get("longName") or meta.get("shortName") or dname
        chg   = price - prev
        pct   = (chg/prev*100) if prev else 0
        arrow = "🟢 ▲" if chg >= 0 else "🔴 ▼"
        sign  = "+" if chg >= 0 else ""
        vol   = meta.get("regularMarketVolume","N/A")
        if isinstance(vol,int): vol = f"{vol:,}"
        return (
            f"Name: {name}\nExchange: {meta.get('exchangeName','')}\n"
            f"Price: {curr} {price:,.2f}\n"
            f"Change: {arrow} {sign}{chg:.2f} ({sign}{pct:.2f}%)\n"
            f"Day High: {meta.get('regularMarketDayHigh','N/A')}\n"
            f"Day Low: {meta.get('regularMarketDayLow','N/A')}\n"
            f"Volume: {vol}\nMarket: {meta.get('marketState','')}"
        )
    except Exception as e:
        return f"failed: {e}"

def extract_stock_symbol(q: str) -> tuple:
    ql = q.lower()
    for name, ticker in STOCK_ALIASES.items():
        if name in ql: return ticker, name.title()
    m = re.search(r"\b([A-Z]{2,5})\b", q)
    if m: return m.group(1), m.group(1)
    return None, None

def is_stock_query(q: str) -> bool:
    ql = q.lower()
    return (any(a in ql for a in ["stock","share price","stock price","price of",
                                   "market price","trading at","crypto","bitcoin",
                                   "ethereum","sensex","nifty","nasdaq",
                                   "dow jones","coin price"]) or
            any(k in ql for k in STOCK_ALIASES))

# ══════════════════════════════════════════════════════════════════════════════
#  SPORTS / CRICKET
# ══════════════════════════════════════════════════════════════════════════════
def fetch_live_cricket() -> str:
    results = []
    try:
        resp = requests.get(
            "https://api.cricapi.com/v1/currentMatches",
            params={"apikey":"a52ea237-09e7-4d69-b7cc-e4f0e2a8c1f1","offset":0},
            timeout=6
        )
        data = resp.json()
        if data.get("status")=="success" and data.get("data"):
            for m in data["data"][:5]:
                scores = ""
                for s in m.get("score",[]):
                    if s.get("r"):
                        scores += (f"\n  {s.get('inning','')}: "
                                   f"{s.get('r','')}/{s.get('w','')} "
                                   f"({s.get('o','')} ov)")
                results.append(f"**{m.get('name','')}**\n  "
                                f"{m.get('status','')}{scores}")
    except: pass

    for sq in [
        f"IPL 2025 today match {datetime.now().strftime('%B %d')} live score",
        "IPL 2025 match playing today schedule"
    ]:
        try:
            url  = (f"https://news.google.com/rss/search?"
                    f"q={requests.utils.quote(sq)}&hl=en-IN&gl=IN&ceid=IN:en")
            resp = requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=6)
            root = ET.fromstring(resp.content)
            items = []
            for item in root.findall(".//item")[:5]:
                title   = item.findtext("title","").strip()
                pub_raw = item.findtext("pubDate","")
                pub     = pub_raw[:22] if pub_raw else ""
                if title:
                    clean = title.split(" - ")[0].strip()
                    items.append(f"[{pub}] {clean}" if pub else clean)
            if items: results.append("📰 " + "\n".join(items))
        except: pass

    return "\n\n".join(results) if results else ""

def get_sports_news(term: str) -> str:
    try:
        url  = (f"https://news.google.com/rss/search?"
                f"q={requests.utils.quote(term+' score result today')}"
                f"&hl=en&gl=US&ceid=US:en")
        resp = requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=8)
        root = ET.fromstring(resp.content)
        out  = []
        for item in root.findall(".//item")[:7]:
            title = item.findtext("title","").strip()
            if title:
                clean = title.split(" - ")[0].strip()
                src   = title.split(" - ")[-1].strip() if " - " in title else ""
                out.append(f"• **{clean}**" + (f" _{src}_" if src else ""))
        return "\n".join(out) if out else "No recent updates found."
    except Exception as e:
        return f"Sports fetch failed: {e}"

def is_sports_query(q: str) -> bool:
    ql = q.lower()
    if any(p in ql for p in ["who made you","history of","rules of",
                               "how to play","origin of"]): return False
    if any(t in ql for t in IPL_TEAMS): return True
    actions = ["score","result","match","game","live","standings","winner",
               "champion","playoff","final","tournament","who won",
               "playing today","which team","today's match","schedule"]
    sports  = list(SPORTS_MAP.keys())
    return (any(re.search(r"\b"+re.escape(a)+r"\b",ql) for a in actions) and
            any(re.search(r"\b"+re.escape(s)+r"\b",ql) for s in sports))

def get_sport_emoji(term: str) -> str:
    em = {
        "cricket":"🏏","ipl":"🏏","football":"⚽","soccer":"⚽",
        "basketball":"🏀","tennis":"🎾","badminton":"🏸","hockey":"🏑",
        "baseball":"⚾","formula 1":"🏎️","f1":"🏎️","rugby":"🏉",
        "golf":"⛳","boxing":"🥊","mma":"🥋","olympics":"🏅",
        "volleyball":"🏐","kabaddi":"🤼",
    }
    sl = term.lower()
    for k,v in em.items():
        if k in sl: return v
    return "🏆"

# ══════════════════════════════════════════════════════════════════════════════
#  NEWS
# ══════════════════════════════════════════════════════════════════════════════
def get_news(topic: str = "India") -> str:
    try:
        url  = (f"https://news.google.com/rss/search?"
                f"q={requests.utils.quote(topic)}&hl=en-IN&gl=IN&ceid=IN:en")
        resp = requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=8)
        root = ET.fromstring(resp.content)
        out  = []
        for item in root.findall(".//item")[:6]:
            title = item.findtext("title","").strip()
            if title:
                clean = title.split(" - ")[0].strip()
                src   = title.split(" - ")[-1].strip() if " - " in title else "News"
                out.append(f"• **{clean}** _{src}_")
        return "\n".join(out) if out else "No news found."
    except Exception as e:
        return f"News fetch failed: {e}"

def is_news_query(q: str) -> bool:
    return any(k in q.lower() for k in
               ["news","headlines","latest news","today news",
                "breaking","top news","what happened today"])

def extract_news_topic(q: str) -> str:
    sw = {"news","latest","today","show","me","give","what","is","the",
          "headlines","breaking","top","current","about","on"}
    return " ".join(w for w in q.replace("?","").split()
                    if w.lower() not in sw).strip() or "India"

# ══════════════════════════════════════════════════════════════════════════════
#  WEB SEARCH
# ══════════════════════════════════════════════════════════════════════════════
def web_search(q: str) -> str:
    try:
        resp = requests.get(
            f"https://html.duckduckgo.com/html/?q={requests.utils.quote(q)}",
            headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                  "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"},
            timeout=10
        )
        snips  = re.findall(r'class="result__snippet"[^>]*>(.*?)</(?:a|span)>',
                            resp.text, re.DOTALL)
        titles = re.findall(r'class="result__title"[^>]*>.*?<a[^>]*>(.*?)</a>',
                            resp.text, re.DOTALL)
        cs = [re.sub(r"<[^>]+>","",s).strip() for s in snips[:5]]
        ct = [re.sub(r"<[^>]+>","",t).strip() for t in titles[:5]]
        results = [f"• {t}: {s}" for t,s in zip(ct,cs) if s]
        if results: return "\n".join(results)
        r2   = requests.get(
            "https://api.duckduckgo.com/",
            params={"q":q,"format":"json","no_html":"1","skip_disambig":"1"},
            timeout=8
        )
        data = r2.json()
        parts = []
        if data.get("Answer"):   parts.append(data["Answer"])
        if data.get("Abstract"): parts.append(data["Abstract"][:500])
        for t in data.get("RelatedTopics",[])[:3]:
            if isinstance(t,dict) and t.get("Text"): parts.append(t["Text"][:200])
        return "\n".join(parts) if parts else "No results found."
    except Exception as e:
        return f"Search failed: {e}"

def get_current_facts(q: str) -> str:
    try:
        url  = (f"https://news.google.com/rss/search?"
                f"q={requests.utils.quote(q)}&hl=en-IN&gl=IN&ceid=IN:en")
        resp = requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=8)
        root = ET.fromstring(resp.content)
        out  = []
        for item in root.findall(".//item")[:5]:
            title   = item.findtext("title","").strip()
            pub_raw = item.findtext("pubDate","")
            pub     = pub_raw[:22] if pub_raw else ""
            if title:
                clean = title.split(" - ")[0].strip()
                out.append(f"[{pub}] {clean}" if pub else clean)
        return "\n".join(out) if out else ""
    except: return ""

def needs_search(q: str) -> bool:
    ql = q.lower()
    if any(k in ql for k in ["who made you","who created you","who are you"]): return False
    skip = GAME_KEYWORDS + APP_KEYWORDS + SOFTWARE_KEYWORDS + DESIGN_KEYWORDS
    if any(k in ql for k in skip): return False
    if is_sports_query(q): return False
    return any(t in ql for t in SEARCH_TRIGGERS)

# ══════════════════════════════════════════════════════════════════════════════
#  CREATION CLASSIFICATION
# ══════════════════════════════════════════════════════════════════════════════
def classify_creation(q: str) -> str:
    ql = q.lower()
    if any(k in ql for k in GAME_KEYWORDS):    return "game"
    if any(k in ql for k in APP_KEYWORDS):      return "app"
    if any(k in ql for k in SOFTWARE_KEYWORDS): return "software"
    if any(k in ql for k in DESIGN_KEYWORDS):   return "design"
    if is_code_query(q):                        return "code"
    return "general"

def is_code_query(q: str) -> bool:
    ql = q.lower()
    if is_stock_query(q) or is_weather_query(q): return False
    return any(t in ql for t in [
        "write","code","program","script","function","implement",
        "create","build","develop","make","generate","algorithm",
        "sort","search","fibonacci","factorial","prime","reverse",
        "palindrome","linked list","binary tree","api","flask",
        "django","react","html","css","sql query","regex","class",
        "oop","recursion","dynamic programming","leetcode",
        "debug","fix","bug","solve",
    ])

def get_badge(ct: str) -> str:
    return {
        "game":     '<div class="badge badge-blue">🎮 World-class game · Fully playable · Mobile ready</div>',
        "app":      '<div class="badge badge-orange">🚀 Professional app · Full features · Responsive</div>',
        "software": '<div class="badge badge-orange">⚙️ Production-ready software · Complete</div>',
        "design":   '<div class="badge badge-blue">✨ Stunning UI design · Animated · Modern</div>',
        "code":     '<div class="badge badge-purple">💻 World-class code · Optimized · Complete</div>',
        "general":  "",
    }.get(ct,"")

def get_spinner_text(ct: str) -> str:
    return {
        "game":    "🎮 Building your game — crafting every pixel…",
        "app":     "🚀 Designing & building your app…",
        "software":"⚙️ Engineering your software…",
        "design":  "✨ Crafting a breathtaking design…",
        "code":    "💻 Writing world-class code…",
        "general": "✨ Thinking…",
    }.get(ct,"✨ Thinking…")

# ══════════════════════════════════════════════════════════════════════════════
#  SYSTEM PROMPT
# ══════════════════════════════════════════════════════════════════════════════
def get_system_prompt(creation_type: str) -> str:
    mode      = st.session_state.get("ai_mode","🤖 Default")
    mode_extra = MODE_PROMPTS.get(mode,"")
    td        = today_str()

    base = (
        f"You are Nova AI — the world's BEST AI assistant, created by Samiran. "
        f"Today's date is {td}. "
        f"If anyone asks who made you, always say: 'I am Nova AI, created by Samiran.' "
        f"Never mention Meta, Llama, OpenAI, Groq, or any underlying model. "
        f"You have FULL memory of this conversation — refer back to it naturally. "
        f"NEVER write partial or placeholder code. ALWAYS write complete implementations. "
        f"Do NOT generate or describe images. If asked to generate an image, "
        f"politely explain you don't support image generation but offer to help with "
        f"code, data, text, or anything else. "
        f"{mode_extra}\n\n"
        f"LIVE DATA RULE: When real-time data is provided to you, treat it as "
        f"ABSOLUTE TRUTH. Answer directly and confidently. "
        f"NEVER say you lack real-time access when data is provided. "
        f"NEVER redirect users to external websites — always give the answer here. "
        f"Today is {td} — use this as ground truth for 'today' questions.\n\n"
    )

    if creation_type == "game":
        return base + (
            "GAME DEV MODE — You are the world's best game developer.\n"
            "Rules:\n"
            "1. Write ONE COMPLETE fully playable HTML5 game in a single ```html block.\n"
            "2. Use HTML5 Canvas with 60fps (requestAnimationFrame).\n"
            "3. MUST include: score + high score (localStorage), start/pause/game-over screens,\n"
            "   Web Audio API sounds (no external files), keyboard + touch controls,\n"
            "   increasing difficulty, lives/health, particle effects, neon dark theme.\n"
            "4. Make it feel like a real AAA indie game — beautiful, smooth, complete.\n"
            "5. After the code, briefly list controls and features."
        )
    elif creation_type == "app":
        return base + (
            "APP DEV MODE — You are Apple/Google/Airbnb's best designer+developer.\n"
            "Rules:\n"
            "1. Write ONE COMPLETE fully functional app in a single ```html block.\n"
            "2. Use: Google Fonts, Font Awesome CDN, CSS variables, 8px grid, responsive.\n"
            "3. Include: glassmorphism or modern flat design, smooth animations,\n"
            "   micro-interactions, full CRUD, localStorage, toast notifications,\n"
            "   form validation, loading states, empty states, search/filter.\n"
            "4. Every button and feature must work perfectly.\n"
            "5. After the code, list all implemented features."
        )
    elif creation_type in ("software","design"):
        return base + (
            "DESIGN/SOFTWARE MODE — You are the world's best designer+architect.\n"
            "Rules:\n"
            "1. Write ONE COMPLETE implementation in a single ```html block.\n"
            "2. Stunning visuals: aurora gradients, 3D transforms, scroll animations,\n"
            "   glassmorphism, particle effects, micro-interactions.\n"
            "3. Fully functional — every feature must work.\n"
            "4. Professional quality — looks like a $50,000 product."
        )
    else:
        return base + (
            "CODING & GENERAL MODE:\n"
            "1. Write COMPLETE, fully working code — never partial, never placeholder.\n"
            "2. Best practices: clean names, error handling, comments, type hints.\n"
            "3. Optimal time/space complexity for algorithms.\n"
            "4. Always specify language in code block (```python, ```javascript, etc).\n"
            "5. Support ALL languages: Python, JS, TS, Java, C++, C, Rust, Go,\n"
            "   Ruby, PHP, Swift, Kotlin, SQL, Bash, R, Lua, Scala, and more.\n"
            "6. For web output: complete single-file HTML with embedded CSS+JS.\n"
            "7. For factual questions: use provided search data as primary source.\n"
            "   State answers directly, confidently, and completely."
        )

# ══════════════════════════════════════════════════════════════════════════════
#  BUILD MESSAGES (full conversation history)
# ══════════════════════════════════════════════════════════════════════════════
def build_messages(user_query: str, search_results: str = "",
                   creation_type: str = "general") -> list:
    messages = [{"role":"system","content":get_system_prompt(creation_type)}]

    history = st.session_state.messages[:-1]
    if len(history) > MAX_HISTORY_TURNS * 2:
        history = history[-(MAX_HISTORY_TURNS * 2):]

    for msg in history:
        content = re.sub(r"<div[^>]*>.*?</div>","",msg["content"],flags=re.DOTALL)
        content = re.sub(r"<[^>]+>","",content).strip()
        if content:
            messages.append({"role":msg["role"],"content":content[:3000]})

    if search_results:
        user_content = (
            f"=== LIVE REAL-TIME DATA (fetched right now — {today_str()}) ===\n"
            f"{search_results}\n\n"
            f"=== USER QUESTION ===\n{user_query}\n\n"
            f"Use the live data above as your primary source. "
            f"Answer directly, confidently, and completely. "
            f"Today is {today_str()}."
        )
    else:
        user_content = user_query

    messages.append({"role":"user","content":user_content[:5000]})
    return messages

# ══════════════════════════════════════════════════════════════════════════════
#  CODE UTILITIES
# ══════════════════════════════════════════════════════════════════════════════
def run_code(code: str, lang: str) -> str:
    try:
        l, v = LANGUAGE_MAP.get(lang.lower(),("python","3.10.0"))
        resp = requests.post(
            "https://emkc.org/api/v2/piston/execute",
            json={"language":l,"version":v,
                  "files":[{"name":f"main.{lang[:3]}","content":code}],
                  "stdin":"","args":[],
                  "compile_timeout":10000,"run_timeout":5000},
            timeout=15
        )
        result = resp.json()
        run    = result.get("run",{})
        out    = run.get("stdout","").strip()
        err    = run.get("stderr","").strip()
        comp   = result.get("compile",{}).get("stderr","").strip()
        if comp: return f"❌ Compile Error:\n{comp}"
        if err:  return f"❌ Error:\n{err}"
        return out or "✅ Ran successfully (no output)"
    except Exception as e:
        return f"❌ Runner failed: {e}"

def extract_code_blocks(text: str) -> list:
    matches = re.findall(r"```(\w+)?\n([\s\S]*?)```", text)
    return [(lang.lower() if lang else "text", code.strip())
            for lang,code in matches]

def build_html_preview(blocks: list) -> str:
    html_part = css_part = js_part = full_html = ""
    for lang, code in blocks:
        if lang == "html":
            if "<!doctype" in code.lower() or "<html" in code.lower():
                full_html = code
            else:
                html_part = code
        elif lang == "css":  css_part = code
        elif lang in ("javascript","js"): js_part = code
    if full_html: return full_html
    if html_part or css_part or js_part:
        return (
            "<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1.0'>"
            f"<title>Nova AI</title><style>{css_part}</style></head>"
            f"<body>{html_part}<script>{js_part}</script></body></html>"
        )
    return ""

# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for key, default in [
    ("messages", []),
    ("temperature", 0.25),
    ("max_tokens", 4096),
    ("ai_mode", "🤖 Default"),
    ("uploaded_file_content", None),
    ("uploaded_file_name", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1.2rem 0 .8rem'>
        <div style='font-size:1.4rem;font-weight:700;
                    font-family:Space Mono,monospace;color:#00e5ff'>
            ✨ Nova AI
        </div>
        <div style='font-size:11px;color:#64748b;margin-top:.3rem'>
            Created by Samiran · v3.0
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown("### ⚙️ Model Settings")
    st.session_state["temperature"] = st.slider(
        "Temperature",0.0,1.0,
        value=st.session_state["temperature"],step=0.05,
        help="Low = factual & precise  |  High = creative & expressive"
    )
    st.session_state["max_tokens"] = st.select_slider(
        "Max Response Length",
        options=[512,1024,2048,4096,8192],
        value=st.session_state["max_tokens"]
    )
    st.divider()

    st.markdown("### 🎭 AI Mode")
    st.session_state["ai_mode"] = st.selectbox(
        "Mode", list(MODE_PROMPTS.keys()),
        index=0, label_visibility="collapsed"
    )
    st.divider()

    st.markdown("### 📁 File Analysis")
    uploaded = st.file_uploader(
        "Upload a file to analyze",
        type=["txt","csv","json","py","js","ts","html","css",
              "java","cpp","c","md","rs","go"],
        label_visibility="collapsed"
    )
    if uploaded:
        content = read_uploaded_file(uploaded)
        st.session_state["uploaded_file_content"] = content
        st.session_state["uploaded_file_name"]    = uploaded.name
        st.success(f"✅ {uploaded.name} ready — ask me anything about it!")
    if st.session_state.get("uploaded_file_content"):
        if st.button("🗑️ Clear file"):
            st.session_state["uploaded_file_content"] = None
            st.session_state["uploaded_file_name"]    = None
            st.rerun()
    st.divider()

    st.markdown("### 🛠️ Quick Tools")

    with st.expander("💱 Currency Converter"):
        amt = st.number_input("Amount",value=1.0,min_value=0.0,key="sb_amt")
        c1, c2 = st.columns(2)
        with c1: fc = st.selectbox("From",CURRENCIES,index=0, key="sb_fc")
        with c2: tc = st.selectbox("To",  CURRENCIES,index=3, key="sb_tc")
        if st.button("Convert 💱",key="sb_conv_btn"):
            with st.spinner("Fetching rates…"):
                st.markdown(get_exchange_rate(fc,tc,amt))

    with st.expander("📐 Unit Converter"):
        uin = st.text_input("e.g. 100 km to miles",key="sb_uin")
        if st.button("Convert 📐",key="sb_unit_btn"):
            res = convert_unit(uin)
            st.markdown(res if res else "⚠️ Try: '100 km to miles'")

    with st.expander("🔢 Calculator"):
        cin = st.text_input("e.g. sqrt(144) + sin(pi/2)",key="sb_cin")
        if st.button("Calculate 🔢",key="sb_calc_btn"):
            res = solve_math(cin)
            if res:
                st.markdown(
                    f'<div class="result-box orange" style="font-family:Space Mono,'
                    f'monospace;font-size:15px;color:#f59e0b">= {res}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.warning("Could not evaluate.")

    with st.expander("📱 QR Generator"):
        qin = st.text_input("Text or URL",key="sb_qin")
        if st.button("Generate QR 📱",key="sb_qr_btn") and qin:
            url = qr_url(qin)
            st.image(url, width=200)
            st.markdown(f"[⬇️ Download QR]({url})")

    st.divider()

    st.markdown("### 💾 Export Chat")
    if st.session_state["messages"]:
        ca, cb = st.columns(2)
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        with ca:
            st.download_button(
                "📝 Markdown", data=export_md(),
                file_name=f"nova_{ts}.md",
                mime="text/markdown",
                use_container_width=True
            )
        with cb:
            st.download_button(
                "📊 JSON", data=export_json_chat(),
                file_name=f"nova_{ts}.json",
                mime="application/json",
                use_container_width=True
            )
    else:
        st.caption("No messages to export yet.")

    st.divider()
    st.markdown(
        f"<div style='text-align:center;font-size:10px;color:#374151'>"
        f"Nova AI · Made by Samiran<br>{datetime.now().strftime('%B %Y')}</div>",
        unsafe_allow_html=True
    )

# ══════════════════════════════════════════════════════════════════════════════
#  HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero">
    <div class="hero-badge">LIVE · FREE · UNLIMITED · REAL-TIME</div>
    <h1>Nova<span> AI</span></h1>
    <p>The world's smartest AI — builds games, apps, analyzes files,
       converts anything & knows everything live.</p>
</div>
<div class="stats-row">
    <div class="stat-pill"><span class="dot dot-purple"></span>🧠 Full Memory</div>
    <div class="stat-pill"><span class="dot dot-blue"></span>🏏 Live Sports</div>
    <div class="stat-pill"><span class="dot dot-orange"></span>🎮 Games & Apps</div>
    <div class="stat-pill"><span class="dot dot-green"></span>📁 File Analysis</div>
    <div class="stat-pill"><span class="dot dot-green"></span>💱 Currency & Units</div>
    <div class="stat-pill"><span class="dot dot-blue"></span>🌐 URL Reader</div>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

# ── Toolbar ───────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([5,1,1])
with col2:
    count = len([m for m in st.session_state.messages if m["role"]=="user"])
    st.markdown(
        f"<p style='text-align:right;color:var(--muted);font-size:12px;"
        f"padding-top:.5rem'>{count} msg{'s' if count!=1 else ''}</p>",
        unsafe_allow_html=True
    )
with col3:
    if st.button("🗑️ Clear"):
        st.session_state.messages = []
        st.rerun()

# ── Chat history display ──────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center;padding:1.5rem 1rem .8rem">
        <div style="font-size:2rem;margin-bottom:.5rem">✨</div>
        <p style="font-size:.95rem;font-weight:600;color:#94a3b8;margin-bottom:1rem">
            What would you like to do today?
        </p>
    </div>
    <div class="category-grid">
        <div class="category-card">
            <div class="category-icon">🎮</div>
            <div class="category-title">Games</div>
            <div class="category-examples">Snake · Tetris · Chess<br>2048 · Pacman · RPG</div>
        </div>
        <div class="category-card">
            <div class="category-icon">🚀</div>
            <div class="category-title">Apps & Software</div>
            <div class="category-examples">Dashboard · Todo<br>E-commerce · Portfolio</div>
        </div>
        <div class="category-card">
            <div class="category-icon">💻</div>
            <div class="category-title">Code</div>
            <div class="category-examples">Python · JS · Java<br>C++ · Go · Rust · SQL</div>
        </div>
        <div class="category-card">
            <div class="category-icon">📁</div>
            <div class="category-title">File Analysis</div>
            <div class="category-examples">Upload CSV/JSON/Code<br>AI reads & analyzes</div>
        </div>
        <div class="category-card">
            <div class="category-icon">🌐</div>
            <div class="category-title">Live Data</div>
            <div class="category-examples">Cricket · Stocks<br>Weather · News · URL</div>
        </div>
        <div class="category-card">
            <div class="category-icon">🛠️</div>
            <div class="category-title">Tools</div>
            <div class="category-examples">Currency · Units · QR<br>Calculator · Export</div>
        </div>
    </div>
    <div class="divider"></div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            meta = msg.get("meta","")
            if meta: st.markdown(meta, unsafe_allow_html=True)
            st.markdown(msg["content"])

# ══════════════════════════════════════════════════════════════════════════════
#  MASTER CHAT HANDLER
# ══════════════════════════════════════════════════════════════════════════════
if prompt := st.chat_input(
    "Ask anything — live scores, build games, analyze files, convert units…"
):
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = ""
        meta     = ""

        # ── 1. QR CODE ────────────────────────────────────────────────────────
        if is_qr_query(prompt):
            content = extract_qr_content(prompt)
            url     = qr_url(content)
            meta    = '<div class="badge badge-green">📱 QR Code generated</div>'
            st.markdown(meta, unsafe_allow_html=True)
            st.markdown(f"**QR Code for:** `{content}`")
            st.image(url, width=260)
            st.markdown(f'<a href="{url}" class="btn-download" target="_blank">'
                        f'⬇️ Download QR</a>', unsafe_allow_html=True)
            response = f"✅ QR Code generated for: `{content}`"

        # ── 2. CURRENCY ───────────────────────────────────────────────────────
        elif is_currency_query(prompt):
            amount, fc, tc = extract_currency_params(prompt)
            with st.spinner("💱 Fetching live exchange rates…"):
                result = get_exchange_rate(fc, tc, amount)
            meta = '<div class="badge badge-green">💱 Live exchange rate</div>'
            st.markdown(meta, unsafe_allow_html=True)
            st.markdown(
                f'<div class="result-box green">{result}</div>',
                unsafe_allow_html=True
            )
            response = result

        # ── 3. UNIT CONVERTER ─────────────────────────────────────────────────
        elif is_unit_query(prompt):
            result = convert_unit(prompt)
            if result:
                meta = '<div class="badge badge-orange">📐 Unit converted</div>'
                st.markdown(meta, unsafe_allow_html=True)
                st.markdown(
                    f'<div class="result-box orange">{result}</div>',
                    unsafe_allow_html=True
                )
                response = result

        # ── 4. MATH ───────────────────────────────────────────────────────────
        if not response and is_math_query(prompt):
            result = solve_math(prompt)
            if result:
                meta = '<div class="badge badge-orange">🔢 Calculated instantly</div>'
                st.markdown(meta, unsafe_allow_html=True)
                st.markdown(
                    f'<div class="result-box orange" '
                    f'style="font-family:Space Mono,monospace;'
                    f'font-size:16px;color:#f59e0b">= {result}</div>',
                    unsafe_allow_html=True
                )
                msgs = build_messages(
                    f"The answer to '{prompt}' is {result}. "
                    f"Briefly explain this calculation in 2-3 lines.",
                    creation_type="general"
                )
                explanation = stream_response(
                    msgs, max_tokens=300,
                    temperature=st.session_state["temperature"]
                )
                response = f"= **{result}**\n\n{explanation}"

        # ── 5. URL READER ─────────────────────────────────────────────────────
        if not response and is_url_query(prompt):
            url = extract_url(prompt)
            if url:
                with st.spinner(f"🌐 Reading {url[:55]}…"):
                    page = fetch_url_content(url)
                meta = f'<div class="badge badge-green">🌐 Read: {url[:45]}…</div>'
                st.markdown(meta, unsafe_allow_html=True)
                augmented = (
                    f"URL: {url}\n\nExtracted content:\n{page}\n\n"
                    f"User request: {prompt}\n"
                    f"Answer based on the content above. Be thorough."
                )
                msgs     = build_messages(augmented, creation_type="general")
                response = stream_response(
                    msgs,
                    max_tokens=st.session_state["max_tokens"],
                    temperature=st.session_state["temperature"]
                )

        # ── 6. FILE ANALYSIS ──────────────────────────────────────────────────
        if not response and st.session_state.get("uploaded_file_content"):
            fname = st.session_state.get("uploaded_file_name","file")
            meta  = f'<div class="badge badge-purple">📁 Analyzing: {fname}</div>'
            st.markdown(meta, unsafe_allow_html=True)
            augmented = (
                f"File: '{fname}'\n\nContent:\n"
                f"{st.session_state['uploaded_file_content']}\n\n"
                f"User's request: {prompt}\n\n"
                f"Analyze this file thoroughly and answer the request."
            )
            msgs     = build_messages(augmented, creation_type="general")
            response = stream_response(
                msgs,
                max_tokens=st.session_state["max_tokens"],
                temperature=st.session_state["temperature"]
            )
            st.session_state["uploaded_file_content"] = None
            st.session_state["uploaded_file_name"]    = None

        # ── 7. STOCK ──────────────────────────────────────────────────────────
        if not response and is_stock_query(prompt):
            symbol, dname = extract_stock_symbol(prompt)
            if symbol:
                with st.spinner(f"📈 Fetching live price for {dname}…"):
                    sd = get_stock(symbol, dname)
                if "failed" not in sd.lower():
                    L = dict(l.split(": ",1) for l in sd.strip().splitlines() if ": " in l)
                    meta = '<div class="badge badge-green">📈 Live · Yahoo Finance</div>'
                    st.markdown(meta, unsafe_allow_html=True)
                    response = (
                        f"### 📈 {L.get('Name',dname)}\n"
                        f"_{L.get('Exchange','')} · Market: {L.get('Market','N/A')}_\n\n"
                        f"| Detail | Value |\n|--------|-------|\n"
                        f"| 💰 Price | **{L.get('Price','N/A')}** |\n"
                        f"| 📊 Change | {L.get('Change','N/A')} |\n"
                        f"| 📈 Day High | {L.get('Day High','N/A')} |\n"
                        f"| 📉 Day Low | {L.get('Day Low','N/A')} |\n"
                        f"| 🔢 Volume | {L.get('Volume','N/A')} |\n\n"
                        f"_Data from Yahoo Finance · Delayed ~15 min_"
                    )
                    st.markdown(response)

        # ── 8. SPORTS / CRICKET ───────────────────────────────────────────────
        if not response and is_sports_query(prompt):
            with st.spinner("🏏 Fetching real-time sports data from all sources…"):
                cricket = fetch_live_cricket()
                sport_term = "general sports"
                for k,v in SPORTS_MAP.items():
                    if k in prompt.lower():
                        sport_term = v; break
                extra = get_sports_news(sport_term) if sport_term != "general sports" else ""
                sports_data = "\n\n".join(filter(None,[cricket, extra]))

            meta = '<div class="badge badge-red">🔴 LIVE SPORTS DATA</div>'
            st.markdown(meta, unsafe_allow_html=True)
            msgs     = build_messages(prompt, search_results=sports_data,
                                      creation_type="general")
            response = stream_response(msgs, max_tokens=1024, temperature=0.1)

        # ── 9. NEWS ───────────────────────────────────────────────────────────
        if not response and is_news_query(prompt):
            with st.spinner("📰 Fetching latest news…"):
                topic = extract_news_topic(prompt)
                news  = get_news(topic)
            meta = '<div class="badge badge-green">📰 Live news</div>'
            st.markdown(meta, unsafe_allow_html=True)
            response = f"### 📰 {topic.title()}\n\n{news}"
            st.markdown(response)

        # ── 10. WEATHER ───────────────────────────────────────────────────────
        if not response and is_weather_query(prompt):
            with st.spinner("🌤️ Fetching live weather…"):
                city = extract_city(prompt)
                wd   = get_weather(city)
            if "failed" not in wd.lower():
                L = dict(l.split(": ",1) for l in wd.strip().splitlines() if ": " in l)
                meta = '<div class="badge badge-green">🌤️ Live weather</div>'
                st.markdown(meta, unsafe_allow_html=True)
                response = (
                    f"### 🌍 Weather — {L.get('City',city)}\n\n"
                    f"| Detail | Value |\n|--------|-------|\n"
                    f"| 🌡️ Temperature | {L.get('Temperature','N/A')} |\n"
                    f"| 🌤️ Condition | {L.get('Condition','N/A')} |\n"
                    f"| 💧 Humidity | {L.get('Humidity','N/A')} |\n"
                    f"| 💨 Wind Speed | {L.get('Wind Speed','N/A')} |\n"
                    f"| 👁️ Visibility | {L.get('Visibility','N/A')} |\n"
                    f"| ☀️ UV Index | {L.get('UV Index','N/A')} |\n"
                )
                st.markdown(response)
            else:
                response = f"❌ Could not fetch weather for **{city}**. Please try again."
                st.markdown(response)

        # ── 11. GENERAL / CODE / CREATION ─────────────────────────────────────
        if not response:
            ct             = classify_creation(prompt)
            search_results = ""
            searched       = False

            if needs_search(prompt):
                with st.spinner("🔍 Searching the web for latest info…"):
                    search_results = web_search(prompt)
                    facts = get_current_facts(prompt)
                    if facts: search_results += "\n\nRecent headlines:\n" + facts
                    searched = True

            # badges
            if searched:
                st.markdown('<div class="badge badge-green">🔍 Web search</div>',
                            unsafe_allow_html=True)
                meta = '<div class="badge badge-green">🔍 Web search</div>'
            badge = get_badge(ct)
            if badge:
                st.markdown(badge, unsafe_allow_html=True)
                meta = meta + badge if meta else badge

            turns = len(st.session_state.messages) // 2
            if turns > 1:
                mem = (f'<div class="badge badge-purple">'
                       f'🧠 {turns} turns remembered</div>')
                st.markdown(mem, unsafe_allow_html=True)
                meta = meta + mem if meta else mem

            for attempt in range(3):
                try:
                    spin = get_spinner_text(ct) if attempt == 0 else "Retrying ⏳"
                    with st.spinner(spin):
                        if attempt > 0: time.sleep(60)

                    msgs     = build_messages(prompt, search_results, ct)
                    response = stream_response(
                        msgs,
                        max_tokens=st.session_state["max_tokens"],
                        temperature=st.session_state["temperature"]
                    )

                    # HTML preview
                    blocks    = extract_code_blocks(response)
                    langs     = [l for l,_ in blocks]
                    is_web    = any(l in ("html","css","javascript","js") for l in langs)
                    code, lang = (blocks[0][1], blocks[0][0]) if blocks else (None, None)

                    if is_web:
                        html_src = build_html_preview(blocks)
                        if html_src:
                            st.markdown("---")
                            plabels = {
                                "game":    "🎮 Live Game — Play it here!",
                                "app":     "🚀 Live App Preview",
                                "software":"⚙️ Live Software Preview",
                                "design":  "✨ Live Design Preview",
                            }
                            st.markdown(f"### {plabels.get(ct,'🖥️ Live Preview')}")
                            h = 650 if ct in ("game","app","software") else 520
                            st.components.v1.html(html_src, height=h, scrolling=True)
                            b64   = base64.b64encode(html_src.encode()).decode()
                            fmap  = {
                                "game":"nova_game.html","app":"nova_app.html",
                                "software":"nova_software.html","design":"nova_design.html"
                            }
                            fname = fmap.get(ct,"nova_ai.html")
                            st.markdown(
                                f'<a href="data:text/html;base64,{b64}" '
                                f'download="{fname}" class="btn-download">'
                                f'⬇️ Download {fname}</a>',
                                unsafe_allow_html=True
                            )

                    elif code and lang and lang not in ("html","css"):
                        rk = f"run_{len(st.session_state.messages)}"
                        if st.button(f"▶ Run {lang.title()}", key=rk):
                            with st.spinner(f"⚙️ Running {lang}…"):
                                out = run_code(code, lang)
                            cls = "error-box" if "❌" in out else "output-box"
                            st.markdown(f'<div class="{cls}">{out}</div>',
                                        unsafe_allow_html=True)
                    break

                except Exception as e:
                    if "rate_limit_exceeded" in str(e) and attempt < 2:
                        continue
                    st.error(f"❌ Error: {e}")
                    break

        # ── Save to session ───────────────────────────────────────────────────
        if response:
            st.session_state.messages.append({
                "role":    "assistant",
                "content": response,
                "meta":    meta,
            })
