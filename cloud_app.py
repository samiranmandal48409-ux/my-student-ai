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
.code-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(124,58,237,.08); border: 1px solid rgba(124,58,237,.3);
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
.preview-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(0,229,255,.08); border: 1px solid rgba(0,229,255,.25);
    border-radius: 6px; padding: 3px 10px;
    font-size: 11px; color: var(--accent); margin-bottom: .5rem;
}
.preview-frame {
    width: 100%; border: 1px solid var(--border);
    border-radius: 12px; margin-top: .5rem;
    background: #fff; overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

# ── Groq client ───────────────────────────────────────────────────────────────
client = Groq(api_key="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")
MODEL = "llama-3.3-70b-versatile"

# ── Weather via wttr.in (100% free, no API key needed) ───────────────────────
def get_weather(city: str) -> str:
    """Fetch real-time weather from wttr.in — no API key required."""
    try:
        url = f"https://wttr.in/{requests.utils.quote(city)}?format=j1"
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        data = resp.json()

        current     = data["current_condition"][0]
        area        = data["nearest_area"][0]
        city_name   = area["areaName"][0]["value"]
        country     = area["country"][0]["value"]
        temp        = current["temp_C"]
        feels_like  = current["FeelsLikeC"]
        humidity    = current["humidity"]
        description = current["weatherDesc"][0]["value"]
        wind_speed  = current["windspeedKmph"]
        visibility  = current["visibility"]
        uv_index    = current["uvIndex"]

        return (
            f"City: {city_name}, {country}\n"
            f"Temperature: {temp}°C (Feels like {feels_like}°C)\n"
            f"Condition: {description}\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind_speed} km/h\n"
            f"Visibility: {visibility} km\n"
            f"UV Index: {uv_index}"
        )
    except Exception as e:
        return f"Weather fetch failed: {e}"


def extract_city_from_query(query: str) -> str:
    """Extract city name from a weather query using regex — much more reliable."""
    import re
    match = re.search(
        r'(?:weather|temperature|forecast|humidity|climate)\s+(?:report\s+)?(?:in|for|of|at)\s+([A-Za-z ,]+?)(?:\?|$)',
        query, re.IGNORECASE
    )
    if match:
        city = match.group(1).strip().rstrip(",")
        return city
    stopwords = {
        "what", "is", "the", "weather", "report", "temperature", "forecast",
        "today", "current", "now", "like", "how", "give", "me", "show",
        "humidity", "climate", "condition", "conditions", "a", "an"
    }
    words = query.replace("?", "").split()
    city_words = [w for w in words if w.lower() not in stopwords]
    return " ".join(city_words).strip() or "Guwahati"


# ── Universal Sports via Google News RSS (free, no API key, all sports) ───────
SPORTS_MAP = {
    # Cricket
    "cricket": "cricket", "ipl": "IPL cricket", "test match": "test cricket",
    "odi": "ODI cricket", "t20": "T20 cricket", "wicket": "cricket",
    "innings": "cricket innings", "batting": "cricket batting",

    # Football / Soccer
    "football": "football", "soccer": "soccer", "premier league": "Premier League",
    "fifa": "FIFA football", "champions league": "UEFA Champions League",
    "la liga": "La Liga", "bundesliga": "Bundesliga", "serie a": "Serie A",
    "world cup": "FIFA World Cup", "euro": "UEFA Euro football",

    # Basketball
    "basketball": "basketball", "nba": "NBA basketball", "nbl": "NBL basketball",

    # Tennis
    "tennis": "tennis", "wimbledon": "Wimbledon tennis", "us open tennis": "US Open tennis",
    "french open": "French Open tennis", "australian open": "Australian Open tennis",
    "atp": "ATP tennis", "wta": "WTA tennis",

    # Badminton
    "badminton": "badminton", "bwf": "BWF badminton",

    # Hockey
    "hockey": "hockey", "field hockey": "field hockey", "ice hockey": "ice hockey",
    "nhl": "NHL ice hockey",

    # Baseball
    "baseball": "baseball", "mlb": "MLB baseball",

    # Formula 1 / motorsport
    "formula 1": "Formula 1", "f1": "F1 race", "motorsport": "motorsport",
    "motogp": "MotoGP", "nascar": "NASCAR racing",

    # Rugby
    "rugby": "rugby", "rugby world cup": "Rugby World Cup",

    # Golf
    "golf": "golf", "masters": "Masters golf", "pga": "PGA golf",

    # Boxing / MMA
    "boxing": "boxing", "mma": "MMA UFC", "ufc": "UFC fight",
    "wrestling": "wrestling WWE",

    # Olympics
    "olympics": "Olympics", "asian games": "Asian Games",
    "commonwealth games": "Commonwealth Games",

    # Table Tennis
    "table tennis": "table tennis", "ping pong": "ping pong",

    # Volleyball
    "volleyball": "volleyball",

    # Kabaddi
    "kabaddi": "kabaddi PKL",

    # Athletics
    "athletics": "athletics sprint", "marathon": "marathon running",
    "swimming": "swimming sport", "cycling": "cycling sport",
}

def detect_sport(query: str) -> str:
    """Detect which sport the user is asking about and return a search term."""
    q = query.lower()
    for keyword, search_term in SPORTS_MAP.items():
        if keyword in q:
            return search_term
    return "sports scores today"   # generic fallback


def get_sports_news(sport_term: str) -> str:
    """Fetch live sports news/scores from Google News RSS — no API key needed."""
    try:
        import xml.etree.ElementTree as ET
        query = requests.utils.quote(f"{sport_term} score result today")
        url = f"https://news.google.com/rss/search?q={query}&hl=en&gl=US&ceid=US:en"
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        root = ET.fromstring(resp.content)
        items = root.findall(".//item")[:7]
        results = []
        for item in items:
            title = item.findtext("title", "").strip()
            pub   = item.findtext("pubDate", "")[:22].strip()
            if title:
                clean = title.split(" - ")[0].strip()
                src   = title.split(" - ")[-1].strip() if " - " in title else ""
                results.append(f"• **{clean}**" + (f" _{src}_" if src else ""))
        return "\n".join(results) if results else "No recent sports updates found."
    except Exception as e:
        return f"Sports fetch failed: {e}"


def is_sports_query(query: str) -> bool:
    """Strict sports detection — only trigger on clear sports intent."""
    import re
    q = query.lower()

    # Hard exclude — these are never sports questions even if they contain sport words
    non_sport_phrases = [
        "why", "how does", "explain", "what does", "politics", "economy",
        "government", "policy", "modi", "minister", "election", "vote",
        "buy", "sell", "market", "gold", "holiday", "travel", "foreign",
        "history of", "origin of", "definition", "meaning of", "what is the",
        "tell me about", "who invented", "science", "health", "study",
    ]
    if any(phrase in q for phrase in non_sport_phrases):
        return False

    # Must contain a clear sports action word AND a sport name
    action_words = [
        "score", "scores", "result", "results", "match", "game", "live",
        "fixture", "standings", "winner", "champion", "playoff", "final",
        "semifinal", "quarterfinal", "tournament", "league table", "points table",
        "who won", "who is playing", "today's match", "latest score",
    ]
    sport_names = list(SPORTS_MAP.keys())

    has_action = any(re.search(r'\b' + re.escape(a) + r'\b', q) for a in action_words)
    has_sport  = any(re.search(r'\b' + re.escape(s) + r'\b', q) for s in sport_names)

    return has_action and has_sport


def get_sport_emoji(sport_term: str) -> str:
    """Return an emoji for the detected sport."""
    emoji_map = {
        "cricket": "🏏", "ipl": "🏏", "football": "⚽", "soccer": "⚽",
        "basketball": "🏀", "nba": "🏀", "tennis": "🎾", "badminton": "🏸",
        "hockey": "🏑", "baseball": "⚾", "formula 1": "🏎️", "f1": "🏎️",
        "rugby": "🏉", "golf": "⛳", "boxing": "🥊", "mma": "🥋", "ufc": "🥋",
        "olympics": "🏅", "volleyball": "🏐", "kabaddi": "🤼", "swimming": "🏊",
        "cycling": "🚴", "athletics": "🏃", "wrestling": "🤼", "motorsport": "🏎️",
    }
    sport_lower = sport_term.lower()
    for key, emoji in emoji_map.items():
        if key in sport_lower:
            return emoji
    return "🏆"


# ── News via Google News RSS (free, no API key, unlimited) ────────────────────
def get_news(topic: str = "India") -> str:
    """Fetch latest news from Google News RSS — no API key needed."""
    try:
        import xml.etree.ElementTree as ET
        query = requests.utils.quote(topic)
        url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        root = ET.fromstring(resp.content)
        items = root.findall(".//item")[:6]
        news_list = []
        for item in items:
            title = item.findtext("title", "").strip()
            pub   = item.findtext("pubDate", "").strip()
            source = item.findtext("source", title)
            if title:
                # Clean up title (Google News adds source at end after " - ")
                clean_title = title.split(" - ")[0].strip()
                src = title.split(" - ")[-1].strip() if " - " in title else "News"
                news_list.append(f"• **{clean_title}** _{src}_")
        return "\n".join(news_list) if news_list else "No news found for this topic."
    except Exception as e:
        return f"News fetch failed: {e}"


def is_news_query(query: str) -> bool:
    q = query.lower()
    keywords = ["news", "headlines", "latest news", "today news", "breaking",
                "top news", "current news", "what happened today"]
    return any(k in q for k in keywords)


def extract_news_topic(query: str) -> str:
    """Extract news topic from query."""
    stopwords = {"news", "latest", "today", "show", "me", "give", "what", "is",
                 "the", "headlines", "breaking", "top", "current", "about", "on"}
    words = query.replace("?", "").split()
    topic_words = [w for w in words if w.lower() not in stopwords]
    return " ".join(topic_words).strip() or "India"


# ── Stock prices via Yahoo Finance (free, no API key, unlimited) ──────────────

# Common stock name → ticker symbol map
STOCK_ALIASES = {
    # Indian stocks
    "reliance": "RELIANCE.NS", "tata": "TATAMOTORS.NS", "tcs": "TCS.NS",
    "infosys": "INFY.NS", "wipro": "WIPRO.NS", "hdfc": "HDFCBANK.NS",
    "icici": "ICICIBANK.NS", "sbi": "SBIN.NS", "bajaj": "BAJFINANCE.NS",
    "adani": "ADANIENT.NS", "ongc": "ONGC.NS", "itc": "ITC.NS",
    "hindustan unilever": "HINDUNILVR.NS", "hul": "HINDUNILVR.NS",
    "maruti": "MARUTI.NS", "mahindra": "M&M.NS", "nestle": "NESTLEIND.NS",
    "kotak": "KOTAKBANK.NS", "axis bank": "AXISBANK.NS", "titan": "TITAN.NS",
    "sun pharma": "SUNPHARMA.NS", "dr reddy": "DRREDDY.NS",
    "nifty": "^NSEI", "sensex": "^BSESN", "bank nifty": "^NSEBANK",

    # US stocks
    "apple": "AAPL", "microsoft": "MSFT", "google": "GOOGL",
    "alphabet": "GOOGL", "amazon": "AMZN", "tesla": "TSLA",
    "meta": "META", "facebook": "META", "netflix": "NFLX",
    "nvidia": "NVDA", "samsung": "005930.KS", "intel": "INTC",
    "amd": "AMD", "uber": "UBER", "twitter": "X", "x corp": "X",

    # Crypto
    "bitcoin": "BTC-USD", "btc": "BTC-USD", "ethereum": "ETH-USD",
    "eth": "ETH-USD", "dogecoin": "DOGE-USD", "doge": "DOGE-USD",
    "solana": "SOL-USD", "bnb": "BNB-USD", "xrp": "XRP-USD",

    # Indices
    "dow jones": "^DJI", "nasdaq": "^IXIC", "s&p 500": "^GSPC",
    "s&p": "^GSPC", "ftse": "^FTSE", "nikkei": "^N225",
}

def extract_stock_symbol(query: str) -> tuple:
    """Extract stock ticker and display name from query."""
    q = query.lower()
    # Check alias map first
    for name, ticker in STOCK_ALIASES.items():
        if name in q:
            return ticker, name.title()
    # Try to extract uppercase ticker directly e.g. "AAPL stock"
    import re
    match = re.search(r'\b([A-Z]{1,5})\b', query)
    if match:
        return match.group(1), match.group(1)
    return None, None


def get_stock_price(symbol: str, display_name: str) -> str:
    """Fetch live stock price from Yahoo Finance — no API key needed."""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=2d"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        }
        resp = requests.get(url, headers=headers, timeout=8)
        data = resp.json()

        meta   = data["chart"]["result"][0]["meta"]
        price  = meta.get("regularMarketPrice", 0)
        prev   = meta.get("chartPreviousClose", 0)
        curr   = meta.get("currency", "USD")
        name   = meta.get("longName") or meta.get("shortName") or display_name
        exch   = meta.get("exchangeName", "")
        mktst  = meta.get("marketState", "")

        change     = price - prev
        change_pct = (change / prev * 100) if prev else 0
        arrow      = "🟢 ▲" if change >= 0 else "🔴 ▼"
        sign       = "+" if change >= 0 else ""

        high = meta.get("regularMarketDayHigh", "N/A")
        low  = meta.get("regularMarketDayLow",  "N/A")
        vol  = meta.get("regularMarketVolume",  "N/A")
        if isinstance(vol, int):
            vol = f"{vol:,}"

        return (
            f"Name: {name}\n"
            f"Exchange: {exch}\n"
            f"Price: {curr} {price:,.2f}\n"
            f"Change: {arrow} {sign}{change:.2f} ({sign}{change_pct:.2f}%)\n"
            f"Day High: {high}\n"
            f"Day Low: {low}\n"
            f"Volume: {vol}\n"
            f"Market: {mktst}"
        )
    except Exception as e:
        return f"Stock fetch failed: {e}"


def is_stock_query(query: str) -> bool:
    """Detect stock/crypto price queries strictly."""
    import re
    q = query.lower()

    # Must contain a finance action word
    action_words = [
        "stock", "share price", "stock price", "price of", "how much is",
        "market price", "trading at", "crypto", "bitcoin", "ethereum",
        "sensex", "nifty", "nasdaq", "dow jones", "index", "ticker",
        "coin price", "token price", "market cap",
    ]
    # OR a known alias
    known = list(STOCK_ALIASES.keys())

    has_action = any(a in q for a in action_words)
    has_known  = any(k in q for k in known)

    return has_action or has_known

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

def is_weather_query(query: str) -> bool:
    """Check if the query is asking about weather."""
    q = query.lower()
    weather_keywords = ["weather", "temperature", "forecast", "humidity", "rain", "sunny", "cloudy", "wind speed", "climate today"]
    return any(k in q for k in weather_keywords)

def needs_search(query: str) -> bool:
    q = query.lower()
    identity_keywords = ["who made you", "who created you", "who built you", "who are you", "your creator", "your developer"]
    if any(k in q for k in identity_keywords):
        return False
    return any(trigger in q for trigger in SEARCH_TRIGGERS)


# ── Piston API: free, unlimited, 50+ languages code runner ───────────────────
LANGUAGE_MAP = {
    "python": ("python", "3.10.0"),
    "javascript": ("javascript", "18.15.0"), "js": ("javascript", "18.15.0"),
    "typescript": ("typescript", "5.0.3"),   "ts": ("typescript", "5.0.3"),
    "java": ("java", "15.0.2"),
    "c++": ("c++", "10.2.0"),               "cpp": ("c++", "10.2.0"),
    "c": ("c", "10.2.0"),
    "rust": ("rust", "1.68.2"),
    "go": ("go", "1.16.2"),
    "ruby": ("ruby", "3.0.1"),
    "php": ("php", "8.2.3"),
    "swift": ("swift", "5.3.3"),
    "kotlin": ("kotlin", "1.8.20"),
    "r": ("r", "4.1.1"),
    "bash": ("bash", "5.2.0"),              "shell": ("bash", "5.2.0"),
    "sql": ("sqlite3", "3.36.0"),
    "lua": ("lua", "5.4.4"),
    "perl": ("perl", "5.36.0"),
    "scala": ("scala", "3.2.2"),
}

def run_code(code: str, language: str) -> str:
    """Run code using Piston API — free, unlimited, no API key."""
    try:
        lang, version = LANGUAGE_MAP.get(language.lower(), ("python", "3.10.0"))
        payload = {
            "language": lang,
            "version": version,
            "files": [{"name": f"main.{language[:2]}", "content": code}],
            "stdin": "", "args": [], "compile_timeout": 10000, "run_timeout": 5000,
        }
        resp = requests.post(
            "https://emkc.org/api/v2/piston/execute",
            json=payload, timeout=15
        )
        result = resp.json()
        run = result.get("run", {})
        output  = run.get("stdout", "").strip()
        stderr  = run.get("stderr", "").strip()
        compile_out = result.get("compile", {}).get("stderr", "").strip()

        if compile_out:
            return f"❌ Compile Error:\n{compile_out}"
        if stderr:
            return f"❌ Error:\n{stderr}"
        return output or "✅ Code ran successfully (no output)"
    except Exception as e:
        return f"❌ Runner failed: {e}"


def extract_code_and_language(text: str):
    """Extract code blocks and language from markdown response."""
    import re
    pattern = r"```(\w+)?\n([\s\S]*?)```"
    matches = re.findall(pattern, text)
    if matches:
        lang, code = matches[0]
        return code.strip(), (lang.lower() if lang else "python")
    return None, None


def is_code_query(query: str) -> bool:
    """Detect if user wants code written."""
    import re
    q = query.lower()
    if is_stock_query(query) or is_weather_query(query):
        return False
    code_triggers = [
        "write", "code", "program", "script", "function", "implement",
        "create", "build", "develop", "make", "generate", "algorithm",
        "sort", "search", "fibonacci", "factorial", "prime", "reverse",
        "palindrome", "linked list", "binary tree", "api", "flask",
        "django", "react", "html", "css", "sql query", "regex",
        "class", "oop", "recursion", "dynamic programming", "leetcode",
        "debug", "fix", "error in", "bug", "solve", "calculator",
        "game", "snake game", "todo", "login", "crud", "rest api",
    ]
    return any(t in q for t in code_triggers)


def is_app_query(query: str) -> bool:
    """Detect if user wants a full app, UI, website, or software."""
    q = query.lower()
    app_triggers = [
        "app", "application", "website", "web app", "software", "ui", "design",
        "landing page", "dashboard", "portfolio", "login page", "signup",
        "admin panel", "e-commerce", "shop", "store", "blog", "chat app",
        "todo app", "weather app", "calculator app", "quiz app", "game",
        "snake game", "tic tac toe", "2048", "music player", "timer",
        "stopwatch", "clock", "form", "registration", "survey",
        "expense tracker", "budget", "note app", "kanban", "trello",
        "netflix clone", "youtube clone", "twitter clone", "instagram",
        "whatsapp ui", "mobile app ui", "responsive", "animated",
    ]
    return any(t in q for t in app_triggers)


def extract_all_code_blocks(text: str):
    """Extract ALL code blocks from response."""
    import re
    pattern = r"```(\w+)?\n([\s\S]*?)```"
    matches = re.findall(pattern, text)
    return [(lang.lower() if lang else "text", code.strip()) for lang, code in matches]


def build_html_app(code_blocks: list) -> str:
    """Merge html/css/js blocks into one complete HTML file."""
    html_part, css_part, js_part = "", "", ""
    full_html = ""
    for lang, code in code_blocks:
        if lang in ("html",):
            if "<!doctype" in code.lower() or "<html" in code.lower():
                full_html = code   # already complete
            else:
                html_part = code
        elif lang == "css":
            css_part = code
        elif lang in ("javascript", "js"):
            js_part = code

    if full_html:
        return full_html
    if html_part or css_part or js_part:
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nova AI App</title>
<style>{css_part}</style>
</head>
<body>
{html_part}
<script>{js_part}</script>
</body>
</html>"""
    return ""


# ── Build prompt ──────────────────────────────────────────────────────────────
def build_messages(user_query: str, search_results: str = "", is_weather: bool = False):
    system = (
        "You are Nova AI — the world's best AI coding assistant and smart assistant, created by Samiran. "
        "If anyone asks who made you, always say: 'I am Nova AI, created by Samiran.' "
        "Never mention Meta, Llama, OpenAI, Groq, Anthropic, or any underlying model. "

        # ── Coding excellence ──
        "When writing code, you produce WORLD-CLASS, production-ready code. Follow these rules: "
        "1. Always write complete, fully working code — never write partial or placeholder code. "
        "2. Use best practices: clean variable names, proper error handling, comments, and structure. "
        "3. For algorithms, use the most optimal time and space complexity. "
        "4. Always specify the programming language in the code block (```python, ```javascript, etc). "
        "5. After the code, briefly explain what it does and the time/space complexity if relevant. "
        "6. If asked to fix code, explain exactly what was wrong and why. "
        "7. Support ALL languages: Python, JavaScript, TypeScript, Java, C++, C, Rust, Go, Ruby, PHP, Swift, Kotlin, SQL, Bash, R, Lua, Scala, and more. "
        "8. For web apps and UI design: write COMPLETE single-file HTML with embedded CSS and JS. "
        "   Use beautiful modern design — gradients, animations, glassmorphism, dark themes. "
        "   Make it fully functional and interactive. Include ALL features the user asked for. "
        "   Use Google Fonts, Font Awesome icons via CDN. Make it mobile responsive. "
        "9. For app requests: think like a senior UI/UX designer + developer. "
        "   Create stunning, professional designs that look like real products. "
        "10. Never truncate code — always write the full implementation. "

        # ── General ──
        "Answer clearly and directly. Never hallucinate. "
        "If web search results are provided, use ONLY those for factual questions. "
        "Be concise but complete."
    )
    if search_results and is_weather:
        user_content = (
            f"Here is the live weather data fetched for '{user_query}':\n\n"
            f"{search_results}\n\nPresent this weather information clearly."
        )
    elif search_results:
        user_content = (
            f"Web search results for '{user_query}':\n{search_results}\n\n"
            f"Based on the above, answer accurately: {user_query}"
        )
    else:
        user_content = user_query

    return [
        {"role": "system", "content": system},
        {"role": "user",   "content": user_content[:4000]}
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
    <div class="stat-pill"><span class="dot dot-purple"></span> World-class coding</div>
    <div class="stat-pill"><span class="dot dot-green"></span> Run code live</div>
    <div class="stat-pill"><span class="dot dot-blue"></span> 20+ languages</div>
    <div class="stat-pill"><span class="dot dot-green"></span> Stocks · Sports · News</div>
    <div class="stat-pill"><span class="dot dot-blue"></span> Live weather</div>
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
            💻 <em>"Write a Python web scraper"</em><br>
            🔧 <em>"Build a REST API in Flask"</em><br>
            🌤️ <em>"Weather in Guwahati, Assam"</em><br>
            📈 <em>"Apple stock price"</em> · <em>"Bitcoin price"</em><br>
            ⚽ <em>"Premier League scores"</em> · <em>"IPL result"</em><br>
            📰 <em>"Latest news about India"</em>
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

        # ── Stock prices: Yahoo Finance, no API key ───────────────────────────
        if is_stock_query(prompt):
            symbol, display_name = extract_stock_symbol(prompt)
            if not symbol:
                response = "❌ Sorry, I couldn't identify the stock. Try asking like: *'Apple stock price'* or *'Reliance share price'*."
            else:
                with st.spinner(f"📈 Fetching live price for {display_name}…"):
                    stock_data = get_stock_price(symbol, display_name)
                if "failed" in stock_data.lower():
                    response = f"❌ Couldn't fetch price for **{display_name}**. The market may be closed or symbol not found."
                else:
                    lines = dict(line.split(": ", 1) for line in stock_data.strip().splitlines() if ": " in line)
                    chg   = lines.get('Change', '')
                    color = "#10b981" if "▲" in chg else "#ef4444"
                    response = (
                        f'<div class="search-badge">📈 Live market data · Yahoo Finance</div>\n\n'
                        f"### 📈 {lines.get('Name', display_name)}\n"
                        f"_{lines.get('Exchange', '')} · Market: {lines.get('Market', 'N/A')}_\n\n"
                        f"| Detail | Value |\n"
                        f"|--------|-------|\n"
                        f"| 💰 Price | **{lines.get('Price', 'N/A')}** |\n"
                        f"| 📊 Change | {lines.get('Change', 'N/A')} |\n"
                        f"| 📈 Day High | {lines.get('Day High', 'N/A')} |\n"
                        f"| 📉 Day Low | {lines.get('Day Low', 'N/A')} |\n"
                        f"| 🔢 Volume | {lines.get('Volume', 'N/A')} |\n\n"
                        f"_Data from Yahoo Finance · Delayed ~15 min_"
                    )
            st.markdown(response, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": response})

        # ── Sports: universal handler for ALL world sports ────────────────────
        elif is_sports_query(prompt):
            sport_term = detect_sport(prompt)
            emoji = get_sport_emoji(sport_term)
            with st.spinner(f"{emoji} Fetching live sports updates…"):
                sports_data = get_sports_news(sport_term)
            response = (
                f'<div class="search-badge">{emoji} Live sports data</div>\n\n'
                f"### {emoji} Latest — {sport_term.title()}\n\n"
                f"{sports_data}"
            )
            st.markdown(response, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": response})

        # ── News: fetch & display directly ────────────────────────────────────
        elif is_news_query(prompt):
            with st.spinner("📰 Fetching latest news…"):
                topic = extract_news_topic(prompt)
                news_data = get_news(topic)
            response = (
                f'<div class="search-badge">📰 Live news</div>\n\n'
                f"### 📰 Latest News — {topic.title()}\n\n"
                f"{news_data}"
            )
            st.markdown(response, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": response})

        # ── Weather: fetch & display directly, NO AI involved ────────────────
        elif is_weather_query(prompt):
            with st.spinner("🌤️ Fetching live weather…"):
                city = extract_city_from_query(prompt)
                weather_data = get_weather(city)

            if "failed" in weather_data.lower() or "error" in weather_data.lower():
                response = f"❌ Sorry, I couldn't fetch weather for **{city}**. Please try again."
            else:
                # Parse the weather string into a nice formatted response
                lines = dict(line.split(": ", 1) for line in weather_data.strip().splitlines() if ": " in line)
                response = (
                    f'<div class="search-badge">🌤️ Live weather data</div>\n\n'
                    f"### 🌍 Weather Report — {lines.get('City', city)}\n\n"
                    f"| Detail | Value |\n"
                    f"|--------|-------|\n"
                    f"| 🌡️ Temperature | {lines.get('Temperature', 'N/A')} |\n"
                    f"| 🌤️ Condition | {lines.get('Condition', 'N/A')} |\n"
                    f"| 💧 Humidity | {lines.get('Humidity', 'N/A')} |\n"
                    f"| 💨 Wind Speed | {lines.get('Wind Speed', 'N/A')} |\n"
                    f"| 👁️ Visibility | {lines.get('Visibility', 'N/A')} |\n"
                    f"| ☀️ UV Index | {lines.get('UV Index', 'N/A')} |\n"
                )

            st.markdown(response, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": response})

        # ── Web search → AI (with world-class coding) ────────────────────────
        else:
            if needs_search(prompt):
                with st.spinner("🔍 Searching the web…"):
                    search_results = web_search(prompt)
                    searched = True

            for attempt in range(3):
                try:
                    spinner_msg = "✨ Thinking…" if attempt == 0 else "Rate limited — retrying in 60s ⏳"
                    with st.spinner(spinner_msg):
                        if attempt > 0:
                            time.sleep(60)
                        completion = client.chat.completions.create(
                            messages=build_messages(prompt, search_results),
                            model=MODEL,
                            max_tokens=2048,   # more tokens for complete code
                            temperature=0.2,   # lower = more precise code
                        )
                    response = completion.choices[0].message.content

                    if searched:
                        st.markdown('<div class="search-badge">🔍 Searched the web</div>', unsafe_allow_html=True)

                    # Extract all code blocks
                    code_blocks = extract_all_code_blocks(response)
                    code, lang = extract_code_and_language(response)

                    # Check if it's a web app (has html/css/js)
                    langs_found = [l for l, _ in code_blocks]
                    is_web_app  = any(l in ("html", "css", "javascript", "js") for l in langs_found)

                    if code:
                        if is_web_app:
                            st.markdown('<div class="preview-badge">🖥️ Live app preview · Scroll down to see it running</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="code-badge">💻 Code ready · Click ▶ Run to execute</div>', unsafe_allow_html=True)

                    st.markdown(response)

                    # ── Live HTML preview for web apps ────────────────────────
                    if is_web_app:
                        html_src = build_html_app(code_blocks)
                        if html_src:
                            st.markdown("---")
                            st.markdown("### 🖥️ Live Preview")
                            st.components.v1.html(html_src, height=520, scrolling=True)

                            # Download button
                            import base64
                            b64 = base64.b64encode(html_src.encode()).decode()
                            dl_link = f'<a href="data:text/html;base64,{b64}" download="nova_app.html" style="display:inline-flex;align-items:center;gap:6px;background:rgba(0,229,255,.1);border:1px solid rgba(0,229,255,.3);color:#00e5ff;padding:6px 16px;border-radius:8px;text-decoration:none;font-size:13px;font-family:DM Sans,sans-serif;margin-top:.5rem">⬇️ Download App</a>'
                            st.markdown(dl_link, unsafe_allow_html=True)

                    # ── Run button for non-web code ───────────────────────────
                    elif code and lang and lang not in ("html", "css"):
                        run_key = f"run_{len(st.session_state.messages)}"
                        if st.button(f"▶ Run {lang.title()} Code", key=run_key):
                            with st.spinner(f"⚙️ Running {lang} code…"):
                                output = run_code(code, lang)
                            if "❌" in output:
                                st.markdown(f'<div class="error-box">{output}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="output-box">✅ Output:\n\n{output}</div>', unsafe_allow_html=True)

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
