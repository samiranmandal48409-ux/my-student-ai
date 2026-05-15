import streamlit as st
from groq import Groq
import time
import requests
import re
import base64

st.set_page_config(
    page_title="Nova AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
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
    max-width: 900px !important;
    padding: 0 1.5rem 6rem !important;
    margin: 0 auto !important;
}

.hero { text-align: center; padding: 3rem 1rem 2rem; position: relative; }
.hero::before {
    content: ''; position: absolute; top: 0; left: 50%;
    transform: translateX(-50%);
    width: 700px; height: 350px;
    background: radial-gradient(ellipse at center, rgba(0,229,255,.08) 0%, transparent 70%);
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
    font-size: clamp(1.8rem, 4vw, 2.8rem) !important;
    font-weight: 700 !important;
    color: #fff !important; line-height: 1.15 !important;
    letter-spacing: -.02em; margin-bottom: .6rem !important;
}
.hero h1 span { color: var(--accent); }
.hero p { font-size: 1rem; color: var(--muted); font-weight: 300; max-width: 480px; margin: 0 auto; }
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
    background: var(--user-bg) !important;
    border-color: rgba(0,229,255,.15) !important;
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
    transform: translateX(-50%) !important; width: 100% !important;
    max-width: 900px !important; padding: 1rem 1.5rem 1.5rem !important;
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
    box-shadow: 0 0 0 3px rgba(0,229,255,.1) !important;
    outline: none !important;
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
    font-weight: 500 !important; padding: .4rem 1rem !important;
    transition: all .2s !important;
}
.stButton > button:hover {
    border-color: var(--accent) !important; color: var(--accent) !important;
    background: rgba(0,229,255,.06) !important;
}

.stats-row {
    display: flex; gap: .8rem; margin: 1.2rem 0 1.8rem;
    justify-content: center; flex-wrap: wrap;
}
.stat-pill {
    display: flex; align-items: center; gap: 7px;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 999px; padding: 6px 14px;
    font-size: 12.5px; color: var(--muted);
}
.stat-pill .dot { width:7px; height:7px; border-radius:50%; }
.dot-green  { background: var(--green);  box-shadow: 0 0 6px var(--green); }
.dot-blue   { background: var(--accent); box-shadow: 0 0 6px var(--accent); }
.dot-purple { background: var(--purple); box-shadow: 0 0 6px var(--purple); }
.dot-orange { background: var(--orange); box-shadow: 0 0 6px var(--orange); }

.search-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(16,185,129,.08); border: 1px solid rgba(16,185,129,.2);
    border-radius: 6px; padding: 3px 10px;
    font-size: 11px; color: var(--green); margin-bottom: .5rem;
}
.code-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(124,58,237,.08); border: 1px solid rgba(124,58,237,.3);
    border-radius: 6px; padding: 3px 10px;
    font-size: 11px; color: #a78bfa; margin-bottom: .5rem;
}
.app-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(245,158,11,.08); border: 1px solid rgba(245,158,11,.3);
    border-radius: 6px; padding: 3px 10px;
    font-size: 11px; color: var(--orange); margin-bottom: .5rem;
}
.game-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(0,229,255,.08); border: 1px solid rgba(0,229,255,.25);
    border-radius: 6px; padding: 3px 10px;
    font-size: 11px; color: var(--accent); margin-bottom: .5rem;
}
.preview-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(0,229,255,.08); border: 1px solid rgba(0,229,255,.25);
    border-radius: 6px; padding: 3px 10px;
    font-size: 11px; color: var(--accent); margin-bottom: .5rem;
}
.memory-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(124,58,237,.08); border: 1px solid rgba(124,58,237,.25);
    border-radius: 6px; padding: 3px 10px;
    font-size: 11px; color: #a78bfa; margin-bottom: .5rem;
}
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
.btn-download {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(0,229,255,.1); border: 1px solid rgba(0,229,255,.3);
    color: var(--accent); padding: 5px 12px; border-radius: 7px;
    text-decoration: none; font-size: 12px;
    font-family: 'DM Sans', sans-serif; font-weight: 500; transition: all .2s;
}
.category-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem; margin: 1.5rem 0;
}
.category-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 1.2rem; text-align: center;
    transition: border-color .2s, transform .2s;
}
.category-card:hover { border-color: var(--accent); transform: translateY(-2px); }
.category-icon { font-size: 1.8rem; margin-bottom: .5rem; }
.category-title { font-size: 13px; font-weight: 600; color: #94a3b8; margin-bottom: .3rem; }
.category-examples { font-size: 11.5px; color: var(--muted); line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# ── Groq client ───────────────────────────────────────────────────────────────
client = Groq(api_key="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")
MODEL  = "llama-3.3-70b-versatile"

# ── Max history turns to send (keeps token usage sane) ────────────────────────
MAX_HISTORY_TURNS = 20   # = 20 user + 20 assistant messages

# ══════════════════════════════════════════════════════════════════════════════
#  CREATION CLASSIFICATION
# ══════════════════════════════════════════════════════════════════════════════
GAME_KEYWORDS = [
    "game","snake game","tetris","pacman","flappy bird","2048",
    "tic tac toe","chess","checkers","sudoku","minesweeper",
    "platformer","shooter","puzzle game","card game","dice",
    "memory game","quiz game","trivia","word game","breakout",
    "pong","asteroids","space invaders","racing game","rpg",
    "tower defense","clicker game","idle game","endless runner",
    "battle","dungeon","maze","arcade",
]
APP_KEYWORDS = [
    "app","application","dashboard","admin panel","landing page",
    "portfolio","website","web app","e-commerce","shop","store",
    "blog","chat app","todo app","weather app","calculator app",
    "login page","signup","form","registration","survey",
    "expense tracker","budget","note app","kanban","timer",
    "stopwatch","clock","music player","video player","image gallery",
    "calendar","booking","invoice","analytics","chart","crm",
    "netflix clone","youtube clone","twitter clone","spotify clone",
    "whatsapp ui","instagram clone","responsive","animated",
]
SOFTWARE_KEYWORDS = [
    "software","tool","utility","desktop app","system",
    "file manager","text editor","password manager","api tester",
    "converter","downloader","scraper","automation","cli tool",
]
DESIGN_KEYWORDS = [
    "design","ui","ux","mockup","prototype","wireframe",
    "beautiful","modern","stunning","animated","glassmorphism",
    "neumorphism","gradient","dark theme","light theme",
    "responsive","component","ui kit","hero section",
    "navbar","sidebar","modal","dropdown","landing",
]

def classify_creation_request(query: str) -> str:
    q = query.lower()
    if any(k in q for k in GAME_KEYWORDS):     return "game"
    if any(k in q for k in APP_KEYWORDS):       return "app"
    if any(k in q for k in SOFTWARE_KEYWORDS):  return "software"
    if any(k in q for k in DESIGN_KEYWORDS):    return "design"
    if is_code_query(query):                    return "code"
    return "general"

def get_creation_system_prompt(creation_type: str) -> str:
    base = (
        "You are Nova AI — the world's BEST AI assistant and code generator, "
        "created by Samiran. "
        "If anyone asks who made you, say: 'I am Nova AI, created by Samiran.' "
        "Never mention Meta, Llama, OpenAI, Groq, or any underlying model. "
        "You have FULL memory of this conversation — always refer back to what "
        "the user said earlier when relevant. "
        "NEVER write partial code. NEVER use placeholders. "
        "ALWAYS write the complete implementation. "
    )
    if creation_type == "game":
        return base + """
You are the WORLD'S BEST game developer.
RULES:
1. Write COMPLETE, fully playable games — every feature must work.
2. Use HTML5 Canvas or pure HTML/CSS/JS.
3. Every game MUST include:
   - Smooth 60fps animations (requestAnimationFrame)
   - Score + high score (localStorage)
   - Start / Game Over / Restart screens
   - Sound effects via Web Audio API (no external files)
   - Keyboard AND touch/mobile controls
   - Increasing difficulty, lives/health system, pause (P key)
   - Particle effects, glows, neon dark theme
   - Full HUD: score, lives, level, time
4. Output ONE complete ```html block.
5. After code: briefly list controls and features.
"""
    elif creation_type == "app":
        return base + """
You are the WORLD'S BEST UI/UX designer + full-stack developer.
RULES:
1. Write COMPLETE, fully functional apps.
2. Design like Apple / Google / Airbnb senior designers.
3. Must include: Google Fonts, Font Awesome CDN, CSS variables,
   8px grid, responsive, smooth animations, micro-interactions,
   glassmorphism or modern flat design.
4. Functionality: full CRUD, localStorage, form validation,
   toast notifications, loading states, empty states,
   search/filter, keyboard shortcuts.
5. Output ONE complete ```html block.
6. After code: list all features.
"""
    elif creation_type == "software":
        return base + """
You are the WORLD'S BEST software architect.
RULES:
1. Write COMPLETE, production-ready software.
2. Include error handling, input validation, clean architecture.
3. For browser tools: single HTML file, use IndexedDB/localStorage.
4. Make it feel like a real professional desktop application.
5. Output complete code block(s) + brief architecture notes.
"""
    elif creation_type == "design":
        return base + """
You are the WORLD'S BEST UI/UX designer.
RULES:
1. Create STUNNING pixel-perfect designs.
2. Use: glassmorphism, aurora gradients, 3D transforms,
   scroll animations (Intersection Observer), custom cursor,
   particle backgrounds, stagger animations.
3. Mix display + body fonts. Generous whitespace. Max 2 accent colors.
4. Include hover/focus/active states on everything.
5. Dark mode by default. Smooth scrolling.
6. Output ONE complete ```html block — make it breathtaking.
"""
    else:
        return base + """
CODING & GENERAL RULES:
1. Write COMPLETE, fully working code — never partial.
2. Best practices: clean names, error handling, comments.
3. Optimal time/space complexity for algorithms.
4. Always specify language in code block.
5. Support ALL languages: Python, JS, TS, Java, C++, C, Rust,
   Go, Ruby, PHP, Swift, Kotlin, SQL, Bash, R, Lua, Scala, etc.
6. For web output: complete single-file HTML with embedded CSS/JS.
7. Add type hints, TypeScript types, JSDoc where appropriate.

FACTUAL QUESTION RULES:
- When search results are provided, use them as primary source.
- State answers directly and confidently.
- Never say info is unavailable if results contain it.

MEMORY RULES:
- Always remember everything the user said earlier in this chat.
- Reference previous context naturally when relevant.
"""

def get_creation_badge(creation_type: str) -> str:
    badges = {
        "game":     '<div class="game-badge">🎮 World-class game · Fully playable · Mobile ready</div>',
        "app":      '<div class="app-badge">🚀 Professional app · Full features · Responsive</div>',
        "software": '<div class="app-badge">⚙️ Production-ready software · Complete</div>',
        "design":   '<div class="preview-badge">✨ Stunning UI design · Animated · Modern</div>',
        "code":     '<div class="code-badge">💻 World-class code · Optimized · Production ready</div>',
        "general":  "",
    }
    return badges.get(creation_type, "")

def get_creation_spinner(creation_type: str) -> str:
    return {
        "game":     "🎮 Building your game — crafting the perfect experience…",
        "app":      "🚀 Designing & building your app — making it stunning…",
        "software": "⚙️ Engineering your software — production-grade quality…",
        "design":   "✨ Crafting a breathtaking design — pixel-perfect…",
        "code":     "💻 Writing world-class code — optimizing for perfection…",
        "general":  "✨ Thinking…",
    }.get(creation_type, "✨ Thinking…")


# ══════════════════════════════════════════════════════════════════════════════
#  WEATHER · SPORTS · NEWS · STOCKS
# ══════════════════════════════════════════════════════════════════════════════
def get_weather(city: str) -> str:
    try:
        url  = f"https://wttr.in/{requests.utils.quote(city)}?format=j1"
        resp = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=8)
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

def extract_city_from_query(query: str) -> str:
    m = re.search(
        r'(?:weather|temperature|forecast|humidity|climate)'
        r'\s+(?:report\s+)?(?:in|for|of|at)\s+([A-Za-z ,]+?)(?:\?|$)',
        query, re.IGNORECASE
    )
    if m: return m.group(1).strip().rstrip(",")
    stopwords = {
        "what","is","the","weather","report","temperature","forecast",
        "today","current","now","like","how","give","me","show",
        "humidity","climate","condition","conditions","a","an"
    }
    words = query.replace("?","").split()
    return " ".join(w for w in words if w.lower() not in stopwords).strip() or "Guwahati"

def is_weather_query(q: str) -> bool:
    return any(k in q.lower() for k in [
        "weather","temperature","forecast","humidity",
        "rain","sunny","cloudy","wind speed","climate today"
    ])

SPORTS_MAP = {
    "cricket":"cricket","ipl":"IPL cricket","test match":"test cricket",
    "odi":"ODI cricket","t20":"T20 cricket","football":"football",
    "soccer":"soccer","premier league":"Premier League",
    "champions league":"UEFA Champions League","la liga":"La Liga",
    "world cup":"FIFA World Cup","basketball":"basketball","nba":"NBA basketball",
    "tennis":"tennis","wimbledon":"Wimbledon tennis","badminton":"badminton",
    "hockey":"hockey","baseball":"baseball","formula 1":"Formula 1",
    "f1":"F1 race","motogp":"MotoGP","rugby":"rugby","golf":"golf",
    "boxing":"boxing","mma":"MMA UFC","ufc":"UFC fight",
    "olympics":"Olympics","table tennis":"table tennis",
    "volleyball":"volleyball","kabaddi":"kabaddi PKL",
}

def detect_sport(query: str) -> str:
    q = query.lower()
    for kw, term in SPORTS_MAP.items():
        if kw in q: return term
    return "sports scores today"

def get_sports_news(sport_term: str) -> str:
    try:
        import xml.etree.ElementTree as ET
        url  = (f"https://news.google.com/rss/search?"
                f"q={requests.utils.quote(sport_term+' score result today')}"
                f"&hl=en&gl=US&ceid=US:en")
        resp = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=8)
        root = ET.fromstring(resp.content)
        results = []
        for item in root.findall(".//item")[:7]:
            title = item.findtext("title","").strip()
            if title:
                clean = title.split(" - ")[0].strip()
                src   = title.split(" - ")[-1].strip() if " - " in title else ""
                results.append(f"• **{clean}**" + (f" _{src}_" if src else ""))
        return "\n".join(results) if results else "No recent sports updates found."
    except Exception as e:
        return f"Sports fetch failed: {e}"

def is_sports_query(query: str) -> bool:
    q = query.lower()
    if any(p in q for p in ["why","how does","explain","politics","history of"]): return False
    actions = ["score","scores","result","match","game","live","standings",
               "winner","champion","playoff","final","tournament","who won"]
    sports  = list(SPORTS_MAP.keys())
    return (any(re.search(r'\b'+re.escape(a)+r'\b',q) for a in actions) and
            any(re.search(r'\b'+re.escape(s)+r'\b',q) for s in sports))

def get_sport_emoji(sport_term: str) -> str:
    em = {"cricket":"🏏","ipl":"🏏","football":"⚽","soccer":"⚽",
          "basketball":"🏀","tennis":"🎾","badminton":"🏸","hockey":"🏑",
          "baseball":"⚾","formula 1":"🏎️","f1":"🏎️","rugby":"🏉",
          "golf":"⛳","boxing":"🥊","mma":"🥋","ufc":"🥋","olympics":"🏅",
          "volleyball":"🏐","kabaddi":"🤼"}
    sl = sport_term.lower()
    for k, v in em.items():
        if k in sl: return v
    return "🏆"

def get_news(topic: str = "India") -> str:
    try:
        import xml.etree.ElementTree as ET
        url  = (f"https://news.google.com/rss/search?"
                f"q={requests.utils.quote(topic)}&hl=en-IN&gl=IN&ceid=IN:en")
        resp = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=8)
        root = ET.fromstring(resp.content)
        news = []
        for item in root.findall(".//item")[:6]:
            title = item.findtext("title","").strip()
            if title:
                clean = title.split(" - ")[0].strip()
                src   = title.split(" - ")[-1].strip() if " - " in title else "News"
                news.append(f"• **{clean}** _{src}_")
        return "\n".join(news) if news else "No news found."
    except Exception as e:
        return f"News fetch failed: {e}"

def is_news_query(q: str) -> bool:
    return any(k in q.lower() for k in [
        "news","headlines","latest news","today news",
        "breaking","top news","current news","what happened today"
    ])

def extract_news_topic(query: str) -> str:
    stopwords = {"news","latest","today","show","me","give","what","is",
                 "the","headlines","breaking","top","current","about","on"}
    words = query.replace("?","").split()
    return " ".join(w for w in words if w.lower() not in stopwords).strip() or "India"

STOCK_ALIASES = {
    "reliance":"RELIANCE.NS","tata":"TATAMOTORS.NS","tcs":"TCS.NS",
    "infosys":"INFY.NS","wipro":"WIPRO.NS","hdfc":"HDFCBANK.NS",
    "icici":"ICICIBANK.NS","sbi":"SBIN.NS","bajaj":"BAJFINANCE.NS",
    "adani":"ADANIENT.NS","ongc":"ONGC.NS","itc":"ITC.NS",
    "maruti":"MARUTI.NS","mahindra":"M&M.NS","kotak":"KOTAKBANK.NS",
    "axis bank":"AXISBANK.NS","titan":"TITAN.NS",
    "nifty":"^NSEI","sensex":"^BSESN","bank nifty":"^NSEBANK",
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

def get_stock_price(symbol: str, display_name: str) -> str:
    try:
        url  = (f"https://query1.finance.yahoo.com/v8/finance/chart/"
                f"{symbol}?interval=1d&range=2d")
        resp = requests.get(
            url,
            headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"},
            timeout=8
        )
        data  = resp.json()
        meta  = data["chart"]["result"][0]["meta"]
        price = meta.get("regularMarketPrice", 0)
        prev  = meta.get("chartPreviousClose", 0)
        curr  = meta.get("currency","USD")
        name  = meta.get("longName") or meta.get("shortName") or display_name
        exch  = meta.get("exchangeName","")
        mktst = meta.get("marketState","")
        chg   = price - prev
        pct   = (chg/prev*100) if prev else 0
        arrow = "🟢 ▲" if chg >= 0 else "🔴 ▼"
        sign  = "+" if chg >= 0 else ""
        high  = meta.get("regularMarketDayHigh","N/A")
        low   = meta.get("regularMarketDayLow","N/A")
        vol   = meta.get("regularMarketVolume","N/A")
        if isinstance(vol, int): vol = f"{vol:,}"
        return (
            f"Name: {name}\nExchange: {exch}\n"
            f"Price: {curr} {price:,.2f}\n"
            f"Change: {arrow} {sign}{chg:.2f} ({sign}{pct:.2f}%)\n"
            f"Day High: {high}\nDay Low: {low}\n"
            f"Volume: {vol}\nMarket: {mktst}"
        )
    except Exception as e:
        return f"Stock fetch failed: {e}"

def is_stock_query(query: str) -> bool:
    q = query.lower()
    return (any(a in q for a in [
                "stock","share price","stock price","price of","how much is",
                "market price","trading at","crypto","bitcoin","ethereum",
                "sensex","nifty","nasdaq","dow jones","coin price"]) or
            any(k in q for k in STOCK_ALIASES))

def web_search(query: str, max_results: int = 5) -> str:
    try:
        resp = requests.get(
            f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}",
            headers={"User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"},
            timeout=10
        )
        snippets = re.findall(
            r'class="result__snippet"[^>]*>(.*?)</(?:a|span)>',
            resp.text, re.DOTALL
        )
        titles = re.findall(
            r'class="result__title"[^>]*>.*?<a[^>]*>(.*?)</a>',
            resp.text, re.DOTALL
        )
        clean_s = [re.sub(r'<[^>]+>','',s).strip() for s in snippets[:max_results]]
        clean_t = [re.sub(r'<[^>]+>','',t).strip() for t in titles[:max_results]]
        results = [f"• {t}: {s}" for t,s in zip(clean_t,clean_s) if s]
        if results: return "\n".join(results)
        # fallback
        r2   = requests.get(
            "https://api.duckduckgo.com/",
            params={"q":query,"format":"json","no_html":"1","skip_disambig":"1"},
            timeout=8
        )
        data = r2.json()
        parts = []
        if data.get("Answer"):   parts.append(f"Answer: {data['Answer']}")
        if data.get("Abstract"): parts.append(f"Summary: {data['Abstract'][:500]}")
        for t in data.get("RelatedTopics",[])[:3]:
            if isinstance(t,dict) and t.get("Text"): parts.append(t["Text"][:200])
        return "\n".join(parts) if parts else "No results found."
    except Exception as e:
        return f"Search failed: {e}"

def get_current_facts(query: str) -> str:
    try:
        import xml.etree.ElementTree as ET
        url  = (f"https://news.google.com/rss/search?"
                f"q={requests.utils.quote(query)}&hl=en-IN&gl=IN&ceid=IN:en")
        resp = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=8)
        root = ET.fromstring(resp.content)
        results = []
        for item in root.findall(".//item")[:5]:
            title   = item.findtext("title","").strip()
            pub_raw = item.findtext("pubDate","")
            pub     = pub_raw[:22].strip() if pub_raw else ""
            if title:
                clean = title.split(" - ")[0].strip()
                results.append(f"[{pub}] {clean}" if pub else clean)
        return "\n".join(results) if results else ""
    except: return ""

SEARCH_TRIGGERS = [
    "who is","who was","who won","who are","who did",
    "what is","what was","what are","what happened",
    "when is","when was","when did","when will",
    "where is","where was","current","latest","recent",
    "today","election","prime minister","president",
    "chief minister","cm of","governor","minister of",
    "score","match","winner","champion","result",
    "price","stock","weather","2023","2024","2025",
]

def needs_search(query: str) -> bool:
    q = query.lower()
    if any(k in q for k in ["who made you","who created you","who built you",
                              "who are you","your creator"]): return False
    creation_kw = GAME_KEYWORDS + APP_KEYWORDS + SOFTWARE_KEYWORDS + DESIGN_KEYWORDS
    if any(k in q for k in creation_kw): return False
    return any(t in q for t in SEARCH_TRIGGERS)

LANGUAGE_MAP = {
    "python":("python","3.10.0"),
    "javascript":("javascript","18.15.0"),"js":("javascript","18.15.0"),
    "typescript":("typescript","5.0.3"),  "ts":("typescript","5.0.3"),
    "java":("java","15.0.2"),
    "c++":("c++","10.2.0"),              "cpp":("c++","10.2.0"),
    "c":("c","10.2.0"),
    "rust":("rust","1.68.2"),
    "go":("go","1.16.2"),
    "ruby":("ruby","3.0.1"),
    "php":("php","8.2.3"),
    "swift":("swift","5.3.3"),
    "kotlin":("kotlin","1.8.20"),
    "r":("r","4.1.1"),
    "bash":("bash","5.2.0"),"shell":("bash","5.2.0"),
    "sql":("sqlite3","3.36.0"),
    "lua":("lua","5.4.4"),
    "perl":("perl","5.36.0"),
    "scala":("scala","3.2.2"),
}

def run_code(code: str, language: str) -> str:
    try:
        lang, version = LANGUAGE_MAP.get(language.lower(), ("python","3.10.0"))
        resp   = requests.post(
            "https://emkc.org/api/v2/piston/execute",
            json={
                "language":lang,"version":version,
                "files":[{"name":f"main.{language[:3]}","content":code}],
                "stdin":"","args":[],"compile_timeout":10000,"run_timeout":5000,
            },
            timeout=15
        )
        result = resp.json()
        run    = result.get("run",{})
        out    = run.get("stdout","").strip()
        err    = run.get("stderr","").strip()
        comp   = result.get("compile",{}).get("stderr","").strip()
        if comp: return f"❌ Compile Error:\n{comp}"
        if err:  return f"❌ Error:\n{err}"
        return out or "✅ Code ran successfully (no output)"
    except Exception as e:
        return f"❌ Runner failed: {e}"

def extract_code_and_language(text: str):
    matches = re.findall(r"```(\w+)?\n([\s\S]*?)```", text)
    if matches:
        lang, code = matches[0]
        return code.strip(), (lang.lower() if lang else "python")
    return None, None

def extract_all_code_blocks(text: str):
    matches = re.findall(r"```(\w+)?\n([\s\S]*?)```", text)
    return [(lang.lower() if lang else "text", code.strip()) for lang,code in matches]

def is_code_query(query: str) -> bool:
    q = query.lower()
    if is_stock_query(query) or is_weather_query(query): return False
    return any(t in q for t in [
        "write","code","program","script","function","implement",
        "create","build","develop","make","generate","algorithm",
        "sort","search","fibonacci","factorial","prime","reverse",
        "palindrome","linked list","binary tree","api","flask",
        "django","react","html","css","sql query","regex",
        "class","oop","recursion","dynamic programming","leetcode",
        "debug","fix","error in","bug","solve","calculator",
    ])

def build_html_app(code_blocks: list) -> str:
    html_part, css_part, js_part, full_html = "", "", "", ""
    for lang, code in code_blocks:
        if lang == "html":
            if "<!doctype" in code.lower() or "<html" in code.lower():
                full_html = code
            else:
                html_part = code
        elif lang == "css":
            css_part = code
        elif lang in ("javascript","js"):
            js_part = code
    if full_html: return full_html
    if html_part or css_part or js_part:
        return (
            "<!DOCTYPE html>\n<html lang='en'>\n<head>\n"
            "<meta charset='UTF-8'>\n"
            "<meta name='viewport' content='width=device-width,initial-scale=1.0'>\n"
            "<title>Nova AI</title>\n"
            f"<style>{css_part}</style>\n</head>\n<body>\n"
            f"{html_part}\n<script>{js_part}</script>\n</body>\n</html>"
        )
    return ""


# ══════════════════════════════════════════════════════════════════════════════
#  ✅ THE FIX: build_messages now includes full conversation history
# ══════════════════════════════════════════════════════════════════════════════

def build_messages(
    user_query:     str,
    search_results: str  = "",
    is_weather:     bool = False,
    creation_type:  str  = "general"
) -> list:
    system = get_creation_system_prompt(creation_type)

    # ── 1. System prompt (always first) ───────────────────────────────────────
    messages = [{"role": "system", "content": system}]

    # ── 2. Conversation history (all previous turns) ──────────────────────────
    #    Skip the LAST item because that's the user message we're about to add.
    #    Also clean content: strip HTML badges before sending to API.
    history = st.session_state.messages[:-1]   # everything except current user msg

    # Keep only the last N turns to avoid token overflow
    if len(history) > MAX_HISTORY_TURNS * 2:
        history = history[-(MAX_HISTORY_TURNS * 2):]

    for msg in history:
        role    = msg["role"]
        content = msg["content"]

        # Strip HTML badge divs — the API doesn't need them
        content = re.sub(r'<div[^>]*>.*?</div>', '', content, flags=re.DOTALL)
        content = re.sub(r'<[^>]+>', '', content)          # strip any remaining HTML
        content = content.strip()

        if content:   # skip empty messages after stripping
            messages.append({"role": role, "content": content[:3000]})

    # ── 3. Current user message (with optional search context) ────────────────
    if search_results and is_weather:
        user_content = (
            f"Live weather data for '{user_query}':\n\n{search_results}\n\n"
            f"Present this weather info clearly."
        )
    elif search_results:
        user_content = (
            f"Web search results for '{user_query}':\n\n{search_results}\n\n"
            f"Answer this accurately based on the above: {user_query}\n"
            f"Use search data as primary source. Be direct and confident."
        )
    else:
        user_content = user_query

    messages.append({"role": "user", "content": user_content[:4000]})
    return messages


# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
if "messages" not in st.session_state:
    st.session_state.messages = []


# ══════════════════════════════════════════════════════════════════════════════
#  HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-badge">LIVE &nbsp;·&nbsp; FREE &nbsp;·&nbsp; UNLIMITED &nbsp;·&nbsp; MEMORY ✓</div>
    <h1>Nova<span> AI</span></h1>
    <p>World-class AI with full memory — builds games, apps, software & anything you imagine.</p>
</div>
<div class="stats-row">
    <div class="stat-pill"><span class="dot dot-purple"></span> 🧠 Full Memory</div>
    <div class="stat-pill"><span class="dot dot-blue"></span>  🎮 Games</div>
    <div class="stat-pill"><span class="dot dot-orange"></span> 🚀 Apps</div>
    <div class="stat-pill"><span class="dot dot-green"></span> 💻 20+ Languages</div>
    <div class="stat-pill"><span class="dot dot-green"></span> 📈 Live Data</div>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

# ── Toolbar ───────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([5, 1, 1])
with col2:
    count = len([m for m in st.session_state.messages if m["role"] == "user"])
    st.markdown(
        f"<p style='text-align:right;color:var(--muted);font-size:12.5px;"
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
    <div style="text-align:center;padding:2rem 1rem 1rem;color:var(--muted);">
        <div style="font-size:2.2rem;margin-bottom:.8rem">✨</div>
        <p style="font-size:1rem;font-weight:600;color:#94a3b8;margin-bottom:1.2rem">
            What would you like to create today?
        </p>
    </div>
    <div class="category-grid">
        <div class="category-card">
            <div class="category-icon">🎮</div>
            <div class="category-title">Games</div>
            <div class="category-examples">Snake · Tetris · 2048<br>Flappy Bird · Chess</div>
        </div>
        <div class="category-card">
            <div class="category-icon">🚀</div>
            <div class="category-title">Apps</div>
            <div class="category-examples">Dashboard · Todo · Chat<br>E-commerce · Portfolio</div>
        </div>
        <div class="category-card">
            <div class="category-icon">✨</div>
            <div class="category-title">UI Design</div>
            <div class="category-examples">Landing Pages · Components<br>Animations · Themes</div>
        </div>
        <div class="category-card">
            <div class="category-icon">💻</div>
            <div class="category-title">Code</div>
            <div class="category-examples">Python · JS · Java · C++<br>Algorithms · APIs</div>
        </div>
        <div class="category-card">
            <div class="category-icon">🌐</div>
            <div class="category-title">Live Data</div>
            <div class="category-examples">Weather · Stocks · Crypto<br>Sports · News</div>
        </div>
        <div class="category-card">
            <div class="category-icon">🧠</div>
            <div class="category-title">Memory ✓</div>
            <div class="category-examples">Remembers everything<br>Full conversation context</div>
        </div>
    </div>
    <div class="divider"></div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("searched"):
                st.markdown('<div class="search-badge">🔍 Searched the web</div>',
                            unsafe_allow_html=True)
            ct = msg.get("creation_type","")
            if ct and ct != "general":
                st.markdown(get_creation_badge(ct), unsafe_allow_html=True)
            st.markdown(msg["content"])


# ══════════════════════════════════════════════════════════════════════════════
#  CHAT INPUT
# ══════════════════════════════════════════════════════════════════════════════
if prompt := st.chat_input("Ask me anything — I remember our full conversation 🧠"):

    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        searched       = False
        search_results = ""

        # ── Stock ─────────────────────────────────────────────────────────────
        if is_stock_query(prompt):
            symbol, dname = extract_stock_symbol(prompt)
            if not symbol:
                response = "❌ Couldn't identify the stock. Try: *'Apple stock price'*"
            else:
                with st.spinner(f"📈 Fetching live price for {dname}…"):
                    sd = get_stock_price(symbol, dname)
                if "failed" in sd.lower():
                    response = f"❌ Couldn't fetch price for **{dname}**."
                else:
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

        # ── Sports ────────────────────────────────────────────────────────────
        elif is_sports_query(prompt):
            sport_term = detect_sport(prompt)
            emoji = get_sport_emoji(sport_term)
            with st.spinner(f"{emoji} Fetching live sports…"):
                sports_data = get_sports_news(sport_term)
            response = (
                f'<div class="search-badge">{emoji} Live sports</div>\n\n'
                f"### {emoji} {sport_term.title()}\n\n{sports_data}"
            )
            st.markdown(response, unsafe_allow_html=True)
            st.session_state.messages.append({"role":"assistant","content":response})

        # ── News ──────────────────────────────────────────────────────────────
        elif is_news_query(prompt):
            with st.spinner("📰 Fetching news…"):
                topic     = extract_news_topic(prompt)
                news_data = get_news(topic)
            response = (
                f'<div class="search-badge">📰 Live news</div>\n\n'
                f"### 📰 {topic.title()}\n\n{news_data}"
            )
            st.markdown(response, unsafe_allow_html=True)
            st.session_state.messages.append({"role":"assistant","content":response})

        # ── Weather ───────────────────────────────────────────────────────────
        elif is_weather_query(prompt):
            with st.spinner("🌤️ Fetching weather…"):
                city         = extract_city_from_query(prompt)
                weather_data = get_weather(city)
            if "failed" in weather_data.lower():
                response = f"❌ Couldn't fetch weather for **{city}**."
            else:
                L = dict(l.split(": ",1) for l in weather_data.strip().splitlines() if ": " in l)
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
            st.markdown(response, unsafe_allow_html=True)
            st.session_state.messages.append({"role":"assistant","content":response})

        # ── Creation / Code / General (WITH MEMORY) ───────────────────────────
        else:
            creation_type = classify_creation_request(prompt)

            if needs_search(prompt):
                with st.spinner("🔍 Searching the web…"):
                    search_results = web_search(prompt)
                    news_ctx = get_current_facts(prompt)
                    if news_ctx:
                        search_results += "\n\nRecent headlines:\n" + news_ctx
                    searched = True

            for attempt in range(3):
                try:
                    spin = (get_creation_spinner(creation_type)
                            if attempt == 0 else "Rate limited — retrying ⏳")
                    with st.spinner(spin):
                        if attempt > 0: time.sleep(60)

                        # ✅ Full history is passed here
                        completion = client.chat.completions.create(
                            messages=build_messages(
                                prompt,
                                search_results,
                                creation_type=creation_type
                            ),
                            model=MODEL,
                            max_tokens=4096,
                            temperature=0.25,
                        )
                    response = completion.choices[0].message.content

                    # Badges
                    if searched:
                        st.markdown('<div class="search-badge">🔍 Web search</div>',
                                    unsafe_allow_html=True)
                    badge = get_creation_badge(creation_type)
                    if badge:
                        st.markdown(badge, unsafe_allow_html=True)

                    # Memory indicator for follow-up questions
                    if len(st.session_state.messages) > 2:
                        st.markdown(
                            f'<div class="memory-badge">'
                            f'🧠 Remembering {len(st.session_state.messages)//2} turns</div>',
                            unsafe_allow_html=True
                        )

                    # Parse & render
                    code_blocks = extract_all_code_blocks(response)
                    code, lang  = extract_code_and_language(response)
                    langs_found = [l for l,_ in code_blocks]
                    is_web      = any(l in ("html","css","javascript","js")
                                      for l in langs_found)

                    st.markdown(response)

                    # Live HTML preview
                    if is_web:
                        html_src = build_html_app(code_blocks)
                        if html_src:
                            st.markdown("---")
                            labels = {
                                "game":    "🎮 Live Game — Play it here!",
                                "app":     "🚀 Live App Preview",
                                "software":"⚙️ Live Software Preview",
                                "design":  "✨ Live Design Preview",
                            }
                            st.markdown(f"### {labels.get(creation_type,'🖥️ Live Preview')}")
                            h = 650 if creation_type in ("game","app","software") else 520
                            st.components.v1.html(html_src, height=h, scrolling=True)
                            b64   = base64.b64encode(html_src.encode()).decode()
                            fnames = {"game":"nova_game.html","app":"nova_app.html",
                                      "software":"nova_software.html","design":"nova_design.html"}
                            fname = fnames.get(creation_type,"nova_ai.html")
                            st.markdown(
                                f'<a href="data:text/html;base64,{b64}" '
                                f'download="{fname}" class="btn-download">'
                                f'⬇️ Download {fname}</a>',
                                unsafe_allow_html=True
                            )

                    # Run button for non-web code
                    elif code and lang and lang not in ("html","css"):
                        rk = f"run_{len(st.session_state.messages)}"
                        if st.button(f"▶ Run {lang.title()}", key=rk):
                            with st.spinner(f"⚙️ Running {lang}…"):
                                out = run_code(code, lang)
                            st.markdown(
                                f'<div class="{"error-box" if "❌" in out else "output-box"}">'
                                f'{out}</div>',
                                unsafe_allow_html=True
                            )

                    st.session_state.messages.append({
                        "role":          "assistant",
                        "content":       response,
                        "searched":      searched,
                        "creation_type": creation_type,
                    })
                    break

                except Exception as e:
                    if "rate_limit_exceeded" in str(e) and attempt < 2:
                        continue
                    st.error(f"❌ Error: {e}")
                    break
