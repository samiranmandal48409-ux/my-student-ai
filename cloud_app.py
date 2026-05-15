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

/* Sidebar */
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
[data-testid="stSidebar"] .stSlider > div { color: var(--accent) !important; }
[data-testid="stSidebar"] label { color: var(--muted) !important; font-size: 12px !important; }
[data-testid="stSidebar"] h3 {
    color: var(--accent) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 13px !important; margin: .8rem 0 .4rem !important;
}
[data-testid="stSidebar"] hr { border-color: var(--border) !important; }
[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--muted) !important;
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
    border-radius: 8px !important;
}

/* Hero */
.hero { text-align: center; padding: 2.5rem 1rem 1.5rem; position: relative; }
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
    color: var(--accent); letter-spacing: .05em; margin-bottom: 1rem;
}
.hero-badge::before { content: '●'; font-size: 8px; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }
.hero h1 {
    font-family: 'Space Mono', monospace !important;
    font-size: clamp(1.8rem,4vw,2.6rem) !important;
    font-weight: 700 !important; color: #fff !important;
    line-height: 1.15 !important; letter-spacing: -.02em;
    margin-bottom: .5rem !important;
}
.hero h1 span { color: var(--accent); }
.hero p { font-size: .95rem; color: var(--muted); font-weight: 300; max-width: 420px; margin: 0 auto; }
.divider { height: 1px; background: linear-gradient(90deg,transparent,var(--border),transparent); margin: 1.2rem 0; }

/* Stats */
.stats-row { display: flex; gap: .6rem; margin: 1rem 0 1.5rem; justify-content: center; flex-wrap: wrap; }
.stat-pill {
    display: flex; align-items: center; gap: 6px;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 999px; padding: 5px 12px; font-size: 12px; color: var(--muted);
}
.stat-pill .dot { width:6px; height:6px; border-radius:50%; }
.dot-green  { background: var(--green);  box-shadow: 0 0 5px var(--green); }
.dot-blue   { background: var(--accent); box-shadow: 0 0 5px var(--accent); }
.dot-purple { background: var(--purple); box-shadow: 0 0 5px var(--purple); }
.dot-orange { background: var(--orange); box-shadow: 0 0 5px var(--orange); }

/* Chat messages */
[data-testid="stChatMessage"] { background: transparent !important; border: none !important; padding: 0 !important; }
[data-testid="stChatMessage"] > div { background: transparent !important; }
[data-testid="stChatMessageContent"] { background: transparent !important; }
.stChatMessage {
    border-radius: var(--radius) !important; padding: 1rem 1.2rem !important;
    border: 1px solid var(--border) !important; margin-bottom: .6rem !important;
    background: var(--surface) !important; animation: fadeUp .25s ease;
}
@keyframes fadeUp { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) {
    background: var(--user-bg) !important; border-color: rgba(0,229,255,.15) !important;
}

/* Code */
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

/* Input */
[data-testid="stChatInputContainer"] {
    position: fixed !important; bottom: 0 !important; left: 50% !important;
    transform: translateX(-50%) !important; width: 100% !important;
    max-width: 860px !important; padding: 1rem 1.5rem 1.5rem !important;
    background: linear-gradient(to top, var(--bg) 70%, transparent) !important;
    backdrop-filter: blur(10px); z-index: 999 !important;
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

/* Badges */
.search-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(16,185,129,.08); border: 1px solid rgba(16,185,129,.2);
    border-radius: 6px; padding: 3px 10px; font-size: 11px; color: var(--green); margin-bottom: .5rem;
}
.live-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(239,68,68,.08); border: 1px solid rgba(239,68,68,.3);
    border-radius: 6px; padding: 3px 10px; font-size: 11px; color: #fca5a5; margin-bottom: .5rem;
}
.code-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(124,58,237,.08); border: 1px solid rgba(124,58,237,.3);
    border-radius: 6px; padding: 3px 10px; font-size: 11px; color: #a78bfa; margin-bottom: .5rem;
}
.app-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(245,158,11,.08); border: 1px solid rgba(245,158,11,.3);
    border-radius: 6px; padding: 3px 10px; font-size: 11px; color: var(--orange); margin-bottom: .5rem;
}
.game-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(0,229,255,.08); border: 1px solid rgba(0,229,255,.25);
    border-radius: 6px; padding: 3px 10px; font-size: 11px; color: var(--accent); margin-bottom: .5rem;
}
.preview-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(0,229,255,.08); border: 1px solid rgba(0,229,255,.25);
    border-radius: 6px; padding: 3px 10px; font-size: 11px; color: var(--accent); margin-bottom: .5rem;
}
.memory-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(124,58,237,.08); border: 1px solid rgba(124,58,237,.25);
    border-radius: 6px; padding: 3px 10px; font-size: 11px; color: #a78bfa; margin-bottom: .5rem;
}
.url-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(16,185,129,.08); border: 1px solid rgba(16,185,129,.25);
    border-radius: 6px; padding: 3px 10px; font-size: 11px; color: var(--green); margin-bottom: .5rem;
}
.math-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(245,158,11,.08); border: 1px solid rgba(245,158,11,.25);
    border-radius: 6px; padding: 3px 10px; font-size: 11px; color: var(--orange); margin-bottom: .5rem;
}
.file-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(124,58,237,.08); border: 1px solid rgba(124,58,237,.25);
    border-radius: 6px; padding: 3px 10px; font-size: 11px; color: #a78bfa; margin-bottom: .5rem;
}

/* Output boxes */
.output-box {
    background: #0d1117; border: 1px solid var(--border);
    border-left: 3px solid var(--green); border-radius: 10px;
    padding: .8rem 1.2rem; font-family: 'Space Mono', monospace;
    font-size: 13px; color: #a3e635; margin-top: .5rem; white-space: pre-wrap;
}
.error-box {
    background: #1a0a0a; border: 1px solid #7f1d1d;
    border-left: 3px solid #ef4444; border-radius: 10px;
    padding: .8rem 1.2rem; font-family: 'Space Mono', monospace;
    font-size: 13px; color: #fca5a5; margin-top: .5rem; white-space: pre-wrap;
}
.math-result {
    background: linear-gradient(135deg,#0d1117,#111827);
    border: 1px solid var(--border); border-left: 3px solid var(--orange);
    border-radius: 10px; padding: .8rem 1.2rem;
    font-family: 'Space Mono', monospace; font-size: 15px;
    color: var(--orange); margin: .5rem 0;
}
.currency-result {
    background: linear-gradient(135deg,#0d1117,#111827);
    border: 1px solid var(--border); border-left: 3px solid var(--green);
    border-radius: 10px; padding: .8rem 1.2rem; font-size: 14px;
    color: var(--text); margin: .5rem 0;
}

/* Download button */
.btn-download {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(0,229,255,.1); border: 1px solid rgba(0,229,255,.3);
    color: var(--accent); padding: 5px 12px; border-radius: 7px;
    text-decoration: none; font-size: 12px;
    font-family: 'DM Sans', sans-serif; font-weight: 500;
}

/* Category grid */
.category-grid {
    display: grid; grid-template-columns: repeat(auto-fit,minmax(170px,1fr));
    gap: .8rem; margin: 1.2rem 0;
}
.category-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 1rem; text-align: center;
    transition: border-color .2s, transform .2s;
}
.category-card:hover { border-color: var(--accent); transform: translateY(-2px); }
.category-icon { font-size: 1.6rem; margin-bottom: .4rem; }
.category-title { font-size: 12.5px; font-weight: 600; color: #94a3b8; margin-bottom: .25rem; }
.category-examples { font-size: 11px; color: var(--muted); line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  CLIENT & CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_KEY = "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"

client = Groq(api_key=GROQ_KEY)
MODEL  = "llama-3.3-70b-versatile"
MAX_HISTORY_TURNS = 20

CURRENCIES = [
    "USD","EUR","GBP","INR","JPY","CAD","AUD","CHF","CNY","HKD",
    "SGD","NOK","SEK","DKK","NZD","MXN","BRL","ZAR","RUB","KRW",
    "TRY","AED","SAR","THB","IDR","MYR","PHP","VND","EGP","PKR",
]

MODE_PROMPTS = {
    "🤖 Default":  "",
    "💻 Coder":    "You are in CODER MODE. Focus exclusively on writing perfect production-ready code. Always include error handling, type hints, and comments.",
    "🎨 Creative": "You are in CREATIVE MODE. Be imaginative and expressive. Think outside the box and offer unique, creative solutions.",
    "📊 Analyst":  "You are in ANALYST MODE. Be data-driven and precise. Use bullet points, tables, and structured formats.",
    "🎓 Teacher":  "You are in TEACHER MODE. Explain everything simply step by step. Use examples and analogies.",
    "✍️ Writer":   "You are in WRITER MODE. Focus on clear engaging writing. Help polish grammar, style, and content.",
}

# ══════════════════════════════════════════════════════════════════════════════
#  STREAMING
# ══════════════════════════════════════════════════════════════════════════════
def stream_response(messages: list, max_tokens: int = 4096, temperature: float = 0.25) -> str:
    full_response = ""
    placeholder   = st.empty()
    try:
        stream = client.chat.completions.create(
            messages=messages, model=MODEL,
            max_tokens=max_tokens, temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                full_response += delta
                placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)
        return full_response
    except Exception as e:
        placeholder.error(f"❌ Error: {e}")
        return ""

# ══════════════════════════════════════════════════════════════════════════════
#  URL READER
# ══════════════════════════════════════════════════════════════════════════════
def fetch_url_content(url: str) -> str:
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                   "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"},
            timeout=10
        )
        resp.raise_for_status()
        text = resp.text
        for tag in ['script','style','nav','footer','header','aside']:
            text = re.sub(f'<{tag}[^>]*>[\\s\\S]*?</{tag}>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:4000] if len(text) > 100 else "Could not extract meaningful content."
    except Exception as e:
        return f"URL fetch failed: {e}"

def is_url_query(query: str) -> bool:
    return bool(re.search(r'https?://\S+', query))

def extract_url(query: str) -> str:
    match = re.search(r'https?://\S+', query)
    return match.group(0).rstrip('.,)>') if match else ""

# ══════════════════════════════════════════════════════════════════════════════
#  MATH ENGINE
# ══════════════════════════════════════════════════════════════════════════════
def solve_math(expression: str) -> str:
    try:
        expr = re.sub(
            r'(calculate|compute|solve|evaluate|what is|how much is|=)',
            '', expression, flags=re.IGNORECASE
        ).strip()
        expr = re.sub(r'[?!]', '', expr).strip()
        expr = expr.replace('^', '**')
        safe_dict = {
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "asin": math.asin, "acos": math.acos, "atan": math.atan,
            "log": math.log10, "ln": math.log, "log2": math.log2,
            "sqrt": math.sqrt, "exp": math.exp, "abs": abs,
            "pi": math.pi, "e": math.e, "ceil": math.ceil,
            "floor": math.floor, "round": round, "pow": math.pow,
            "factorial": math.factorial,
        }
        result = eval(expr, {"__builtins__": {}}, safe_dict)
        if isinstance(result, float):
            result = round(result, 10)
        return str(result)
    except:
        return ""

def is_math_query(query: str) -> bool:
    q = query.lower()
    if any(k in q for k in ["stock","weather","ipl","cricket","news","price of","how much is 1"]):
        return False
    triggers = ["calculate","compute","sqrt","factorial","sin","cos","tan","log"]
    has_num  = bool(re.search(r'\d', query))
    has_ops  = bool(re.search(r'[+\-*/^%()]', query))
    has_trig = any(t in q for t in triggers)
    return has_num and (has_ops or has_trig)

# ══════════════════════════════════════════════════════════════════════════════
#  CURRENCY CONVERTER
# ══════════════════════════════════════════════════════════════════════════════
def get_exchange_rate(from_curr: str, to_curr: str, amount: float = 1.0) -> str:
    try:
        resp = requests.get(
            f"https://api.exchangerate-api.com/v4/latest/{from_curr.upper()}",
            timeout=6
        )
        data  = resp.json()
        rates = data.get("rates", {})
        to_c  = to_curr.upper()
        if to_c not in rates:
            return f"❌ Currency '{to_c}' not found."
        rate   = rates[to_c]
        result = amount * rate
        return (
            f"**{amount:,.2f} {from_curr.upper()}** = **{result:,.4f} {to_c}**\n\n"
            f"Rate: 1 {from_curr.upper()} = {rate:.6f} {to_c}\n"
            f"_Updated: {data.get('date','today')} · ExchangeRate-API_"
        )
    except Exception as e:
        return f"Currency fetch failed: {e}"

def is_currency_query(query: str) -> bool:
    q    = query.lower()
    curr = [c.lower() for c in CURRENCIES]
    triggers = ["convert","exchange rate","to inr","to usd","to eur","to gbp",
                "how much is","in dollars","in rupees","in euros"]
    found = sum(1 for c in curr if re.search(r'\b'+c+r'\b', q))
    return found >= 2 or (any(t in q for t in triggers) and found >= 1)

def extract_currency_params(query: str) -> tuple:
    q     = query.lower()
    curr  = [c.lower() for c in CURRENCIES]
    found = [c for c in curr if re.search(r'\b'+c+r'\b', q)]
    am    = re.search(r'(\d+(?:\.\d+)?)', query)
    amount = float(am.group(1)) if am else 1.0
    if len(found) >= 2:
        return amount, found[0].upper(), found[1].upper()
    elif len(found) == 1:
        other = "INR" if found[0] != "inr" else "USD"
        return amount, found[0].upper(), other
    return amount, "USD", "INR"

# ══════════════════════════════════════════════════════════════════════════════
#  UNIT CONVERTER
# ══════════════════════════════════════════════════════════════════════════════
UNIT_CONVERSIONS = {
    ("celsius","fahrenheit"):    lambda x: (x*9/5)+32,
    ("fahrenheit","celsius"):    lambda x: (x-32)*5/9,
    ("celsius","kelvin"):        lambda x: x+273.15,
    ("kelvin","celsius"):        lambda x: x-273.15,
    ("fahrenheit","kelvin"):     lambda x: ((x-32)*5/9)+273.15,
    ("km","miles"):              lambda x: x*0.621371,
    ("miles","km"):              lambda x: x*1.60934,
    ("meters","feet"):           lambda x: x*3.28084,
    ("feet","meters"):           lambda x: x/3.28084,
    ("cm","inches"):             lambda x: x*0.393701,
    ("inches","cm"):             lambda x: x*2.54,
    ("km","meters"):             lambda x: x*1000,
    ("meters","km"):             lambda x: x/1000,
    ("kg","pounds"):             lambda x: x*2.20462,
    ("pounds","kg"):             lambda x: x/2.20462,
    ("kg","grams"):              lambda x: x*1000,
    ("grams","kg"):              lambda x: x/1000,
    ("tons","kg"):               lambda x: x*1000,
    ("kg","tons"):               lambda x: x/1000,
    ("kmh","mph"):               lambda x: x*0.621371,
    ("mph","kmh"):               lambda x: x*1.60934,
    ("ms","kmh"):                lambda x: x*3.6,
    ("kmh","ms"):                lambda x: x/3.6,
    ("sqm","sqft"):              lambda x: x*10.7639,
    ("sqft","sqm"):              lambda x: x/10.7639,
    ("acres","sqm"):             lambda x: x*4046.86,
    ("hectares","acres"):        lambda x: x*2.47105,
    ("liters","gallons"):        lambda x: x*0.264172,
    ("gallons","liters"):        lambda x: x*3.78541,
    ("ml","liters"):             lambda x: x/1000,
    ("liters","ml"):             lambda x: x*1000,
    ("gb","mb"):                 lambda x: x*1024,
    ("mb","gb"):                 lambda x: x/1024,
    ("tb","gb"):                 lambda x: x*1024,
    ("gb","tb"):                 lambda x: x/1024,
    ("mb","kb"):                 lambda x: x*1024,
    ("kb","mb"):                 lambda x: x/1024,
}

def convert_unit(query: str) -> str:
    q = query.lower()
    am = re.search(r'(\d+(?:\.\d+)?)', query)
    amount = float(am.group(1)) if am else 1.0
    for (fu, tu), fn in UNIT_CONVERSIONS.items():
        if fu in q and tu in q:
            result = fn(amount)
            return f"**{amount} {fu}** = **{round(result,6)} {tu}**"
    return ""

def is_unit_query(query: str) -> bool:
    q     = query.lower()
    units = ["km","miles","meters","feet","cm","inches","kg","pounds","grams",
             "celsius","fahrenheit","kelvin","liters","gallons","mph","kmh",
             "acres","hectares","gb","mb","tb","kb","sqm","sqft","ms"]
    triggers = ["convert","how many","how much","to","equals","in"]
    return (any(u in q for u in units) and
            any(t in q for t in triggers) and
            bool(re.search(r'\d', query)))

# ══════════════════════════════════════════════════════════════════════════════
#  QR CODE
# ══════════════════════════════════════════════════════════════════════════════
def generate_qr_url(text: str) -> str:
    return f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(text)}"

def is_qr_query(query: str) -> bool:
    q = query.lower()
    return any(k in q for k in ["qr code","qr for","generate qr","make qr","create qr","qr generator"])

def extract_qr_content(query: str) -> str:
    url_match = re.search(r'https?://\S+', query)
    if url_match: return url_match.group(0)
    stopwords = {"qr","code","generate","make","create","for","me","a","an","the","of","my"}
    return " ".join(w for w in query.replace("?","").split() if w.lower() not in stopwords).strip() or query

# ══════════════════════════════════════════════════════════════════════════════
#  FILE READER
# ══════════════════════════════════════════════════════════════════════════════
def read_uploaded_file(uploaded_file) -> str:
    try:
        fname = uploaded_file.name.lower()
        if fname.endswith(('.txt','.md','.py','.js','.ts','.html',
                           '.css','.java','.cpp','.c','.rs','.go')):
            return uploaded_file.read().decode('utf-8', errors='ignore')[:5000]
        elif fname.endswith('.csv'):
            content = uploaded_file.read().decode('utf-8', errors='ignore')
            lines   = content.split('\n')
            return (f"CSV — {len(lines)} rows\n\nFirst 50 rows:\n"
                    + '\n'.join(lines[:50]))
        elif fname.endswith('.json'):
            content = uploaded_file.read().decode('utf-8', errors='ignore')
            try:
                parsed = json.loads(content)
                return "JSON:\n" + json.dumps(parsed, indent=2)[:4000]
            except:
                return content[:4000]
        else:
            return f"File: {uploaded_file.name} (binary/unsupported — describe what you need)"
    except Exception as e:
        return f"File read error: {e}"

# ══════════════════════════════════════════════════════════════════════════════
#  CHAT EXPORT
# ══════════════════════════════════════════════════════════════════════════════
def export_markdown() -> str:
    lines = [
        "# Nova AI — Conversation Export",
        f"_Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n---\n"
    ]
    for msg in st.session_state.messages:
        role    = "🧑 You" if msg["role"] == "user" else "✨ Nova AI"
        content = re.sub(r'<[^>]+>', '', msg["content"]).strip()
        lines.append(f"### {role}\n{content}\n")
    return "\n".join(lines)

def export_json() -> str:
    return json.dumps(
        [{"role": m["role"], "content": re.sub(r'<[^>]+>','',m["content"]).strip()}
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
        data = resp.json()
        c    = data["current_condition"][0]
        area = data["nearest_area"][0]
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
        return f"Weather fetch failed: {e}"

def extract_city(query: str) -> str:
    m = re.search(
        r'(?:weather|temperature|forecast|humidity|climate)'
        r'\s+(?:report\s+)?(?:in|for|of|at)\s+([A-Za-z ,]+?)(?:\?|$)',
        query, re.IGNORECASE
    )
    if m: return m.group(1).strip().rstrip(",")
    sw = {"what","is","the","weather","report","temperature","forecast",
          "today","current","now","like","how","give","me","show",
          "humidity","climate","condition","conditions","a","an"}
    return " ".join(w for w in query.replace("?","").split()
                    if w.lower() not in sw).strip() or "Guwahati"

def is_weather_query(q: str) -> bool:
    return any(k in q.lower() for k in
               ["weather","temperature","forecast","humidity",
                "rain","sunny","cloudy","wind speed","climate today"])

# ══════════════════════════════════════════════════════════════════════════════
#  STOCKS
# ══════════════════════════════════════════════════════════════════════════════
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

def extract_stock_symbol(query: str) -> tuple:
    q = query.lower()
    for name, ticker in STOCK_ALIASES.items():
        if name in q: return ticker, name.title()
    m = re.search(r'\b([A-Z]{2,5})\b', query)
    if m: return m.group(1), m.group(1)
    return None, None

def get_stock_price(symbol: str, dname: str) -> str:
    try:
        resp = requests.get(
            f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=2d",
            headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"}, timeout=8
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
        if isinstance(vol, int): vol = f"{vol:,}"
        return (
            f"Name: {name}\nExchange: {meta.get('exchangeName','')}\n"
            f"Price: {curr} {price:,.2f}\n"
            f"Change: {arrow} {sign}{chg:.2f} ({sign}{pct:.2f}%)\n"
            f"Day High: {meta.get('regularMarketDayHigh','N/A')}\n"
            f"Day Low: {meta.get('regularMarketDayLow','N/A')}\n"
            f"Volume: {vol}\nMarket: {meta.get('marketState','')}"
        )
    except Exception as e:
        return f"Stock fetch failed: {e}"

def is_stock_query(query: str) -> bool:
    q = query.lower()
    return (any(a in q for a in ["stock","share price","stock price","price of",
                                  "market price","trading at","crypto","bitcoin",
                                  "ethereum","sensex","nifty","nasdaq","dow jones",
                                  "coin price"]) or
            any(k in q for k in STOCK_ALIASES))

# ══════════════════════════════════════════════════════════════════════════════
#  CRICKET / SPORTS
# ══════════════════════════════════════════════════════════════════════════════
def get_today_str() -> str:
    return datetime.now().strftime("%B %d, %Y")

def fetch_live_cricket() -> str:
    results = []
    try:
        resp = requests.get(
            "https://api.cricapi.com/v1/currentMatches",
            params={"apikey":"a52ea237-09e7-4d69-b7cc-e4f0e2a8c1f1","offset":0},
            timeout=6
        )
        data = resp.json()
        if data.get("status") == "success" and data.get("data"):
            for m in data["data"][:5]:
                scores = ""
                for s in m.get("score",[]):
                    if s.get("r"):
                        scores += f"\n  {s.get('inning','')}: {s.get('r','')}/{s.get('w','')} ({s.get('o','')} ov)"
                results.append(f"**{m.get('name','')}**\n  {m.get('status','')}{scores}")
    except: pass

    for q in [f"IPL 2025 today match {datetime.now().strftime('%B %d')} live score",
              "IPL 2025 CSK MI RCB KKR SRH PBKS DC GT LSG match today"]:
        try:
            url  = f"https://news.google.com/rss/search?q={requests.utils.quote(q)}&hl=en-IN&gl=IN&ceid=IN:en"
            resp = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=6)
            root = ET.fromstring(resp.content)
            items = []
            for item in root.findall(".//item")[:5]:
                title   = item.findtext("title","").strip()
                pub_raw = item.findtext("pubDate","")
                pub     = pub_raw[:22] if pub_raw else ""
                if title:
                    clean = title.split(" - ")[0].strip()
                    items.append(f"[{pub}] {clean}" if pub else clean)
            if items: results.append("📰 " + q + ":\n" + "\n".join(items))
        except: pass

    return "\n\n".join(results) if results else ""

SPORTS_MAP = {
    "cricket":"cricket","ipl":"IPL cricket","t20":"T20 cricket",
    "football":"football","soccer":"soccer","premier league":"Premier League",
    "champions league":"UEFA Champions League","la liga":"La Liga",
    "world cup":"FIFA World Cup","basketball":"basketball","nba":"NBA basketball",
    "tennis":"tennis","wimbledon":"Wimbledon","badminton":"badminton",
    "hockey":"hockey","baseball":"baseball","formula 1":"Formula 1",
    "f1":"F1 race","motogp":"MotoGP","rugby":"rugby","golf":"golf",
    "boxing":"boxing","mma":"MMA UFC","ufc":"UFC","olympics":"Olympics",
    "table tennis":"table tennis","volleyball":"volleyball","kabaddi":"kabaddi",
}

IPL_TEAMS = ["csk","mi","rcb","kkr","srh","pbks","dc","gt","lsg","rr",
             "chennai","mumbai","bangalore","kolkata","hyderabad","punjab",
             "delhi","gujarat","lucknow","rajasthan"]

def is_sports_query(query: str) -> bool:
    q = query.lower()
    if any(p in q for p in ["who made you","history of","rules of","how to play",
                              "explain","origin of"]): return False
    if any(t in q for t in IPL_TEAMS): return True
    actions = ["score","result","match","game","live","standings","winner",
               "champion","playoff","final","tournament","who won","playing today",
               "which team","today's match","schedule"]
    sports  = list(SPORTS_MAP.keys())
    return (any(re.search(r'\b'+re.escape(a)+r'\b',q) for a in actions) and
            any(re.search(r'\b'+re.escape(s)+r'\b',q) for s in sports))

def get_sport_emoji(term: str) -> str:
    em = {"cricket":"🏏","ipl":"🏏","football":"⚽","soccer":"⚽",
          "basketball":"🏀","tennis":"🎾","badminton":"🏸","hockey":"🏑",
          "baseball":"⚾","formula 1":"🏎️","f1":"🏎️","rugby":"🏉",
          "golf":"⛳","boxing":"🥊","mma":"🥋","olympics":"🏅",
          "volleyball":"🏐","kabaddi":"🤼"}
    sl = term.lower()
    for k,v in em.items():
        if k in sl: return v
    return "🏆"

def get_sports_news(term: str) -> str:
    try:
        url  = (f"https://news.google.com/rss/search?"
                f"q={requests.utils.quote(term+' score result today')}"
                f"&hl=en&gl=US&ceid=US:en")
        resp = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=8)
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

# ══════════════════════════════════════════════════════════════════════════════
#  NEWS
# ══════════════════════════════════════════════════════════════════════════════
def get_news(topic: str = "India") -> str:
    try:
        url  = (f"https://news.google.com/rss/search?"
                f"q={requests.utils.quote(topic)}&hl=en-IN&gl=IN&ceid=IN:en")
        resp = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=8)
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
    return any(k in q.lower() for k in ["news","headlines","latest news",
               "today news","breaking","top news","what happened today"])

def extract_news_topic(query: str) -> str:
    sw = {"news","latest","today","show","me","give","what","is","the",
          "headlines","breaking","top","current","about","on"}
    return " ".join(w for w in query.replace("?","").split()
                    if w.lower() not in sw).strip() or "India"

# ══════════════════════════════════════════════════════════════════════════════
#  WEB SEARCH
# ══════════════════════════════════════════════════════════════════════════════
def web_search(query: str) -> str:
    try:
        resp = requests.get(
            f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}",
            headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                  "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"},
            timeout=10
        )
        snips  = re.findall(r'class="result__snippet"[^>]*>(.*?)</(?:a|span)>',resp.text,re.DOTALL)
        titles = re.findall(r'class="result__title"[^>]*>.*?<a[^>]*>(.*?)</a>',resp.text,re.DOTALL)
        cs = [re.sub(r'<[^>]+>','',s).strip() for s in snips[:5]]
        ct = [re.sub(r'<[^>]+>','',t).strip() for t in titles[:5]]
        results = [f"• {t}: {s}" for t,s in zip(ct,cs) if s]
        if results: return "\n".join(results)
        r2   = requests.get("https://api.duckduckgo.com/",
                            params={"q":query,"format":"json","no_html":"1","skip_disambig":"1"},
                            timeout=8)
        data = r2.json()
        parts = []
        if data.get("Answer"):   parts.append(data["Answer"])
        if data.get("Abstract"): parts.append(data["Abstract"][:500])
        for t in data.get("RelatedTopics",[])[:3]:
            if isinstance(t,dict) and t.get("Text"): parts.append(t["Text"][:200])
        return "\n".join(parts) if parts else "No results found."
    except Exception as e:
        return f"Search failed: {e}"

def get_current_facts(query: str) -> str:
    try:
        url  = (f"https://news.google.com/rss/search?"
                f"q={requests.utils.quote(query)}&hl=en-IN&gl=IN&ceid=IN:en")
        resp = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=8)
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

SEARCH_TRIGGERS = [
    "who is","who was","who won","who are","who did",
    "what is","what was","what are","what happened",
    "when is","when was","when did","when will",
    "where is","where was","current","latest","recent","today",
    "election","prime minister","president","chief minister",
    "cm of","minister of","winner","champion","result",
    "2023","2024","2025","2026",
]

def needs_search(query: str) -> bool:
    q = query.lower()
    if any(k in q for k in ["who made you","who created you","who are you"]): return False
    skip = GAME_KEYWORDS + APP_KEYWORDS + SOFTWARE_KEYWORDS + DESIGN_KEYWORDS
    if any(k in q for k in skip): return False
    if is_sports_query(query): return False
    return any(t in q for t in SEARCH_TRIGGERS)

# ══════════════════════════════════════════════════════════════════════════════
#  CREATION CLASSIFICATION
# ══════════════════════════════════════════════════════════════════════════════
GAME_KEYWORDS = [
    "game","snake game","tetris","pacman","flappy bird","2048",
    "tic tac toe","chess","checkers","sudoku","minesweeper","platformer",
    "shooter","puzzle game","card game","memory game","quiz game","breakout",
    "pong","asteroids","space invaders","racing game","rpg","tower defense",
    "clicker game","battle","dungeon","maze","arcade",
]
APP_KEYWORDS = [
    "app","application","dashboard","admin panel","landing page","portfolio",
    "website","web app","e-commerce","shop","store","blog","chat app",
    "todo app","weather app","calculator app","login page","signup","form",
    "expense tracker","budget","note app","kanban","timer","stopwatch","clock",
    "music player","image gallery","calendar","analytics","chart","crm",
    "netflix clone","youtube clone","twitter clone","whatsapp ui","instagram clone",
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
]

def classify_creation(query: str) -> str:
    q = query.lower()
    if any(k in q for k in GAME_KEYWORDS):    return "game"
    if any(k in q for k in APP_KEYWORDS):      return "app"
    if any(k in q for k in SOFTWARE_KEYWORDS): return "software"
    if any(k in q for k in DESIGN_KEYWORDS):   return "design"
    if is_code_query(query):                   return "code"
    return "general"

def is_code_query(query: str) -> bool:
    q = query.lower()
    if is_stock_query(query) or is_weather_query(query): return False
    return any(t in q for t in [
        "write","code","program","script","function","implement","create","build",
        "develop","make","generate","algorithm","sort","search","fibonacci",
        "factorial","prime","reverse","palindrome","linked list","binary tree",
        "api","flask","django","react","html","css","sql query","regex","class",
        "oop","recursion","dynamic programming","leetcode","debug","fix","bug","solve",
    ])

def get_creation_badge(ct: str) -> str:
    return {
        "game":     '<div class="game-badge">🎮 World-class game · Fully playable · Mobile ready</div>',
        "app":      '<div class="app-badge">🚀 Professional app · Full features · Responsive</div>',
        "software": '<div class="app-badge">⚙️ Production-ready software</div>',
        "design":   '<div class="preview-badge">✨ Stunning UI design · Animated · Modern</div>',
        "code":     '<div class="code-badge">💻 World-class code · Optimized</div>',
        "general":  "",
    }.get(ct, "")

def get_creation_spinner(ct: str) -> str:
    return {
        "game":    "🎮 Building your game — crafting the perfect experience…",
        "app":     "🚀 Designing & building your app…",
        "software":"⚙️ Engineering your software…",
        "design":  "✨ Crafting a breathtaking design…",
        "code":    "💻 Writing world-class code…",
        "general": "✨ Thinking…",
    }.get(ct, "✨ Thinking…")

# ══════════════════════════════════════════════════════════════════════════════
#  SYSTEM PROMPT BUILDER
# ══════════════════════════════════════════════════════════════════════════════
def get_system_prompt(creation_type: str) -> str:
    mode      = st.session_state.get("ai_mode", "🤖 Default")
    mode_text = MODE_PROMPTS.get(mode, "")
    today     = get_today_str()

    base = (
        f"You are Nova AI — the world's BEST AI assistant, created by Samiran. "
        f"Today's date is {today}. "
        f"If asked who made you: 'I am Nova AI, created by Samiran.' "
        f"Never mention Meta, Llama, OpenAI, Groq, or any underlying model. "
        f"You have FULL memory of this entire conversation — refer back to it naturally. "
        f"NEVER write partial code. ALWAYS write complete implementations. "
        f"{mode_text}\n\n"
        f"CRITICAL — LIVE DATA RULE: When real-time data is provided, treat it as "
        f"ABSOLUTE TRUTH. Answer directly and confidently. NEVER say you lack "
        f"real-time data when data is provided above. NEVER redirect to external sites. "
        f"Today is {today} — use this when answering 'today' questions.\n\n"
    )

    if creation_type == "game":
        return base + (
            "GAME DEV MODE: Write COMPLETE fully playable HTML5 games. "
            "Include: 60fps Canvas, score/highscore (localStorage), start/gameover screens, "
            "Web Audio API sounds, keyboard+touch controls, particles, neon dark theme. "
            "ONE complete ```html block."
        )
    elif creation_type == "app":
        return base + (
            "APP DEV MODE: Write COMPLETE fully functional apps in one HTML file. "
            "Design like Apple/Google: Google Fonts, Font Awesome CDN, CSS variables, "
            "animations, glassmorphism, full CRUD, localStorage, toast notifications, responsive. "
            "ONE complete ```html block."
        )
    elif creation_type in ("software","design"):
        return base + (
            "Write COMPLETE production-ready code. Stunning design. "
            "Full functionality. ONE complete ```html block."
        )
    else:
        return base + (
            "Write COMPLETE working code. Best practices. Optimal complexity. "
            "All languages supported. Full implementations only."
        )

# ══════════════════════════════════════════════════════════════════════════════
#  BUILD MESSAGES WITH HISTORY
# ══════════════════════════════════════════════════════════════════════════════
def build_messages(user_query: str, search_results: str = "",
                   creation_type: str = "general") -> list:
    messages = [{"role":"system","content": get_system_prompt(creation_type)}]

    history = st.session_state.messages[:-1]
    if len(history) > MAX_HISTORY_TURNS * 2:
        history = history[-(MAX_HISTORY_TURNS * 2):]

    for msg in history:
        content = re.sub(r'<div[^>]*>.*?</div>', '', msg["content"], flags=re.DOTALL)
        content = re.sub(r'<[^>]+>', '', content).strip()
        if content:
            messages.append({"role": msg["role"], "content": content[:3000]})

    if search_results:
        user_content = (
            f"=== LIVE REAL-TIME DATA (fetched right now — {get_today_str()}) ===\n"
            f"{search_results}\n\n"
            f"=== USER QUESTION ===\n{user_query}\n\n"
            f"Answer directly using the live data above. Be confident and complete."
        )
    else:
        user_content = user_query

    messages.append({"role":"user","content": user_content[:5000]})
    return messages

# ══════════════════════════════════════════════════════════════════════════════
#  CODE UTILITIES
# ══════════════════════════════════════════════════════════════════════════════
LANGUAGE_MAP = {
    "python":("python","3.10.0"),
    "javascript":("javascript","18.15.0"),"js":("javascript","18.15.0"),
    "typescript":("typescript","5.0.3"),"ts":("typescript","5.0.3"),
    "java":("java","15.0.2"),
    "c++":("c++","10.2.0"),"cpp":("c++","10.2.0"),
    "c":("c","10.2.0"),"rust":("rust","1.68.2"),"go":("go","1.16.2"),
    "ruby":("ruby","3.0.1"),"php":("php","8.2.3"),"swift":("swift","5.3.3"),
    "kotlin":("kotlin","1.8.20"),"r":("r","4.1.1"),
    "bash":("bash","5.2.0"),"shell":("bash","5.2.0"),
    "sql":("sqlite3","3.36.0"),"lua":("lua","5.4.4"),
    "perl":("perl","5.36.0"),"scala":("scala","3.2.2"),
}

def run_code(code: str, language: str) -> str:
    try:
        lang, ver = LANGUAGE_MAP.get(language.lower(), ("python","3.10.0"))
        resp   = requests.post(
            "https://emkc.org/api/v2/piston/execute",
            json={"language":lang,"version":ver,
                  "files":[{"name":f"main.{language[:3]}","content":code}],
                  "stdin":"","args":[],"compile_timeout":10000,"run_timeout":5000},
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
    return [(lang.lower() if lang else "text", code.strip()) for lang,code in matches]

def extract_first_code(text: str) -> tuple:
    blocks = extract_code_blocks(text)
    if blocks: return blocks[0][1], blocks[0][0]
    return None, None

def build_html_app(blocks: list) -> str:
    html_part = css_part = js_part = full_html = ""
    for lang, code in blocks:
        if lang == "html":
            if "<!doctype" in code.lower() or "<html" in code.lower(): full_html = code
            else: html_part = code
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
                    font-family:Space Mono,monospace;color:#00e5ff'>✨ Nova AI</div>
        <div style='font-size:11px;color:#64748b;margin-top:.3rem'>
            Created by Samiran
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # ── Model settings ─────────────────────────────────────────────────────────
    st.markdown("### ⚙️ Model Settings")
    st.session_state["temperature"] = st.slider(
        "Temperature", 0.0, 1.0,
        value=st.session_state["temperature"], step=0.05,
        help="Low = factual  |  High = creative"
    )
    st.session_state["max_tokens"] = st.select_slider(
        "Max Length", options=[512,1024,2048,4096,8192],
        value=st.session_state["max_tokens"]
    )

    st.divider()

    # ── AI Mode ────────────────────────────────────────────────────────────────
    st.markdown("### 🎭 AI Mode")
    st.session_state["ai_mode"] = st.selectbox(
        "Mode", list(MODE_PROMPTS.keys()), index=0, label_visibility="collapsed"
    )

    st.divider()

    # ── File Upload ────────────────────────────────────────────────────────────
    st.markdown("### 📁 File Analysis")
    uploaded = st.file_uploader(
        "Upload file for AI to analyze",
        type=["txt","csv","json","py","js","ts","html","css","java","cpp","c","md","rs","go"],
        label_visibility="collapsed"
    )
    if uploaded:
        content = read_uploaded_file(uploaded)
        st.session_state["uploaded_file_content"] = content
        st.session_state["uploaded_file_name"]    = uploaded.name
        st.success(f"✅ {uploaded.name} loaded")
        if st.button("🗑️ Clear file"):
            st.session_state["uploaded_file_content"] = None
            st.session_state["uploaded_file_name"]    = None
            st.rerun()

    st.divider()

    # ── Quick Tools ────────────────────────────────────────────────────────────
    st.markdown("### 🛠️ Quick Tools")

    with st.expander("💱 Currency Converter"):
        am_in = st.number_input("Amount", value=1.0, min_value=0.0, key="sb_amount")
        c1, c2 = st.columns(2)
        with c1: fc = st.selectbox("From", CURRENCIES, index=0,  key="sb_from")
        with c2: tc = st.selectbox("To",   CURRENCIES, index=3,  key="sb_to")
        if st.button("Convert 💱", key="sb_conv"):
            with st.spinner("Fetching rates…"):
                st.markdown(get_exchange_rate(fc, tc, am_in))

    with st.expander("📐 Unit Converter"):
        unit_in = st.text_input("e.g. 100 km to miles", key="sb_unit")
        if st.button("Convert 📐", key="sb_unit_btn"):
            res = convert_unit(unit_in)
            st.markdown(res if res else "⚠️ Try: '100 km to miles'")

    with st.expander("🔢 Calculator"):
        calc_in = st.text_input("e.g. sqrt(144) + sin(pi/2)", key="sb_calc")
        if st.button("Calculate 🔢", key="sb_calc_btn"):
            res = solve_math(calc_in)
            if res:
                st.markdown(f'<div class="math-result">= {res}</div>', unsafe_allow_html=True)
            else:
                st.warning("Could not evaluate.")

    with st.expander("📱 QR Generator"):
        qr_in = st.text_input("Text or URL", key="sb_qr")
        if st.button("Generate QR 📱", key="sb_qr_btn") and qr_in:
            qr_url = generate_qr_url(qr_in)
            st.image(qr_url, width=200)
            st.markdown(f"[⬇️ Download QR]({qr_url})")

    st.divider()

    # ── Export ─────────────────────────────────────────────────────────────────
    st.markdown("### 💾 Export Chat")
    if st.session_state["messages"]:
        col_a, col_b = st.columns(2)
        with col_a:
            st.download_button(
                "📝 MD", data=export_markdown(),
                file_name=f"nova_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown", use_container_width=True
            )
        with col_b:
            st.download_button(
                "📊 JSON", data=export_json(),
                file_name=f"nova_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json", use_container_width=True
            )
    else:
        st.caption("No messages yet.")

    st.divider()
    st.markdown(
        f"<div style='text-align:center;font-size:10px;color:#374151'>"
        f"Nova AI · Samiran · v3.0<br>{datetime.now().strftime('%B %Y')}</div>",
        unsafe_allow_html=True
    )

# ══════════════════════════════════════════════════════════════════════════════
#  HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero">
    <div class="hero-badge">LIVE · FREE · UNLIMITED · REAL-TIME</div>
    <h1>Nova<span> AI</span></h1>
    <p>The smartest AI — builds games, apps, reads files, converts units & knows everything live.</p>
</div>
<div class="stats-row">
    <div class="stat-pill"><span class="dot dot-purple"></span> 🧠 Memory</div>
    <div class="stat-pill"><span class="dot dot-blue"></span>  🏏 Live Sports</div>
    <div class="stat-pill"><span class="dot dot-orange"></span> 🎮 Games & Apps</div>
    <div class="stat-pill"><span class="dot dot-green"></span> 📁 File Analysis</div>
    <div class="stat-pill"><span class="dot dot-green"></span> 💱 Currency & Units</div>
    <div class="stat-pill"><span class="dot dot-blue"></span>  🌐 URL Reader</div>
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

# ── Chat history ──────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center;padding:1.5rem 1rem 1rem;color:var(--muted);">
        <div style="font-size:2rem;margin-bottom:.6rem">✨</div>
        <p style="font-size:.95rem;font-weight:600;color:#94a3b8;margin-bottom:1rem">
            What would you like to do today?
        </p>
    </div>
    <div class="category-grid">
        <div class="category-card">
            <div class="category-icon">🎮</div>
            <div class="category-title">Games</div>
            <div class="category-examples">Snake · Tetris · Chess<br>2048 · Pacman</div>
        </div>
        <div class="category-card">
            <div class="category-icon">🚀</div>
            <div class="category-title">Apps</div>
            <div class="category-examples">Dashboard · Todo<br>E-commerce · Portfolio</div>
        </div>
        <div class="category-card">
            <div class="category-icon">💻</div>
            <div class="category-title">Code</div>
            <div class="category-examples">Python · JS · Java<br>Algorithms · APIs</div>
        </div>
        <div class="category-card">
            <div class="category-icon">📁</div>
            <div class="category-title">Files</div>
            <div class="category-examples">Upload CSV/JSON/Code<br>AI analyzes it</div>
        </div>
        <div class="category-card">
            <div class="category-icon">🌐</div>
            <div class="category-title">Live Data</div>
            <div class="category-examples">Cricket · Stocks<br>Weather · News</div>
        </div>
        <div class="category-card">
            <div class="category-icon">🛠️</div>
            <div class="category-title">Tools</div>
            <div class="category-examples">Currency · Units · QR<br>Calculator · URL Reader</div>
        </div>
    </div>
    <div class="divider"></div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("live_data"):
                st.markdown('<div class="live-badge"> LIVE DATA</div>', unsafe_allow_html=True)
            elif msg.get("searched"):
                st.markdown('<div class="search-badge">🔍 Web search</div>', unsafe_allow_html=True)
            ct = msg.get("creation_type","")
            if ct and ct != "general":
                st.markdown(get_creation_badge(ct), unsafe_allow_html=True)
            st.markdown(msg["content"])

# ══════════════════════════════════════════════════════════════════════════════
#  CHAT INPUT — MASTER HANDLER
# ══════════════════════════════════════════════════════════════════════════════
if prompt := st.chat_input("Ask anything — build games, analyze files, live scores, convert units…"):

    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        searched  = False
        live_data = False
        response  = ""

        # ── 1. QR CODE ────────────────────────────────────────────────────────
        if is_qr_query(prompt):
            content = extract_qr_content(prompt)
            qr_url  = generate_qr_url(content)
            st.markdown('<div class="search-badge">📱 QR Code generated</div>',
                        unsafe_allow_html=True)
            st.markdown(f"**QR Code for:** `{content}`")
            st.image(qr_url, width=250)
            st.markdown(f"[⬇️ Download QR]({qr_url})")
            response = f"✅ QR Code generated for: `{content}`"
            st.session_state.messages.append({"role":"assistant","content":response})

        # ── 2. CURRENCY ───────────────────────────────────────────────────────
        elif is_currency_query(prompt):
            amount, fc, tc = extract_currency_params(prompt)
            with st.spinner("💱 Fetching live rates…"):
                result = get_exchange_rate(fc, tc, amount)
            st.markdown('<div class="search-badge">💱 Live exchange rate</div>',
                        unsafe_allow_html=True)
            st.markdown(f'<div class="currency-result">{result}</div>',
                        unsafe_allow_html=True)
            response = result
            st.session_state.messages.append({"role":"assistant","content":response})

        # ── 3. UNIT CONVERTER ─────────────────────────────────────────────────
        elif is_unit_query(prompt):
            result = convert_unit(prompt)
            if result:
                st.markdown('<div class="math-badge">📐 Unit conversion</div>',
                            unsafe_allow_html=True)
                st.markdown(f'<div class="math-result">{result}</div>',
                            unsafe_allow_html=True)
                response = result
                st.session_state.messages.append({"role":"assistant","content":response})
            else:
                # Fall through to AI
                pass

        # ── 4. MATH ───────────────────────────────────────────────────────────
        if not response and is_math_query(prompt):
            result = solve_math(prompt)
            if result:
                st.markdown('<div class="math-badge">🔢 Calculated instantly</div>',
                            unsafe_allow_html=True)
                st.markdown(f'<div class="math-result">= {result}</div>',
                            unsafe_allow_html=True)
                # Also send to AI to explain
                msgs = build_messages(
                    f"The math result is {result}. User asked: {prompt}. "
                    f"Briefly explain the calculation.",
                    creation_type="general"
                )
                explanation = stream_response(
                    msgs,
                    max_tokens=512,
                    temperature=st.session_state["temperature"]
                )
                response = f"= {result}\n\n{explanation}"
                st.session_state.messages.append({"role":"assistant","content":response})

        # ── 5. URL READER ─────────────────────────────────────────────────────
        if not response and is_url_query(prompt):
            url = extract_url(prompt)
            if url:
                with st.spinner(f"🌐 Reading {url[:60]}…"):
                    page_content = fetch_url_content(url)
                st.markdown('<div class="url-badge">🌐 URL content read</div>',
                            unsafe_allow_html=True)
                augmented = (
                    f"URL: {url}\n\nContent extracted:\n{page_content}\n\n"
                    f"User's request: {prompt}\n"
                    f"Answer based on the content above."
                )
                msgs     = build_messages(augmented, creation_type="general")
                response = stream_response(
                    msgs,
                    max_tokens=st.session_state["max_tokens"],
                    temperature=st.session_state["temperature"]
                )
                st.session_state.messages.append({
                    "role":"assistant","content":response,"searched":True
                })

        # ── 6. FILE ANALYSIS ──────────────────────────────────────────────────
        if not response and st.session_state.get("uploaded_file_content"):
            file_content = st.session_state["uploaded_file_content"]
            fname        = st.session_state.get("uploaded_file_name","file")
            st.markdown(f'<div class="file-badge">📁 Analyzing: {fname}</div>',
                        unsafe_allow_html=True)
            augmented = (
                f"File: '{fname}'\n\nContent:\n{file_content}\n\n"
                f"User's request: {prompt}\n\n"
                f"Analyze this file thoroughly and answer the request."
            )
            msgs     = build_messages(augmented, creation_type="general")
            response = stream_response(
                msgs,
                max_tokens=st.session_state["max_tokens"],
                temperature=st.session_state["temperature"]
            )
            st.session_state.messages.append({
                "role":"assistant","content":response,"searched":False
            })
            st.session_state["uploaded_file_content"] = None
            st.session_state["uploaded_file_name"]    = None

        # ── 7. STOCK ──────────────────────────────────────────────────────────
        if not response and is_stock_query(prompt):
            symbol, dname = extract_stock_symbol(prompt)
            if symbol:
                with st.spinner(f"📈 Fetching {dname}…"):
                    sd = get_stock_price(symbol, dname)
                if "failed" not in sd.lower():
                    L = dict(l.split(": ",1) for l in sd.strip().splitlines() if ": " in l)
                    response = (
                        f'<div class="search-badge">📈 Live · Yahoo Finance</div>\n\n'
                        f"### 📈 {L.get('Name',dname)}\n"
                        f"_{L.get('Exchange','')} · {L.get('Market','')}_\n\n"
                        f"| Detail | Value |\n|--------|-------|\n"
                        f"| 💰 Price | **{L.get('Price','N/A')}** |\n"
                        f"| 📊 Change | {L.get('Change','N/A')} |\n"
                        f"| 📈 Day High | {L.get('Day High','N/A')} |\n"
                        f"| 📉 Day Low | {L.get('Day Low','N/A')} |\n"
                        f"| 🔢 Volume | {L.get('Volume','N/A')} |\n\n"
                        f"_Delayed ~15 min_"
                    )
                    st.markdown(response, unsafe_allow_html=True)
                    st.session_state.messages.append({"role":"assistant","content":response})

        # ── 8. SPORTS / CRICKET ───────────────────────────────────────────────
        if not response and is_sports_query(prompt):
            with st.spinner("🏏 Fetching real-time match data…"):
                cricket_data = fetch_live_cricket()
                # Also check general sports
                sport_term = "general sports"
                for k,v in SPORTS_MAP.items():
                    if k in prompt.lower():
                        sport_term = v; break
                if sport_term == "general sports":
                    general_data = get_sports_news("sports today")
                    sports_data  = cricket_data + "\n\n" + general_data
                else:
                    sports_data = cricket_data or get_sports_news(sport_term)
                live_data = True

            st.markdown('<div class="live-badge"> LIVE SPORTS DATA</div>',
                        unsafe_allow_html=True)
            msgs = build_messages(prompt, search_results=sports_data, creation_type="general")
            response = stream_response(msgs, max_tokens=1024, temperature=0.1)
            st.session_state.messages.append({
                "role":"assistant","content":response,"live_data":True
            })

        # ── 9. NEWS ───────────────────────────────────────────────────────────
        if not response and is_news_query(prompt):
            with st.spinner("📰 Fetching news…"):
                topic = extract_news_topic(prompt)
                news  = get_news(topic)
            response = (
                f'<div class="search-badge">📰 Live news</div>\n\n'
                f"### 📰 {topic.title()}\n\n{news}"
            )
            st.markdown(response, unsafe_allow_html=True)
            st.session_state.messages.append({"role":"assistant","content":response})

        # ── 10. WEATHER ───────────────────────────────────────────────────────
        if not response and is_weather_query(prompt):
            with st.spinner("🌤️ Fetching weather…"):
                city = extract_city(prompt)
                wd   = get_weather(city)
            if "failed" not in wd.lower():
                L = dict(l.split(": ",1) for l in wd.strip().splitlines() if ": " in l)
                response = (
                    f'<div class="search-badge">🌤️ Live weather</div>\n\n'
                    f"### 🌍 {L.get('City',city)}\n\n"
                    f"| Detail | Value |\n|--------|-------|\n"
                    f"| 🌡️ Temperature | {L.get('Temperature','N/A')} |\n"
                    f"| 🌤️ Condition | {L.get('Condition','N/A')} |\n"
                    f"| 💧 Humidity | {L.get('Humidity','N/A')} |\n"
                    f"| 💨 Wind Speed | {L.get('Wind Speed','N/A')} |\n"
                    f"| 👁️ Visibility | {L.get('Visibility','N/A')} |\n"
                    f"| ☀️ UV Index | {L.get('UV Index','N/A')} |\n"
                )
            else:
                response = f"❌ Couldn't fetch weather for **{city}**."
            st.markdown(response, unsafe_allow_html=True)
            st.session_state.messages.append({"role":"assistant","content":response})

        # ── 11. CREATION / CODE / GENERAL (with streaming) ───────────────────
        if not response:
            creation_type  = classify_creation(prompt)
            search_results = ""

            if needs_search(prompt):
                with st.spinner("🔍 Searching the web…"):
                    search_results = web_search(prompt)
                    facts = get_current_facts(prompt)
                    if facts: search_results += "\n\nRecent headlines:\n" + facts
                    searched = True

            if searched:
                st.markdown('<div class="search-badge">🔍 Web search</div>',
                            unsafe_allow_html=True)
            badge = get_creation_badge(creation_type)
            if badge: st.markdown(badge, unsafe_allow_html=True)
            if len(st.session_state.messages) > 2:
                turns = len(st.session_state.messages) // 2
                st.markdown(
                    f'<div class="memory-badge">🧠 {turns} turns remembered</div>',
                    unsafe_allow_html=True
                )

            for attempt in range(3):
                try:
                    spin = get_creation_spinner(creation_type) if attempt == 0 else "Retrying ⏳"
                    with st.spinner(spin):
                        if attempt > 0: time.sleep(60)

                    msgs     = build_messages(prompt, search_results, creation_type)
                    response = stream_response(
                        msgs,
                        max_tokens=st.session_state["max_tokens"],
                        temperature=st.session_state["temperature"]
                    )

                    # Live HTML preview
                    blocks    = extract_code_blocks(response)
                    code, lang = extract_first_code(response)
                    langs_found = [l for l,_ in blocks]
                    is_web = any(l in ("html","css","javascript","js") for l in langs_found)

                    if is_web:
                        html_src = build_html_app(blocks)
                        if html_src:
                            st.markdown("---")
                            labels = {"game":"🎮 Live Game!","app":"🚀 Live App",
                                      "software":"⚙️ Live Software","design":"✨ Live Design"}
                            st.markdown(f"### {labels.get(creation_type,'🖥️ Preview')}")
                            h = 650 if creation_type in ("game","app","software") else 520
                            st.components.v1.html(html_src, height=h, scrolling=True)
                            b64   = base64.b64encode(html_src.encode()).decode()
                            fnames = {"game":"nova_game.html","app":"nova_app.html",
                                      "software":"nova_software.html",
                                      "design":"nova_design.html"}
                            fname = fnames.get(creation_type,"nova_ai.html")
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

                    st.session_state.messages.append({
                        "role":"assistant","content":response,
                        "searched":searched,"creation_type":creation_type,
                    })
                    break

                except Exception as e:
                    if "rate_limit_exceeded" in str(e) and attempt < 2: continue
                    st.error(f"❌ Error: {e}"); break
