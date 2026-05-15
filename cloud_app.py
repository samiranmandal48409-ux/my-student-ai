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
    q = query.lower()
    sport_keywords = list(SPORTS_MAP.keys()) + [
        "score", "match", "game", "tournament", "league", "championship",
        "result", "winner", "live score", "standings", "fixture", "squad",
        "player", "team", "coach", "transfer", "draft", "playoff", "final",
        "semifinal", "quarterfinal", "grand prix", "bout", "fight night"
    ]
    return any(k in q for k in sport_keywords)


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
    # Never search for identity questions about Nova AI itself
    identity_keywords = ["who made you", "who created you", "who built you", "who are you", "your creator", "your developer"]
    if any(k in q for k in identity_keywords):
        return False
    return any(trigger in q for trigger in SEARCH_TRIGGERS)


# ── Build prompt ──────────────────────────────────────────────────────────────
def build_messages(user_query: str, search_results: str = "", is_weather: bool = False):
    system = (
        "You are Nova AI — a smart, accurate, and friendly AI assistant. "
        "You were created by Samiran. "
        "If anyone asks who made you, who created you, who built you, or who you are, "
        "always say: 'I am Nova AI, created by Samiran.' "
        "Never mention Meta, Llama, OpenAI, Groq, Anthropic, or any underlying model or company. "
        "Answer clearly and directly. Never hallucinate. "
        "If weather data is provided, present it as the current weather report — do NOT say the data is wrong or unrelated. "
        "If web search results are provided, use ONLY those to answer factual questions — do not guess. "
        "Format code with markdown code blocks. Be concise."
    )
    if search_results and is_weather:
        user_content = (
            f"Here is the live weather data fetched for the user's query '{user_query}':\n\n"
            f"{search_results}\n\n"
            f"Present this weather information clearly and helpfully to the user."
        )
    elif search_results:
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
    <div class="stat-pill"><span class="dot dot-green"></span> All world sports</div>
    <div class="stat-pill"><span class="dot dot-blue"></span> Latest news</div>
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
            🌤️ <em>"Weather in Guwahati, Assam"</em><br>
            ⚽ <em>"Latest Premier League scores"</em><br>
            🏏 <em>"IPL match result today"</em><br>
            🎾 <em>"Wimbledon latest update"</em><br>
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

        # ── Sports: universal handler for ALL world sports ────────────────────
        if is_sports_query(prompt):
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

        # ── Web search → AI ───────────────────────────────────────────────────
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
