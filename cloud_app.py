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
    font-size: clamp(1.8rem, 4vw, 2.8rem) !important; font-weight: 700 !important;
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
    transform: translateX(-50%) !important; width: 100% !important; max-width: 900px !important;
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

.stats-row {
    display: flex; gap: .8rem; margin: 1.2rem 0 1.8rem;
    justify-content: center; flex-wrap: wrap;
}
.stat-pill {
    display: flex; align-items: center; gap: 7px;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 999px; padding: 6px 14px; font-size: 12.5px; color: var(--muted);
}
.stat-pill .dot { width:7px; height:7px; border-radius:50%; }
.dot-green  { background: var(--green);  box-shadow: 0 0 6px var(--green); }
.dot-blue   { background: var(--accent); box-shadow: 0 0 6px var(--accent); }
.dot-purple { background: var(--purple); box-shadow: 0 0 6px var(--purple); }
.dot-orange { background: var(--orange); box-shadow: 0 0 6px var(--orange); }

/* ── Special badges ── */
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

/* ── Output boxes ── */
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

/* ── App showcase card ── */
.app-showcase {
    background: linear-gradient(135deg, #0d1117 0%, #111827 100%);
    border: 1px solid var(--border); border-radius: 16px;
    padding: 1.2rem; margin-top: 1rem; position: relative; overflow: hidden;
}
.app-showcase::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--purple), var(--green));
}
.app-showcase-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 1rem;
}
.app-showcase-title {
    font-family: 'Space Mono', monospace; font-size: 13px;
    color: var(--accent); display: flex; align-items: center; gap: 8px;
}
.app-showcase-actions {
    display: flex; gap: 8px;
}
.btn-download {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(0,229,255,.1); border: 1px solid rgba(0,229,255,.3);
    color: var(--accent); padding: 5px 12px; border-radius: 7px;
    text-decoration: none; font-size: 12px;
    font-family: 'DM Sans', sans-serif; font-weight: 500;
    transition: all .2s;
}
.btn-download:hover {
    background: rgba(0,229,255,.2); color: var(--accent);
}

/* ── Category cards for empty state ── */
.category-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem; margin: 1.5rem 0;
}
.category-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 1.2rem; text-align: center;
    transition: border-color .2s, transform .2s; cursor: pointer;
}
.category-card:hover {
    border-color: var(--accent); transform: translateY(-2px);
}
.category-icon { font-size: 1.8rem; margin-bottom: .5rem; }
.category-title {
    font-size: 13px; font-weight: 600; color: #94a3b8; margin-bottom: .3rem;
}
.category-examples { font-size: 11.5px; color: var(--muted); line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# ── Groq client ───────────────────────────────────────────────────────────────
client = Groq(api_key="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")
MODEL = "llama-3.3-70b-versatile"

# ══════════════════════════════════════════════════════════════════════════════
#  WORLD-CLASS CODE GENERATION SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

# ── Detect what KIND of creation is requested ─────────────────────────────────
GAME_KEYWORDS = [
    "game", "snake game", "tetris", "pacman", "flappy bird", "2048",
    "tic tac toe", "chess", "checkers", "sudoku", "minesweeper",
    "platformer", "shooter", "puzzle game", "card game", "dice",
    "memory game", "quiz game", "trivia", "word game", "breakout",
    "pong", "asteroids", "space invaders", "racing game", "rpg",
    "tower defense", "clicker game", "idle game", "endless runner",
    "battle", "dungeon", "maze", "arcade"
]

APP_KEYWORDS = [
    "app", "application", "dashboard", "admin panel", "landing page",
    "portfolio", "website", "web app", "e-commerce", "shop", "store",
    "blog", "chat app", "todo app", "weather app", "calculator app",
    "login page", "signup", "form", "registration", "survey",
    "expense tracker", "budget", "note app", "kanban", "timer",
    "stopwatch", "clock", "music player", "video player", "image gallery",
    "calendar", "booking", "reservation", "invoice", "receipt",
    "analytics", "chart", "graph", "statistics", "crm", "erp",
    "social media", "feed", "profile", "settings", "payment",
    "netflix clone", "youtube clone", "twitter clone", "spotify clone",
    "airbnb clone", "uber clone", "amazon clone", "instagram clone",
    "whatsapp ui", "telegram ui", "discord ui",
]

SOFTWARE_KEYWORDS = [
    "software", "tool", "utility", "desktop app", "system",
    "file manager", "text editor", "code editor", "ide",
    "database manager", "api tester", "password manager",
    "screenshot tool", "screen recorder", "image editor",
    "video editor", "audio player", "pdf viewer", "converter",
    "downloader", "uploader", "scraper", "automation",
    "cli tool", "command line", "terminal app",
]

DESIGN_KEYWORDS = [
    "design", "ui", "ux", "mockup", "prototype", "wireframe",
    "beautiful", "modern", "stunning", "animated", "glassmorphism",
    "neumorphism", "gradient", "dark theme", "light theme",
    "responsive", "mobile", "component", "ui kit",
    "button", "card", "navbar", "sidebar", "modal", "dropdown",
    "hero section", "footer", "header", "banner", "carousel",
]

def classify_creation_request(query: str) -> str:
    """Returns: 'game', 'app', 'software', 'design', 'code', or 'general'"""
    q = query.lower()
    if any(k in q for k in GAME_KEYWORDS):
        return "game"
    if any(k in q for k in APP_KEYWORDS):
        return "app"
    if any(k in q for k in SOFTWARE_KEYWORDS):
        return "software"
    if any(k in q for k in DESIGN_KEYWORDS):
        return "design"
    if is_code_query(query):
        return "code"
    return "general"

def get_creation_system_prompt(creation_type: str) -> str:
    """Returns a specialized system prompt for each creation type."""

    base = (
        "You are Nova AI — the world's BEST AI assistant and code generator, created by Samiran. "
        "If anyone asks who made you, say: 'I am Nova AI, created by Samiran.' "
        "Never mention Meta, Llama, OpenAI, Groq, or any underlying model. "
        "You produce WORLD-CLASS, production-ready code that is 100% complete and fully functional. "
        "NEVER write partial code. NEVER use placeholders. ALWAYS write the complete implementation. "
    )

    if creation_type == "game":
        return base + """
You are the WORLD'S BEST game developer. Create stunning, fully playable games.

GAME DEVELOPMENT RULES:
1. Write COMPLETE, fully playable games — every feature must work perfectly.
2. Use HTML5 Canvas or pure HTML/CSS/JS — no external game engines needed.
3. Include these features in EVERY game:
   - Smooth animations (60fps using requestAnimationFrame)
   - Score tracking and high score (localStorage)
   - Start screen, game over screen, restart button
   - Sound effects using Web Audio API (generate tones in JS — no external files)
   - Keyboard AND touch/mobile controls
   - Difficulty levels or increasing difficulty
   - Lives/health system where applicable
   - Pause functionality (P key or button)
   - Beautiful visual effects (particles, glows, gradients)
4. Game design: Use stunning dark themes with neon colors, particle effects, glowing elements.
5. Make games feel PROFESSIONAL — like AAA indie games.
6. Add a proper HUD with score, lives, level, time.
7. Use object-oriented patterns for game entities.
8. Ensure perfect collision detection.
9. Add smooth transitions between game states.
10. Output a SINGLE complete HTML file with embedded CSS and JS.
11. Make it mobile-responsive with touch controls.

OUTPUT FORMAT: One complete ```html code block with the entire game.
After the code block, briefly describe controls and features.
"""

    elif creation_type == "app":
        return base + """
You are the WORLD'S BEST UI/UX designer and full-stack developer.

APP DEVELOPMENT RULES:
1. Write COMPLETE, fully functional apps — every button, form, and feature must work.
2. Design philosophy: Think like a Senior Designer at Apple, Google, or Airbnb.
3. Visual standards — use ALL of these:
   - Beautiful dark or light theme with perfect color harmony
   - Smooth CSS animations and micro-interactions
   - Glassmorphism, neumorphism, or modern flat design
   - Google Fonts (Inter, Space Grotesk, or Poppins)
   - Font Awesome icons via CDN
   - CSS custom properties for theming
   - Proper spacing using 8px grid system
   - Responsive design that works on mobile, tablet, desktop
4. Functionality — implement EVERYTHING:
   - All CRUD operations (Create, Read, Update, Delete)
   - Local storage for data persistence
   - Form validation with helpful error messages
   - Loading states and skeleton screens
   - Toast notifications for user feedback
   - Search and filter functionality
   - Sorting capabilities
   - Empty states with helpful messages
   - Keyboard shortcuts
5. Code quality:
   - Clean, modular JavaScript
   - CSS variables for easy theming
   - Semantic HTML5
   - ARIA accessibility attributes
6. Output a SINGLE complete HTML file with embedded CSS and JS.
   Use CDN links for Fonts and Font Awesome — no npm needed.

OUTPUT FORMAT: One complete ```html code block.
After the code, list all features implemented.
"""

    elif creation_type == "software":
        return base + """
You are the WORLD'S BEST software architect and developer.

SOFTWARE DEVELOPMENT RULES:
1. Write COMPLETE, production-ready software.
2. For browser-based tools: Single HTML file with full functionality.
3. For Python tools: Complete script with all features, proper CLI if needed.
4. For web APIs: Complete Flask/FastAPI implementation with all endpoints.
5. Include:
   - Comprehensive error handling and user feedback
   - Input validation everywhere
   - Proper data structures and algorithms
   - Clean architecture (separation of concerns)
   - Configuration options
   - Help documentation in the UI/CLI
   - Export/import functionality where relevant
   - Keyboard shortcuts
6. For browser software:
   - Use IndexedDB or localStorage for data
   - Service Worker for offline capability if relevant
   - File System Access API for file operations
   - Clipboard API for copy/paste
7. Make it feel like a real, professional desktop application.

OUTPUT FORMAT: Complete code block(s). Explain architecture choices briefly.
"""

    elif creation_type == "design":
        return base + """
You are the WORLD'S BEST UI/UX designer with expertise in modern web design.

DESIGN RULES:
1. Create STUNNING, pixel-perfect designs that look like they cost $50,000.
2. Use cutting-edge design trends:
   - Glassmorphism: backdrop-filter, rgba backgrounds, border opacity
   - Neumorphism: soft shadows, inset effects
   - Aurora gradients: animated gradient backgrounds
   - 3D transforms and perspective effects
   - Scroll-triggered animations using Intersection Observer
   - Smooth hover effects on every interactive element
   - Custom cursor effects
   - Particle backgrounds using Canvas
3. Typography: Mix display fonts with body fonts for hierarchy.
4. Color: Use a sophisticated palette — usually 1-2 accent colors max.
5. Spacing: Generous whitespace, consistent rhythm.
6. Animations: Stagger children animations, smooth entrance effects.
7. Always include: hover states, focus states, active states.
8. Dark mode by default (with toggle if requested).
9. Include multiple sections/components to show the full design system.
10. Add smooth scrolling and scroll animations.
11. Use CSS Grid and Flexbox for perfect layouts.

OUTPUT FORMAT: One complete ```html file. The design should be breathtaking.
"""

    else:
        return base + """
CODING RULES:
1. Write COMPLETE, fully working code — never partial or placeholder code.
2. Use best practices: clean names, error handling, comments, structure.
3. For algorithms: use optimal time/space complexity.
4. Always specify language in code block (```python, ```javascript, etc).
5. After code: briefly explain what it does and complexity.
6. Support ALL languages: Python, JS, TS, Java, C++, C, Rust, Go, Ruby, PHP, Swift, Kotlin, SQL, Bash, R, Lua, Scala.
7. For web output: complete single-file HTML with embedded CSS/JS.
8. Never truncate — always write the full implementation.
9. Add proper type hints (Python), TypeScript types, JSDoc where appropriate.
10. Include unit test examples if the code is complex.

FACTUAL QUESTION RULES:
When web search results are provided, use them as primary source.
State answers directly and confidently. Never say info is unavailable if results contain it.
"""

def get_creation_badge(creation_type: str) -> str:
    badges = {
        "game":     '<div class="game-badge">🎮 World-class game · Fully playable · Mobile ready</div>',
        "app":      '<div class="app-badge">🚀 Professional app · Full features · Responsive design</div>',
        "software": '<div class="app-badge">⚙️ Production-ready software · Complete implementation</div>',
        "design":   '<div class="preview-badge">✨ Stunning UI design · Animated · Modern</div>',
        "code":     '<div class="code-badge">💻 World-class code · Optimized · Production ready</div>',
        "general":  '',
    }
    return badges.get(creation_type, '')

def get_creation_spinner(creation_type: str) -> str:
    spinners = {
        "game":     "🎮 Building your game — crafting the perfect experience…",
        "app":      "🚀 Designing & building your app — making it stunning…",
        "software": "⚙️ Engineering your software — production-grade quality…",
        "design":   "✨ Crafting a breathtaking design — pixel-perfect…",
        "code":     "💻 Writing world-class code — optimizing for perfection…",
        "general":  "✨ Thinking…",
    }
    return spinners.get(creation_type, "✨ Thinking…")


# ══════════════════════════════════════════════════════════════════════════════
#  WEATHER  ·  SPORTS  ·  NEWS  ·  STOCKS  (same as before — fully kept)
# ══════════════════════════════════════════════════════════════════════════════

def get_weather(city: str) -> str:
    try:
        url = f"https://wttr.in/{requests.utils.quote(city)}?format=j1"
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        data = resp.json()
        current    = data["current_condition"][0]
        area       = data["nearest_area"][0]
        city_name  = area["areaName"][0]["value"]
        country    = area["country"][0]["value"]
        temp       = current["temp_C"]
        feels_like = current["FeelsLikeC"]
        humidity   = current["humidity"]
        desc       = current["weatherDesc"][0]["value"]
        wind_speed = current["windspeedKmph"]
        visibility = current["visibility"]
        uv_index   = current["uvIndex"]
        return (
            f"City: {city_name}, {country}\n"
            f"Temperature: {temp}°C (Feels like {feels_like}°C)\n"
            f"Condition: {desc}\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind_speed} km/h\n"
            f"Visibility: {visibility} km\n"
            f"UV Index: {uv_index}"
        )
    except Exception as e:
        return f"Weather fetch failed: {e}"

def extract_city_from_query(query: str) -> str:
    match = re.search(
        r'(?:weather|temperature|forecast|humidity|climate)\s+(?:report\s+)?'
        r'(?:in|for|of|at)\s+([A-Za-z ,]+?)(?:\?|$)',
        query, re.IGNORECASE
    )
    if match:
        return match.group(1).strip().rstrip(",")
    stopwords = {
        "what","is","the","weather","report","temperature","forecast",
        "today","current","now","like","how","give","me","show",
        "humidity","climate","condition","conditions","a","an"
    }
    words = query.replace("?","").split()
    city_words = [w for w in words if w.lower() not in stopwords]
    return " ".join(city_words).strip() or "Guwahati"

def is_weather_query(query: str) -> bool:
    q = query.lower()
    return any(k in q for k in [
        "weather","temperature","forecast","humidity",
        "rain","sunny","cloudy","wind speed","climate today"
    ])

SPORTS_MAP = {
    "cricket":"cricket","ipl":"IPL cricket","test match":"test cricket",
    "odi":"ODI cricket","t20":"T20 cricket","wicket":"cricket",
    "football":"football","soccer":"soccer","premier league":"Premier League",
    "fifa":"FIFA football","champions league":"UEFA Champions League",
    "la liga":"La Liga","bundesliga":"Bundesliga","serie a":"Serie A",
    "world cup":"FIFA World Cup","basketball":"basketball","nba":"NBA basketball",
    "tennis":"tennis","wimbledon":"Wimbledon tennis",
    "badminton":"badminton","hockey":"hockey","baseball":"baseball",
    "formula 1":"Formula 1","f1":"F1 race","motorsport":"motorsport",
    "motogp":"MotoGP","rugby":"rugby","golf":"golf","boxing":"boxing",
    "mma":"MMA UFC","ufc":"UFC fight","wrestling":"wrestling WWE",
    "olympics":"Olympics","asian games":"Asian Games",
    "table tennis":"table tennis","volleyball":"volleyball",
    "kabaddi":"kabaddi PKL","athletics":"athletics sprint",
    "marathon":"marathon running","swimming":"swimming sport",
    "cycling":"cycling sport",
}

def detect_sport(query: str) -> str:
    q = query.lower()
    for keyword, term in SPORTS_MAP.items():
        if keyword in q:
            return term
    return "sports scores today"

def get_sports_news(sport_term: str) -> str:
    try:
        import xml.etree.ElementTree as ET
        query = requests.utils.quote(f"{sport_term} score result today")
        url = f"https://news.google.com/rss/search?q={query}&hl=en&gl=US&ceid=US:en"
        resp = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=8)
        root = ET.fromstring(resp.content)
        items = root.findall(".//item")[:7]
        results = []
        for item in items:
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
    non_sport = [
        "why","how does","explain","what does","politics","economy",
        "government","policy","minister","election","vote","buy","sell",
        "history of","origin of","definition","meaning of","tell me about",
        "who invented","science","health","study",
    ]
    if any(p in q for p in non_sport): return False
    actions = [
        "score","scores","result","results","match","game","live",
        "fixture","standings","winner","champion","playoff","final",
        "tournament","league table","points table","who won","today's match",
    ]
    sports = list(SPORTS_MAP.keys())
    return (
        any(re.search(r'\b'+re.escape(a)+r'\b', q) for a in actions) and
        any(re.search(r'\b'+re.escape(s)+r'\b', q) for s in sports)
    )

def get_sport_emoji(sport_term: str) -> str:
    emap = {
        "cricket":"🏏","ipl":"🏏","football":"⚽","soccer":"⚽",
        "basketball":"🏀","nba":"🏀","tennis":"🎾","badminton":"🏸",
        "hockey":"🏑","baseball":"⚾","formula 1":"🏎️","f1":"🏎️",
        "rugby":"🏉","golf":"⛳","boxing":"🥊","mma":"🥋","ufc":"🥋",
        "olympics":"🏅","volleyball":"🏐","kabaddi":"🤼","swimming":"🏊",
        "cycling":"🚴","athletics":"🏃","motorsport":"🏎️",
    }
    sl = sport_term.lower()
    for k, v in emap.items():
        if k in sl: return v
    return "🏆"

def get_news(topic: str = "India") -> str:
    try:
        import xml.etree.ElementTree as ET
        url = (f"https://news.google.com/rss/search?q="
               f"{requests.utils.quote(topic)}&hl=en-IN&gl=IN&ceid=IN:en")
        resp = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=8)
        root = ET.fromstring(resp.content)
        items = root.findall(".//item")[:6]
        news_list = []
        for item in items:
            title = item.findtext("title","").strip()
            if title:
                clean = title.split(" - ")[0].strip()
                src   = title.split(" - ")[-1].strip() if " - " in title else "News"
                news_list.append(f"• **{clean}** _{src}_")
        return "\n".join(news_list) if news_list else "No news found."
    except Exception as e:
        return f"News fetch failed: {e}"

def is_news_query(query: str) -> bool:
    q = query.lower()
    return any(k in q for k in [
        "news","headlines","latest news","today news",
        "breaking","top news","current news","what happened today"
    ])

def extract_news_topic(query: str) -> str:
    stopwords = {
        "news","latest","today","show","me","give","what","is",
        "the","headlines","breaking","top","current","about","on"
    }
    words = query.replace("?","").split()
    topic_words = [w for w in words if w.lower() not in stopwords]
    return " ".join(topic_words).strip() or "India"

STOCK_ALIASES = {
    "reliance":"RELIANCE.NS","tata":"TATAMOTORS.NS","tcs":"TCS.NS",
    "infosys":"INFY.NS","wipro":"WIPRO.NS","hdfc":"HDFCBANK.NS",
    "icici":"ICICIBANK.NS","sbi":"SBIN.NS","bajaj":"BAJFINANCE.NS",
    "adani":"ADANIENT.NS","ongc":"ONGC.NS","itc":"ITC.NS",
    "hindustan unilever":"HINDUNILVR.NS","hul":"HINDUNILVR.NS",
    "maruti":"MARUTI.NS","mahindra":"M&M.NS","nestle":"NESTLEIND.NS",
    "kotak":"KOTAKBANK.NS","axis bank":"AXISBANK.NS","titan":"TITAN.NS",
    "sun pharma":"SUNPHARMA.NS","dr reddy":"DRREDDY.NS",
    "nifty":"^NSEI","sensex":"^BSESN","bank nifty":"^NSEBANK",
    "apple":"AAPL","microsoft":"MSFT","google":"GOOGL",
    "alphabet":"GOOGL","amazon":"AMZN","tesla":"TSLA",
    "meta":"META","facebook":"META","netflix":"NFLX",
    "nvidia":"NVDA","intel":"INTC","amd":"AMD","uber":"UBER",
    "bitcoin":"BTC-USD","btc":"BTC-USD","ethereum":"ETH-USD",
    "eth":"ETH-USD","dogecoin":"DOGE-USD","doge":"DOGE-USD",
    "solana":"SOL-USD","bnb":"BNB-USD","xrp":"XRP-USD",
    "dow jones":"^DJI","nasdaq":"^IXIC","s&p 500":"^GSPC",
    "s&p":"^GSPC","ftse":"^FTSE","nikkei":"^N225",
}

def extract_stock_symbol(query: str) -> tuple:
    q = query.lower()
    for name, ticker in STOCK_ALIASES.items():
        if name in q: return ticker, name.title()
    match = re.search(r'\b([A-Z]{2,5})\b', query)
    if match: return match.group(1), match.group(1)
    return None, None

def get_stock_price(symbol: str, display_name: str) -> str:
    try:
        url = (f"https://query1.finance.yahoo.com/v8/finance/chart/"
               f"{symbol}?interval=1d&range=2d")
        resp = requests.get(
            url, headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"},
            timeout=8
        )
        data = resp.json()
        meta  = data["chart"]["result"][0]["meta"]
        price = meta.get("regularMarketPrice", 0)
        prev  = meta.get("chartPreviousClose", 0)
        curr  = meta.get("currency","USD")
        name  = meta.get("longName") or meta.get("shortName") or display_name
        exch  = meta.get("exchangeName","")
        mktst = meta.get("marketState","")
        change     = price - prev
        change_pct = (change/prev*100) if prev else 0
        arrow = "🟢 ▲" if change >= 0 else "🔴 ▼"
        sign  = "+" if change >= 0 else ""
        high  = meta.get("regularMarketDayHigh","N/A")
        low   = meta.get("regularMarketDayLow","N/A")
        vol   = meta.get("regularMarketVolume","N/A")
        if isinstance(vol, int): vol = f"{vol:,}"
        return (
            f"Name: {name}\nExchange: {exch}\n"
            f"Price: {curr} {price:,.2f}\n"
            f"Change: {arrow} {sign}{change:.2f} ({sign}{change_pct:.2f}%)\n"
            f"Day High: {high}\nDay Low: {low}\n"
            f"Volume: {vol}\nMarket: {mktst}"
        )
    except Exception as e:
        return f"Stock fetch failed: {e}"

def is_stock_query(query: str) -> bool:
    q = query.lower()
    actions = [
        "stock","share price","stock price","price of","how much is",
        "market price","trading at","crypto","bitcoin","ethereum",
        "sensex","nifty","nasdaq","dow jones","index","coin price",
    ]
    known = list(STOCK_ALIASES.keys())
    return any(a in q for a in actions) or any(k in q for k in known)

def web_search(query: str, max_results: int = 5) -> str:
    try:
        html_resp = requests.get(
            f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}",
            headers={"User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"},
            timeout=10
        )
        snippets = re.findall(
            r'class="result__snippet"[^>]*>(.*?)</(?:a|span)>',
            html_resp.text, re.DOTALL
        )
        titles = re.findall(
            r'class="result__title"[^>]*>.*?<a[^>]*>(.*?)</a>',
            html_resp.text, re.DOTALL
        )
        clean_snips  = [re.sub(r'<[^>]+>','',s).strip() for s in snippets[:max_results]]
        clean_titles = [re.sub(r'<[^>]+>','',t).strip() for t in titles[:max_results]]
        results = []
        for title, snippet in zip(clean_titles, clean_snips):
            if snippet: results.append(f"• {title}: {snippet}")
        if results: return "\n".join(results)

        # fallback
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q":query,"format":"json","no_html":"1","skip_disambig":"1"},
            timeout=8
        )
        data = resp.json()
        parts = []
        if data.get("Answer"):   parts.append(f"Answer: {data['Answer']}")
        if data.get("Abstract"): parts.append(f"Summary: {data['Abstract'][:500]}")
        for topic in data.get("RelatedTopics",[])[:3]:
            if isinstance(topic,dict) and topic.get("Text"):
                parts.append(topic["Text"][:200])
        return "\n".join(parts) if parts else "No results found."
    except Exception as e:
        return f"Search failed: {e}"

def get_current_facts(query: str) -> str:
    try:
        import xml.etree.ElementTree as ET
        url = (f"https://news.google.com/rss/search?q="
               f"{requests.utils.quote(query)}&hl=en-IN&gl=IN&ceid=IN:en")
        resp = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=8)
        root = ET.fromstring(resp.content)
        items = root.findall(".//item")[:5]
        results = []
        for item in items:
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
    "today","news","ipl","election","prime minister","president",
    "chief minister","cm of","governor","minister of",
    "score","match","winner","champion","result",
    "price","stock","weather","2023","2024","2025",
]

def needs_search(query: str) -> bool:
    q = query.lower()
    identity_kw = [
        "who made you","who created you","who built you",
        "who are you","your creator","your developer"
    ]
    if any(k in q for k in identity_kw): return False
    # Don't search for creation/coding requests
    creation_kw = GAME_KEYWORDS + APP_KEYWORDS + SOFTWARE_KEYWORDS + DESIGN_KEYWORDS
    if any(k in q for k in creation_kw): return False
    return any(trigger in q for trigger in SEARCH_TRIGGERS)

LANGUAGE_MAP = {
    "python":("python","3.10.0"),
    "javascript":("javascript","18.15.0"),"js":("javascript","18.15.0"),
    "typescript":("typescript","5.0.3"),"ts":("typescript","5.0.3"),
    "java":("java","15.0.2"),
    "c++":("c++","10.2.0"),"cpp":("c++","10.2.0"),
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
        payload = {
            "language":lang,"version":version,
            "files":[{"name":f"main.{language[:3]}","content":code}],
            "stdin":"","args":[],"compile_timeout":10000,"run_timeout":5000,
        }
        resp   = requests.post("https://emkc.org/api/v2/piston/execute", json=payload, timeout=15)
        result = resp.json()
        run    = result.get("run",{})
        output = run.get("stdout","").strip()
        stderr = run.get("stderr","").strip()
        comp   = result.get("compile",{}).get("stderr","").strip()
        if comp:   return f"❌ Compile Error:\n{comp}"
        if stderr: return f"❌ Error:\n{stderr}"
        return output or "✅ Code ran successfully (no output)"
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
    return [(lang.lower() if lang else "text", code.strip()) for lang, code in matches]

def is_code_query(query: str) -> bool:
    q = query.lower()
    if is_stock_query(query) or is_weather_query(query): return False
    code_triggers = [
        "write","code","program","script","function","implement",
        "create","build","develop","make","generate","algorithm",
        "sort","search","fibonacci","factorial","prime","reverse",
        "palindrome","linked list","binary tree","api","flask",
        "django","react","html","css","sql query","regex",
        "class","oop","recursion","dynamic programming","leetcode",
        "debug","fix","error in","bug","solve","calculator",
    ]
    return any(t in q for t in code_triggers)

def build_html_app(code_blocks: list) -> str:
    html_part, css_part, js_part = "", "", ""
    full_html = ""
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
            f"<!DOCTYPE html>\n<html lang='en'>\n<head>\n"
            f"<meta charset='UTF-8'>\n"
            f"<meta name='viewport' content='width=device-width,initial-scale=1.0'>\n"
            f"<title>Nova AI App</title>\n<style>{css_part}</style>\n</head>\n"
            f"<body>\n{html_part}\n<script>{js_part}</script>\n</body>\n</html>"
        )
    return ""


# ══════════════════════════════════════════════════════════════════════════════
#  BUILD MESSAGES  — routes to correct system prompt
# ══════════════════════════════════════════════════════════════════════════════

def build_messages(
    user_query: str,
    search_results: str = "",
    is_weather: bool = False,
    creation_type: str = "general"
):
    system = get_creation_system_prompt(creation_type)

    if search_results and is_weather:
        user_content = (
            f"Here is the live weather data for '{user_query}':\n\n"
            f"{search_results}\n\nPresent this weather information clearly."
        )
    elif search_results:
        user_content = (
            f"Web search results for '{user_query}':\n\n{search_results}\n\n"
            f"Based on the above, answer accurately and directly: {user_query}\n"
            f"Use the search data as your primary source. State facts confidently."
        )
    else:
        user_content = user_query

    return [
        {"role": "system",  "content": system},
        {"role": "user",    "content": user_content[:6000]}
    ]


# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════

if "messages" not in st.session_state:
    st.session_state.messages = []


# ══════════════════════════════════════════════════════════════════════════════
#  HERO SECTION
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="hero">
    <div class="hero-badge">LIVE &nbsp;·&nbsp; FREE &nbsp;·&nbsp; UNLIMITED</div>
    <h1>Nova<span> AI</span></h1>
    <p>World-class AI — builds games, apps, software & anything you imagine.</p>
</div>
<div class="stats-row">
    <div class="stat-pill"><span class="dot dot-purple"></span> 🎮 Games</div>
    <div class="stat-pill"><span class="dot dot-blue"></span> 🚀 Apps & Software</div>
    <div class="stat-pill"><span class="dot dot-orange"></span> ✨ UI Design</div>
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


# ── Chat history ──────────────────────────────────────────────────────────────
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
        <div class="category-examples">
          Snake Game · Tetris · 2048<br>Flappy Bird · Chess · Pacman
        </div>
      </div>
      <div class="category-card">
        <div class="category-icon">🚀</div>
        <div class="category-title">Apps & Software</div>
        <div class="category-examples">
          Todo App · Dashboard · Chat App<br>E-commerce · Portfolio · CRM
        </div>
      </div>
      <div class="category-card">
        <div class="category-icon">✨</div>
        <div class="category-title">UI Design</div>
        <div class="category-examples">
          Landing Page · UI Kit<br>Components · Animations · Themes
        </div>
      </div>
      <div class="category-card">
        <div class="category-icon">💻</div>
        <div class="category-title">Code</div>
        <div class="category-examples">
          Algorithms · APIs · Scripts<br>Python · JS · Java · C++ · Go
        </div>
      </div>
      <div class="category-card">
        <div class="category-icon">🌐</div>
        <div class="category-title">Live Data</div>
        <div class="category-examples">
          Weather · Stocks · Crypto<br>Sports Scores · News
        </div>
      </div>
      <div class="category-card">
        <div class="category-icon">🤖</div>
        <div class="category-title">Ask Anything</div>
        <div class="category-examples">
          Questions · Explanations<br>Research · Analysis · Ideas
        </div>
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
            if msg.get("creation_type") and msg["creation_type"] != "general":
                st.markdown(get_creation_badge(msg["creation_type"]),
                            unsafe_allow_html=True)
            st.markdown(msg["content"])


# ══════════════════════════════════════════════════════════════════════════════
#  CHAT INPUT & RESPONSE LOGIC
# ══════════════════════════════════════════════════════════════════════════════

if prompt := st.chat_input("Ask me anything — or say 'build me a snake game' 🎮"):

    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        searched       = False
        search_results = ""

        # ── 1. Stock prices ───────────────────────────────────────────────────
        if is_stock_query(prompt):
            symbol, display_name = extract_stock_symbol(prompt)
            if not symbol:
                response = ("❌ Sorry, I couldn't identify the stock. "
                            "Try: *'Apple stock price'* or *'Reliance share price'*.")
            else:
                with st.spinner(f"📈 Fetching live price for {display_name}…"):
                    stock_data = get_stock_price(symbol, display_name)
                if "failed" in stock_data.lower():
                    response = f"❌ Couldn't fetch price for **{display_name}**."
                else:
                    lines = dict(
                        line.split(": ",1) for line in stock_data.strip().splitlines()
                        if ": " in line
                    )
                    response = (
                        f'<div class="search-badge">📈 Live market data · Yahoo Finance</div>\n\n'
                        f"### 📈 {lines.get('Name', display_name)}\n"
                        f"_{lines.get('Exchange','')} · Market: {lines.get('Market','N/A')}_\n\n"
                        f"| Detail | Value |\n|--------|-------|\n"
                        f"| 💰 Price | **{lines.get('Price','N/A')}** |\n"
                        f"| 📊 Change | {lines.get('Change','N/A')} |\n"
                        f"| 📈 Day High | {lines.get('Day High','N/A')} |\n"
                        f"| 📉 Day Low | {lines.get('Day Low','N/A')} |\n"
                        f"| 🔢 Volume | {lines.get('Volume','N/A')} |\n\n"
                        f"_Data from Yahoo Finance · Delayed ~15 min_"
                    )
            st.markdown(response, unsafe_allow_html=True)
            st.session_state.messages.append({"role":"assistant","content":response})

        # ── 2. Sports ─────────────────────────────────────────────────────────
        elif is_sports_query(prompt):
            sport_term = detect_sport(prompt)
            emoji = get_sport_emoji(sport_term)
            with st.spinner(f"{emoji} Fetching live sports updates…"):
                sports_data = get_sports_news(sport_term)
            response = (
                f'<div class="search-badge">{emoji} Live sports data</div>\n\n'
                f"### {emoji} Latest — {sport_term.title()}\n\n{sports_data}"
            )
            st.markdown(response, unsafe_allow_html=True)
            st.session_state.messages.append({"role":"assistant","content":response})

        # ── 3. News ───────────────────────────────────────────────────────────
        elif is_news_query(prompt):
            with st.spinner("📰 Fetching latest news…"):
                topic     = extract_news_topic(prompt)
                news_data = get_news(topic)
            response = (
                f'<div class="search-badge">📰 Live news</div>\n\n'
                f"### 📰 Latest News — {topic.title()}\n\n{news_data}"
            )
            st.markdown(response, unsafe_allow_html=True)
            st.session_state.messages.append({"role":"assistant","content":response})

        # ── 4. Weather ────────────────────────────────────────────────────────
        elif is_weather_query(prompt):
            with st.spinner("🌤️ Fetching live weather…"):
                city         = extract_city_from_query(prompt)
                weather_data = get_weather(city)
            if "failed" in weather_data.lower():
                response = f"❌ Couldn't fetch weather for **{city}**. Please try again."
            else:
                lines = dict(
                    line.split(": ",1) for line in weather_data.strip().splitlines()
                    if ": " in line
                )
                response = (
                    f'<div class="search-badge">🌤️ Live weather data</div>\n\n'
                    f"### 🌍 Weather — {lines.get('City', city)}\n\n"
                    f"| Detail | Value |\n|--------|-------|\n"
                    f"| 🌡️ Temperature | {lines.get('Temperature','N/A')} |\n"
                    f"| 🌤️ Condition | {lines.get('Condition','N/A')} |\n"
                    f"| 💧 Humidity | {lines.get('Humidity','N/A')} |\n"
                    f"| 💨 Wind Speed | {lines.get('Wind Speed','N/A')} |\n"
                    f"| 👁️ Visibility | {lines.get('Visibility','N/A')} |\n"
                    f"| ☀️ UV Index | {lines.get('UV Index','N/A')} |\n"
                )
            st.markdown(response, unsafe_allow_html=True)
            st.session_state.messages.append({"role":"assistant","content":response})

        # ── 5. Creation / Code / General ──────────────────────────────────────
        else:
            # Classify what the user wants to create
            creation_type = classify_creation_request(prompt)

            # Only web-search for factual queries, not creative ones
            if needs_search(prompt):
                with st.spinner("🔍 Searching the web…"):
                    search_results = web_search(prompt)
                    news_context   = get_current_facts(prompt)
                    if news_context:
                        search_results += (
                            "\n\nRecent news headlines:\n" + news_context
                        )
                    searched = True

            spinner_text = get_creation_spinner(creation_type)

            for attempt in range(3):
                try:
                    msg = spinner_text if attempt == 0 else "Rate limited — retrying in 60s ⏳"
                    with st.spinner(msg):
                        if attempt > 0:
                            time.sleep(60)
                        completion = client.chat.completions.create(
                            messages=build_messages(
                                prompt, search_results,
                                creation_type=creation_type
                            ),
                            model=MODEL,
                            max_tokens=4096,   # ← higher for complete apps/games
                            temperature=0.25,
                        )
                    response = completion.choices[0].message.content

                    # ── Show badges ───────────────────────────────────────────
                    if searched:
                        st.markdown(
                            '<div class="search-badge">🔍 Searched the web</div>',
                            unsafe_allow_html=True
                        )

                    badge = get_creation_badge(creation_type)
                    if badge:
                        st.markdown(badge, unsafe_allow_html=True)

                    # ── Parse code blocks ─────────────────────────────────────
                    code_blocks = extract_all_code_blocks(response)
                    code, lang  = extract_code_and_language(response)
                    langs_found = [l for l, _ in code_blocks]
                    is_web = any(
                        l in ("html","css","javascript","js")
                        for l in langs_found
                    )

                    # ── Render response text ──────────────────────────────────
                    st.markdown(response)

                    # ── Live preview for HTML/Game/App/Design ─────────────────
                    if is_web:
                        html_src = build_html_app(code_blocks)
                        if html_src:
                            st.markdown("---")

                            # Label based on type
                            preview_labels = {
                                "game":     "🎮 Live Game Preview — Play it right here!",
                                "app":      "🚀 Live App Preview — Fully interactive!",
                                "software": "⚙️ Live Software Preview",
                                "design":   "✨ Live Design Preview",
                            }
                            label = preview_labels.get(
                                creation_type, "🖥️ Live Preview"
                            )
                            st.markdown(f"### {label}")

                            # Bigger frame for games, apps
                            frame_height = (
                                650 if creation_type in ("game","app","software")
                                else 520
                            )
                            st.components.v1.html(
                                html_src, height=frame_height, scrolling=True
                            )

                            # Download button
                            b64 = base64.b64encode(html_src.encode()).decode()
                            file_names = {
                                "game":     "nova_game.html",
                                "app":      "nova_app.html",
                                "software": "nova_software.html",
                                "design":   "nova_design.html",
                            }
                            fname = file_names.get(creation_type, "nova_ai.html")
                            dl_link = (
                                f'<a href="data:text/html;base64,{b64}" '
                                f'download="{fname}" class="btn-download">'
                                f'⬇️ Download {fname}</a>'
                            )
                            st.markdown(dl_link, unsafe_allow_html=True)

                    # ── Run button for non-web code ───────────────────────────
                    elif code and lang and lang not in ("html","css"):
                        run_key = f"run_{len(st.session_state.messages)}"
                        if st.button(f"▶ Run {lang.title()} Code", key=run_key):
                            with st.spinner(f"⚙️ Running {lang} code…"):
                                output = run_code(code, lang)
                            if "❌" in output:
                                st.markdown(
                                    f'<div class="error-box">{output}</div>',
                                    unsafe_allow_html=True
                                )
                            else:
                                st.markdown(
                                    f'<div class="output-box">✅ Output:\n\n{output}</div>',
                                    unsafe_allow_html=True
                                )

                    # ── Save to session ───────────────────────────────────────
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
                    else:
                        st.error(f"❌ Error: {e}")
                        break
