import streamlit as st
from groq import Groq
import time, requests, re, base64, json, math, os, sqlite3, hashlib
from datetime import datetime, timedelta
import urllib.parse
import xml.etree.ElementTree as ET
from PIL import Image
import io
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import pandas as pd

# ══════════════════════════════════════════════════════════════════════════════
#  PWA MANIFEST & SERVICE WORKER
# ══════════════════════════════════════════════════════════════════════════════
def inject_pwa():
    """Inject PWA manifest and service worker for mobile app installation."""
    st.markdown("""
    <link rel="manifest" href="/app/manifest.json">
    <meta name="theme-color" content="#0a0c10">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    """, unsafe_allow_html=True)

inject_pwa()

st.set_page_config(
    page_title="Nova AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/samiran/nova-ai',
        'Report a bug': 'https://github.com/samiran/nova-ai/issues',
        'About': "# Nova AI v5.0\nBuilt by Samiran with ❤️"
    }
)

# ══════════════════════════════════════════════════════════════════════════════
#  DATABASE SETUP — Persistent Memory
# ══════════════════════════════════════════════════════════════════════════════
DB_FILE = "nova_ai.db"

def init_db():
    """Initialize SQLite database for persistent storage."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )''')
    
    # Conversations table
    c.execute('''CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # Messages table
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        image_b64 TEXT,
        image_mime TEXT,
        image_name TEXT,
        meta TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id)
    )''')
    
    conn.commit()
    conn.close()

init_db()

def get_db():
    """Get database connection."""
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def hash_password(password: str) -> str:
    """Hash password with SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username: str, password: str) -> bool:
    """Create new user."""
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                  (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username: str, password: str) -> dict:
    """Verify user credentials."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, username FROM users WHERE username = ? AND password_hash = ?",
              (username, hash_password(password)))
    row = c.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1]}
    return None

def save_conversation(user_id: int, title: str, messages: list) -> int:
    """Save conversation to database."""
    conn = get_db()
    c = conn.cursor()
    
    # Create or update conversation
    c.execute("INSERT INTO conversations (user_id, title) VALUES (?, ?)",
              (user_id, title[:100]))
    conv_id = c.lastrowid
    
    # Save messages
    for msg in messages:
        c.execute("""INSERT INTO messages 
                    (conversation_id, role, content, image_b64, image_mime, image_name, meta)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                  (conv_id, msg["role"], msg["content"],
                   msg.get("image_b64"), msg.get("image_mime"),
                   msg.get("image_name"), msg.get("meta")))
    
    conn.commit()
    conn.close()
    return conv_id

def load_conversations(user_id: int) -> list:
    """Load user's conversations."""
    conn = get_db()
    c = conn.cursor()
    c.execute("""SELECT id, title, created_at, updated_at 
                 FROM conversations 
                 WHERE user_id = ? 
                 ORDER BY updated_at DESC""", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "created": r[2], "updated": r[3]} for r in rows]

def load_conversation_messages(conv_id: int) -> list:
    """Load messages from a conversation."""
    conn = get_db()
    c = conn.cursor()
    c.execute("""SELECT role, content, image_b64, image_mime, image_name, meta
                 FROM messages WHERE conversation_id = ? ORDER BY created_at""", (conv_id,))
    rows = c.fetchall()
    conn.close()
    messages = []
    for r in rows:
        msg = {"role": r[0], "content": r[1], "meta": r[5]}
        if r[2]: msg["image_b64"] = r[2]
        if r[3]: msg["image_mime"] = r[3]
        if r[4]: msg["image_name"] = r[4]
        messages.append(msg)
    return messages

def delete_conversation(conv_id: int, user_id: int) -> bool:
    """Delete a conversation."""
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
    c.execute("DELETE FROM conversations WHERE id = ? AND user_id = ?", (conv_id, user_id))
    deleted = c.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

# ══════════════════════════════════════════════════════════════════════════════
#  MULTI-LANGUAGE SUPPORT
# ══════════════════════════════════════════════════════════════════════════════
TRANSLATIONS = {
    "en": {
        "name": "English",
        "chat_placeholder": "Ask anything — type here or click 🖼️ Image / 📄 File above…",
        "clear": "🗑️ Clear",
        "upload_image": "🖼️ Image",
        "upload_file": "📄 File",
        "help": "❓ Help",
        "model_settings": "⚙️ Model Settings",
        "temperature": "Temperature",
        "max_length": "Max Length",
        "ai_mode": "🎭 AI Mode",
        "quick_tools": "🛠️ Quick Tools",
        "currency": "💱 Currency",
        "units": "📐 Units",
        "calculator": "🔢 Calculator",
        "qr_code": "📱 QR Code",
        "export": "💾 Export",
        "login": "🔐 Login",
        "logout": "🚪 Logout",
        "username": "Username",
        "password": "Password",
        "signup": "Sign Up",
        "signin": "Sign In",
        "welcome": "Welcome",
        "conversations": "💬 Conversations",
        "new_chat": "➕ New Chat",
        "delete": "🗑️ Delete",
        "load": "📂 Load",
        "pdf_export": "🖨️ PDF Export",
        "chart": "📊 Chart",
        "models": "🤖 Model",
        "language": "🌍 Language",
        "hero_title": "Nova AI",
        "hero_subtitle": "The world's smartest AI — sees images, builds apps, knows everything live.",
        "live": "LIVE",
        "free": "FREE",
        "unlimited": "UNLIMITED",
        "vision": "VISION AI",
        "memory": "Memory",
        "sports": "Live Sports",
        "games": "Games & Apps",
        "files": "Files & URLs",
        "data": "Live Data",
        "what_today": "What would you like to do today?",
        "vision_card": "Vision AI",
        "vision_desc": "Click 📎 below\nUpload any image\nAI reads & analyzes",
        "games_card": "Games",
        "games_desc": "Snake · Tetris\nChess · 2048\nPacman · RPG",
        "apps_card": "Apps",
        "apps_desc": "Dashboard · Todo\nE-commerce\nPortfolio",
        "code_card": "Code",
        "code_desc": "Python · JS · Java\nC++ · Go · Rust\nSQL & more",
        "files_card": "Files",
        "files_desc": "Click 📄 below\nCSV · JSON · Code\nAI analyzes it",
        "live_card": "Live Data",
        "live_desc": "Cricket · Stocks\nWeather · News\nAny URL",
        "example_what": "What is in this image?",
        "example_read": "Read the text",
        "example_solve": "Solve this math",
        "example_explain": "Explain this code",
        "example_analyze": "Analyze this chart",
        "upload_image_title": "👁️ Upload Image for Vision AI",
        "upload_image_supports": "Supports: JPG, PNG, GIF, BMP, WebP, TIFF",
        "upload_file_title": "📁 Upload File for Analysis",
        "upload_file_supports": "Supports: TXT, CSV, JSON, Python, JS, HTML, CSS, Java, C++, Markdown",
        "ready": "Ready",
        "type_question": "Now type your question in the chat below!",
        "converting": "Fetching rates…",
        "fetching_weather": "Fetching weather…",
        "fetching_news": "Fetching news…",
        "fetching_stock": "Fetching",
        "fetching_sports": "Fetching live sports data…",
        "searching": "Searching…",
        "analyzing_image": "👁️ Analyzing image…",
        "reading_url": "🌐 Reading",
        "running_code": "⚙️ Running",
        "building_game": "🎮 Building your game…",
        "building_app": "🚀 Building your app…",
        "engineering": "⚙️ Engineering software…",
        "crafting": "✨ Crafting design…",
        "writing_code": "💻 Writing world-class code…",
        "thinking": "✨ Thinking…",
        "retrying": "Retrying ⏳",
        "error": "❌ Error:",
        "no_results": "No results found.",
        "failed": "failed",
        "live_rate": "💱 Live rate",
        "unit_converted": "📐 Unit converted",
        "calculated": "🔢 Calculated",
        "url_read": "🌐 URL read",
        "live_sports": "🔴 LIVE SPORTS",
        "live_news": "📰 Live news",
        "live_weather": "🌤️ Live weather",
        "web_search": "🔍 Web search",
        "turns_remembered": "turns remembered",
        "download": "⬇️ Download",
        "run": "▶ Run",
        "clear_file": "✕",
        "clear_image": "✕",
        "msg": "msg",
        "msgs": "msgs",
    },
    "hi": {
        "name": "हिंदी",
        "chat_placeholder": "कुछ भी पूछें — यहाँ टाइप करें या 🖼️ इमेज / 📄 फ़ाइल क्लिक करें…",
        "clear": "🗑️ साफ़ करें",
        "upload_image": "🖼️ इमेज",
        "upload_file": "📄 फ़ाइल",
        "help": "❓ मदद",
        "model_settings": "⚙️ मॉडल सेटिंग्स",
        "temperature": "तापमान",
        "max_length": "अधिकतम लंबाई",
        "ai_mode": "🎭 AI मोड",
        "quick_tools": "🛠️ त्वरित टूल्स",
        "currency": "💱 मुद्रा",
        "units": "📐 इकाइयाँ",
        "calculator": "🔢 कैलकुलेटर",
        "qr_code": "📱 QR कोड",
        "export": "💾 निर्यात",
        "login": "🔐 लॉगिन",
        "logout": "🚪 लॉगआउट",
        "username": "उपयोगकर्ता नाम",
        "password": "पासवर्ड",
        "signup": "साइन अप",
        "signin": "साइन इन",
        "welcome": "स्वागत है",
        "conversations": "💬 संवाद",
        "new_chat": "➕ नया चैट",
        "delete": "🗑️ हटाएं",
        "load": "📂 लोड",
        "pdf_export": "🖨️ PDF निर्यात",
        "chart": "📊 चार्ट",
        "models": "🤖 मॉडल",
        "language": "🌍 भाषा",
        "hero_title": "नोवा AI",
        "hero_subtitle": "दुनिया का सबसे स्मार्ट AI — इमेज देखता है, ऐप्स बनाता है, सब कुछ जानता है।",
        "live": "लाइव",
        "free": "मुफ्त",
        "unlimited": "असीमित",
        "vision": "विजन AI",
        "memory": "मेमोरी",
        "sports": "लाइव स्पोर्ट्स",
        "games": "गेम्स और ऐप्स",
        "files": "फ़ाइलें और URL",
        "data": "लाइव डेटा",
        "what_today": "आज आप क्या करना चाहेंगे?",
        "vision_card": "विजन AI",
        "vision_desc": "नीचे 📎 क्लिक करें\nकोई भी इमेज अपलोड करें\nAI पढ़ता और विश्लेषण करता है",
        "games_card": "गेम्स",
        "games_desc": "स्नेक · टेट्रिस\nचेस · 2048\nपैकमैन · RPG",
        "apps_card": "ऐप्स",
        "apps_desc": "डैशबोर्ड · टूडू\nई-कॉमर्स\nपोर्टफोलियो",
        "code_card": "कोड",
        "code_desc": "पायथन · JS · जावा\nC++ · Go · Rust\nSQL और अधिक",
        "files_card": "फ़ाइलें",
        "files_desc": "नीचे 📄 क्लिक करें\nCSV · JSON · कोड\nAI विश्लेषण करता है",
        "live_card": "लाइव डेटा",
        "live_desc": "क्रिकेट · स्टॉक\nमौसम · समाचार\nकोई भी URL",
        "example_what": "इस इमेज में क्या है?",
        "example_read": "टेक्स्ट पढ़ें",
        "example_solve": "यह गणित हल करें",
        "example_explain": "इस कोड की व्याख्या करें",
        "example_analyze": "इस चार्ट का विश्लेषण करें",
        "upload_image_title": "👁️ विजन AI के लिए इमेज अपलोड करें",
        "upload_image_supports": "समर्थित: JPG, PNG, GIF, BMP, WebP, TIFF",
        "upload_file_title": "📁 विश्लेषण के लिए फ़ाइल अपलोड करें",
        "upload_file_supports": "समर्थित: TXT, CSV, JSON, Python, JS, HTML, CSS, Java, C++, Markdown",
        "ready": "तैयार",
        "type_question": "अब नीचे चैट में अपना प्रश्न टाइप करें!",
        "converting": "दरें ला रहे हैं…",
        "fetching_weather": "मौसम ला रहे हैं…",
        "fetching_news": "समाचार ला रहे हैं…",
        "fetching_stock": "ला रहे हैं",
        "fetching_sports": "लाइव स्पोर्ट्स डेटा ला रहे हैं…",
        "searching": "खोज रहे हैं…",
        "analyzing_image": "👁️ इमेज का विश्लेषण कर रहे हैं…",
        "reading_url": "🌐 पढ़ रहे हैं",
        "running_code": "⚙️ चला रहे हैं",
        "building_game": "🎮 आपका गेम बना रहे हैं…",
        "building_app": "🚀 आपका ऐप बना रहे हैं…",
        "engineering": "⚙️ सॉफ्टवेयर इंजीनियरिंग कर रहे हैं…",
        "crafting": "✨ डिज़ाइन तैयार कर रहे हैं…",
        "writing_code": "💻 विश्व-स्तरीय कोड लिख रहे हैं…",
        "thinking": "✨ सोच रहे हैं…",
        "retrying": "पुनः प्रयास ⏳",
        "error": "❌ त्रुटि:",
        "no_results": "कोई परिणाम नहीं मिला।",
        "failed": "विफल",
        "live_rate": "💱 लाइव दर",
        "unit_converted": "📐 इकाई परिवर्तित",
        "calculated": "🔢 गणना की गई",
        "url_read": "🌐 URL पढ़ा गया",
        "live_sports": "🔴 लाइव स्पोर्ट्स",
        "live_news": "📰 लाइव समाचार",
        "live_weather": "🌤️ लाइव मौसम",
        "web_search": "🔍 वेब खोज",
        "turns_remembered": "बातचीत याद रखी गईं",
        "download": "⬇️ डाउनलोड",
        "run": "▶ चलाएं",
        "clear_file": "✕",
        "clear_image": "✕",
        "msg": "संदेश",
        "msgs": "संदेश",
    },
    "bn": {
        "name": "বাংলা",
        "chat_placeholder": "যেকোনো কিছু জিজ্ঞাসা করুন — এখানে টাইপ করুন অথবা 🖼️ ইমেজ / 📄 ফাইল ক্লিক করুন…",
        "clear": "🗑️ মুছুন",
        "upload_image": "🖼️ ইমেজ",
        "upload_file": "📄 ফাইল",
        "help": "❓ সাহায্য",
        "model_settings": "⚙️ মডেল সেটিংস",
        "temperature": "তাপমাত্রা",
        "max_length": "সর্বোচ্চ দৈর্ঘ্য",
        "ai_mode": "🎭 AI মোড",
        "quick_tools": "🛠️ দ্রুত টুলস",
        "currency": "💱 মুদ্রা",
        "units": "📐 একক",
        "calculator": "🔢 ক্যালকুলেটর",
        "qr_code": "📱 QR কোড",
        "export": "💾 এক্সপোর্ট",
        "login": "🔐 লগইন",
        "logout": "🚪 লগআউট",
        "username": "ব্যবহারকারীর নাম",
        "password": "পাসওয়ার্ড",
        "signup": "সাইন আপ",
        "signin": "সাইন ইন",
        "welcome": "স্বাগতম",
        "conversations": "💬 কথোপকথন",
        "new_chat": "➕ নতুন চ্যাট",
        "delete": "🗑️ মুছুন",
        "load": "📂 লোড",
        "pdf_export": "🖨️ PDF এক্সপোর্ট",
        "chart": "📊 চার্ট",
        "models": "🤖 মডেল",
        "language": "🌍 ভাষা",
        "hero_title": "নোভা AI",
        "hero_subtitle": "বিশ্বের সবচেয়ে স্মার্ট AI — ইমেজ দেখে, অ্যাপ তৈরি করে, সবকিছু জানে।",
        "live": "লাইভ",
        "free": "বিনামূল্যে",
        "unlimited": "অসীম",
        "vision": "ভিশন AI",
        "memory": "মেমোরি",
        "sports": "লাইভ স্পোর্টস",
        "games": "গেমস ও অ্যাপস",
        "files": "ফাইল ও URL",
        "data": "লাইভ ডেটা",
        "what_today": "আজ আপনি কী করতে চান?",
        "vision_card": "ভিশন AI",
        "vision_desc": "নীচে 📎 ক্লিক করুন\nযেকোনো ইমেজ আপলোড করুন\nAI পড়ে ও বিশ্লেষণ করে",
        "games_card": "গেমস",
        "games_desc": "স্নেক · টেট্রিস\nদাবা · 2048\nপ্যাকম্যান · RPG",
        "apps_card": "অ্যাপস",
        "apps_desc": "ড্যাশবোর্ড · টুডু\nই-কমার্স\nপোর্টফোলিও",
        "code_card": "কোড",
        "code_desc": "পাইথন · JS · জাভা\nC++ · Go · Rust\nSQL ও আরও",
        "files_card": "ফাইলস",
        "files_desc": "নীচে 📄 ক্লিক করুন\nCSV · JSON · কোড\nAI বিশ্লেষণ করে",
        "live_card": "লাইভ ডেটা",
        "live_desc": "ক্রিকেট · স্টক\nআবহাওয়া · সংবাদ\nযেকোনো URL",
        "example_what": "এই ইমেজে কী আছে?",
        "example_read": "টেক্সট পড়ুন",
        "example_solve": "এই গণিত সমাধান করুন",
        "example_explain": "এই কোড ব্যাখ্যা করুন",
        "example_analyze": "এই চার্ট বিশ্লেষণ করুন",
        "upload_image_title": "👁️ ভিশন AI-এর জন্য ইমেজ আপলোড করুন",
        "upload_image_supports": "সমর্থিত: JPG, PNG, GIF, BMP, WebP, TIFF",
        "upload_file_title": "📁 বিশ্লেষণের জন্য ফাইল আপলোড করুন",
        "upload_file_supports": "সমর্থিত: TXT, CSV, JSON, Python, JS, HTML, CSS, Java, C++, Markdown",
        "ready": "প্রস্তুত",
        "type_question": "এখন নীচে চ্যাটে আপনার প্রশ্ন টাইপ করুন!",
        "converting": "হার আনা হচ্ছে…",
        "fetching_weather": "আবহাওয়া আনা হচ্ছে…",
        "fetching_news": "সংবাদ আনা হচ্ছে…",
        "fetching_stock": "আনা হচ্ছে",
        "fetching_sports": "লাইভ স্পোর্টস ডেটা আনা হচ্ছে…",
        "searching": "অনুসন্ধান করা হচ্ছে…",
        "analyzing_image": "👁️ ইমেজ বিশ্লেষণ করা হচ্ছে…",
        "reading_url": "🌐 পড়া হচ্ছে",
        "running_code": "⚙️ চালানো হচ্ছে",
        "building_game": "🎮 আপনার গেম তৈরি করা হচ্ছে…",
        "building_app": "🚀 আপনার অ্যাপ তৈরি করা হচ্ছে…",
        "engineering": "⚙️ সফটওয়্যার ইঞ্জিনিয়ারিং করা হচ্ছে…",
        "crafting": "✨ ডিজাইন তৈরি করা হচ্ছে…",
        "writing_code": "💻 বিশ্বমানের কোড লেখা হচ্ছে…",
        "thinking": "✨ ভাবা হচ্ছে…",
        "retrying": "পুনরায় চেষ্টা ⏳",
        "error": "❌ ত্রুটি:",
        "no_results": "কোনো ফলাফল পাওয়া যায়নি।",
        "failed": "ব্যর্থ",
        "live_rate": "💱 লাইভ রেট",
        "unit_converted": "📐 একক রূপান্তরিত",
        "calculated": "🔢 গণনা করা হয়েছে",
        "url_read": "🌐 URL পড়া হয়েছে",
        "live_sports": "🔴 লাইভ স্পোর্টস",
        "live_news": "📰 লাইভ সংবাদ",
        "live_weather": "🌤️ লাইভ আবহাওয়া",
        "web_search": "🔍 ওয়েব অনুসন্ধান",
        "turns_remembered": "কথোপকথন মনে রাখা হয়েছে",
        "download": "⬇️ ডাউনলোড",
        "run": "▶ চালান",
        "clear_file": "✕",
        "clear_image": "✕",
        "msg": "বার্তা",
        "msgs": "বার্তা",
    }
}

def t(key: str) -> str:
    """Get translation for current language."""
    lang = st.session_state.get("language", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

# ══════════════════════════════════════════════════════════════════════════════
#  PDF EXPORT
# ══════════════════════════════════════════════════════════════════════════════
class PDFChat(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Nova AI - Chat Export', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def export_chat_pdf(messages: list, title: str = "Nova AI Chat") -> bytes:
    """Export chat to PDF."""
    pdf = PDFChat()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, title, 0, 1, 'L')
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 10, f'Exported: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'L')
    pdf.ln(5)
    
    for msg in messages:
        role = "🧑 You" if msg["role"] == "user" else "✨ Nova AI"
        content = re.sub(r'<[^>]+>', '', msg["content"])[:2000]
        
        pdf.set_font('Arial', 'B', 11)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 8, role, 0, 1, 'L', fill=True)
        
        pdf.set_font('Arial', '', 10)
        for line in content.split('\n'):
            pdf.multi_cell(0, 6, line[:180])
        pdf.ln(3)
    
    return pdf.output(dest='S').encode('latin-1')

# ══════════════════════════════════════════════════════════════════════════════
#  CHART GENERATION FROM CSV
# ══════════════════════════════════════════════════════════════════════════════
def generate_chart_from_csv(csv_content: str, chart_type: str = "line") -> go.Figure:
    """Generate Plotly chart from CSV data."""
    try:
        df = pd.read_csv(io.StringIO(csv_content))
        
        # Auto-detect numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        non_numeric = df.select_dtypes(exclude=['number']).columns.tolist()
        
        if len(numeric_cols) < 1:
            return go.Figure().add_annotation(text="No numeric data found in CSV")
        
        x_col = non_numeric[0] if non_numeric else df.columns[0]
        y_col = numeric_cols[0]
        
        if chart_type == "line":
            fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} over {x_col}")
        elif chart_type == "bar":
            fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
        elif chart_type == "pie" and len(numeric_cols) >= 1:
            fig = px.pie(df, names=x_col, values=y_col, title=f"{y_col} Distribution")
        else:
            fig = px.line(df, x=x_col, y=y_col)
        
        fig.update_layout(
            template="plotly_dark",
            font=dict(family="DM Sans", size=12),
            paper_bgcolor='#111318',
            plot_bgcolor='#0a0c10',
        )
        return fig
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f"Error: {e}", showarrow=False)
        return fig

# ══════════════════════════════════════════════════════════════════════════════
#  GROQ CLIENT & MODELS
# ══════════════════════════════════════════════════════════════════════════════
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_KEY = "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"

client = Groq(api_key=GROQ_KEY)

AVAILABLE_MODELS = {
    "llama-3.3-70b-versatile": "🦙 Llama 3.3 70B (Default)",
    "llama-3.1-8b-instant": "⚡ Llama 3.1 8B (Fast)",
    "mixtral-8x7b-32768": "🌀 Mixtral 8x7B",
    "gemma2-9b-it": "💎 Gemma 2 9B",
}

MODEL = st.session_state.get("selected_model", "llama-3.3-70b-versatile")
MAX_HISTORY = 20

# ══════════════════════════════════════════════════════════════════════════════
#  IMAGE PROCESSING
# ══════════════════════════════════════════════════════════════════════════════
def image_to_base64(uploaded_file) -> tuple:
    try:
        uploaded_file.seek(0)
        img = Image.open(uploaded_file)
        fmt = img.format or "PNG"
        mime = f"image/{fmt.lower()}"
        if mime == "image/jpg": mime = "image/jpeg"
        
        max_size = 1568
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = (int(img.size[0]*ratio), int(img.size[1]*ratio))
            img = img.resize(new_size, Image.LANCZOS)
        
        buf = io.BytesIO()
        save_fmt = "JPEG" if fmt in ("JPEG","JPG") else "PNG"
        if img.mode in ("RGBA","P") and save_fmt == "JPEG":
            img = img.convert("RGB")
        img.save(buf, format=save_fmt, quality=85)
        buf.seek(0)
        
        b64 = base64.b64encode(buf.read()).decode()
        mime = f"image/{save_fmt.lower()}"
        return b64, mime, img.size[0], img.size[1]
    except Exception as e:
        return None, None, 0, 0

def get_vision_prompt(user_text: str) -> str:
    q = user_text.lower()
    if any(k in q for k in ["read","text","ocr","extract text","what does it say"]):
        return f"Read and transcribe ALL text visible in this image exactly. Then answer: {user_text}"
    elif any(k in q for k in ["solve","calculate","math","equation","problem"]):
        return f"Solve the math problem shown. Show step-by-step. {user_text}"
    elif any(k in q for k in ["code","program","script","debug","error"]):
        return f"Read the code exactly. Explain and identify issues. {user_text}"
    elif any(k in q for k in ["chart","graph","table","data","plot"]):
        return f"Analyze this chart/table. Extract all data and insights. {user_text}"
    else:
        return f"Analyze this image comprehensively. Describe everything. Also: {user_text if user_text.strip() else 'What is in this image?'}"

def analyze_image_stream(b64: str, mime: str, user_prompt: str) -> str:
    placeholder = st.empty()
    full = ""
    try:
        stream = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": "You are Nova AI with vision. Analyze images thoroughly."},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                    {"type": "text", "text": user_prompt}
                ]}
            ],
            max_tokens=2048, temperature=0.2, stream=True,
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
#  STREAMING
# ══════════════════════════════════════════════════════════════════════════════
def stream_response(messages: list, max_tokens: int = 4096, temperature: float = 0.25) -> str:
    full = ""
    box = st.empty()
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
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
CURRENCIES = ["USD","EUR","GBP","INR","JPY","CAD","AUD","CHF","CNY","HKD",
              "SGD","NOK","SEK","DKK","NZD","MXN","BRL","ZAR","RUB","KRW",
              "TRY","AED","SAR","THB","IDR","MYR","PHP","VND","EGP","PKR"]

MODE_PROMPTS = {
    "🤖 Default": "",
    "💻 Coder": "CODER MODE: Focus on perfect production-ready code.",
    "🎨 Creative": "CREATIVE MODE: Be imaginative and expressive.",
    "📊 Analyst": "ANALYST MODE: Be data-driven, precise, use tables.",
    "🎓 Teacher": "TEACHER MODE: Explain step by step with examples.",
    "✍️ Writer": "WRITER MODE: Clear, engaging, polished writing.",
}

GAME_KEYWORDS = ["game","snake","tetris","pacman","flappy","2048","chess",
    "checkers","sudoku","minesweeper","platformer","shooter","puzzle",
    "card","memory","quiz","breakout","pong","asteroids","racing","rpg"]
APP_KEYWORDS = ["app","application","dashboard","admin","landing","portfolio",
    "website","web app","e-commerce","shop","store","blog","chat","todo",
    "calculator","login","signup","form","expense","budget","note","kanban"]
SOFTWARE_KEYWORDS = ["software","tool","utility","desktop","file manager",
    "text editor","password","api","converter","automation","cli"]
DESIGN_KEYWORDS = ["design","ui","ux","mockup","prototype","wireframe",
    "beautiful","modern","stunning","animated","glassmorphism","gradient"]

STOCK_ALIASES = {
    "reliance":"RELIANCE.NS","tata":"TATAMOTORS.NS","tcs":"TCS.NS",
    "infosys":"INFY.NS","wipro":"WIPRO.NS","hdfc":"HDFCBANK.NS",
    "icici":"ICICIBANK.NS","sbi":"SBIN.NS","nifty":"^NSEI","sensex":"^BSESN",
    "apple":"AAPL","microsoft":"MSFT","google":"GOOGL","amazon":"AMZN",
    "tesla":"TSLA","meta":"META","bitcoin":"BTC-USD","ethereum":"ETH-USD",
}

SPORTS_MAP = {"cricket":"cricket","ipl":"IPL","football":"football",
    "soccer":"soccer","basketball":"basketball","tennis":"tennis"}
IPL_TEAMS = ["csk","mi","rcb","kkr","srh","pbks","dc","gt","lsg","rr"]

LANGUAGE_MAP = {
    "python":("python","3.10.0"),"javascript":("javascript","18.15.0"),
    "js":("javascript","18.15.0"),"typescript":("typescript","5.0.3"),
    "java":("java","15.0.2"),"c++":("c++","10.2.0"),"cpp":("c++","10.2.0"),
    "c":("c","10.2.0"),"rust":("rust","1.68.2"),"go":("go","1.16.2"),
}

SEARCH_TRIGGERS = ["who is","who was","what is","what was","when is",
    "where is","current","latest","today","election","winner","2024","2025"]

def today_str(): return datetime.now().strftime("%B %d, %Y")

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_weather(city):
    try:
        r = requests.get(f"https://wttr.in/{requests.utils.quote(city)}?format=j1",
                         headers={"User-Agent":"Mozilla/5.0"}, timeout=8)
        d = r.json(); c = d["current_condition"][0]; a = d["nearest_area"][0]
        return (f"City: {a['areaName'][0]['value']}, {a['country'][0]['value']}\n"
                f"Temperature: {c['temp_C']}°C (Feels like {c['FeelsLikeC']}°C)\n"
                f"Condition: {c['weatherDesc'][0]['value']}\n"
                f"Humidity: {c['humidity']}%\nWind: {c['windspeedKmph']} km/h")
    except: return "failed"

def extract_city(q):
    m = re.search(r"(?:weather|temperature|forecast)\s+(?:in|for|of|at)\s+([A-Za-z ,]+?)(?:\?|$)",q,re.IGNORECASE)
    if m: return m.group(1).strip().rstrip(",")
    sw = {"what","is","the","weather","report","temperature","forecast","today","now","how","give","me","show"}
    return " ".join(w for w in q.replace("?","").split() if w.lower() not in sw).strip() or "Guwahati"

def is_weather_query(q): return any(k in q.lower() for k in ["weather","temperature","forecast","humidity","rain","sunny"])

def get_stock(symbol, dname):
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=2d",
                         headers={"User-Agent":"Mozilla/5.0"},timeout=8)
        m = r.json()["chart"]["result"][0]["meta"]
        price=m.get("regularMarketPrice",0); prev=m.get("chartPreviousClose",0)
        chg=price-prev; pct=(chg/prev*100) if prev else 0
        arrow="🟢 ▲" if chg>=0 else "🔴 ▼"; sign="+" if chg>=0 else ""
        return f"Price: {price:,.2f}\nChange: {arrow} {sign}{chg:.2f} ({sign}{pct:.2f}%)"
    except: return "failed"

def extract_stock_symbol(q):
    ql=q.lower()
    for name,ticker in STOCK_ALIASES.items():
        if name in ql: return ticker,name.title()
    m=re.search(r"\b([A-Z]{2,5})\b",q)
    return (m.group(1),m.group(1)) if m else (None,None)

def is_stock_query(q):
    ql=q.lower()
    return any(a in ql for a in ["stock","price","crypto","bitcoin","ethereum","sensex","nifty"]) or any(k in ql for k in STOCK_ALIASES)

def fetch_live_cricket():
    results=[]
    try:
        r=requests.get("https://api.cricapi.com/v1/currentMatches",
                       params={"apikey":"a52ea237-09e7-4d69-b7cc-e4f0e2a8c1f1"},timeout=6)
        data=r.json()
        if data.get("status")=="success" and data.get("data"):
            for m in data["data"][:3]:
                scores=""
                for s in m.get("score",[]):
                    if s.get("r"): scores+=f"\n  {s.get('inning','')}: {s.get('r','')}/{s.get('w','')}"
                results.append(f"**{m.get('name','')}**\n  {m.get('status','')}{scores}")
    except: pass
    return "\n\n".join(results) if results else ""

def is_sports_query(q):
    ql=q.lower()
    if any(p in ql for p in ["history","rules","how to play"]): return False
    if any(t in ql for t in IPL_TEAMS): return True
    return any(k in ql for k in ["score","match","live","winner","cricket","ipl","football"])

def get_news(topic="India"):
    try:
        r=requests.get(f"https://news.google.com/rss/search?q={requests.utils.quote(topic)}&hl=en-IN",
                       headers={"User-Agent":"Mozilla/5.0"},timeout=8)
        root=ET.fromstring(r.content); out=[]
        for item in root.findall(".//item")[:5]:
            title=item.findtext("title","").strip()
            if title: out.append(f"• {title.split(' - ')[0]}")
        return "\n".join(out) if out else "No news."
    except: return "failed"

def is_news_query(q): return any(k in q.lower() for k in ["news","headlines","latest","breaking"])

def web_search(q):
    try:
        r=requests.get(f"https://html.duckduckgo.com/html/?q={requests.utils.quote(q)}",
                       headers={"User-Agent":"Mozilla/5.0"},timeout=10)
        snips=re.findall(r'class="result__snippet"[^>]*>(.*?)</',r.text,re.DOTALL)
        cs=[re.sub(r"<[^>]+>","",s).strip() for s in snips[:4] if s.strip()]
        return "\n".join([f"• {c[:200]}" for c in cs]) if cs else "No results."
    except: return "Search failed"

def needs_search(q):
    ql=q.lower()
    if any(k in ql for k in ["who made you","who created you"]): return False
    skip=GAME_KEYWORDS+APP_KEYWORDS+SOFTWARE_KEYWORDS+DESIGN_KEYWORDS
    if any(k in ql for k in skip): return False
    if is_sports_query(q): return False
    return any(t in ql for t in SEARCH_TRIGGERS)

def solve_math(expr):
    try:
        e=re.sub(r"(calculate|solve|what is|=)","",expr,flags=re.IGNORECASE).strip().replace("^","**")
        safe={"sin":math.sin,"cos":math.cos,"tan":math.tan,"sqrt":math.sqrt,
              "log":math.log10,"ln":math.log,"pi":math.pi,"e":math.e,"abs":abs}
        result=eval(e,{"__builtins__":{}},safe)
        return str(round(result,10) if isinstance(result,float) else result)
    except: return ""

def is_math_query(q):
    ql=q.lower()
    if any(k in ql for k in ["stock","weather","ipl","news","price","convert"]): return False
    return bool(re.search(r"\d",q)) and (bool(re.search(r"[+\-*/^()]",q)) or any(t in ql for t in ["sqrt","sin","cos","log"]))

def get_exchange_rate(fc,tc,amount=1.0):
    try:
        r=requests.get(f"https://api.exchangerate-api.com/v4/latest/{fc.upper()}",timeout=6)
        data=r.json(); rates=data.get("rates",{})
        if tc.upper() not in rates: return f"❌ Currency not found."
        return f"**{amount:,.2f} {fc.upper()}** = **{amount*rates[tc.upper()]:,.4f} {tc.upper()}**"
    except: return "Failed"

def is_currency_query(q):
    ql=q.lower(); curr=[c.lower() for c in CURRENCIES]
    return sum(1 for c in curr if c in ql)>=2 or any(t in ql for t in ["convert","to inr","to usd","to eur"])

def extract_currency_params(q):
    ql=q.lower(); curr=[c.lower() for c in CURRENCIES]
    found=[c for c in curr if c in ql]
    am=re.search(r"(\d+(?:\.\d+)?)",q)
    amount=float(am.group(1)) if am else 1.0
    if len(found)>=2: return amount,found[0].upper(),found[1].upper()
    return amount,"USD","INR"

UNIT_MAP={("celsius","fahrenheit"):lambda x:(x*9/5)+32,("fahrenheit","celsius"):lambda x:(x-32)*5/9,
    ("km","miles"):lambda x:x*0.621371,("miles","km"):lambda x:x*1.60934,
    ("kg","pounds"):lambda x:x*2.20462,("pounds","kg"):lambda x:x/2.20462}

def convert_unit(q):
    ql=q.lower(); am=re.search(r"(\d+(?:\.\d+)?)",q)
    amount=float(am.group(1)) if am else 1.0
    for (fu,tu),fn in UNIT_MAP.items():
        if fu in ql and tu in ql: return f"**{amount} {fu}** = **{round(fn(amount),4)} {tu}**"
    return ""

def is_unit_query(q):
    ql=q.lower()
    return any(u in ql for u in ["km","miles","kg","pounds","celsius","fahrenheit"]) and any(t in ql for t in ["convert","to","equals"])

def qr_url(text): return f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(text)}"
def is_qr_query(q): return any(k in q.lower() for k in ["qr code","qr for","generate qr"])
def extract_qr_content(q):
    m=re.search(r"https?://\S+",q)
    return m.group(0) if m else " ".join(w for w in q.split() if w.lower() not in ["qr","code","generate","make","for","my"])

def read_uploaded_file(f):
    try:
        name=f.name.lower()
        if name.endswith((".txt",".md",".py",".js",".html",".css",".java",".cpp",".c")):
            return f.read().decode("utf-8",errors="ignore")[:5000]
        elif name.endswith(".csv"):
            content=f.read().decode("utf-8",errors="ignore")
            return f"CSV Data:\n{content[:3000]}"
        elif name.endswith(".json"):
            return f.read().decode("utf-8",errors="ignore")[:4000]
        return f"File: {f.name}"
    except: return "Read error"

def fetch_url_content(url):
    try:
        r=requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=10)
        text=re.sub(r"<[^>]+>"," ",r.text)[:4000]
        return text if len(text)>100 else "Could not extract."
    except: return "URL fetch failed"

def is_url_query(q): return bool(re.search(r"https?://\S+",q))
def extract_url(q):
    m=re.search(r"https?://\S+",q)
    return m.group(0).rstrip(".,)>") if m else ""

def export_md(messages):
    lines=[f"# Nova AI Chat\n_Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n---\n"]
    for m in messages:
        role="🧑 You" if m["role"]=="user" else "✨ Nova AI"
        lines.append(f"### {role}\n{re.sub(r'<[^>]+>','',m['content'])[:2000]}\n")
    return "\n".join(lines)

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
    return any(t in ql for t in ["write","code","program","script","function","create","build","algorithm","api","html","css","python","java"])

def get_badge(ct):
    return {"game":'<div class="badge badge-blue">🎮 Game</div>',
            "app":'<div class="badge badge-orange">🚀 App</div>',
            "software":'<div class="badge badge-orange">⚙️ Software</div>',
            "design":'<div class="badge badge-blue">✨ Design</div>',
            "code":'<div class="badge badge-purple">💻 Code</div>',
            "general":""}.get(ct,"")

def get_spinner_text(ct):
    return {"game":t("building_game"),"app":t("building_app"),"software":t("engineering"),
            "design":t("crafting"),"code":t("writing_code"),"general":t("thinking")}.get(ct,t("thinking"))

def get_system_prompt(ct):
    mode=st.session_state.get("ai_mode","🤖 Default")
    mode_extra=MODE_PROMPTS.get(mode,""); td=today_str()
    base=(f"You are Nova AI, created by Samiran. Today: {td}. "
          f"Never mention Meta, Llama, OpenAI, Groq. Full memory. "
          f"NEVER partial code. ALWAYS complete. Do NOT generate images. "
          f"{mode_extra}\nLIVE DATA: Use provided data as TRUTH. Answer directly.\n\n")
    if ct=="game": return base+"GAME: ONE complete HTML5 game in single ```html block. Canvas 60fps, score, controls, sounds."
    elif ct=="app": return base+"APP: ONE complete app in single ```html block. CRUD, localStorage, responsive."
    elif ct in ("software","design"): return base+"ONE complete implementation in single ```html block. Stunning design."
    else: return base+"COMPLETE code always. All languages. Use search data as primary source."

def build_messages(user_query, search_results="", ct="general"):
    messages=[{"role":"system","content":get_system_prompt(ct)}]
    history=st.session_state.messages[:-1]
    if len(history)>MAX_HISTORY*2: history=history[-(MAX_HISTORY*2):]
    for msg in history:
        content=re.sub(r"<[^>]+>","",msg["content"]).strip()
        if content: messages.append({"role":msg["role"],"content":content[:3000]})
    if search_results:
        user_content=f"=== LIVE DATA ({today_str()}) ===\n{search_results}\n\n=== QUESTION ===\n{user_query}\nAnswer using live data."
    else: user_content=user_query
    messages.append({"role":"user","content":user_content[:5000]})
    return messages

def run_code(code,lang):
    try:
        l,v=LANGUAGE_MAP.get(lang.lower(),("python","3.10.0"))
        r=requests.post("https://emkc.org/api/v2/piston/execute",
                        json={"language":l,"version":v,"files":[{"name":f"main.{lang[:3]}","content":code}]},timeout=15)
        result=r.json(); run=result.get("run",{})
        out=run.get("stdout","").strip(); err=run.get("stderr","").strip()
        if err: return f"❌ Error:\n{err}"
        return out or "✅ Success (no output)"
    except Exception as e: return f"❌ Failed: {e}"

def extract_code_blocks(text):
    matches=re.findall(r"```(\w+)?\n([\s\S]*?)```",text)
    return [(lang.lower() if lang else "text",code.strip()) for lang,code in matches]

def build_html_preview(blocks):
    html=css=js=full=""
    for lang,code in blocks:
        if lang=="html": full=code if "<!doctype" in code.lower() or "<html" in code.lower() else html
        elif lang=="css": css=code
        elif lang in ("javascript","js"): js=code
    if full: return full
    if html or css or js:
        return f"<!DOCTYPE html><html><head><meta charset='UTF-8'><style>{css}</style></head><body>{html}<script>{js}</script></body></html>"
    return ""

# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for key,default in [
    ("messages",[]),("temperature",0.25),("max_tokens",4096),
    ("ai_mode","🤖 Default"),("language","en"),("selected_model","llama-3.3-70b-versatile"),
    ("uploaded_file_content",None),("uploaded_file_name",None),
    ("pending_image_b64",None),("pending_image_mime",None),("pending_image_name",None),
    ("show_image_uploader",False),("show_file_uploader",False),
    ("user",None),("conversations",[]),("current_conv_id",None),
]:
    if key not in st.session_state: st.session_state[key]=default

# ══════════════════════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');
:root {
    --bg:#0a0c10; --surface:#111318; --surface2:#1a1d24; --border:#232730;
    --accent:#00e5ff; --text:#e2e8f0; --muted:#64748b; --user-bg:#131b2e;
    --green:#10b981; --purple:#7c3aed; --orange:#f59e0b; --red:#ef4444; --pink:#ec4899;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--text)!important;font-family:'DM Sans',sans-serif!important;}
[data-testid="stHeader"],[data-testid="stToolbar"],.stDeployButton,#MainMenu,footer{display:none!important;}
::-webkit-scrollbar{width:4px;}::-webkit-scrollbar-track{background:var(--bg);}::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px;}
[data-testid="stAppViewContainer"]>.main>.block-container{max-width:860px!important;padding:0 1.5rem 10rem!important;margin:0 auto!important;}
[data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border)!important;}
[data-testid="stSidebar"] *{color:var(--text)!important;}
[data-testid="stSidebar"] .stSelectbox>div,[data-testid="stSidebar"] .stTextInput>div>div{background:var(--surface2)!important;border-color:var(--border)!important;}
[data-testid="stSidebar"] label{color:var(--muted)!important;font-size:12px!important;}
[data-testid="stSidebar"] h3{color:var(--accent)!important;font-family:'Space Mono',monospace!important;font-size:13px!important;margin:.8rem 0 .4rem!important;}
[data-testid="stSidebar"] hr{border-color:var(--border)!important;}
[data-testid="stSidebar"] .stButton>button{width:100%!important;background:var(--surface2)!important;border:1px solid var(--border)!important;color:var(--muted)!important;border-radius:8px!important;font-size:12px!important;}
[data-testid="stSidebar"] .stButton>button:hover{border-color:var(--accent)!important;color:var(--accent)!important;}
[data-testid="stSidebar"] .stDownloadButton>button{width:100%!important;background:rgba(0,229,255,.08)!important;border:1px solid rgba(0,229,255,.25)!important;color:var(--accent)!important;border-radius:8px!important;font-size:12px!important;}
[data-testid="stSidebar"] .stExpander{background:var(--surface2)!important;border:1px solid var(--border)!important;border-radius:10px!important;margin-bottom:.4rem!important;}
.hero{text-align:center;padding:2.5rem 1rem 1.5rem;position:relative;}
.hero::before{content:'';position:absolute;top:0;left:50%;transform:translateX(-50%);width:600px;height:300px;background:radial-gradient(ellipse at center,rgba(0,229,255,.07) 0%,transparent 70%);pointer-events:none;}
.hero-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(0,229,255,.08);border:1px solid rgba(0,229,255,.2);border-radius:999px;padding:4px 14px;font-family:'Space Mono',monospace;font-size:11px;color:var(--accent);letter-spacing:.05em;margin-bottom:1rem;}
.hero-badge::before{content:'●';font-size:8px;animation:pulse 2s infinite;}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.hero h1{font-family:'Space Mono',monospace!important;font-size:clamp(1.8rem,4vw,2.6rem)!important;font-weight:700!important;color:#fff!important;line-height:1.15!important;letter-spacing:-.02em;margin-bottom:.5rem!important;}
.hero h1 span{color:var(--accent);}
.hero p{font-size:.95rem;color:var(--muted);font-weight:300;max-width:460px;margin:0 auto;}
.divider{height:1px;background:linear-gradient(90deg,transparent,var(--border),transparent);margin:1.2rem 0;}
.stats-row{display:flex;gap:.6rem;margin:1rem 0 1.5rem;justify-content:center;flex-wrap:wrap;}
.stat-pill{display:flex;align-items:center;gap:6px;background:var(--surface);border:1px solid var(--border);border-radius:999px;padding:5px 12px;font-size:12px;color:var(--muted);}
.stat-pill .dot{width:6px;height:6px;border-radius:50%;}
.dot-green{background:var(--green);box-shadow:0 0 5px var(--green);}
.dot-blue{background:var(--accent);box-shadow:0 0 5px var(--accent);}
.dot-purple{background:var(--purple);box-shadow:0 0 5px var(--purple);}
.dot-orange{background:var(--orange);box-shadow:0 0 5px var(--orange);}
.dot-pink{background:var(--pink);box-shadow:0 0 5px var(--pink);}
[data-testid="stChatMessage"]{background:transparent!important;border:none!important;padding:0!important;}
[data-testid="stChatMessage"]>div{background:transparent!important;}
[data-testid="stChatMessageContent"]{background:transparent!important;}
.stChatMessage{border-radius:var(--radius)!important;padding:1rem 1.2rem!important;border:1px solid var(--border)!important;margin-bottom:.6rem!important;background:var(--surface)!important;animation:fadeUp .25s ease;}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.stChatMessage:has([data-testid="chatAvatarIcon-user"]){background:var(--user-bg)!important;border-color:rgba(0,229,255,.15)!important;}
pre,code{font-family:'Space Mono',monospace!important;font-size:13px!important;}
pre{background:#0d1117!important;border:1px solid var(--border)!important;border-left:3px solid var(--accent)!important;border-radius:10px!important;padding:1rem 1.2rem!important;overflow-x:auto!important;}
code:not(pre code){background:rgba(0,229,255,.08)!important;color:var(--accent)!important;border-radius:5px!important;padding:2px 6px!important;font-size:12.5px!important;}
[data-testid="stChatInputContainer"]{position:fixed!important;bottom:0!important;left:50%!important;transform:translateX(-50%)!important;width:100%!important;max-width:860px!important;padding:0.5rem 1.5rem 1.2rem!important;background:linear-gradient(to top,var(--bg) 80%,transparent)!important;backdrop-filter:blur(12px);z-index:999!important;}
[data-testid="stChatInput"]{background:var(--surface2)!important;border:1px solid var(--border)!important;border-radius:12px!important;color:var(--text)!important;font-family:'DM Sans',sans-serif!important;font-size:15px!important;}
[data-testid="stChatInput"]:focus{border-color:var(--accent)!important;box-shadow:0 0 0 3px rgba(0,229,255,.1)!important;outline:none!important;}
[data-testid="stChatInputSubmitButton"] button{background:var(--accent)!important;border:none!important;border-radius:8px!important;color:#000!important;font-weight:600!important;}
.upload-toolbar{display:flex;align-items:center;gap:8px;padding:6px 4px;margin-bottom:4px;flex-wrap:wrap;}
.upload-pill{display:inline-flex;align-items:center;gap:6px;background:var(--surface2);border:1px solid var(--border);border-radius:999px;padding:5px 14px;font-size:12px;color:var(--muted);cursor:pointer;transition:all .2s;font-family:'DM Sans',sans-serif;}
.upload-pill:hover{border-color:var(--accent);color:var(--accent);}
.upload-pill.active{border-color:var(--pink);color:var(--pink);background:rgba(236,72,153,.08);}
.badge{display:inline-flex;align-items:center;gap:5px;border-radius:6px;padding:3px 10px;font-size:11px;margin-bottom:.5rem;font-family:'DM Sans',sans-serif;}
.badge-green{background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.25);color:var(--green);}
.badge-red{background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.3);color:#fca5a5;}
.badge-purple{background:rgba(124,58,237,.08);border:1px solid rgba(124,58,237,.3);color:#a78bfa;}
.badge-orange{background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.3);color:var(--orange);}
.badge-blue{background:rgba(0,229,255,.08);border:1px solid rgba(0,229,255,.25);color:var(--accent);}
.badge-pink{background:rgba(236,72,153,.08);border:1px solid rgba(236,72,153,.3);color:var(--pink);}
.output-box{background:#0d1117;border:1px solid var(--border);border-left:3px solid var(--green);border-radius:10px;padding:.8rem 1.2rem;font-family:'Space Mono',monospace;font-size:13px;color:#a3e635;margin-top:.5rem;white-space:pre-wrap;}
.error-box{background:#1a0a0a;border:1px solid #7f1d1d;border-left:3px solid var(--red);border-radius:10px;padding:.8rem 1.2rem;font-family:'Space Mono',monospace;font-size:13px;color:#fca5a5;margin-top:.5rem;white-space:pre-wrap;}
.result-box{background:linear-gradient(135deg,#0d1117,#111827);border:1px solid var(--border);border-radius:10px;padding:.8rem 1.2rem;font-size:14px;color:var(--text);margin:.5rem 0;}
.result-box.orange{border-left:3px solid var(--orange);}
.result-box.green{border-left:3px solid var(--green);}
.btn-download{display:inline-flex;align-items:center;gap:5px;background:rgba(0,229,255,.1);border:1px solid rgba(0,229,255,.3);color:var(--accent);padding:6px 14px;border-radius:8px;text-decoration:none;font-size:12px;font-family:'DM Sans',sans-serif;font-weight:500;margin-top:.5rem;}
.stButton>button{background:var(--surface2)!important;border:1px solid var(--border)!important;color:var(--muted)!important;border-radius:8px!important;font-family:'DM Sans',sans-serif!important;font-size:13px!important;font-weight:500!important;padding:.4rem 1rem!important;transition:all .2s!important;}
.stButton>button:hover{border-color:var(--accent)!important;color:var(--accent)!important;background:rgba(0,229,255,.06)!important;}
.category-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:.8rem;margin:1.2rem 0;}
.category-card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1rem;text-align:center;transition:border-color .2s,transform .2s;}
.category-card:hover{border-color:var(--accent);transform:translateY(-2px);}
.category-icon{font-size:1.6rem;margin-bottom:.4rem;}
.category-title{font-size:12.5px;font-weight:600;color:#94a3b8;margin-bottom:.2rem;}
.category-examples{font-size:11px;color:var(--muted);line-height:1.6;}
.chat-image{max-width:360px;max-height:280px;border-radius:12px;border:1px solid var(--border);margin-bottom:8px;display:block;object-fit:cover;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;padding:1.2rem 0 .8rem'>
        <div style='font-size:1.4rem;font-weight:700;font-family:Space Mono,monospace;color:#00e5ff'>✨ Nova AI</div>
        <div style='font-size:11px;color:#64748b;margin-top:.3rem'>v5.0 · {t("welcome")}</div>
    </div>""", unsafe_allow_html=True)
    st.divider()

    # ── Login / User ──────────────────────────────────────────────────────────
    if not st.session_state.get("user"):
        st.markdown("### 🔐 " + t("login"))
        login_tab, signup_tab = st.tabs([t("signin"), t("signup")])
        with login_tab:
            l_user = st.text_input(t("username"), key="l_user")
            l_pass = st.text_input(t("password"), type="password", key="l_pass")
            if st.button(t("signin"), key="btn_signin"):
                user = verify_user(l_user, l_pass)
                if user:
                    st.session_state["user"] = user
                    st.session_state["conversations"] = load_conversations(user["id"])
                    st.success(f"{t('welcome')}, {user['username']}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        with signup_tab:
            s_user = st.text_input(t("username"), key="s_user")
            s_pass = st.text_input(t("password"), type="password", key="s_pass")
            if st.button(t("signup"), key="btn_signup"):
                if create_user(s_user, s_pass):
                    st.success("Account created! Please sign in.")
                else:
                    st.error("Username already exists")
    else:
        st.markdown(f"### 👤 {st.session_state['user']['username']}")
        if st.button(t("logout"), key="btn_logout"):
            st.session_state["user"] = None
            st.session_state["conversations"] = []
            st.session_state["current_conv_id"] = None
            st.rerun()
        st.divider()

        # ── Conversations List ────────────────────────────────────────────────
        st.markdown("### " + t("conversations"))
        if st.button(t("new_chat"), key="btn_new_conv", use_container_width=True):
            st.session_state["messages"] = []
            st.session_state["current_conv_id"] = None
            st.rerun()
        
        for conv in st.session_state.get("conversations", []):
            col_a, col_b, col_c = st.columns([4,1,1])
            with col_a:
                if st.button(f"📂 {conv['title'][:15]}...", key=f"load_{conv['id']}", use_container_width=True):
                    msgs = load_conversation_messages(conv["id"])
                    if msgs:
                        st.session_state["messages"] = msgs
                        st.session_state["current_conv_id"] = conv["id"]
                        st.rerun()
            with col_b:
                if st.button("🗑️", key=f"del_{conv['id']}"):
                    if delete_conversation(conv["id"], st.session_state["user"]["id"]):
                        st.session_state["conversations"] = load_conversations(st.session_state["user"]["id"])
                        st.rerun()
        st.divider()

    # ── Model & Language ──────────────────────────────────────────────────────
    st.markdown("### " + t("model_settings"))
    st.session_state["selected_model"] = st.selectbox(
        t("models"), 
        options=list(AVAILABLE_MODELS.keys()),
        format_func=lambda x: AVAILABLE_MODELS[x],
        index=list(AVAILABLE_MODELS.keys()).index(st.session_state.get("selected_model", "llama-3.3-70b-versatile")),
        key="sel_model"
    )
    MODEL = st.session_state["selected_model"]
    
    st.session_state["language"] = st.selectbox(
        t("language"),
        options=["en","hi","bn"],
        format_func=lambda x: TRANSLATIONS[x]["name"],
        index=["en","hi","bn"].index(st.session_state.get("language","en")),
        key="sel_lang"
    )
    
    st.session_state["temperature"] = st.slider(t("temperature"), 0.0, 1.0,
        value=st.session_state["temperature"], step=0.05)
    st.session_state["max_tokens"] = st.select_slider(t("max_length"),
        options=[512,1024,2048,4096,8192], value=st.session_state["max_tokens"])
    st.divider()

    st.markdown("### " + t("ai_mode"))
    st.session_state["ai_mode"] = st.selectbox("", list(MODE_PROMPTS.keys()),
        index=0, label_visibility="collapsed", key="sel_mode")
    st.divider()

    st.markdown("### " + t("quick_tools"))
    with st.expander(t("currency")):
        amt=st.number_input("Amount",value=1.0,min_value=0.0,key="sb_amt")
        c1,c2=st.columns(2)
        with c1: fc=st.selectbox("From",CURRENCIES,index=0,key="sb_fc")
        with c2: tc=st.selectbox("To",CURRENCIES,index=3,key="sb_tc")
        if st.button("Convert",key="sb_conv"): st.markdown(get_exchange_rate(fc,tc,amt))

    with st.expander(t("units")):
        uin=st.text_input("e.g. 100 km to miles",key="sb_uin")
        if st.button("Convert",key="sb_unit"):
            res=convert_unit(uin)
            st.markdown(res if res else "⚠️ Try: '100 km to miles'")

    with st.expander(t("calculator")):
        cin=st.text_input("e.g. sqrt(144)",key="sb_cin")
        if st.button("Calculate",key="sb_calc"):
            res=solve_math(cin)
            if res: st.markdown(f"**= {res}**")

    with st.expander(t("qr_code")):
        qin=st.text_input("Text or URL",key="sb_qin")
        if st.button("Generate",key="sb_qr") and qin:
            url=qr_url(qin)
            st.image(url,width=180)

    st.divider()
    st.markdown("### " + t("export"))
    if st.session_state["messages"]:
        ca,cb=st.columns(2)
        ts=datetime.now().strftime("%Y%m%d_%H%M")
        with ca:
            st.download_button("📝 MD",data=export_md(st.session_state["messages"]),
                               file_name=f"nova_{ts}.md",mime="text/markdown",use_container_width=True)
        with cb:
            pdf_bytes = export_chat_pdf(st.session_state["messages"], "Nova AI Chat")
            st.download_button("🖨️ PDF",data=pdf_bytes,
                               file_name=f"nova_{ts}.pdf",mime="application/pdf",use_container_width=True)
    st.divider()
    st.markdown(f"<div style='text-align:center;font-size:10px;color:#374151'>Nova AI v5.0 · Samiran<br>{datetime.now().strftime('%B %Y')}</div>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero">
    <div class="hero-badge">{t("live")} · {t("free")} · {t("unlimited")} · {t("vision")}</div>
    <h1>{t("hero_title")}<span> AI</span></h1>
    <p>{t("hero_subtitle")}</p>
</div>
<div class="stats-row">
    <div class="stat-pill"><span class="dot dot-purple"></span>🧠 {t("memory")}</div>
    <div class="stat-pill"><span class="dot dot-pink"></span>👁️ {t("vision")}</div>
    <div class="stat-pill"><span class="dot dot-blue"></span>🏏 {t("sports")}</div>
    <div class="stat-pill"><span class="dot dot-orange"></span>🎮 {t("games")}</div>
    <div class="stat-pill"><span class="dot dot-green"></span>📁 {t("files")}</div>
    <div class="stat-pill"><span class="dot dot-green"></span>💱 {t("data")}</div>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

# Toolbar
col1,col2,col3=st.columns([5,1,1])
with col2:
    count=len([m for m in st.session_state.messages if m["role"]=="user"])
    st.markdown(f"<p style='text-align:right;color:var(--muted);font-size:12px;padding-top:.5rem'>{count} {t('msg') if count==1 else t('msgs')}</p>",unsafe_allow_html=True)
with col3:
    if st.button(t("clear")): 
        st.session_state.messages=[]
        st.session_state.current_conv_id=None
        st.rerun()

# Chat History
if not st.session_state.messages:
    st.markdown(f"""
    <div style="text-align:center;padding:1rem 1rem .5rem">
        <div style="font-size:2rem;margin-bottom:.5rem">✨</div>
        <p style="font-size:.95rem;font-weight:600;color:#94a3b8;margin-bottom:1rem">{t("what_today")}</p>
    </div>
    <div class="category-grid">
        <div class="category-card"><div class="category-icon">👁️</div><div class="category-title">{t("vision_card")}</div><div class="category-examples">{t("vision_desc")}</div></div>
        <div class="category-card"><div class="category-icon">🎮</div><div class="category-title">{t("games_card")}</div><div class="category-examples">{t("games_desc")}</div></div>
        <div class="category-card"><div class="category-icon">🚀</div><div class="category-title">{t("apps_card")}</div><div class="category-examples">{t("apps_desc")}</div></div>
        <div class="category-card"><div class="category-icon">💻</div><div class="category-title">{t("code_card")}</div><div class="category-examples">{t("code_desc")}</div></div>
        <div class="category-card"><div class="category-icon">📁</div><div class="category-title">{t("files_card")}</div><div class="category-examples">{t("files_desc")}</div></div>
        <div class="category-card"><div class="category-icon">🌐</div><div class="category-title">{t("live_card")}</div><div class="category-examples">{t("live_desc")}</div></div>
    </div>
    <div class="divider"></div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("meta"): st.markdown(msg["meta"],unsafe_allow_html=True)
            if msg.get("image_b64") and msg.get("image_mime"):
                try:
                    img_bytes=base64.b64decode(msg["image_b64"])
                    st.image(Image.open(io.BytesIO(img_bytes)),caption=msg.get("image_name",""),width=350)
                except: pass
            st.markdown(msg["content"])

# Upload Toolbar
st.markdown('<div class="upload-toolbar">', unsafe_allow_html=True)
tb_col1, tb_col2, tb_col3, tb_col4 = st.columns([1,1,1,6])
with tb_col1:
    if st.button(t("upload_image"), key="toggle_img"):
        st.session_state["show_image_uploader"] = not st.session_state["show_image_uploader"]
        st.session_state["show_file_uploader"] = False
        st.rerun()
with tb_col2:
    if st.button(t("upload_file"), key="toggle_file"):
        st.session_state["show_file_uploader"] = not st.session_state["show_file_uploader"]
        st.session_state["show_image_uploader"] = False
        st.rerun()
with tb_col3:
    if st.button(t("help"), key="show_help"):
        st.session_state["show_image_uploader"] = False
        st.session_state["show_file_uploader"] = False
st.markdown('</div>', unsafe_allow_html=True)

# Image Uploader
if st.session_state.get("show_image_uploader"):
    st.markdown(f"""
    <div style='background:#1a1d24;border:1px solid #232730;border-radius:14px;padding:1.2rem;margin-bottom:.5rem;'>
        <div style='font-size:13px;color:#00e5ff;font-weight:600;margin-bottom:.5rem'>{t("upload_image_title")}</div>
        <div style='font-size:11px;color:#64748b;margin-bottom:.8rem'>{t("upload_image_supports")}</div>
    </div>
    """, unsafe_allow_html=True)
    img_file = st.file_uploader("Choose image", type=["jpg","jpeg","png","gif","bmp","webp","tiff"], key="main_img", label_visibility="collapsed")
    if img_file:
        b64, mime, w, h = image_to_base64(img_file)
        if b64:
            st.session_state["pending_image_b64"] = b64
            st.session_state["pending_image_mime"] = mime
            st.session_state["pending_image_name"] = img_file.name
            st.session_state["show_image_uploader"] = False
            st.success(f"✅ {img_file.name} ({w}×{h}px)")
            st.info(t("type_question"))
    st.markdown(f"""
    <div style='margin-top:.8rem'>
        <div style='font-size:11px;color:#64748b;margin-bottom:.4rem'>💡 {t("example_what")}</div>
        <div style='display:flex;flex-wrap:wrap;gap:6px'>
            <span style='background:#1a1d24;border:1px solid #232730;border-radius:999px;padding:3px 10px;font-size:11px;color:#94a3b8'>{t("example_what")}</span>
            <span style='background:#1a1d24;border:1px solid #232730;border-radius:999px;padding:3px 10px;font-size:11px;color:#94a3b8'>{t("example_read")}</span>
            <span style='background:#1a1d24;border:1px solid #232730;border-radius:999px;padding:3px 10px;font-size:11px;color:#94a3b8'>{t("example_solve")}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# File Uploader
if st.session_state.get("show_file_uploader"):
    st.markdown(f"""
    <div style='background:#1a1d24;border:1px solid #232730;border-radius:14px;padding:1.2rem;margin-bottom:.5rem;'>
        <div style='font-size:13px;color:#a78bfa;font-weight:600;margin-bottom:.5rem'>{t("upload_file_title")}</div>
        <div style='font-size:11px;color:#64748b;margin-bottom:.8rem'>{t("upload_file_supports")}</div>
    </div>
    """, unsafe_allow_html=True)
    doc_file = st.file_uploader("Choose file", type=["txt","csv","json","py","js","html","css","java","cpp","c","md"], key="main_doc", label_visibility="collapsed")
    if doc_file:
        content = read_uploaded_file(doc_file)
        st.session_state["uploaded_file_content"] = content
        st.session_state["uploaded_file_name"] = doc_file.name
        st.session_state["show_file_uploader"] = False
        st.success(f"✅ {doc_file.name}")
        st.info(t("type_question"))

# Chart from CSV
if st.session_state.get("uploaded_file_content") and st.session_state.get("uploaded_file_name","").endswith(".csv"):
    if st.button(t("chart") + " 📊", key="btn_chart"):
        fig = generate_chart_from_csv(st.session_state["uploaded_file_content"], "line")
        st.plotly_chart(fig, use_container_width=True)

# Chat Input
if prompt := st.chat_input(t("chat_placeholder")):
    has_image = bool(st.session_state.get("pending_image_b64"))
    has_file = bool(st.session_state.get("uploaded_file_content"))
    
    user_msg = {"role":"user","content":prompt,"meta":""}
    if has_image:
        user_msg["image_b64"] = st.session_state["pending_image_b64"]
        user_msg["image_mime"] = st.session_state["pending_image_mime"]
        user_msg["image_name"] = st.session_state["pending_image_name"]
    
    st.session_state.messages.append(user_msg)
    
    with st.chat_message("user"):
        if has_image:
            try:
                img_bytes=base64.b64decode(st.session_state["pending_image_b64"])
                st.image(Image.open(io.BytesIO(img_bytes)),caption=st.session_state.get("pending_image_name",""),width=350)
            except: pass
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        response=""; meta=""
        
        # Image Analysis
        if has_image:
            b64 = st.session_state["pending_image_b64"]
            mime = st.session_state["pending_image_mime"]
            name = st.session_state.get("pending_image_name","image")
            meta = f'<div class="badge badge-pink">👁️ Vision AI · {name}</div>'
            st.markdown(meta, unsafe_allow_html=True)
            with st.spinner(t("analyzing_image")):
                response = analyze_image_stream(b64, mime, get_vision_prompt(prompt))
            st.session_state["pending_image_b64"] = None
            st.session_state["pending_image_mime"] = None
            st.session_state["pending_image_name"] = None
        
        # QR
        elif is_qr_query(prompt):
            content=extract_qr_content(prompt); url=qr_url(content)
            meta='<div class="badge badge-green">📱 QR</div>'
            st.markdown(meta,unsafe_allow_html=True)
            st.markdown(f"**QR:** `{content}`")
            st.image(url,width=260)
            response=f"✅ QR generated"
        
        # Currency
        elif is_currency_query(prompt):
            amount,fc,tc=extract_currency_params(prompt)
            with st.spinner(t("converting")): result=get_exchange_rate(fc,tc,amount)
            meta='<div class="badge badge-green">💱 '+t("live_rate")+'</div>'
            st.markdown(meta,unsafe_allow_html=True)
            st.markdown(f'<div class="result-box green">{result}</div>',unsafe_allow_html=True)
            response=result
        
        # Unit
        elif is_unit_query(prompt):
            result=convert_unit(prompt)
            if result:
                meta='<div class="badge badge-orange">📐 '+t("unit_converted")+'</div>'
                st.markdown(meta,unsafe_allow_html=True)
                st.markdown(f'<div class="result-box orange">{result}</div>',unsafe_allow_html=True)
                response=result
        
        # Math
        if not response and is_math_query(prompt):
            result=solve_math(prompt)
            if result:
                meta='<div class="badge badge-orange">🔢 '+t("calculated")+'</div>'
                st.markdown(meta,unsafe_allow_html=True)
                st.markdown(f'<div class="result-box orange" style="font-family:Space Mono;font-size:16px;color:#f59e0b">= {result}</div>',unsafe_allow_html=True)
                response=f"= **{result}**"
        
        # URL
        if not response and is_url_query(prompt):
            url=extract_url(prompt)
            if url:
                with st.spinner(t("reading_url")+"..."): page=fetch_url_content(url)
                meta='<div class="badge badge-green">🌐 '+t("url_read")+'</div>'
                st.markdown(meta,unsafe_allow_html=True)
                msgs=build_messages(f"URL: {url}\nContent:\n{page}\n\nRequest: {prompt}")
                response=stream_response(msgs,max_tokens=st.session_state["max_tokens"],temperature=st.session_state["temperature"])
        
        # File
        if not response and has_file:
            fname=st.session_state.get("uploaded_file_name","file")
            meta=f'<div class="badge badge-purple">📁 {fname}</div>'
            st.markdown(meta,unsafe_allow_html=True)
            msgs=build_messages(f"File: '{fname}'\nContent:\n{st.session_state['uploaded_file_content']}\n\nRequest: {prompt}")
            response=stream_response(msgs,max_tokens=st.session_state["max_tokens"],temperature=st.session_state["temperature"])
            st.session_state["uploaded_file_content"]=None
            st.session_state["uploaded_file_name"]=None
        
        # Stock
        if not response and is_stock_query(prompt):
            symbol,dname=extract_stock_symbol(prompt)
            if symbol:
                with st.spinner(t("fetching_stock")+"..."): sd=get_stock(symbol,dname)
                if "failed" not in sd.lower():
                    meta='<div class="badge badge-green">📈 Live</div>'
                    st.markdown(meta,unsafe_allow_html=True)
                    response=f"### 📈 {dname}\n{sd}"
                    st.markdown(response)
        
        # Sports
        if not response and is_sports_query(prompt):
            with st.spinner(t("fetching_sports")):
                cricket=fetch_live_cricket()
                sports_data=cricket if cricket else "No live matches"
            meta='<div class="badge badge-red">🔴 '+t("live_sports")+'</div>'
            st.markdown(meta,unsafe_allow_html=True)
            msgs=build_messages(prompt,search_results=sports_data)
            response=stream_response(msgs,max_tokens=1024,temperature=0.1)
        
        # News
        if not response and is_news_query(prompt):
            with st.spinner(t("fetching_news")):
                topic=prompt.replace("news","").strip() or "India"
                news=get_news(topic)
            meta='<div class="badge badge-green">📰 '+t("live_news")+'</div>'
            st.markdown(meta,unsafe_allow_html=True)
            response=f"### 📰 {topic}\n\n{news}"
            st.markdown(response)
        
        # Weather
        if not response and is_weather_query(prompt):
            with st.spinner(t("fetching_weather")):
                city=extract_city(prompt); wd=get_weather(city)
            if "failed" not in wd.lower():
                L=dict(l.split(": ",1) for l in wd.strip().splitlines() if ": " in l)
                meta='<div class="badge badge-green">🌤️ '+t("live_weather")+'</div>'
                st.markdown(meta,unsafe_allow_html=True)
                response=f"### 🌍 {L.get('City',city)}\n\n{wd}"
                st.markdown(response)
        
        # General
        if not response:
            ct=classify_creation(prompt); search_results=""; searched=False
            if needs_search(prompt):
                with st.spinner(t("searching")):
                    search_results=web_search(prompt)
                    searched=True
            if searched:
                bm='<div class="badge badge-green">🔍 '+t("web_search")+'</div>'
                st.markdown(bm,unsafe_allow_html=True); meta+=bm
            badge=get_badge(ct)
            if badge: st.markdown(badge,unsafe_allow_html=True); meta+=badge
            turns=len(st.session_state.messages)//2
            if turns>1:
                mem=f'<div class="badge badge-purple">🧠 {turns} {t("turns_remembered")}</div>'
                st.markdown(mem,unsafe_allow_html=True); meta+=mem
            
            for attempt in range(3):
                try:
                    with st.spinner(get_spinner_text(ct) if attempt==0 else t("retrying")):
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
                            st.markdown("### 🖥️ Live Preview")
                            h=650 if ct in ("game","app","software") else 520
                            st.components.v1.html(html_src,height=h,scrolling=True)
                            b64_html=base64.b64encode(html_src.encode()).decode()
                            fname={"game":"nova_game.html","app":"nova_app.html","software":"nova_software.html","design":"nova_design.html"}.get(ct,"nova_ai.html")
                            st.markdown(f'<a href="data:text/html;base64,{b64_html}" download="{fname}" class="btn-download">⬇️ {t("download")} {fname}</a>',unsafe_allow_html=True)
                    elif code and lang and lang not in ("html","css"):
                        rk=f"run_{len(st.session_state.messages)}"
                        if st.button(t("run")+" "+lang.title(),key=rk):
                            with st.spinner(t("running_code")+"..."): out=run_code(code,lang)
                            cls="error-box" if "❌" in out else "output-box"
                            st.markdown(f'<div class="{cls}">{out}</div>',unsafe_allow_html=True)
                    break
                except Exception as e:
                    if "rate_limit" in str(e) and attempt<2: continue
                    st.error(f"{t('error')} {e}"); break
        
        if response:
            st.session_state.messages.append({"role":"assistant","content":response,"meta":meta})
            
            # Save to database if logged in
            if st.session_state.get("user"):
                if not st.session_state.get("current_conv_id"):
                    title = prompt[:50] + "..." if len(prompt) > 50 else prompt
                    conv_id = save_conversation(st.session_state["user"]["id"], title, st.session_state.messages)
                    st.session_state["current_conv_id"] = conv_id
                    st.session_state["conversations"] = load_conversations(st.session_state["user"]["id"])
                else:
                    # Update existing conversation
                    save_conversation(st.session_state["user"]["id"], "Updated", st.session_state.messages[-2:])
