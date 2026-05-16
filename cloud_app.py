import streamlit as st
from groq import Groq
import time, requests, re, base64, json, math
from datetime import datetime
import urllib.parse
import xml.etree.ElementTree as ET
from PIL import Image
import io
import sqlite3
import hashlib
import os

# ══════════════════════════════════════════════════════════════════════════════
# 💾 PERSISTENT MEMORY DATABASE SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

DB_PATH = "soveren_memory.db"

def init_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_name TEXT DEFAULT 'User',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_messages INTEGER DEFAULT 0,
            language TEXT DEFAULT 'en'
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS long_term_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            memory_type TEXT,
            memory_key TEXT,
            memory_value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            session_id TEXT PRIMARY KEY,
            ai_mode TEXT DEFAULT '🤖 Default',
            temperature REAL DEFAULT 0.25,
            max_tokens INTEGER DEFAULT 4096,
            language_code TEXT DEFAULT 'en',
            language_name TEXT DEFAULT '🌐 English',
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS pinned_memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            content TEXT,
            pinned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    ''')
    conn.commit()
    conn.close()

def get_or_create_session(session_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
    session = c.fetchone()
    if not session:
        c.execute('''
            INSERT INTO sessions (session_id, created_at, last_active)
            VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''', (session_id,))
        conn.commit()
    else:
        c.execute('''
            UPDATE sessions SET last_active = CURRENT_TIMESTAMP
            WHERE session_id = ?
        ''', (session_id,))
        conn.commit()
    conn.close()

def save_message_db(session_id: str, role: str, content: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    clean_content = re.sub(r'<[^>]+>', '', content).strip()
    if clean_content:
        c.execute('''
            INSERT INTO messages (session_id, role, content, timestamp)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (session_id, role, clean_content))
        c.execute('''
            UPDATE sessions
            SET total_messages = total_messages + 1, last_active = CURRENT_TIMESTAMP
            WHERE session_id = ?
        ''', (session_id,))
        conn.commit()
    conn.close()

def load_messages_db(session_id: str, limit: int = 100):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT role, content, timestamp FROM messages
        WHERE session_id = ?
        ORDER BY timestamp ASC
        LIMIT ?
    ''', (session_id, limit))
    rows = c.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1], "timestamp": r[2], "meta": ""} for r in rows]

def save_long_term_memory(session_id: str, memory_type: str, key: str, value: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT id FROM long_term_memory
        WHERE session_id = ? AND memory_key = ?
    ''', (session_id, key))
    existing = c.fetchone()
    if existing:
        c.execute('''
            UPDATE long_term_memory
            SET memory_value = ?, updated_at = CURRENT_TIMESTAMP
            WHERE session_id = ? AND memory_key = ?
        ''', (value, session_id, key))
    else:
        c.execute('''
            INSERT INTO long_term_memory (session_id, memory_type, memory_key, memory_value)
            VALUES (?, ?, ?, ?)
        ''', (session_id, memory_type, key, value))
    conn.commit()
    conn.close()

def get_long_term_memory(session_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT memory_type, memory_key, memory_value, updated_at
        FROM long_term_memory
        WHERE session_id = ?
        ORDER BY updated_at DESC
    ''', (session_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def delete_long_term_memory(session_id: str, memory_key: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        DELETE FROM long_term_memory
        WHERE session_id = ? AND memory_key = ?
    ''', (session_id, memory_key))
    conn.commit()
    conn.close()

def save_preferences_db(session_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO user_preferences
        (session_id, ai_mode, temperature, max_tokens, language_code, language_name)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        session_id,
        st.session_state.get("ai_mode", "🤖 Default"),
        st.session_state.get("temperature", 0.25),
        st.session_state.get("max_tokens", 4096),
        st.session_state.get("lang_code", "en"),
        st.session_state.get("lang_name", "🌐 English"),
    ))
    conn.commit()
    conn.close()

def load_preferences_db(session_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT ai_mode, temperature, max_tokens, language_code, language_name
        FROM user_preferences WHERE session_id = ?
    ''', (session_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_session_stats(session_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT total_messages, created_at, last_active
        FROM sessions WHERE session_id = ?
    ''', (session_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_all_sessions():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT session_id, user_name, total_messages, last_active
        FROM sessions
        ORDER BY last_active DESC
        LIMIT 10
    ''')
    rows = c.fetchall()
    conn.close()
    return rows

def delete_session_db(session_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    c.execute("DELETE FROM long_term_memory WHERE session_id = ?", (session_id,))
    c.execute("DELETE FROM user_preferences WHERE session_id = ?", (session_id,))
    c.execute("DELETE FROM pinned_memories WHERE session_id = ?", (session_id,))
    c.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

def clear_session_messages(session_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    c.execute('''
        UPDATE sessions SET total_messages = 0
        WHERE session_id = ?
    ''', (session_id,))
    conn.commit()
    conn.close()

def extract_and_save_memories(session_id: str, user_msg: str, ai_response: str):
    text = user_msg.lower()
    name_patterns = [
        r"(?:my name is|i am|i'm|call me)\s+([A-Z][a-z]+)",
        r"([A-Z][a-z]+)\s+(?:here|speaking)",
    ]
    for pattern in name_patterns:
        m = re.search(pattern, user_msg, re.IGNORECASE)
        if m:
            save_long_term_memory(session_id, "personal", "user_name", m.group(1))
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("UPDATE sessions SET user_name = ? WHERE session_id = ?",
                      (m.group(1), session_id))
            conn.commit()
            conn.close()
            break
    prof_patterns = [
        r"i(?:'m| am) (?:a |an )?([a-z]+ (?:developer|engineer|designer|doctor|teacher|student|manager|analyst|scientist|writer|artist))",
        r"i work as (?:a |an )?([a-z ]+)",
        r"my (?:job|profession|occupation) is ([a-z ]+)",
    ]
    for pattern in prof_patterns:
        m = re.search(pattern, text)
        if m:
            save_long_term_memory(session_id, "professional", "profession", m.group(1).strip())
            break
    loc_patterns = [
        r"i(?:'m| am) (?:from|in|based in|living in)\s+([A-Z][a-zA-Z\s,]+?)(?:\.|,|$)",
        r"i live in\s+([A-Z][a-zA-Z\s]+?)(?:\.|,|$)",
    ]
    for pattern in loc_patterns:
        m = re.search(pattern, user_msg)
        if m:
            save_long_term_memory(session_id, "personal", "location", m.group(1).strip())
            break
    tech_keywords = ["python", "javascript", "react", "flutter", "django",
                     "tensorflow", "pytorch", "sql", "java", "swift"]
    found_tech = [t for t in tech_keywords if t in text]
    if found_tech and any(k in text for k in ["i use", "i love", "i prefer", "i work with", "favorite"]):
        save_long_term_memory(session_id, "technical", "preferred_tech", ", ".join(found_tech))
    interest_patterns = [
        r"i (?:love|like|enjoy|am interested in|am passionate about)\s+([a-z\s]+?)(?:\.|,|$)",
    ]
    for pattern in interest_patterns:
        m = re.search(pattern, text)
        if m and len(m.group(1).split()) <= 5:
            save_long_term_memory(session_id, "personal", f"interest_{m.group(1)[:20]}", m.group(1).strip())
            break

def build_memory_context(session_id: str) -> str:
    memories = get_long_term_memory(session_id)
    if not memories:
        return ""
    context_lines = ["=== LONG-TERM MEMORY (Facts about this user) ==="]
    for mem_type, key, value, updated in memories:
        clean_key = key.replace("_", " ").title()
        context_lines.append(f"• {clean_key}: {value}")
    context_lines.append("=== Use these facts naturally in your responses ===")
    return "\n".join(context_lines)

def get_session_id() -> str:
    if "session_id" not in st.session_state or not st.session_state["session_id"]:
        raw = f"soveren_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"
        st.session_state["session_id"] = hashlib.md5(raw.encode()).hexdigest()[:16]
    return st.session_state["session_id"]

# Initialize DB
init_database()
SESSION_ID = get_session_id()
get_or_create_session(SESSION_ID)

# ══════════════════════════════════════════════════════════════════════════════
# LANGUAGE SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
LANGUAGES = {
    "🌐 English": "en",
    "🇮🇳 हिंदी": "hi",
    "🇧🇩 বাংলা": "bn",
    "🇪🇸 Español": "es",
    "🇫🇷 Français": "fr",
    "🇩🇪 Deutsch": "de",
    "🇯🇵 日本語": "ja",
    "🇨🇳 中文": "zh",
    "🇸🇦 العربية": "ar",
    "🇷🇺 Русский": "ru",
    "🇵🇹 Português": "pt",
    "🇰🇷 한국어": "ko",
}

UI_TEXT = {
    "en": {
        "title": "Soveren",
        "subtitle": "The world's smartest AI — sees images, builds apps, knows everything live.",
        "badge": "LIVE · FREE · UNLIMITED · VISION AI",
        "chat_placeholder": "Ask anything — type here or click Image / File 🖼️ 📄 above…",
        "clear": "🗑️ Clear",
        "msgs": "msg",
        "msgp": "msgs",
        "hero_q": "What would you like to do today?",
        "cat_vision": "Vision AI",
        "cat_vision_ex": "Upload any image\nAI reads & analyzes",
        "cat_games": "Games",
        "cat_games_ex": "Snake · Tetris\nChess · 2048\nPacman · RPG",
        "cat_apps": "Apps",
        "cat_apps_ex": "Dashboard · Todo\nE-commerce\nPortfolio",
        "cat_code": "Code",
        "cat_code_ex": "Python · JS · Java\nC++ · Go · Rust\nSQL & more",
        "cat_files": "Files",
        "cat_files_ex": "CSV · JSON · Code\nAI analyzes it",
        "cat_live": "Live Data",
        "cat_live_ex": "Cricket · Stocks\nWeather · News\nAny URL",
        "cat_memory": "Memory",
        "cat_memory_ex": "Remembers you\nAcross sessions\nPersistent DB",
        "img_btn": "🖼️ Image",
        "img_btn_done": "🖼️ ✓",
        "file_btn": "📄 File",
        "file_btn_done": "📄 ✓",
        "help_btn": "❓ Help",
        "settings": "⚙️ Model Settings",
        "temperature": "Temperature",
        "max_length": "Max Length",
        "ai_mode": "🎭 AI Mode",
        "quick_tools": "🛠️ Quick Tools",
        "currency": "💱 Currency",
        "units": "📐 Units",
        "calculator": "🔢 Calculator",
        "qr_code": "📱 QR Code",
        "export": "💾 Export",
        "no_msgs": "No messages yet.",
        "convert_btn": "Convert 💱",
        "calc_btn": "Calculate 🔢",
        "unit_btn": "Convert 📐",
        "qr_btn": "Generate QR",
        "download_md": "📝 MD",
        "download_json": "📊 JSON",
        "img_upload_title": "👁️ Upload Image for Vision AI",
        "img_upload_hint": "Supports: JPG, PNG, GIF, BMP, WebP, TIFF",
        "file_upload_title": "📁 Upload File for Analysis",
        "file_upload_hint": "Supports: TXT, CSV, JSON, Python, JS, HTML, CSS, Java, C++, Markdown",
        "img_ready": "Ready · Type your question below ↓",
        "file_ready": "Ask me anything about this file",
        "analyzing": "👁️ Analyzing image…",
        "searching": "🔍 Searching…",
        "fetching_weather": "🌤️ Fetching weather…",
        "fetching_stock": "📈 Fetching",
        "fetching_sports": "🏏 Fetching live sports data…",
        "fetching_news": "📰 Fetching news…",
        "fetching_rate": "💱 Fetching rates…",
        "reading_url": "🌐 Reading",
        "running_code": "⚙️ Running",
        "run_btn": "▶ Run",
        "live_preview": "🖥️ Preview",
        "live_game": "🎮 Live Game!",
        "live_app": "🚀 Live App",
        "live_software": "⚙️ Live Software",
        "live_design": "✨ Live Design",
        "download": "⬇️ Download",
        "example_q": "💡 Example questions:",
        "ex1": "What is in this image?",
        "ex2": "Read the text",
        "ex3": "Solve this math",
        "ex4": "Explain this code",
        "ex5": "Analyze this chart",
        "unit_placeholder": "e.g. 100 km to miles",
        "calc_placeholder": "e.g. sqrt(144)",
        "qr_placeholder": "Text or URL",
        "amount": "Amount",
        "from_curr": "From",
        "to_curr": "To",
        "no_results": "No results.",
        "stat_memory": "💾 Persistent Memory",
        "stat_vision": "👁️ Vision AI",
        "stat_sports": "🏏 Live Sports",
        "stat_games": "🎮 Games & Apps",
        "stat_files": "📁 Files & URLs",
        "stat_live": "💱 Live Data",
        "language_label": "🌍 Language",
        "sys_prompt_lang": "Respond in English.",
    },
    "hi": {
        "title": "Soveren",
        "subtitle": "दुनिया का सबसे स्मार्ट AI — छवियां देखता है, ऐप्स बनाता है, सब कुछ लाइव जानता है।",
        "badge": "लाइव · मुफ्त · असीमित · विज़न AI",
        "chat_placeholder": "कुछ भी पूछें — यहाँ टाइप करें या Image / File क्लिक करें…",
        "clear": "🗑️ साफ़ करें",
        "msgs": "संदेश",
        "msgp": "संदेश",
        "hero_q": "आज आप क्या करना चाहेंगे?",
        "cat_vision": "विज़न AI",
        "cat_vision_ex": "कोई भी छवि अपलोड करें\nAI पढ़ता और विश्लेषण करता है",
        "cat_games": "गेम्स",
        "cat_games_ex": "Snake · Tetris\nChess · 2048\nPacman · RPG",
        "cat_apps": "ऐप्स",
        "cat_apps_ex": "Dashboard · Todo\nई-कॉमर्स\nPortfolio",
        "cat_code": "कोड",
        "cat_code_ex": "Python · JS · Java\nC++ · Go · Rust\nSQL और अधिक",
        "cat_files": "फ़ाइलें",
        "cat_files_ex": "CSV · JSON · कोड\nAI विश्लेषण करता है",
        "cat_live": "लाइव डेटा",
        "cat_live_ex": "क्रिकेट · स्टॉक्स\nमौसम · समाचार\nकोई भी URL",
        "cat_memory": "मेमोरी",
        "cat_memory_ex": "आपको याद रखता है\nसत्रों में\nडेटाबेस",
        "img_btn": "🖼️ छवि",
        "img_btn_done": "🖼️ ✓",
        "file_btn": "📄 फ़ाइल",
        "file_btn_done": "📄 ✓",
        "help_btn": "❓ सहायता",
        "settings": "⚙️ मॉडल सेटिंग",
        "temperature": "तापमान",
        "max_length": "अधिकतम लंबाई",
        "ai_mode": "🎭 AI मोड",
        "quick_tools": "🛠️ त्वरित टूल्स",
        "currency": "💱 मुद्रा",
        "units": "📐 इकाई",
        "calculator": "🔢 कैलकुलेटर",
        "qr_code": "📱 QR कोड",
        "export": "💾 निर्यात",
        "no_msgs": "अभी कोई संदेश नहीं।",
        "convert_btn": "कन्वर्ट करें 💱",
        "calc_btn": "गणना करें 🔢",
        "unit_btn": "कन्वर्ट करें 📐",
        "qr_btn": "QR बनाएं",
        "download_md": "📝 MD",
        "download_json": "📊 JSON",
        "img_upload_title": "👁️ विज़न AI के लिए छवि अपलोड करें",
        "img_upload_hint": "समर्थित: JPG, PNG, GIF, BMP, WebP, TIFF",
        "file_upload_title": "📁 विश्लेषण के लिए फ़ाइल अपलोड करें",
        "file_upload_hint": "समर्थित: TXT, CSV, JSON, Python, JS, HTML, CSS, Java, C++, Markdown",
        "img_ready": "तैयार · नीचे अपना प्रश्न टाइप करें ↓",
        "file_ready": "इस फ़ाइल के बारे में कुछ भी पूछें",
        "analyzing": "👁️ छवि का विश्लेषण हो रहा है…",
        "searching": "🔍 खोज रहे हैं…",
        "fetching_weather": "🌤️ मौसम जानकारी ला रहे हैं…",
        "fetching_stock": "📈 डेटा ला रहे हैं",
        "fetching_sports": "🏏 लाइव स्पोर्ट्स डेटा ला रहे हैं…",
        "fetching_news": "📰 समाचार ला रहे हैं…",
        "fetching_rate": "💱 विनिमय दर ला रहे हैं…",
        "reading_url": "🌐 पढ़ रहे हैं",
        "running_code": "⚙️ चला रहे हैं",
        "run_btn": "▶ चलाएं",
        "live_preview": "🖥️ प्रीव्यू",
        "live_game": "🎮 लाइव गेम!",
        "live_app": "🚀 लाइव ऐप",
        "live_software": "⚙️ लाइव सॉफ्टवेयर",
        "live_design": "✨ लाइव डिज़ाइन",
        "download": "⬇️ डाउनलोड",
        "example_q": "💡 उदाहरण प्रश्न:",
        "ex1": "इस छवि में क्या है?",
        "ex2": "टेक्स्ट पढ़ें",
        "ex3": "यह गणित हल करें",
        "ex4": "यह कोड समझाएं",
        "ex5": "यह चार्ट विश्लेषण करें",
        "unit_placeholder": "जैसे: 100 किमी से मील",
        "calc_placeholder": "जैसे: sqrt(144)",
        "qr_placeholder": "टेक्स्ट या URL",
        "amount": "राशि",
        "from_curr": "से",
        "to_curr": "में",
        "no_results": "कोई परिणाम नहीं।",
        "stat_memory": "💾 स्थायी मेमोरी",
        "stat_vision": "👁️ विज़न AI",
        "stat_sports": "🏏 लाइव स्पोर्ट्स",
        "stat_games": "🎮 गेम्स और ऐप्स",
        "stat_files": "📁 फ़ाइलें और URLs",
        "stat_live": "💱 लाइव डेटा",
        "language_label": "🌍 भाषा",
        "sys_prompt_lang": "हिंदी में उत्तर दें।",
    },
    "bn": {
        "title": "Soveren",
        "subtitle": "বিশ্বের সবচেয়ে স্মার্ট AI — ছবি দেখে, অ্যাপ তৈরি করে, সব লাইভ জানে।",
        "badge": "লাইভ · বিনামূল্যে · সীমাহীন · ভিশন AI",
        "chat_placeholder": "যেকোনো কিছু জিজ্ঞাসা করুন — এখানে টাইপ করুন বা উপরে 🖼️ ছবি / 📄 ফাইল ক্লিক করুন…",
        "clear": "🗑️ মুছুন",
        "msgs": "বার্তা",
        "msgp": "বার্তা",
        "hero_q": "আজ আপনি কী করতে চান?",
        "cat_vision": "ভিশন AI",
        "cat_vision_ex": "যেকোনো ছবি আপলোড করুন\nAI পড়ে ও বিশ্লেষণ করে",
        "cat_games": "গেমস",
        "cat_games_ex": "Snake · Tetris\nChess · 2048\nPacman · RPG",
        "cat_apps": "অ্যাপস",
        "cat_apps_ex": "Dashboard · Todo\nই-কমার্স\nPortfolio",
        "cat_code": "কোড",
        "cat_code_ex": "Python · JS · Java\nC++ · Go · Rust\nSQL এবং আরও",
        "cat_files": "ফাইলস",
        "cat_files_ex": "CSV · JSON · কোড\nAI বিশ্লেষণ করে",
        "cat_live": "লাইভ ডেটা",
        "cat_live_ex": "ক্রিকেট · শেয়ার\nআবহাওয়া · সংবাদ\nযেকোনো URL",
        "cat_memory": "মেমোরি",
        "cat_memory_ex": "আপনাকে মনে রাখে\nসেশন জুড়ে\nডেটাবেস",
        "img_btn": "🖼️ ছবি",
        "img_btn_done": "🖼️ ✓",
        "file_btn": "📄 ফাইল",
        "file_btn_done": "📄 ✓",
        "help_btn": "❓ সাহায্য",
        "settings": "⚙️ মডেল সেটিংস",
        "temperature": "তাপমাত্রা",
        "max_length": "সর্বোচ্চ দৈর্ঘ্য",
        "ai_mode": "🎭 AI মোড",
        "quick_tools": "🛠️ দ্রুত সরঞ্জাম",
        "currency": "💱 মুদ্রা",
        "units": "📐 একক",
        "calculator": "🔢 ক্যালকুলেটর",
        "qr_code": "📱 QR কোড",
        "export": "💾 রপ্তানি",
        "no_msgs": "এখনো কোনো বার্তা নেই।",
        "convert_btn": "রূপান্তর করুন 💱",
        "calc_btn": "গণনা করুন 🔢",
        "unit_btn": "রূপান্তর করুন 📐",
        "qr_btn": "QR তৈরি করুন",
        "download_md": "📝 MD",
        "download_json": "📊 JSON",
        "img_upload_title": "👁️ ভিশন AI-এর জন্য ছবি আপলোড করুন",
        "img_upload_hint": "সমর্থিত: JPG, PNG, GIF, BMP, WebP, TIFF",
        "file_upload_title": "📁 বিশ্লেষণের জন্য ফাইল আপলোড করুন",
        "file_upload_hint": "সমর্থিত: TXT, CSV, JSON, Python, JS, HTML, CSS, Java, C++, Markdown",
        "img_ready": "প্রস্তুত · নিচে আপনার প্রশ্ন টাইপ করুন ↓",
        "file_ready": "এই ফাইল সম্পর্কে যেকোনো কিছু জিজ্ঞাসা করুন",
        "analyzing": "👁️ ছবি বিশ্লেষণ হচ্ছে…",
        "searching": "🔍 অনুসন্ধান হচ্ছে…",
        "fetching_weather": "🌤️ আবহাওয়া আনা হচ্ছে…",
        "fetching_stock": "📈 ডেটা আনা হচ্ছে",
        "fetching_sports": "🏏 লাইভ স্পোর্টস ডেটা আনা হচ্ছে…",
        "fetching_news": "📰 সংবাদ আনা হচ্ছে…",
        "fetching_rate": "💱 বিনিময় হার আনা হচ্ছে…",
        "reading_url": "🌐 পড়া হচ্ছে",
        "running_code": "⚙️ চালানো হচ্ছে",
        "run_btn": "▶ চালান",
        "live_preview": "🖥️ প্রিভিউ",
        "live_game": "🎮 লাইভ গেম!",
        "live_app": "🚀 লাইভ অ্যাপ",
        "live_software": "⚙️ লাইভ সফটওয়্যার",
        "live_design": "✨ লাইভ ডিজাইন",
        "download": "⬇️ ডাউনলোড",
        "example_q": "💡 উদাহরণ প্রশ্ন:",
        "ex1": "এই ছবিতে কী আছে?",
        "ex2": "টেক্সট পড়ুন",
        "ex3": "এই গণিত সমাধান করুন",
        "ex4": "এই কোড বুঝিয়ে দিন",
        "ex5": "এই চার্ট বিশ্লেষণ করুন",
        "unit_placeholder": "যেমন: ১০০ কিমি থেকে মাইল",
        "calc_placeholder": "যেমন: sqrt(144)",
        "qr_placeholder": "টেক্সট বা URL",
        "amount": "পরিমাণ",
        "from_curr": "থেকে",
        "to_curr": "তে",
        "no_results": "কোনো ফলাফল নেই।",
        "stat_memory": "💾 স্থায়ী মেমোরি",
        "stat_vision": "👁️ ভিশন AI",
        "stat_sports": "🏏 লাইভ স্পোর্টস",
        "stat_games": "🎮 গেমস ও অ্যাপস",
        "stat_files": "📁 ফাইলস ও URLs",
        "stat_live": "💱 লাইভ ডেটা",
        "language_label": "🌍 ভাষা",
        "sys_prompt_lang": "বাংলায় উত্তর দিন।",
    },
    "es": {
        "title": "Soveren",
        "subtitle": "La IA más inteligente del mundo — ve imágenes, crea apps, sabe todo en vivo.",
        "badge": "EN VIVO · GRATIS · ILIMITADO · IA DE VISIÓN",
        "chat_placeholder": "Pregunta lo que quieras — escribe aquí o haz clic en 🖼️ Imagen / 📄 Archivo…",
        "clear": "🗑️ Borrar",
        "msgs": "mensaje", "msgp": "mensajes",
        "hero_q": "¿Qué quieres hacer hoy?",
        "cat_vision": "IA de Visión", "cat_vision_ex": "Sube cualquier imagen\nIA lee y analiza",
        "cat_games": "Juegos", "cat_games_ex": "Snake · Tetris\nAjedrez · 2048\nPacman · RPG",
        "cat_apps": "Aplicaciones", "cat_apps_ex": "Dashboard · Todo\nE-commerce\nPortfolio",
        "cat_code": "Código", "cat_code_ex": "Python · JS · Java\nC++ · Go · Rust\nSQL y más",
        "cat_files": "Archivos", "cat_files_ex": "CSV · JSON · Código\nIA lo analiza",
        "cat_live": "Datos en Vivo", "cat_live_ex": "Cricket · Bolsa\nClima · Noticias\nCualquier URL",
        "cat_memory": "Memoria", "cat_memory_ex": "Te recuerda\nEntre sesiones\nBase de datos",
        "img_btn": "🖼️ Imagen", "img_btn_done": "🖼️ ✓",
        "file_btn": "📄 Archivo", "file_btn_done": "📄 ✓",
        "help_btn": "❓ Ayuda", "settings": "⚙️ Ajustes",
        "temperature": "Temperatura", "max_length": "Longitud máx.",
        "ai_mode": "🎭 Modo IA", "quick_tools": "🛠️ Herramientas",
        "currency": "💱 Divisa", "units": "📐 Unidades",
        "calculator": "🔢 Calculadora", "qr_code": "📱 Código QR", "export": "💾 Exportar",
        "no_msgs": "Aún no hay mensajes.",
        "convert_btn": "Convertir 💱", "calc_btn": "Calcular 🔢", "unit_btn": "Convertir 📐",
        "qr_btn": "Generar QR", "download_md": "📝 MD", "download_json": "📊 JSON",
        "img_upload_title": "👁️ Subir imagen para IA de Visión",
        "img_upload_hint": "Soporta: JPG, PNG, GIF, BMP, WebP, TIFF",
        "file_upload_title": "📁 Subir archivo para análisis",
        "file_upload_hint": "Soporta: TXT, CSV, JSON, Python, JS, HTML, CSS, Java, C++, Markdown",
        "img_ready": "Listo · Escribe tu pregunta abajo ↓",
        "file_ready": "Pregúntame sobre este archivo",
        "analyzing": "👁️ Analizando imagen…", "searching": "🔍 Buscando…",
        "fetching_weather": "🌤️ Obteniendo clima…", "fetching_stock": "📈 Obteniendo",
        "fetching_sports": "🏏 Obteniendo datos deportivos…",
        "fetching_news": "📰 Obteniendo noticias…", "fetching_rate": "💱 Obteniendo tasas…",
        "reading_url": "🌐 Leyendo", "running_code": "⚙️ Ejecutando", "run_btn": "▶ Ejecutar",
        "live_preview": "🖥️ Vista previa", "live_game": "🎮 ¡Juego en Vivo!",
        "live_app": "🚀 App en Vivo", "live_software": "⚙️ Software en Vivo",
        "live_design": "✨ Diseño en Vivo", "download": "⬇️ Descargar",
        "example_q": "💡 Ejemplos:",
        "ex1": "¿Qué hay en esta imagen?", "ex2": "Lee el texto",
        "ex3": "Resuelve esta matemática", "ex4": "Explica este código",
        "ex5": "Analiza este gráfico",
        "unit_placeholder": "ej. 100 km a millas", "calc_placeholder": "ej. sqrt(144)",
        "qr_placeholder": "Texto o URL", "amount": "Cantidad", "from_curr": "De", "to_curr": "A",
        "no_results": "Sin resultados.",
        "stat_memory": "💾 Memoria Persistente", "stat_vision": "👁️ Visión IA",
        "stat_sports": "🏏 Deportes", "stat_games": "🎮 Juegos y Apps",
        "stat_files": "📁 Archivos y URLs", "stat_live": "💱 Datos en Vivo",
        "language_label": "🌍 Idioma", "sys_prompt_lang": "Responde en español.",
    },
    "fr": {
        "title": "Soveren",
        "subtitle": "L'IA la plus intelligente au monde — voit des images, crée des apps, sait tout en direct.",
        "badge": "EN DIRECT · GRATUIT · ILLIMITÉ · IA VISION",
        "chat_placeholder": "Demandez n'importe quoi — tapez ici ou cliquez sur 🖼️ Image / 📄 Fichier…",
        "clear": "🗑️ Effacer", "msgs": "message", "msgp": "messages",
        "hero_q": "Que souhaitez-vous faire aujourd'hui ?",
        "cat_vision": "IA Vision", "cat_vision_ex": "Téléchargez une image\nL'IA lit et analyse",
        "cat_games": "Jeux", "cat_games_ex": "Snake · Tetris\nÉchecs · 2048\nPacman · RPG",
        "cat_apps": "Applications", "cat_apps_ex": "Dashboard · Todo\nE-commerce\nPortfolio",
        "cat_code": "Code", "cat_code_ex": "Python · JS · Java\nC++ · Go · Rust\nSQL et plus",
        "cat_files": "Fichiers", "cat_files_ex": "CSV · JSON · Code\nL'IA analyse",
        "cat_live": "Données Live", "cat_live_ex": "Cricket · Bourse\nMétéo · Actualités\nn'importe quel URL",
        "cat_memory": "Mémoire", "cat_memory_ex": "Se souvient de vous\nEntre sessions\nBase de données",
        "img_btn": "🖼️ Image", "img_btn_done": "🖼️ ✓",
        "file_btn": "📄 Fichier", "file_btn_done": "📄 ✓",
        "help_btn": "❓ Aide", "settings": "⚙️ Paramètres",
        "temperature": "Température", "max_length": "Longueur max.",
        "ai_mode": "🎭 Mode IA", "quick_tools": "🛠️ Outils rapides",
        "currency": "💱 Devise", "units": "📐 Unités",
        "calculator": "🔢 Calculatrice", "qr_code": "📱 Code QR", "export": "💾 Exporter",
        "no_msgs": "Pas encore de messages.",
        "convert_btn": "Convertir 💱", "calc_btn": "Calculer 🔢", "unit_btn": "Convertir 📐",
        "qr_btn": "Générer QR", "download_md": "📝 MD", "download_json": "📊 JSON",
        "img_upload_title": "👁️ Télécharger une image pour l'IA Vision",
        "img_upload_hint": "Supporté: JPG, PNG, GIF, BMP, WebP, TIFF",
        "file_upload_title": "📁 Télécharger un fichier pour analyse",
        "file_upload_hint": "Supporté: TXT, CSV, JSON, Python, JS, HTML, CSS, Java, C++, Markdown",
        "img_ready": "Prêt · Tapez votre question ci-dessous ↓",
        "file_ready": "Posez-moi n'importe quelle question sur ce fichier",
        "analyzing": "👁️ Analyse de l'image…", "searching": "🔍 Recherche…",
        "fetching_weather": "🌤️ Récupération météo…", "fetching_stock": "📈 Récupération",
        "fetching_sports": "🏏 Récupération des données sportives…",
        "fetching_news": "📰 Récupération des actualités…", "fetching_rate": "💱 Récupération des taux…",
        "reading_url": "🌐 Lecture de", "running_code": "⚙️ Exécution", "run_btn": "▶ Exécuter",
        "live_preview": "🖥️ Aperçu", "live_game": "🎮 Jeu en Direct!",
        "live_app": "🚀 App en Direct", "live_software": "⚙️ Logiciel en Direct",
        "live_design": "✨ Design en Direct", "download": "⬇️ Télécharger",
        "example_q": "💡 Exemples de questions:",
        "ex1": "Qu'y a-t-il dans cette image ?", "ex2": "Lire le texte",
        "ex3": "Résoudre ce problème", "ex4": "Expliquer ce code", "ex5": "Analyser ce graphique",
        "unit_placeholder": "ex. 100 km en miles", "calc_placeholder": "ex. sqrt(144)",
        "qr_placeholder": "Texte ou URL", "amount": "Montant", "from_curr": "De", "to_curr": "Vers",
        "no_results": "Aucun résultat.",
        "stat_memory": "💾 Mémoire Persistante", "stat_vision": "👁️ Vision IA",
        "stat_sports": "🏏 Sports Live", "stat_games": "🎮 Jeux et Apps",
        "stat_files": "📁 Fichiers et URLs", "stat_live": "💱 Données Live",
        "language_label": "🌍 Langue", "sys_prompt_lang": "Répondez en français.",
    },
    "de": {
        "title": "Soveren",
        "subtitle": "Die klügste KI der Welt — sieht Bilder, baut Apps, weiß alles live.",
        "badge": "LIVE · KOSTENLOS · UNBEGRENZT · VISION KI",
        "chat_placeholder": "Frag alles — hier tippen oder oben auf 🖼️ Bild / 📄 Datei klicken…",
        "clear": "🗑️ Löschen", "msgs": "Nachricht", "msgp": "Nachrichten",
        "hero_q": "Was möchten Sie heute tun?",
        "cat_vision": "Vision KI", "cat_vision_ex": "Bild hochladen\nKI liest und analysiert",
        "cat_games": "Spiele", "cat_games_ex": "Snake · Tetris\nSchach · 2048\nPacman · RPG",
        "cat_apps": "Apps", "cat_apps_ex": "Dashboard · Todo\nE-Commerce\nPortfolio",
        "cat_code": "Code", "cat_code_ex": "Python · JS · Java\nC++ · Go · Rust\nSQL und mehr",
        "cat_files": "Dateien", "cat_files_ex": "CSV · JSON · Code\nKI analysiert",
        "cat_live": "Live-Daten", "cat_live_ex": "Cricket · Aktien\nWetter · Nachrichten\nJede URL",
        "cat_memory": "Gedächtnis", "cat_memory_ex": "Erinnert sich\nSitzungsübergreifend\nDatenbank",
        "img_btn": "🖼️ Bild", "img_btn_done": "🖼️ ✓",
        "file_btn": "📄 Datei", "file_btn_done": "📄 ✓",
        "help_btn": "❓ Hilfe", "settings": "⚙️ Modelleinstellungen",
        "temperature": "Temperatur", "max_length": "Max. Länge",
        "ai_mode": "🎭 KI-Modus", "quick_tools": "🛠️ Schnellwerkzeuge",
        "currency": "💱 Währung", "units": "📐 Einheiten",
        "calculator": "🔢 Rechner", "qr_code": "📱 QR-Code", "export": "💾 Exportieren",
        "no_msgs": "Noch keine Nachrichten.",
        "convert_btn": "Umrechnen 💱", "calc_btn": "Berechnen 🔢", "unit_btn": "Umrechnen 📐",
        "qr_btn": "QR erstellen", "download_md": "📝 MD", "download_json": "📊 JSON",
        "img_upload_title": "👁️ Bild für Vision KI hochladen",
        "img_upload_hint": "Unterstützt: JPG, PNG, GIF, BMP, WebP, TIFF",
        "file_upload_title": "📁 Datei zur Analyse hochladen",
        "file_upload_hint": "Unterstützt: TXT, CSV, JSON, Python, JS, HTML, CSS, Java, C++, Markdown",
        "img_ready": "Bereit · Frage unten eingeben ↓",
        "file_ready": "Stell mir Fragen zu dieser Datei",
        "analyzing": "👁️ Bild wird analysiert…", "searching": "🔍 Suche läuft…",
        "fetching_weather": "🌤️ Wetter wird abgerufen…", "fetching_stock": "📈 Daten werden abgerufen",
        "fetching_sports": "🏏 Live-Sportdaten werden abgerufen…",
        "fetching_news": "📰 Nachrichten werden abgerufen…", "fetching_rate": "💱 Kurse werden abgerufen…",
        "reading_url": "🌐 Lesen von", "running_code": "⚙️ Ausführen", "run_btn": "▶ Ausführen",
        "live_preview": "🖥️ Vorschau", "live_game": "🎮 Live-Spiel!",
        "live_app": "🚀 Live-App", "live_software": "⚙️ Live-Software",
        "live_design": "✨ Live-Design", "download": "⬇️ Herunterladen",
        "example_q": "💡 Beispielfragen:",
        "ex1": "Was ist auf diesem Bild?", "ex2": "Text lesen",
        "ex3": "Diese Mathe lösen", "ex4": "Diesen Code erklären", "ex5": "Dieses Diagramm analysieren",
        "unit_placeholder": "z.B. 100 km in Meilen", "calc_placeholder": "z.B. sqrt(144)",
        "qr_placeholder": "Text oder URL", "amount": "Betrag", "from_curr": "Von", "to_curr": "Nach",
        "no_results": "Keine Ergebnisse.",
        "stat_memory": "💾 Persistentes Gedächtnis", "stat_vision": "👁️ Vision KI",
        "stat_sports": "🏏 Live-Sport", "stat_games": "🎮 Spiele & Apps",
        "stat_files": "📁 Dateien & URLs", "stat_live": "💱 Live-Daten",
        "language_label": "🌍 Sprache", "sys_prompt_lang": "Antworten Sie auf Deutsch.",
    },
    "ja": {
        "title": "Soveren",
        "subtitle": "世界最高の AI — 画像を見て、アプリを作り、すべてをリアルタイムで知っています。",
        "badge": "ライブ · 無料 · 無制限 · ビジョン AI",
        "chat_placeholder": "何でも聞いてください — ここに入力するか 🖼️ 画像 / 📄 ファイルをクリック…",
        "clear": "🗑️ クリア", "msgs": "メッセージ", "msgp": "メッセージ",
        "hero_q": "今日は何をしたいですか？",
        "cat_vision": "ビジョン AI", "cat_vision_ex": "画像をアップロード\nAI が読み取り分析",
        "cat_games": "ゲーム", "cat_games_ex": "Snake · Tetris\nChess · 2048\nPacman · RPG",
        "cat_apps": "アプリ", "cat_apps_ex": "Dashboard · Todo\nE コマース\nPortfolio",
        "cat_code": "コード", "cat_code_ex": "Python · JS · Java\nC++ · Go · Rust\nSQL など",
        "cat_files": "ファイル", "cat_files_ex": "CSV · JSON · コード\nAI が分析",
        "cat_live": "ライブデータ", "cat_live_ex": "クリケット · 株価\n天気 · ニュース\nどんな URL",
        "cat_memory": "メモリ", "cat_memory_ex": "あなたを覚えている\nセッション間\nデータベース",
        "img_btn": "🖼️ 画像", "img_btn_done": "🖼️ ✓",
        "file_btn": "📄 ファイル", "file_btn_done": "📄 ✓",
        "help_btn": "❓ ヘルプ", "settings": "⚙️ モデル設定",
        "temperature": "温度", "max_length": "最大長",
        "ai_mode": "🎭 AI モード", "quick_tools": "🛠️ クイックツール",
        "currency": "💱 通貨", "units": "📐 単位",
        "calculator": "🔢 計算機", "qr_code": "📱 QR コード", "export": "💾 エクスポート",
        "no_msgs": "まだメッセージはありません。",
        "convert_btn": "変換 💱", "calc_btn": "計算 🔢", "unit_btn": "変換 📐",
        "qr_btn": "QR 生成", "download_md": "📝 MD", "download_json": "📊 JSON",
        "img_upload_title": "👁️ ビジョン AI 用に画像をアップロード",
        "img_upload_hint": "対応: JPG, PNG, GIF, BMP, WebP, TIFF",
        "file_upload_title": "📁 分析用ファイルをアップロード",
        "file_upload_hint": "対応: TXT, CSV, JSON, Python, JS, HTML, CSS, Java, C++, Markdown",
        "img_ready": "準備完了 · 下に質問を入力 ↓",
        "file_ready": "このファイルについて何でも聞いてください",
        "analyzing": "👁️ 画像を分析中…", "searching": "🔍 検索中…",
        "fetching_weather": "🌤️ 天気を取得中…", "fetching_stock": "📈 データを取得中",
        "fetching_sports": "🏏 スポーツデータを取得中…",
        "fetching_news": "📰 ニュースを取得中…", "fetching_rate": "💱 レートを取得中…",
        "reading_url": "🌐 読み込み中", "running_code": "⚙️ 実行中", "run_btn": "▶ 実行",
        "live_preview": "🖥️ プレビュー", "live_game": "🎮 ライブゲーム!",
        "live_app": "🚀 ライブアプリ", "live_software": "⚙️ ライブソフトウェア",
        "live_design": "✨ ライブデザイン", "download": "⬇️ ダウンロード",
        "example_q": "💡 例の質問:",
        "ex1": "この画像には何がありますか？", "ex2": "テキストを読む",
        "ex3": "この数学を解く", "ex4": "このコードを説明する", "ex5": "このグラフを分析する",
        "unit_placeholder": "例: 100 km to miles", "calc_placeholder": "例: sqrt(144)",
        "qr_placeholder": "テキストまたは URL", "amount": "金額", "from_curr": "から", "to_curr": "へ",
        "no_results": "結果なし。",
        "stat_memory": "💾 永続メモリ", "stat_vision": "👁️ ビジョン AI",
        "stat_sports": "🏏 ライブスポーツ", "stat_games": "🎮 ゲームとアプリ",
        "stat_files": "📁 ファイルと URL", "stat_live": "💱 ライブデータ",
        "language_label": "🌍 言語", "sys_prompt_lang": "日本語で答えてください。",
    },
    "zh": {
        "title": "Soveren",
        "subtitle": "世界上最聪明的 AI — 看图像、构建应用、实时了解一切。",
        "badge": "实时 · 免费 · 无限 · 视觉 AI",
        "chat_placeholder": "问任何问题 — 在此输入或点击上方 🖼️ 图像 / 📄 文件…",
        "clear": "🗑️ 清除", "msgs": "条消息", "msgp": "条消息",
        "hero_q": "您今天想做什么？",
        "cat_vision": "视觉 AI", "cat_vision_ex": "上传任何图像\nAI 读取并分析",
        "cat_games": "游戏", "cat_games_ex": "贪吃蛇 · 俄罗斯方块\n国际象棋 · 2048\nPacman · RPG",
        "cat_apps": "应用", "cat_apps_ex": "仪表板 · 待办\n电子商务\n作品集",
        "cat_code": "代码", "cat_code_ex": "Python · JS · Java\nC++ · Go · Rust\nSQL 等",
        "cat_files": "文件", "cat_files_ex": "CSV · JSON · 代码\nAI 分析",
        "cat_live": "实时数据", "cat_live_ex": "板球 · 股票\n天气 · 新闻\n任何 URL",
        "cat_memory": "记忆", "cat_memory_ex": "记住您\n跨会话\n数据库",
        "img_btn": "🖼️ 图像", "img_btn_done": "🖼️ ✓",
        "file_btn": "📄 文件", "file_btn_done": "📄 ✓",
        "help_btn": "❓ 帮助", "settings": "⚙️ 模型设置",
        "temperature": "温度", "max_length": "最大长度",
        "ai_mode": "🎭 AI 模式", "quick_tools": "🛠️ 快速工具",
        "currency": "💱 货币", "units": "📐 单位",
        "calculator": "🔢 计算器", "qr_code": "📱 二维码", "export": "💾 导出",
        "no_msgs": "暂无消息。",
        "convert_btn": "转换 💱", "calc_btn": "计算 🔢", "unit_btn": "转换 📐",
        "qr_btn": "生成二维码", "download_md": "📝 MD", "download_json": "📊 JSON",
        "img_upload_title": "👁️ 上传图像以供视觉 AI 分析",
        "img_upload_hint": "支持: JPG, PNG, GIF, BMP, WebP, TIFF",
        "file_upload_title": "📁 上传文件进行分析",
        "file_upload_hint": "支持: TXT, CSV, JSON, Python, JS, HTML, CSS, Java, C++, Markdown",
        "img_ready": "准备就绪 · 在下方输入问题 ↓",
        "file_ready": "请询问关于此文件的任何问题",
        "analyzing": "👁️ 正在分析图像…", "searching": "🔍 正在搜索…",
        "fetching_weather": "🌤️ 正在获取天气…", "fetching_stock": "📈 正在获取",
        "fetching_sports": "🏏 正在获取实时体育数据…",
        "fetching_news": "📰 正在获取新闻…", "fetching_rate": "💱 正在获取汇率…",
        "reading_url": "🌐 正在读取", "running_code": "⚙️ 正在运行", "run_btn": "▶ 运行",
        "live_preview": "🖥️ 预览", "live_game": "🎮 实时游戏!",
        "live_app": "🚀 实时应用", "live_software": "⚙️ 实时软件",
        "live_design": "✨ 实时设计", "download": "⬇️ 下载",
        "example_q": "💡 示例问题：",
        "ex1": "这张图片里有什么？", "ex2": "读取文字",
        "ex3": "解这道数学题", "ex4": "解释这段代码", "ex5": "分析这个图表",
        "unit_placeholder": "例：100 公里转英里", "calc_placeholder": "例：sqrt(144)",
        "qr_placeholder": "文本或 URL", "amount": "金额", "from_curr": "从", "to_curr": "到",
        "no_results": "无结果。",
        "stat_memory": "💾 持久记忆", "stat_vision": "👁️ 视觉 AI",
        "stat_sports": "🏏 实时体育", "stat_games": "🎮 游戏和应用",
        "stat_files": "📁 文件和 URL", "stat_live": "💱 实时数据",
        "language_label": "🌍 语言", "sys_prompt_lang": "请用中文回答。",
    },
    "ar": {
        "title": "Soveren",
        "subtitle": "أذكى ذكاء اصطناعي في العالم — يرى الصور، يبني التطبيقات، يعرف كل شيء مباشرة.",
        "badge": "مباشر · مجاني · غير محدود · رؤية AI",
        "chat_placeholder": "اسأل أي شيء — اكتب هنا أو انقر على 🖼️ صورة / 📄 ملف…",
        "clear": "🗑️ مسح", "msgs": "رسالة", "msgp": "رسائل",
        "hero_q": "ماذا تريد أن تفعل اليوم؟",
        "cat_vision": "رؤية AI", "cat_vision_ex": "ارفع أي صورة\nالذكاء الاصطناعي يقرأ ويحلل",
        "cat_games": "ألعاب", "cat_games_ex": "Snake · Tetris\n2048 · شطرنج\nPacman · RPG",
        "cat_apps": "تطبيقات", "cat_apps_ex": "لوحة تحكم · مهام\nتجارة إلكترونية\nمحفظة",
        "cat_code": "كود", "cat_code_ex": "Python · JS · Java\nC++ · Go · Rust\nSQL وأكثر",
        "cat_files": "ملفات", "cat_files_ex": "CSV · JSON · كود\nيحللها الذكاء الاصطناعي",
        "cat_live": "بيانات مباشرة", "cat_live_ex": "كريكيت · أسهم\nطقس · أخبار\nأي URL",
        "cat_memory": "ذاكرة", "cat_memory_ex": "يتذكرك\nعبر الجلسات\nقاعدة بيانات",
        "img_btn": "🖼️ صورة", "img_btn_done": "🖼️ ✓",
        "file_btn": "📄 ملف", "file_btn_done": "📄 ✓",
        "help_btn": "❓ مساعدة", "settings": "⚙️ إعدادات النموذج",
        "temperature": "الحرارة", "max_length": "الطول الأقصى",
        "ai_mode": "🎭 وضع AI", "quick_tools": "🛠️ أدوات سريعة",
        "currency": "💱 عملة", "units": "📐 وحدات",
        "calculator": "🔢 حاسبة", "qr_code": "📱 رمز QR", "export": "💾 تصدير",
        "no_msgs": "لا توجد رسائل بعد.",
        "convert_btn": "تحويل 💱", "calc_btn": "احسب 🔢", "unit_btn": "تحويل 📐",
        "qr_btn": "إنشاء QR", "download_md": "📝 MD", "download_json": "📊 JSON",
        "img_upload_title": "👁️ ارفع صورة لرؤية AI",
        "img_upload_hint": "مدعوم: JPG, PNG, GIF, BMP, WebP, TIFF",
        "file_upload_title": "📁 ارفع ملف للتحليل",
        "file_upload_hint": "مدعوم: TXT, CSV, JSON, Python, JS, HTML, CSS, Java, C++, Markdown",
        "img_ready": "جاهز · اكتب سؤالك أدناه ↓",
        "file_ready": "اسألني أي شيء عن هذا الملف",
        "analyzing": "👁️ جاري تحليل الصورة…", "searching": "🔍 جاري البحث…",
        "fetching_weather": "🌤️ جاري جلب الطقس…", "fetching_stock": "📈 جاري جلب",
        "fetching_sports": "🏏 جاري جلب بيانات الرياضة…",
        "fetching_news": "📰 جاري جلب الأخبار…", "fetching_rate": "💱 جاري جلب أسعار الصرف…",
        "reading_url": "🌐 جاري قراءة", "running_code": "⚙️ جاري تشغيل", "run_btn": "▶ تشغيل",
        "live_preview": "🖥️ معاينة", "live_game": "🎮 لعبة مباشرة!",
        "live_app": "🚀 تطبيق مباشر", "live_software": "⚙️ برنامج مباشر",
        "live_design": "✨ تصميم مباشر", "download": "⬇️ تحميل",
        "example_q": "💡 أسئلة مثالية:",
        "ex1": "ماذا يوجد في هذه الصورة؟", "ex2": "اقرأ النص",
        "ex3": "حل هذه الرياضيات", "ex4": "اشرح هذا الكود", "ex5": "حلل هذا الرسم البياني",
        "unit_placeholder": "مثال: 100 كم إلى ميل", "calc_placeholder": "مثال: sqrt(144)",
        "qr_placeholder": "نص أو URL", "amount": "المبلغ", "from_curr": "من", "to_curr": "إلى",
        "no_results": "لا توجد نتائج.",
        "stat_memory": "💾 ذاكرة دائمة", "stat_vision": "👁️ رؤية AI",
        "stat_sports": "🏏 رياضة مباشرة", "stat_games": "🎮 ألعاب وتطبيقات",
        "stat_files": "📁 ملفات و URLs", "stat_live": "💱 بيانات مباشرة",
        "language_label": "🌍 اللغة", "sys_prompt_lang": "أجب باللغة العربية.",
    },
    "ru": {
        "title": "Soveren",
        "subtitle": "Самый умный ИИ в мире — видит изображения, создаёт приложения, знает всё в реальном времени.",
        "badge": "LIVE · БЕСПЛАТНО · БЕЗЛИМИТНО · VISION AI",
        "chat_placeholder": "Спросите что угодно — введите здесь или нажмите 🖼️ Изображение / 📄 Файл…",
        "clear": "🗑️ Очистить", "msgs": "сообщение", "msgp": "сообщений",
        "hero_q": "Что вы хотите сделать сегодня?",
        "cat_vision": "Vision ИИ", "cat_vision_ex": "Загрузите любое изображение\nИИ читает и анализирует",
        "cat_games": "Игры", "cat_games_ex": "Змейка · Тетрис\nШахматы · 2048\nPacman · RPG",
        "cat_apps": "Приложения", "cat_apps_ex": "Дашборд · Задачи\nИнтернет-магазин\nПортфолио",
        "cat_code": "Код", "cat_code_ex": "Python · JS · Java\nC++ · Go · Rust\nSQL и другие",
        "cat_files": "Файлы", "cat_files_ex": "CSV · JSON · Код\nИИ анализирует",
        "cat_live": "Живые данные", "cat_live_ex": "Крикет · Акции\nПогода · Новости\nЛюбой URL",
        "cat_memory": "Память", "cat_memory_ex": "Помнит вас\nМежду сессиями\nБаза данных",
        "img_btn": "🖼️ Фото", "img_btn_done": "🖼️ ✓",
        "file_btn": "📄 Файл", "file_btn_done": "📄 ✓",
        "help_btn": "❓ Помощь", "settings": "⚙️ Настройки модели",
        "temperature": "Температура", "max_length": "Макс. длина",
        "ai_mode": "🎭 Режим ИИ", "quick_tools": "🛠️ Быстрые инструменты",
        "currency": "💱 Валюта", "units": "📐 Единицы",
        "calculator": "🔢 Калькулятор", "qr_code": "📱 QR-код", "export": "💾 Экспорт",
        "no_msgs": "Сообщений пока нет.",
        "convert_btn": "Конвертировать 💱", "calc_btn": "Вычислить 🔢", "unit_btn": "Конвертировать 📐",
        "qr_btn": "Создать QR", "download_md": "📝 MD", "download_json": "📊 JSON",
        "img_upload_title": "👁️ Загрузить изображение для Vision ИИ",
        "img_upload_hint": "Поддерживается: JPG, PNG, GIF, BMP, WebP, TIFF",
        "file_upload_title": "📁 Загрузить файл для анализа",
        "file_upload_hint": "Поддерживается: TXT, CSV, JSON, Python, JS, HTML, CSS, Java, C++, Markdown",
        "img_ready": "Готово · Введите вопрос ниже ↓",
        "file_ready": "Задайте любой вопрос об этом файле",
        "analyzing": "👁️ Анализ изображения…", "searching": "🔍 Поиск…",
        "fetching_weather": "🌤️ Загрузка погоды…", "fetching_stock": "📈 Загрузка данных",
        "fetching_sports": "🏏 Загрузка спортивных данных…",
        "fetching_news": "📰 Загрузка новостей…", "fetching_rate": "💱 Загрузка курсов…",
        "reading_url": "🌐 Чтение", "running_code": "⚙️ Выполнение", "run_btn": "▶ Запустить",
        "live_preview": "🖥️ Предпросмотр", "live_game": "🎮 Живая игра!",
        "live_app": "🚀 Живое приложение", "live_software": "⚙️ Живой софт",
        "live_design": "✨ Живой дизайн", "download": "⬇️ Скачать",
        "example_q": "💡 Примеры вопросов:",
        "ex1": "Что на этом изображении?", "ex2": "Прочитать текст",
        "ex3": "Решить эту математику", "ex4": "Объяснить этот код", "ex5": "Проанализировать график",
        "unit_placeholder": "напр. 100 км в мили", "calc_placeholder": "напр. sqrt(144)",
        "qr_placeholder": "Текст или URL", "amount": "Сумма", "from_curr": "Из", "to_curr": "В",
        "no_results": "Нет результатов.",
        "stat_memory": "💾 Постоянная память", "stat_vision": "👁️ Vision ИИ",
        "stat_sports": "🏏 Live спорт", "stat_games": "🎮 Игры и приложения",
        "stat_files": "📁 Файлы и URLs", "stat_live": "💱 Живые данные",
        "language_label": "🌍 Язык", "sys_prompt_lang": "Отвечайте на русском языке.",
    },
    "pt": {
        "title": "Soveren",
        "subtitle": "A IA mais inteligente do mundo — vê imagens, cria apps, sabe tudo ao vivo.",
        "badge": "AO VIVO · GRÁTIS · ILIMITADO · IA DE VISÃO",
        "chat_placeholder": "Pergunte qualquer coisa — digite aqui ou clique em 🖼️ Imagem / 📄 Arquivo…",
        "clear": "🗑️ Limpar", "msgs": "mensagem", "msgp": "mensagens",
        "hero_q": "O que você quer fazer hoje?",
        "cat_vision": "IA de Visão", "cat_vision_ex": "Envie qualquer imagem\nIA lê e analisa",
        "cat_games": "Jogos", "cat_games_ex": "Snake · Tetris\nXadrez · 2048\nPacman · RPG",
        "cat_apps": "Aplicativos", "cat_apps_ex": "Dashboard · Tarefas\nE-commerce\nPortfólio",
        "cat_code": "Código", "cat_code_ex": "Python · JS · Java\nC++ · Go · Rust\nSQL e mais",
        "cat_files": "Arquivos", "cat_files_ex": "CSV · JSON · Código\nIA analisa",
        "cat_live": "Dados ao Vivo", "cat_live_ex": "Críquete · Ações\nClima · Notícias\nQualquer URL",
        "cat_memory": "Memória", "cat_memory_ex": "Lembra de você\nEntre sessões\nBanco de dados",
        "img_btn": "🖼️ Imagem", "img_btn_done": "🖼️ ✓",
        "file_btn": "📄 Arquivo", "file_btn_done": "📄 ✓",
        "help_btn": "❓ Ajuda", "settings": "⚙️ Configurações",
        "temperature": "Temperatura", "max_length": "Comprimento máx.",
        "ai_mode": "🎭 Modo IA", "quick_tools": "🛠️ Ferramentas rápidas",
        "currency": "💱 Moeda", "units": "📐 Unidades",
        "calculator": "🔢 Calculadora", "qr_code": "📱 Código QR", "export": "💾 Exportar",
        "no_msgs": "Ainda não há mensagens.",
        "convert_btn": "Converter 💱", "calc_btn": "Calcular 🔢", "unit_btn": "Converter 📐",
        "qr_btn": "Gerar QR", "download_md": "📝 MD", "download_json": "📊 JSON",
        "img_upload_title": "👁️ Enviar imagem para IA de Visão",
        "img_upload_hint": "Suporta: JPG, PNG, GIF, BMP, WebP, TIFF",
        "file_upload_title": "📁 Enviar arquivo para análise",
        "file_upload_hint": "Suporta: TXT, CSV, JSON, Python, JS, HTML, CSS, Java, C++, Markdown",
        "img_ready": "Pronto · Digite sua pergunta abaixo ↓",
        "file_ready": "Pergunte qualquer coisa sobre este arquivo",
        "analyzing": "👁️ Analisando imagem…", "searching": "🔍 Pesquisando…",
        "fetching_weather": "🌤️ Obtendo clima…", "fetching_stock": "📈 Obtendo",
        "fetching_sports": "🏏 Obtendo dados esportivos…",
        "fetching_news": "📰 Obtendo notícias…", "fetching_rate": "💱 Obtendo taxas…",
        "reading_url": "🌐 Lendo", "running_code": "⚙️ Executando", "run_btn": "▶ Executar",
        "live_preview": "🖥️ Visualização", "live_game": "🎮 Jogo ao Vivo!",
        "live_app": "🚀 App ao Vivo", "live_software": "⚙️ Software ao Vivo",
        "live_design": "✨ Design ao Vivo", "download": "⬇️ Baixar",
        "example_q": "💡 Exemplos de perguntas:",
        "ex1": "O que há nesta imagem?", "ex2": "Ler o texto",
        "ex3": "Resolver esta matemática", "ex4": "Explicar este código", "ex5": "Analisar este gráfico",
        "unit_placeholder": "ex. 100 km para milhas", "calc_placeholder": "ex. sqrt(144)",
        "qr_placeholder": "Texto ou URL", "amount": "Valor", "from_curr": "De", "to_curr": "Para",
        "no_results": "Sem resultados.",
        "stat_memory": "💾 Memória Persistente", "stat_vision": "👁️ Visão IA",
        "stat_sports": "🏏 Esportes ao Vivo", "stat_games": "🎮 Jogos e Apps",
        "stat_files": "📁 Arquivos e URLs", "stat_live": "💱 Dados ao Vivo",
        "language_label": "🌍 Idioma", "sys_prompt_lang": "Responda em português.",
    },
    "ko": {
        "title": "Soveren",
        "subtitle": "세계 최고의 AI — 이미지를 보고, 앱을 만들고, 실시간으로 모든 것을 알고 있습니다.",
        "badge": "실시간 · 무료 · 무제한 · 비전 AI",
        "chat_placeholder": "무엇이든 물어보세요 — 여기 입력하거나 🖼️ 이미지 / 📄 파일 클릭…",
        "clear": "🗑️ 지우기", "msgs": "메시지", "msgp": "메시지",
        "hero_q": "오늘 무엇을 하시겠습니까?",
        "cat_vision": "비전 AI", "cat_vision_ex": "이미지 업로드\nAI 가 읽고 분석",
        "cat_games": "게임", "cat_games_ex": "뱀 · 테트리스\n체스 · 2048\n팩맨 · RPG",
        "cat_apps": "앱", "cat_apps_ex": "대시보드 · 할일\n이커머스\n포트폴리오",
        "cat_code": "코드", "cat_code_ex": "Python · JS · Java\nC++ · Go · Rust\nSQL 등",
        "cat_files": "파일", "cat_files_ex": "CSV · JSON · 코드\nAI 가 분석",
        "cat_live": "실시간 데이터", "cat_live_ex": "크리켓 · 주식\n날씨 · 뉴스\n모든 URL",
        "cat_memory": "메모리", "cat_memory_ex": "당신을 기억합니다\n세션 간\n데이터베이스",
        "img_btn": "🖼️ 이미지", "img_btn_done": "🖼️ ✓",
        "file_btn": "📄 파일", "file_btn_done": "📄 ✓",
        "help_btn": "❓ 도움말", "settings": "⚙️ 모델 설정",
        "temperature": "온도", "max_length": "최대 길이",
        "ai_mode": "🎭 AI 모드", "quick_tools": "🛠️ 빠른 도구",
        "currency": "💱 통화", "units": "📐 단위",
        "calculator": "🔢 계산기", "qr_code": "📱 QR 코드", "export": "💾 내보내기",
        "no_msgs": "아직 메시지가 없습니다.",
        "convert_btn": "변환 💱", "calc_btn": "계산 🔢", "unit_btn": "변환 📐",
        "qr_btn": "QR 생성", "download_md": "📝 MD", "download_json": "📊 JSON",
        "img_upload_title": "👁️ 비전 AI 용 이미지 업로드",
        "img_upload_hint": "지원: JPG, PNG, GIF, BMP, WebP, TIFF",
        "file_upload_title": "📁 분석용 파일 업로드",
        "file_upload_hint": "지원: TXT, CSV, JSON, Python, JS, HTML, CSS, Java, C++, Markdown",
        "img_ready": "준비 완료 · 아래에 질문 입력 ↓",
        "file_ready": "이 파일에 대해 무엇이든 물어보세요",
        "analyzing": "👁️ 이미지 분석 중…", "searching": "🔍 검색 중…",
        "fetching_weather": "🌤️ 날씨 가져오는 중…", "fetching_stock": "📈 데이터 가져오는 중",
        "fetching_sports": "🏏 실시간 스포츠 데이터 가져오는 중…",
        "fetching_news": "📰 뉴스 가져오는 중…", "fetching_rate": "💱 환율 가져오는 중…",
        "reading_url": "🌐 읽는 중", "running_code": "⚙️ 실행 중", "run_btn": "▶ 실행",
        "live_preview": "🖥️ 미리보기", "live_game": "🎮 라이브 게임!",
        "live_app": "🚀 라이브 앱", "live_software": "⚙️ 라이브 소프트웨어",
        "live_design": "✨ 라이브 디자인", "download": "⬇️ 다운로드",
        "example_q": "💡 예시 질문:",
        "ex1": "이 이미지에 무엇이 있나요?", "ex2": "텍스트 읽기",
        "ex3": "이 수학 풀기", "ex4": "이 코드 설명하기", "ex5": "이 차트 분석하기",
        "unit_placeholder": "예: 100 km 를 miles 로", "calc_placeholder": "예: sqrt(144)",
        "qr_placeholder": "텍스트 또는 URL", "amount": "금액", "from_curr": "에서", "to_curr": "로",
        "no_results": "결과 없음.",
        "stat_memory": "💾 영구 메모리", "stat_vision": "👁️ 비전 AI",
        "stat_sports": "🏏 실시간 스포츠", "stat_games": "🎮 게임 및 앱",
        "stat_files": "📁 파일 및 URL", "stat_live": "💱 실시간 데이터",
        "language_label": "🌍 언어", "sys_prompt_lang": "한국어로 답변해 주세요.",
    },
}

def T(key: str) -> str:
    lang_code = st.session_state.get("lang_code", "en")
    return UI_TEXT.get(lang_code, UI_TEXT["en"]).get(key, UI_TEXT["en"].get(key, key))

def is_rtl() -> bool:
    return st.session_state.get("lang_code", "en") == "ar"

st.set_page_config(
    page_title="Soveren",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

rtl_css = """
body, [data-testid="stAppViewContainer"] { direction: rtl !important; text-align: right !important; }
[data-testid="stChatInput"] { direction: rtl !important; }
[data-testid="stSidebar"] { direction: rtl !important; }
""" if is_rtl() else ""

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&family=Noto+Sans+Devanagari:wght@300;400;500;600&family=Noto+Sans+Bengali:wght@300;400;500;600&family=Noto+Sans+Arabic:wght@300;400;500;600&family=Noto+Sans+JP:wght@300;400;500&family=Noto+Sans+KR:wght@300;400;500&family=Noto+Sans+SC:wght@300;400;500&display=swap');
:root {{
    --bg:#0a0c10;--surface:#111318;--surface2:#1a1d24;--border:#232730;
    --accent:#00e5ff;--text:#e2e8f0;--muted:#64748b;--user-bg:#131b2e;
    --green:#10b981;--purple:#7c3aed;--orange:#f59e0b;--red:#ef4444;
    --pink:#ec4899;--radius:14px;
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html,body,[data-testid="stAppViewContainer"]{{background:var(--bg)!important;color:var(--text)!important;font-family:'DM Sans','Noto Sans Devanagari','Noto Sans Bengali','Noto Sans Arabic','Noto Sans JP','Noto Sans KR','Noto Sans SC',sans-serif!important}}
[data-testid="stHeader"],[data-testid="stToolbar"],.stDeployButton,#MainMenu,footer{{display:none!important}}
::-webkit-scrollbar{{width:4px}}::-webkit-scrollbar-track{{background:var(--bg)}}::-webkit-scrollbar-thumb{{background:var(--border);border-radius:4px}}
[data-testid="stAppViewContainer"]>.main>.block-container{{max-width:860px!important;padding:0 1.5rem 10rem!important;margin:0 auto!important}}
[data-testid="stSidebar"]{{background:var(--surface)!important;border-right:1px solid var(--border)!important}}
[data-testid="stSidebar"] *{{color:var(--text)!important}}
[data-testid="stSidebar"] .stSelectbox>div,[data-testid="stSidebar"] .stTextInput>div>div{{background:var(--surface2)!important;border-color:var(--border)!important}}
[data-testid="stSidebar"] label{{color:var(--muted)!important;font-size:12px!important}}
[data-testid="stSidebar"] h3{{color:var(--accent)!important;font-family:'Space Mono',monospace!important;font-size:13px!important;margin:.8rem 0 .4rem!important}}
[data-testid="stSidebar"] hr{{border-color:var(--border)!important}}
[data-testid="stSidebar"] .stButton>button{{width:100%!important;background:var(--surface2)!important;border:1px solid var(--border)!important;color:var(--muted)!important;border-radius:8px!important;font-size:12px!important}}
[data-testid="stSidebar"] .stButton>button:hover{{border-color:var(--accent)!important;color:var(--accent)!important}}
[data-testid="stSidebar"] .stDownloadButton>button{{width:100%!important;background:rgba(0,229,255,.08)!important;border:1px solid rgba(0,229,255,.25)!important;color:var(--accent)!important;border-radius:8px!important;font-size:12px!important}}
[data-testid="stSidebar"] .stExpander{{background:var(--surface2)!important;border:1px solid var(--border)!important;border-radius:10px!important;margin-bottom:.4rem!important}}
.hero{{text-align:center;padding:2.5rem 1rem 1.5rem;position:relative}}
.hero::before{{content:'';position:absolute;top:0;left:50%;transform:translateX(-50%);width:600px;height:300px;background:radial-gradient(ellipse at center,rgba(0,229,255,.07) 0%,transparent 70%);pointer-events:none}}
.hero-badge{{display:inline-flex;align-items:center;gap:6px;background:rgba(0,229,255,.08);border:1px solid rgba(0,229,255,.2);border-radius:999px;padding:4px 14px;font-family:'Space Mono',monospace;font-size:11px;color:var(--accent);letter-spacing:.05em;margin-bottom:1rem}}
.hero-badge::before{{content:'●';font-size:8px;animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
.hero h1{{font-family:'Space Mono',monospace!important;font-size:clamp(1.8rem,4vw,2.6rem)!important;font-weight:700!important;color:#fff!important;line-height:1.15!important;letter-spacing:-.02em;margin-bottom:.5rem!important}}
.hero h1 span{{color:var(--accent)}}
.hero p{{font-size:.95rem;color:var(--muted);font-weight:300;max-width:460px;margin:0 auto}}
.divider{{height:1px;background:linear-gradient(90deg,transparent,var(--border),transparent);margin:1.2rem 0}}
.stats-row{{display:flex;gap:.6rem;margin:1rem 0 1.5rem;justify-content:center;flex-wrap:wrap}}
.stat-pill{{display:flex;align-items:center;gap:6px;background:var(--surface);border:1px solid var(--border);border-radius:999px;padding:5px 12px;font-size:12px;color:var(--muted)}}
.stat-pill .dot{{width:6px;height:6px;border-radius:50%}}
.dot-green{{background:var(--green);box-shadow:0 0 5px var(--green)}}
.dot-blue{{background:var(--accent);box-shadow:0 0 5px var(--accent)}}
.dot-purple{{background:var(--purple);box-shadow:0 0 5px var(--purple)}}
.dot-orange{{background:var(--orange);box-shadow:0 0 5px var(--orange)}}
.dot-pink{{background:var(--pink);box-shadow:0 0 5px var(--pink)}}
[data-testid="stChatMessage"]{{background:transparent!important;border:none!important;padding:0!important}}
[data-testid="stChatMessage"]>div{{background:transparent!important}}
[data-testid="stChatMessageContent"]{{background:transparent!important}}
.stChatMessage{{border-radius:var(--radius)!important;padding:1rem 1.2rem!important;border:1px solid var(--border)!important;margin-bottom:.6rem!important;background:var(--surface)!important;animation:fadeUp .25s ease}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}
.stChatMessage:has([data-testid="chatAvatarIcon-user"]){{background:var(--user-bg)!important;border-color:rgba(0,229,255,.15)!important}}
pre,code{{font-family:'Space Mono',monospace!important;font-size:13px!important}}
pre{{background:#0d1117!important;border:1px solid var(--border)!important;border-left:3px solid var(--accent)!important;border-radius:10px!important;padding:1rem 1.2rem!important;overflow-x:auto!important}}
code:not(pre code){{background:rgba(0,229,255,.08)!important;color:var(--accent)!important;border-radius:5px!important;padding:2px 6px!important;font-size:12.5px!important}}
[data-testid="stChatInputContainer"]{{position:fixed!important;bottom:0!important;left:50%!important;transform:translateX(-50%)!important;width:100%!important;max-width:860px!important;padding:0.5rem 1.5rem 1.2rem!important;background:linear-gradient(to top,var(--bg) 80%,transparent)!important;backdrop-filter:blur(12px);z-index:999!important}}
[data-testid="stChatInput"]{{background:var(--surface2)!important;border:1px solid var(--border)!important;border-radius:12px!important;color:var(--text)!important;font-size:15px!important}}
[data-testid="stChatInput"]:focus{{border-color:var(--accent)!important;box-shadow:0 0 0 3px rgba(0,229,255,.1)!important;outline:none!important}}
[data-testid="stChatInputSubmitButton"] button{{background:var(--accent)!important;border:none!important;border-radius:8px!important;color:#000!important;font-weight:600!important}}
.badge{{display:inline-flex;align-items:center;gap:5px;border-radius:6px;padding:3px 10px;font-size:11px;margin-bottom:.5rem}}
.badge-green{{background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.25);color:var(--green)}}
.badge-red{{background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.3);color:#fca5a5}}
.badge-purple{{background:rgba(124,58,237,.08);border:1px solid rgba(124,58,237,.3);color:#a78bfa}}
.badge-orange{{background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.3);color:var(--orange)}}
.badge-blue{{background:rgba(0,229,255,.08);border:1px solid rgba(0,229,255,.25);color:var(--accent)}}
.badge-pink{{background:rgba(236,72,153,.08);border:1px solid rgba(236,72,153,.3);color:var(--pink)}}
.output-box{{background:#0d1117;border:1px solid var(--border);border-left:3px solid var(--green);border-radius:10px;padding:.8rem 1.2rem;font-family:'Space Mono',monospace;font-size:13px;color:#a3e635;margin-top:.5rem;white-space:pre-wrap}}
.error-box{{background:#1a0a0a;border:1px solid #7f1d1d;border-left:3px solid var(--red);border-radius:10px;padding:.8rem 1.2rem;font-family:'Space Mono',monospace;font-size:13px;color:#fca5a5;margin-top:.5rem;white-space:pre-wrap}}
.result-box{{background:linear-gradient(135deg,#0d1117,#111827);border:1px solid var(--border);border-radius:10px;padding:.8rem 1.2rem;font-size:14px;color:var(--text);margin:.5rem 0}}
.result-box.orange{{border-left:3px solid var(--orange)}}.result-box.green{{border-left:3px solid var(--green)}}
.btn-download{{display:inline-flex;align-items:center;gap:5px;background:rgba(0,229,255,.1);border:1px solid rgba(0,229,255,.3);color:var(--accent);padding:6px 14px;border-radius:8px;text-decoration:none;font-size:12px;font-weight:500;margin-top:.5rem}}
.stButton>button{{background:var(--surface2)!important;border:1px solid var(--border)!important;color:var(--muted)!important;border-radius:8px!important;font-size:13px!important;font-weight:500!important;padding:.4rem 1rem!important;transition:all .2s!important}}
.stButton>button:hover{{border-color:var(--accent)!important;color:var(--accent)!important;background:rgba(0,229,255,.06)!important}}
.category-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:.8rem;margin:1.2rem 0}}
.category-card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1rem;text-align:center;transition:border-color .2s,transform .2s}}
.category-card:hover{{border-color:var(--accent);transform:translateY(-2px)}}
.category-icon{{font-size:1.6rem;margin-bottom:.4rem}}
.category-title{{font-size:12.5px;font-weight:600;color:#94a3b8;margin-bottom:.2rem}}
.category-examples{{font-size:11px;color:var(--muted);line-height:1.6}}
.lang-selector-wrap{{display:flex;align-items:center;gap:8px;background:rgba(0,229,255,.05);border:1px solid rgba(0,229,255,.15);border-radius:12px;padding:8px 12px;margin-bottom:8px}}
.lang-flag{{font-size:18px}}.lang-name{{font-size:13px;color:var(--accent);font-weight:500}}
.memory-card{{background:#111318;border:1px solid #232730;border-radius:8px;padding:8px 10px;margin-bottom:4px}}
.memory-type{{font-size:10px;color:#64748b;text-transform:uppercase}}
.memory-value{{font-size:12px;color:#e2e8f0}}
{rtl_css}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CLIENT
# ══════════════════════════════════════════════════════════════════════════════
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_KEY = "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"

client = Groq(api_key=GROQ_KEY)
MODEL = "llama-3.3-70b-versatile"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
MAX_HISTORY = 20

# ══════════════════════════════════════════════════════════════════════════════
# IMAGE PROCESSING
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
    except:
        return None, None, 0, 0

# ══════════════════════════════════════════════════════════════════════════════
# VISION ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
def get_vision_prompt(user_text: str) -> str:
    q = user_text.lower()
    if any(k in q for k in ["read","text","ocr","extract text","what does it say","what text","words","written","transcribe"]):
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
    placeholder = st.empty()
    full = ""
    lang_instruction = T("sys_prompt_lang")
    try:
        stream = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {"role":"system","content":(
                    f"You are Soveren with powerful vision. Created by Samiran. "
                    f"Analyze images with exceptional detail and accuracy. "
                    f"Read text perfectly (OCR), identify objects, solve problems, "
                    f"analyze data, review code, and answer any question about images. "
                    f"Be thorough, accurate, and helpful. {lang_instruction}"
                )},
                {"role":"user","content":[
                    {"type":"image_url","image_url":{"url":f"data:{mime};base64,{b64}"}},
                    {"type":"text","text":user_prompt}
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
# STREAMING TEXT
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
# CONSTANTS & HELPERS
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

GAME_KEYWORDS = ["game","snake game","tetris","pacman","flappy bird","2048",
                 "tic tac toe","chess","checkers","sudoku","minesweeper","platformer",
                 "shooter","puzzle game","card game","memory game","quiz game","breakout",
                 "pong","asteroids","space invaders","racing game","rpg","tower defense",
                 "clicker game","battle","dungeon","maze","arcade"]
APP_KEYWORDS = ["app","application","dashboard","admin panel","landing page",
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
    "python":("python","3.10.0"),"javascript":("javascript","18.15.0"),
    "js":("javascript","18.15.0"),"typescript":("typescript","5.0.3"),
    "java":("java","15.0.2"),"c++":("c++","10.2.0"),"cpp":("c++","10.2.0"),
    "c":("c","10.2.0"),"rust":("rust","1.68.2"),"go":("go","1.16.2"),
    "ruby":("ruby","3.0.1"),"php":("php","8.2.3"),"swift":("swift","5.3.3"),
    "kotlin":("kotlin","1.8.20"),"r":("r","4.1.1"),"bash":("bash","5.2.0"),
    "shell":("bash","5.2.0"),"sql":("sqlite3","3.36.0"),"lua":("lua","5.4.4"),
    "scala":("scala","3.2.2"),
}
SEARCH_TRIGGERS = [
    "who is","who was","who won","who are","what is","what was","what happened",
    "when is","when was","where is","current","latest","recent","today",
    "election","prime minister","president","chief minister","cm of",
    "winner","champion","result","2024","2025","2026",
]

def today_str(): return datetime.now().strftime("%B %d, %Y")

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
    m = re.search(r"(?:weather|temperature|forecast|humidity|climate)\s+(?:report\s+)?(?:in|for|of|at)\s+([A-Za-z ,]+?)(?:\?|$)", q, re.IGNORECASE)
    if m: return m.group(1).strip().rstrip(",")
    sw = {"what","is","the","weather","report","temperature","forecast","today","current","now","like","how","give","me","show","humidity","climate","condition","a","an"}
    return " ".join(w for w in q.replace("?","").split() if w.lower() not in sw).strip() or "Guwahati"

def is_weather_query(q):
    return any(k in q.lower() for k in ["weather","temperature","forecast","humidity","rain","sunny","cloudy","wind speed"])

def get_stock(symbol, dname):
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=2d",
                         headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"}, timeout=8)
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
    for sq in [f"IPL 2025 today match {datetime.now().strftime('%B %d')} live score"]:
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

def qr_url(text): return f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(text)}"
def is_qr_query(q): return any(k in q.lower() for k in ["qr code","qr for","generate qr","make qr","create qr"])
def extract_qr_content(q):
    m=re.search(r"https?://\S+",q)
    if m: return m.group(0)
    sw={"qr","code","generate","make","create","for","me","a","an","the","of","my"}
    return " ".join(w for w in q.replace("?","").split() if w.lower() not in sw).strip() or q

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

def export_md():
    lines=["# Soveren — Chat Export",f"_Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n---\n"]
    for m in st.session_state.messages:
        role="🧑 You" if m["role"]=="user" else "✨ Soveren"
        content=re.sub(r"<[^>]+>","",m["content"]).strip()
        lines.append(f"### {role}\n{content}\n")
    return "\n".join(lines)

def export_json_chat():
    return json.dumps([{"role":m["role"],"content":re.sub(r"<[^>]+>","",m["content"]).strip()}
                       for m in st.session_state.messages],indent=2,ensure_ascii=False)

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
    return {"game":T("live_game"),"app":T("live_app"),
            "software":T("live_software"),"design":T("live_design"),
            "code":"💻 Writing world-class code…","general":"✨ Thinking…"}.get(ct,"✨ Thinking…")

def get_system_prompt(ct):
    mode=st.session_state.get("ai_mode","🤖 Default")
    mode_extra=MODE_PROMPTS.get(mode,""); td=today_str()
    lang_instruction=T("sys_prompt_lang")
    memory_context=build_memory_context(SESSION_ID)
    base=(f"You are Soveren — world's BEST AI assistant with vision, created by Samiran. "
          f"Today: {td}. If asked who made you: 'Soveren, created by Samiran.' "
          f"Never mention Meta, Llama, OpenAI, Groq. Full conversation memory. "
          f"NEVER write partial code. ALWAYS complete implementations. "
          f"Do NOT generate images — you can ANALYZE images but not create them. "
          f"{lang_instruction} {mode_extra}\n\n"
          f"LIVE DATA: When real-time data provided, use as ABSOLUTE TRUTH. "
          f"Answer directly. NEVER redirect to external sites. Today is {td}.\n\n"
          f"{memory_context}\n\n")
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
        if err: return f"❌ Error:\n{err}"
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
                f"<title>Soveren</title><style>{css_part}</style></head>"
                f"<body>{html_part}<script>{js_part}</script></body></html>")
    return ""

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for key,default in [
    ("messages",[]),("temperature",0.25),("max_tokens",4096),
    ("ai_mode","🤖 Default"),("uploaded_file_content",None),
    ("uploaded_file_name",None),("pending_image_b64",None),
    ("pending_image_mime",None),("pending_image_name",None),
    ("show_image_uploader",False),("show_file_uploader",False),
    ("lang_code","en"),("lang_name","🌐 English"),
    ("db_loaded",False),("show_memory_panel",False),
]:
    if key not in st.session_state: st.session_state[key]=default

# Load from DB on first run
if not st.session_state["db_loaded"]:
    prefs=load_preferences_db(SESSION_ID)
    if prefs:
        st.session_state["ai_mode"]=prefs[0]
        st.session_state["temperature"]=prefs[1]
        st.session_state["max_tokens"]=prefs[2]
        st.session_state["lang_code"]=prefs[3]
        st.session_state["lang_name"]=prefs[4]
    saved_msgs=load_messages_db(SESSION_ID,limit=100)
    if saved_msgs: st.session_state["messages"]=saved_msgs
    st.session_state["db_loaded"]=True

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1.2rem 0 .8rem'>
        <div style='font-size:1.4rem;font-weight:700;font-family:Space Mono,monospace;color:#00e5ff'>✨ Soveren</div>
        <div style='font-size:11px;color:#64748b;margin-top:.3rem'>Created by Samiran · v5.0</div>
    </div>""", unsafe_allow_html=True)
    st.divider()

    st.markdown(f"### {T('language_label')}")
    st.markdown(f"""
    <div class="lang-selector-wrap">
        <span class="lang-flag">{st.session_state['lang_name'].split()[0]}</span>
        <span class="lang-name">{st.session_state['lang_name']}</span>
    </div>""", unsafe_allow_html=True)

    lang_choice=st.selectbox("Choose Language",options=list(LANGUAGES.keys()),
                              index=list(LANGUAGES.keys()).index(st.session_state["lang_name"]),
                              label_visibility="collapsed",key="lang_select")
    if lang_choice!=st.session_state["lang_name"]:
        st.session_state["lang_name"]=lang_choice
        st.session_state["lang_code"]=LANGUAGES[lang_choice]
        save_preferences_db(SESSION_ID)
        st.rerun()

    st.markdown("<div style='font-size:10px;color:#64748b;margin-top:6px;margin-bottom:4px'>Quick select:</div>",unsafe_allow_html=True)
    lang_keys=list(LANGUAGES.keys())
    cols=st.columns(4)
    for i,lk in enumerate(lang_keys):
        with cols[i%4]:
            flag=lk.split()[0]; code=LANGUAGES[lk]
            if st.button(flag,key=f"lang_flag_{code}",help=lk,use_container_width=True):
                st.session_state["lang_name"]=lk
                st.session_state["lang_code"]=code
                save_preferences_db(SESSION_ID)
                st.rerun()

    st.divider()
    st.markdown(f"### {T('settings')}")
    st.session_state["temperature"]=st.slider(T("temperature"),0.0,1.0,value=st.session_state["temperature"],step=0.05)
    st.session_state["max_tokens"]=st.select_slider(T("max_length"),options=[512,1024,2048,4096,8192],value=st.session_state["max_tokens"])
    st.divider()
    st.markdown(f"### {T('ai_mode')}")
    st.session_state["ai_mode"]=st.selectbox("Mode",list(MODE_PROMPTS.keys()),index=0,label_visibility="collapsed")
    st.divider()
    st.markdown(f"### {T('quick_tools')}")

    with st.expander(T("currency")):
        amt=st.number_input(T("amount"),value=1.0,min_value=0.0,key="sb_amt")
        c1,c2=st.columns(2)
        with c1: fc=st.selectbox(T("from_curr"),CURRENCIES,index=0,key="sb_fc")
        with c2: tc=st.selectbox(T("to_curr"),CURRENCIES,index=3,key="sb_tc")
        if st.button(T("convert_btn"),key="sb_conv"): st.markdown(get_exchange_rate(fc,tc,amt))

    with st.expander(T("units")):
        uin=st.text_input(T("unit_placeholder"),key="sb_uin")
        if st.button(T("unit_btn"),key="sb_unit"):
            res=convert_unit(uin)
            st.markdown(res if res else "⚠️ Try: '100 km to miles'")

    with st.expander(T("calculator")):
        cin=st.text_input(T("calc_placeholder"),key="sb_cin")
        if st.button(T("calc_btn"),key="sb_calc"):
            res=solve_math(cin)
            if res: st.markdown(f"**= {res}**")
            else: st.warning("Could not evaluate.")

    with st.expander(T("qr_code")):
        qin=st.text_input(T("qr_placeholder"),key="sb_qin")
        if st.button(T("qr_btn"),key="sb_qr") and qin:
            url=qr_url(qin)
            st.image(url,width=180)
            st.markdown(f"[⬇️ Download]({url})")

    st.divider()
    st.markdown(f"### {T('export')}")
    if st.session_state["messages"]:
        ca,cb=st.columns(2)
        ts=datetime.now().strftime("%Y%m%d_%H%M")
        with ca: st.download_button(T("download_md"),data=export_md(),file_name=f"soveren_{ts}.md",mime="text/markdown",use_container_width=True)
        with cb: st.download_button(T("download_json"),data=export_json_chat(),file_name=f"soveren_{ts}.json",mime="application/json",use_container_width=True)
    else: st.caption(T("no_msgs"))

    st.divider()

    # ══════════════════════════════════════════════════════════════════════════
    # 💾 PERSISTENT MEMORY PANEL
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("### 💾 Memory")
    stats=get_session_stats(SESSION_ID)
    if stats:
        total_msgs,created_at,last_active=stats
        st.markdown(f"""
        <div style='background:#1a1d24;border:1px solid #232730;border-radius:10px;padding:10px 12px;margin-bottom:8px'>
            <div style='font-size:11px;color:#64748b;margin-bottom:6px'>📊 Session Stats</div>
            <div style='font-size:12px;color:#e2e8f0'>
                💬 {total_msgs} messages saved<br>
                🕐 Since: {str(created_at)[:10] if created_at else 'Now'}<br>
                🆔 ID: <code style='color:#00e5ff'>{SESSION_ID[:8]}…</code>
            </div>
        </div>""", unsafe_allow_html=True)

    memories=get_long_term_memory(SESSION_ID)
    if memories:
        with st.expander(f"🧠 Long-term Memory ({len(memories)})"):
            for mem_type,key,value,updated in memories:
                clean_key=key.replace("_"," ").title()
                col_m,col_d=st.columns([4,1])
                with col_m:
                    st.markdown(f"""
                    <div class="memory-card">
                        <span class="memory-type">{mem_type}</span><br>
                        <span class="memory-value"><b>{clean_key}:</b> {value[:40]}{'…' if len(value)>40 else ''}</span>
                    </div>""", unsafe_allow_html=True)
                with col_d:
                    if st.button("🗑️",key=f"del_mem_{key}",help=f"Delete {clean_key}"):
                        delete_long_term_memory(SESSION_ID,key)
                        st.rerun()

    with st.expander("➕ Add Memory"):
        mem_key=st.text_input("Key (e.g. 'My Project')",key="new_mem_key")
        mem_val=st.text_area("Value",key="new_mem_val",height=80)
        if st.button("💾 Save Memory",key="save_mem_btn"):
            if mem_key and mem_val:
                save_long_term_memory(SESSION_ID,"manual",mem_key.lower().replace(" ","_"),mem_val)
                st.success("✅ Memory saved!")
                st.rerun()

    st.divider()
    st.markdown("### 📂 Sessions")
    all_sessions=get_all_sessions()
    if len(all_sessions)>1:
        with st.expander(f"🔄 Switch Session ({len(all_sessions)})"):
            for sid,uname,nmsg,last in all_sessions:
                is_current=sid==SESSION_ID
                btn_label=f"{'✅ ' if is_current else ''}{uname or 'User'} · {nmsg} msgs · {str(last)[:10]}"
                if st.button(btn_label,key=f"sess_{sid}",disabled=is_current,use_container_width=True):
                    st.session_state["session_id"]=sid
                    st.session_state["db_loaded"]=False
                    st.session_state["messages"]=[]
                    st.rerun()

    col_ns,col_ds=st.columns(2)
    with col_ns:
        if st.button("➕ New Chat",use_container_width=True,key="new_session_btn"):
            save_preferences_db(SESSION_ID)
            raw=f"soveren_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}_new"
            new_sid=hashlib.md5(raw.encode()).hexdigest()[:16]
            st.session_state["session_id"]=new_sid
            st.session_state["messages"]=[]
            st.session_state["db_loaded"]=False
            st.rerun()
    with col_ds:
        if st.button("🗑️ Delete",use_container_width=True,key="del_session_btn"):
            delete_session_db(SESSION_ID)
            raw=f"soveren_{datetime.now().strftime('%Y%m%d_%H%M%S')}_fresh"
            st.session_state["session_id"]=hashlib.md5(raw.encode()).hexdigest()[:16]
            st.session_state["messages"]=[]
            st.session_state["db_loaded"]=False
            st.rerun()

    st.divider()
    st.markdown(f"<div style='text-align:center;font-size:10px;color:#374151'>Soveren · Samiran · v5.0<br>{datetime.now().strftime('%B %Y')}</div>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero">
    <div class="hero-badge">{T('badge')}</div>
    <h1>Sove<span>ren</span></h1>
    <p>{T('subtitle')}</p>
</div>
<div class="stats-row">
    <div class="stat-pill"><span class="dot dot-purple"></span>{T('stat_memory')}</div>
    <div class="stat-pill"><span class="dot dot-pink"></span>{T('stat_vision')}</div>
    <div class="stat-pill"><span class="dot dot-blue"></span>{T('stat_sports')}</div>
    <div class="stat-pill"><span class="dot dot-orange"></span>{T('stat_games')}</div>
    <div class="stat-pill"><span class="dot dot-green"></span>{T('stat_files')}</div>
    <div class="stat-pill"><span class="dot dot-green"></span>{T('stat_live')}</div>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

col1,col2,col3=st.columns([5,1,1])
with col2:
    count=len([m for m in st.session_state.messages if m["role"]=="user"])
    label=f"{count} {T('msgp') if count!=1 else T('msgs')}"
    st.markdown(f"<p style='text-align:right;color:var(--muted);font-size:12px;padding-top:.5rem'>{label}</p>",unsafe_allow_html=True)
with col3:
    if st.button(T("clear")):
        st.session_state.messages=[]
        clear_session_messages(SESSION_ID)
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# CHAT HISTORY
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.messages:
    st.markdown(f"""
    <div style="text-align:center;padding:1rem 1rem .5rem">
        <div style="font-size:2rem;margin-bottom:.5rem">✨</div>
        <p style="font-size:.95rem;font-weight:600;color:#94a3b8;margin-bottom:1rem">{T('hero_q')}</p>
    </div>
    <div class="category-grid">
        <div class="category-card"><div class="category-icon">👁️</div><div class="category-title">{T('cat_vision')}</div><div class="category-examples">{T('cat_vision_ex')}</div></div>
        <div class="category-card"><div class="category-icon">🎮</div><div class="category-title">{T('cat_games')}</div><div class="category-examples">{T('cat_games_ex')}</div></div>
        <div class="category-card"><div class="category-icon">🚀</div><div class="category-title">{T('cat_apps')}</div><div class="category-examples">{T('cat_apps_ex')}</div></div>
        <div class="category-card"><div class="category-icon">💻</div><div class="category-title">{T('cat_code')}</div><div class="category-examples">{T('cat_code_ex')}</div></div>
        <div class="category-card"><div class="category-icon">📁</div><div class="category-title">{T('cat_files')}</div><div class="category-examples">{T('cat_files_ex')}</div></div>
        <div class="category-card"><div class="category-icon">🌐</div><div class="category-title">{T('cat_live')}</div><div class="category-examples">{T('cat_live_ex')}</div></div>
        <div class="category-card"><div class="category-icon">💾</div><div class="category-title">{T('cat_memory')}</div><div class="category-examples">{T('cat_memory_ex')}</div></div>
    </div>
    <div class="divider"></div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("meta"):
                st.markdown(msg["meta"],unsafe_allow_html=True)
            if msg.get("image_b64") and msg.get("image_mime"):
                try:
                    img_bytes=base64.b64decode(msg["image_b64"])
                    img=Image.open(io.BytesIO(img_bytes))
                    st.image(img,caption=msg.get("image_name","Uploaded image"),width=350)
                except: pass
            st.markdown(msg["content"])

# ══════════════════════════════════════════════════════════════════════════════
# BOTTOM INPUT AREA
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.get("pending_image_b64"):
    fname=st.session_state.get("pending_image_name","image")
    try:
        img_bytes=base64.b64decode(st.session_state["pending_image_b64"])
        img=Image.open(io.BytesIO(img_bytes))
        col_img,col_info,col_x=st.columns([1,5,1])
        with col_img: st.image(img,width=56)
        with col_info:
            st.markdown(f"<div style='padding-top:8px'><div style='font-size:13px;color:#e2e8f0;font-weight:500'>🖼️ {fname}</div><div style='font-size:11px;color:#64748b'>{T('img_ready')}</div></div>",unsafe_allow_html=True)
        with col_x:
            if st.button("✕",key="clear_pending_img"):
                st.session_state["pending_image_b64"]=None
                st.session_state["pending_image_mime"]=None
                st.session_state["pending_image_name"]=None
                st.rerun()
    except: pass

if st.session_state.get("uploaded_file_content"):
    fname=st.session_state.get("uploaded_file_name","file")
    col_fi,col_fx=st.columns([8,1])
    with col_fi:
        st.markdown(f'<div class="badge badge-purple" style="margin:4px 0">📁 {fname} — {T("file_ready")}</div>',unsafe_allow_html=True)
    with col_fx:
        if st.button("✕",key="clear_pending_file"):
            st.session_state["uploaded_file_content"]=None
            st.session_state["uploaded_file_name"]=None
            st.rerun()

tb_col1,tb_col2,tb_col3,tb_col4=st.columns([1,1,1,6])
with tb_col1:
    img_btn_label=T("img_btn_done") if st.session_state.get("pending_image_b64") else T("img_btn")
    if st.button(img_btn_label,key="toggle_img_upload"):
        st.session_state["show_image_uploader"]=not st.session_state["show_image_uploader"]
        st.session_state["show_file_uploader"]=False
        st.rerun()
with tb_col2:
    file_btn_label=T("file_btn_done") if st.session_state.get("uploaded_file_content") else T("file_btn")
    if st.button(file_btn_label,key="toggle_file_upload"):
        st.session_state["show_file_uploader"]=not st.session_state["show_file_uploader"]
        st.session_state["show_image_uploader"]=False
        st.rerun()
with tb_col3:
    if st.button(T("help_btn"),key="show_help"):
        st.session_state["show_image_uploader"]=False
        st.session_state["show_file_uploader"]=False

if st.session_state.get("show_image_uploader"):
    st.markdown(f"""
    <div style='background:#1a1d24;border:1px solid #232730;border-radius:14px;padding:1.2rem;margin-bottom:.5rem;'>
        <div style='font-size:13px;color:#00e5ff;font-weight:600;margin-bottom:.5rem'>{T('img_upload_title')}</div>
        <div style='font-size:11px;color:#64748b;margin-bottom:.8rem'>{T('img_upload_hint')}</div>
    </div>""", unsafe_allow_html=True)
    img_file=st.file_uploader("Choose image",type=["jpg","jpeg","png","gif","bmp","webp","tiff"],key="main_img_upload",label_visibility="collapsed")
    if img_file is not None:
        b64,mime,w,h=image_to_base64(img_file)
        if b64:
            st.session_state["pending_image_b64"]=b64
            st.session_state["pending_image_mime"]=mime
            st.session_state["pending_image_name"]=img_file.name
            st.session_state["show_image_uploader"]=False
            col_prev,col_info=st.columns([1,2])
            with col_prev:
                preview=Image.open(io.BytesIO(base64.b64decode(b64)))
                st.image(preview,width=120)
            with col_info:
                st.success(f"✅ {img_file.name}")
                st.caption(f"Size: {w}×{h}px · {mime}")
                st.info(T("img_ready"))
        else:
            st.error("❌ Could not process image.")
    st.markdown(f"""
    <div style='margin-top:.8rem'>
        <div style='font-size:11px;color:#64748b;margin-bottom:.4rem'>{T('example_q')}</div>
        <div style='display:flex;flex-wrap:wrap;gap:6px'>
            <span style='background:#1a1d24;border:1px solid #232730;border-radius:999px;padding:3px 10px;font-size:11px;color:#94a3b8'>{T('ex1')}</span>
            <span style='background:#1a1d24;border:1px solid #232730;border-radius:999px;padding:3px 10px;font-size:11px;color:#94a3b8'>{T('ex2')}</span>
            <span style='background:#1a1d24;border:1px solid #232730;border-radius:999px;padding:3px 10px;font-size:11px;color:#94a3b8'>{T('ex3')}</span>
            <span style='background:#1a1d24;border:1px solid #232730;border-radius:999px;padding:3px 10px;font-size:11px;color:#94a3b8'>{T('ex4')}</span>
            <span style='background:#1a1d24;border:1px solid #232730;border-radius:999px;padding:3px 10px;font-size:11px;color:#94a3b8'>{T('ex5')}</span>
        </div>
    </div>""", unsafe_allow_html=True)

if st.session_state.get("show_file_uploader"):
    st.markdown(f"""
    <div style='background:#1a1d24;border:1px solid #232730;border-radius:14px;padding:1.2rem;margin-bottom:.5rem;'>
        <div style='font-size:13px;color:#a78bfa;font-weight:600;margin-bottom:.5rem'>{T('file_upload_title')}</div>
        <div style='font-size:11px;color:#64748b;margin-bottom:.8rem'>{T('file_upload_hint')}</div>
    </div>""", unsafe_allow_html=True)
    doc_file=st.file_uploader("Choose file",type=["txt","csv","json","py","js","ts","html","css","java","cpp","c","md","rs","go"],key="main_doc_upload",label_visibility="collapsed")
    if doc_file is not None:
        content=read_uploaded_file(doc_file)
        st.session_state["uploaded_file_content"]=content
        st.session_state["uploaded_file_name"]=doc_file.name
        st.session_state["show_file_uploader"]=False
        st.success(f"✅ {doc_file.name} ready!")
        st.info(T("file_ready"))

# ══════════════════════════════════════════════════════════════════════════════
# CHAT INPUT
# ══════════════════════════════════════════════════════════════════════════════
if prompt := st.chat_input(T("chat_placeholder")):
    has_image=bool(st.session_state.get("pending_image_b64"))
    has_file=bool(st.session_state.get("uploaded_file_content"))
    user_msg={"role":"user","content":prompt,"meta":""}
    if has_image:
        user_msg["image_b64"]=st.session_state["pending_image_b64"]
        user_msg["image_mime"]=st.session_state["pending_image_mime"]
        user_msg["image_name"]=st.session_state["pending_image_name"]
    st.session_state.messages.append(user_msg)
    # 💾 Save to DB
    save_message_db(SESSION_ID,"user",prompt)
    save_preferences_db(SESSION_ID)

    with st.chat_message("user"):
        if has_image:
            try:
                img_bytes=base64.b64decode(st.session_state["pending_image_b64"])
                st.image(Image.open(io.BytesIO(img_bytes)),caption=st.session_state.get("pending_image_name","Image"),width=350)
            except: pass
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response=""; meta=""

        if has_image:
            b64=st.session_state["pending_image_b64"]
            mime=st.session_state["pending_image_mime"]
            name=st.session_state.get("pending_image_name","image")
            meta=f'<div class="badge badge-pink">👁️ Vision AI · {name}</div>'
            st.markdown(meta,unsafe_allow_html=True)
            with st.spinner(T("analyzing")):
                response=analyze_image_stream(b64,mime,get_vision_prompt(prompt))
            st.session_state["pending_image_b64"]=None
            st.session_state["pending_image_mime"]=None
            st.session_state["pending_image_name"]=None

        elif is_qr_query(prompt):
            content=extract_qr_content(prompt); url=qr_url(content)
            meta='<div class="badge badge-green">📱 QR Code</div>'
            st.markdown(meta,unsafe_allow_html=True)
            st.markdown(f"**QR for:** `{content}`")
            st.image(url,width=260)
            st.markdown(f'<a href="{url}" class="btn-download" target="_blank">{T("download")} QR</a>',unsafe_allow_html=True)
            response=f"✅ QR Code generated for: `{content}`"

        elif is_currency_query(prompt):
            amount,fc,tc=extract_currency_params(prompt)
            with st.spinner(T("fetching_rate")): result=get_exchange_rate(fc,tc,amount)
            meta='<div class="badge badge-green">💱 Live rate</div>'
            st.markdown(meta,unsafe_allow_html=True)
            st.markdown(f'<div class="result-box green">{result}</div>',unsafe_allow_html=True)
            response=result

        elif is_unit_query(prompt):
            result=convert_unit(prompt)
            if result:
                meta='<div class="badge badge-orange">📐 Unit converted</div>'
                st.markdown(meta,unsafe_allow_html=True)
                st.markdown(f'<div class="result-box orange">{result}</div>',unsafe_allow_html=True)
                response=result

        if not response and is_math_query(prompt):
            result=solve_math(prompt)
            if result:
                meta='<div class="badge badge-orange">🔢 Calculated</div>'
                st.markdown(meta,unsafe_allow_html=True)
                st.markdown(f'<div class="result-box orange" style="font-family:Space Mono,monospace;font-size:16px;color:#f59e0b">= {result}</div>',unsafe_allow_html=True)
                msgs=build_messages(f"The answer to '{prompt}' is {result}. Briefly explain in 2 lines.")
                explanation=stream_response(msgs,max_tokens=200,temperature=st.session_state["temperature"])
                response=f"= **{result}**\n\n{explanation}"

        if not response and is_url_query(prompt):
            url=extract_url(prompt)
            if url:
                with st.spinner(f"{T('reading_url')} {url[:50]}…"): page=fetch_url_content(url)
                meta='<div class="badge badge-green">🌐 URL read</div>'
                st.markdown(meta,unsafe_allow_html=True)
                msgs=build_messages(f"URL: {url}\nContent:\n{page}\n\nRequest: {prompt}")
                response=stream_response(msgs,max_tokens=st.session_state["max_tokens"],temperature=st.session_state["temperature"])

        if not response and has_file:
            fname=st.session_state.get("uploaded_file_name","file")
            meta=f'<div class="badge badge-purple">📁 {fname}</div>'
            st.markdown(meta,unsafe_allow_html=True)
            msgs=build_messages(f"File: '{fname}'\nContent:\n{st.session_state['uploaded_file_content']}\n\nRequest: {prompt}")
            response=stream_response(msgs,max_tokens=st.session_state["max_tokens"],temperature=st.session_state["temperature"])
            st.session_state["uploaded_file_content"]=None
            st.session_state["uploaded_file_name"]=None

        if not response and is_stock_query(prompt):
            symbol,dname=extract_stock_symbol(prompt)
            if symbol:
                with st.spinner(f"{T('fetching_stock')} {dname}…"): sd=get_stock(symbol,dname)
                if "failed" not in sd.lower():
                    L=dict(l.split(": ",1) for l in sd.strip().splitlines() if ": " in l)
                    meta='<div class="badge badge-green">📈 Live · Yahoo Finance</div>'
                    st.markdown(meta,unsafe_allow_html=True)
                    response=(f"### {L.get('Name',dname)} 📈\n_{L.get('Exchange','')} · {L.get('Market','')}_\n\n"
                              f"| Detail | Value |\n|--------|-------|\n"
                              f"| 💰 Price | **{L.get('Price','N/A')}** |\n"
                              f"| 📊 Change | {L.get('Change','N/A')} |\n"
                              f"| 📈 Day High | {L.get('Day High','N/A')} |\n"
                              f"| 📉 Day Low | {L.get('Day Low','N/A')} |\n"
                              f"| 🔢 Volume | {L.get('Volume','N/A')} |\n\n_Delayed ~15 min_")
                    st.markdown(response)

        if not response and is_sports_query(prompt):
            with st.spinner(T("fetching_sports")):
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

        if not response and is_news_query(prompt):
            with st.spinner(T("fetching_news")):
                topic=extract_news_topic(prompt); news=get_news(topic)
            meta='<div class="badge badge-green">📰 Live news</div>'
            st.markdown(meta,unsafe_allow_html=True)
            response=f"### 📰 {topic.title()}\n\n{news}"
            st.markdown(response)

        if not response and is_weather_query(prompt):
            with st.spinner(T("fetching_weather")):
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

        if not response:
            ct=classify_creation(prompt); search_results=""; searched=False
            if needs_search(prompt):
                with st.spinner(T("searching")):
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
                    with st.spinner(get_spinner_text(ct) if attempt==0 else "⏳ Retrying…"):
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
                                plabels={"game":T("live_game"),"app":T("live_app"),"software":T("live_software"),"design":T("live_design")}
                                st.markdown(f"### {plabels.get(ct,T('live_preview'))}")
                                h=650 if ct in ("game","app","software") else 520
                                st.components.v1.html(html_src,height=h,scrolling=True)
                                b64_html=base64.b64encode(html_src.encode()).decode()
                                fname={"game":"soveren_game.html","app":"soveren_app.html","software":"soveren_software.html","design":"soveren_design.html"}.get(ct,"soveren.html")
                                st.markdown(f'<a href="data:text/html;base64,{b64_html}" download="{fname}" class="btn-download">{T("download")} {fname}</a>',unsafe_allow_html=True)
                        elif code and lang and lang not in ("html","css"):
                            rk=f"run_{len(st.session_state.messages)}"
                            if st.button(f"{T('run_btn')} {lang.title()}",key=rk):
                                with st.spinner(f"{T('running_code')} {lang}…"): out=run_code(code,lang)
                                cls="error-box" if "❌" in out else "output-box"
                                st.markdown(f'<div class="{cls}">{out}</div>',unsafe_allow_html=True)
                        break
                except Exception as e:
                    if "rate_limit_exceeded" in str(e) and attempt<2: continue
                    st.error(f"❌ Error: {e}"); break

        if response:
            st.session_state.messages.append({"role":"assistant","content":response,"meta":meta})
            # 💾 Save AI response to DB
            save_message_db(SESSION_ID,"assistant",response)
            # 🧠 Auto-extract memories
            extract_and_save_memories(SESSION_ID,prompt,response)
