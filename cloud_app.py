import streamlit as st
from groq import Groq
import time, requests, re, base64, json, math
from datetime import datetime
import urllib.parse
import xml.etree.ElementTree as ET
from PIL import Image
import io
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff

# ══════════════════════════════════════════════════════════════════════════════
#  LANGUAGE SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
LANGUAGES = {
    "🌐 English": "en",
    "🇮🇳 हिंदी":   "hi",
    "🇧🇩 বাংলা":  "bn",
    "🇪🇸 Español": "es",
    "🇫🇷 Français":"fr",
    "🇩🇪 Deutsch": "de",
    "🇯🇵 日本語":   "ja",
    "🇨🇳 中文":    "zh",
    "🇦🇪 العربية": "ar",
    "🇷🇺 Русский": "ru",
    "🇵🇹 Português":"pt",
    "🇰🇷 한국어":   "ko",
}

UI_TEXT = {
    "en": {
        "title":"Nova AI","subtitle":"The world's smartest AI — sees images, builds apps, visualizes data, knows everything live.",
        "badge":"LIVE · FREE · UNLIMITED · VISION AI","chat_placeholder":"Ask anything — type here or click 🖼️ Image / 📄 File / 📊 CSV above…",
        "clear":"🗑️ Clear","msgs":"msg","msgp":"msgs","hero_q":"What would you like to do today?",
        "cat_vision":"Vision AI","cat_vision_ex":"Upload any image\nAI reads & analyzes",
        "cat_games":"Games","cat_games_ex":"Snake · Tetris\nChess · 2048\nPacman · RPG",
        "cat_apps":"Apps","cat_apps_ex":"Dashboard · Todo\nE-commerce\nPortfolio",
        "cat_code":"Code","cat_code_ex":"Python · JS · Java\nC++ · Go · Rust\nSQL & more",
        "cat_files":"Files","cat_files_ex":"CSV · JSON · Code\nAI analyzes it",
        "cat_charts":"Charts & Data","cat_charts_ex":"Upload CSV\nAuto-generate charts\nAI insights",
        "cat_live":"Live Data","cat_live_ex":"Cricket · Stocks\nWeather · News\nAny URL",
        "img_btn":"🖼️ Image","img_btn_done":"🖼️ ✓",
        "file_btn":"📄 File","file_btn_done":"📄 ✓",
        "csv_btn":"📊 CSV","csv_btn_done":"📊 ✓",
        "help_btn":"❓ Help",
        "settings":"⚙️ Model Settings","temperature":"Temperature","max_length":"Max Length",
        "ai_mode":"🎭 AI Mode","quick_tools":"🛠️ Quick Tools",
        "currency":"💱 Currency","units":"📐 Units","calculator":"🔢 Calculator","qr_code":"📱 QR Code",
        "export":"💾 Export","no_msgs":"No messages yet.",
        "convert_btn":"Convert 💱","calc_btn":"Calculate 🔢","unit_btn":"Convert 📐","qr_btn":"Generate QR",
        "download_md":"📝 MD","download_json":"📊 JSON",
        "img_upload_title":"👁️ Upload Image for Vision AI","img_upload_hint":"Supports: JPG, PNG, GIF, BMP, WebP, TIFF",
        "file_upload_title":"📁 Upload File for Analysis","file_upload_hint":"Supports: TXT, CSV, JSON, Python, JS, HTML, CSS, Java, C++, Markdown",
        "csv_upload_title":"📊 Upload CSV for Data Visualization","csv_upload_hint":"Upload any CSV file — Nova AI auto-generates charts & insights",
        "img_ready":"Ready · Type your question below ↓","file_ready":"Ask me anything about this file",
        "csv_ready":"CSV loaded · Charts auto-generated below!",
        "analyzing":"👁️ Analyzing image…","searching":"🔍 Searching…",
        "fetching_weather":"🌤️ Fetching weather…","fetching_stock":"📈 Fetching",
        "fetching_sports":"🏏 Fetching live sports data…","fetching_news":"📰 Fetching news…",
        "fetching_rate":"💱 Fetching rates…","reading_url":"🌐 Reading",
        "running_code":"⚙️ Running","run_btn":"▶ Run",
        "live_preview":"🖥️ Preview","live_game":"🎮 Live Game!","live_app":"🚀 Live App",
        "live_software":"⚙️ Live Software","live_design":"✨ Live Design",
        "download":"⬇️ Download","example_q":"💡 Example questions:",
        "ex1":"What is in this image?","ex2":"Read the text","ex3":"Solve this math",
        "ex4":"Explain this code","ex5":"Analyze this chart",
        "unit_placeholder":"e.g. 100 km to miles","calc_placeholder":"e.g. sqrt(144)",
        "qr_placeholder":"Text or URL","amount":"Amount","from_curr":"From","to_curr":"To",
        "no_results":"No results.","stat_memory":"🧠 Memory","stat_vision":"👁️ Vision AI",
        "stat_sports":"🏏 Live Sports","stat_games":"🎮 Games & Apps",
        "stat_files":"📁 Files & URLs","stat_live":"💱 Live Data","stat_charts":"📊 Data Viz",
        "language_label":"🌍 Language","sys_prompt_lang":"Respond in English.",
        "chart_title":"📊 Auto-Generated Charts","chart_overview":"📋 Dataset Overview",
        "chart_ai_insights":"🤖 AI Data Insights","chart_rows":"rows","chart_cols":"columns",
        "chart_numeric":"Numeric columns","chart_categorical":"Categorical columns",
        "chart_missing":"Missing values","chart_ask":"Ask AI about this data…",
        "chart_generating":"📊 Generating charts…","chart_analyzing":"🤖 Analyzing data with AI…",
        "chart_types":"Chart Types","chart_select_x":"X-axis","chart_select_y":"Y-axis",
        "chart_select_color":"Color by","chart_custom":"🎨 Custom Chart Builder",
        "chart_bar":"Bar","chart_line":"Line","chart_scatter":"Scatter","chart_pie":"Pie",
        "chart_histogram":"Histogram","chart_box":"Box","chart_heatmap":"Heatmap",
        "chart_area":"Area","chart_violin":"Violin","chart_sunburst":"Sunburst",
        "chart_generate":"Generate Chart","chart_correlation":"Correlation Matrix",
        "chart_distribution":"Distribution Analysis","chart_summary":"Statistical Summary",
        "chart_top_insights":"Top Insights","chart_download_csv":"⬇️ Download Processed CSV",
    },
    "hi": {
        "title":"Nova AI","subtitle":"दुनिया का सबसे स्मार्ट AI — छवियां देखता है, ऐप्स बनाता है, डेटा विज़ुअलाइज़ करता है।",
        "badge":"लाइव · मुफ़्त · असीमित · विज़न AI","chat_placeholder":"कुछ भी पूछें — यहाँ टाइप करें या ऊपर 🖼️ Image / 📄 File / 📊 CSV क्लिक करें…",
        "clear":"🗑️ साफ़ करें","msgs":"संदेश","msgp":"संदेश","hero_q":"आज आप क्या करना चाहेंगे?",
        "cat_vision":"विज़न AI","cat_vision_ex":"कोई भी छवि अपलोड करें\nAI पढ़ता और विश्लेषण करता है",
        "cat_games":"गेम्स","cat_games_ex":"Snake · Tetris\nChess · 2048",
        "cat_apps":"ऐप्स","cat_apps_ex":"Dashboard · Todo\nई-कॉमर्स",
        "cat_code":"कोड","cat_code_ex":"Python · JS · Java\nC++ · Go · Rust",
        "cat_files":"फ़ाइलें","cat_files_ex":"CSV · JSON · कोड\nAI विश्लेषण करता है",
        "cat_charts":"चार्ट और डेटा","cat_charts_ex":"CSV अपलोड करें\nचार्ट स्वतः बनाएं\nAI अंतर्दृष्टि",
        "cat_live":"लाइव डेटा","cat_live_ex":"क्रिकेट · शेयर\nमौसम · समाचार",
        "img_btn":"🖼️ छवि","img_btn_done":"🖼️ ✓",
        "file_btn":"📄 फ़ाइल","file_btn_done":"📄 ✓",
        "csv_btn":"📊 CSV","csv_btn_done":"📊 ✓",
        "help_btn":"❓ सहायता","settings":"⚙️ मॉडल सेटिंग","temperature":"तापमान","max_length":"अधिकतम लंबाई",
        "ai_mode":"🎭 AI मोड","quick_tools":"🛠️ त्वरित टूल्स",
        "currency":"💱 मुद्रा","units":"📐 इकाई","calculator":"🔢 कैलकुलेटर","qr_code":"📱 QR कोड",
        "export":"💾 निर्यात","no_msgs":"अभी कोई संदेश नहीं।",
        "convert_btn":"कन्वर्ट करें 💱","calc_btn":"गणना करें 🔢","unit_btn":"कन्वर्ट करें 📐","qr_btn":"QR बनाएं",
        "download_md":"📝 MD","download_json":"📊 JSON",
        "img_upload_title":"👁️ विज़न AI के लिए छवि अपलोड करें","img_upload_hint":"समर्थित: JPG, PNG, GIF, BMP, WebP, TIFF",
        "file_upload_title":"📁 विश्लेषण के लिए फ़ाइल अपलोड करें","file_upload_hint":"समर्थित: TXT, CSV, JSON, Python, JS",
        "csv_upload_title":"📊 डेटा विज़ुअलाइज़ेशन के लिए CSV अपलोड करें","csv_upload_hint":"कोई भी CSV फ़ाइल अपलोड करें — Nova AI स्वतः चार्ट बनाएगा",
        "img_ready":"तैयार · नीचे अपना प्रश्न टाइप करें ↓","file_ready":"इस फ़ाइल के बारे में कुछ भी पूछें",
        "csv_ready":"CSV लोड हो गया · चार्ट स्वतः बन गए!",
        "analyzing":"👁️ छवि का विश्लेषण हो रहा है…","searching":"🔍 खोज रहे हैं…",
        "fetching_weather":"🌤️ मौसम जानकारी ला रहे हैं…","fetching_stock":"📈 डेटा ला रहे हैं",
        "fetching_sports":"🏏 लाइव स्पोर्ट्स डेटा ला रहे हैं…","fetching_news":"📰 समाचार ला रहे हैं…",
        "fetching_rate":"💱 विनिमय दर ला रहे हैं…","reading_url":"🌐 पढ़ रहे हैं",
        "running_code":"⚙️ चला रहे हैं","run_btn":"▶ चलाएं",
        "live_preview":"🖥️ प्रीव्यू","live_game":"🎮 लाइव गेम!","live_app":"🚀 लाइव ऐप",
        "live_software":"⚙️ लाइव सॉफ़्टवेयर","live_design":"✨ लाइव डिज़ाइन",
        "download":"⬇️ डाउनलोड","example_q":"💡 उदाहरण प्रश्न:","ex1":"इस छवि में क्या है?",
        "ex2":"टेक्स्ट पढ़ें","ex3":"यह गणित हल करें","ex4":"यह कोड समझाएं","ex5":"यह चार्ट विश्लेषण करें",
        "unit_placeholder":"जैसे: 100 किमी से मील","calc_placeholder":"जैसे: sqrt(144)",
        "qr_placeholder":"टेक्स्ट या URL","amount":"राशि","from_curr":"से","to_curr":"में",
        "no_results":"कोई परिणाम नहीं।","stat_memory":"🧠 मेमोरी","stat_vision":"👁️ विज़न AI",
        "stat_sports":"🏏 लाइव स्पोर्ट्स","stat_games":"🎮 गेम्स और ऐप्स",
        "stat_files":"📁 फ़ाइलें और URLs","stat_live":"💱 लाइव डेटा","stat_charts":"📊 डेटा विज़",
        "language_label":"🌍 भाषा","sys_prompt_lang":"हिंदी में उत्तर दें।",
        "chart_title":"📊 स्वतः बने चार्ट","chart_overview":"📋 डेटासेट अवलोकन","chart_ai_insights":"🤖 AI डेटा अंतर्दृष्टि",
        "chart_rows":"पंक्तियाँ","chart_cols":"कॉलम","chart_numeric":"संख्यात्मक कॉलम",
        "chart_categorical":"श्रेणीबद्ध कॉलम","chart_missing":"अनुपस्थित मान",
        "chart_ask":"इस डेटा के बारे में AI से पूछें…","chart_generating":"📊 चार्ट बन रहे हैं…",
        "chart_analyzing":"🤖 AI डेटा विश्लेषण कर रहा है…","chart_types":"चार्ट प्रकार",
        "chart_select_x":"X-अक्ष","chart_select_y":"Y-अक्ष","chart_select_color":"रंग द्वारा",
        "chart_custom":"🎨 कस्टम चार्ट बिल्डर",
        "chart_bar":"बार","chart_line":"लाइन","chart_scatter":"स्कैटर","chart_pie":"पाई",
        "chart_histogram":"हिस्टोग्राम","chart_box":"बॉक्स","chart_heatmap":"हीटमैप",
        "chart_area":"एरिया","chart_violin":"वायलिन","chart_sunburst":"सनबर्स्ट",
        "chart_generate":"चार्ट बनाएं","chart_correlation":"सहसंबंध मैट्रिक्स",
        "chart_distribution":"वितरण विश्लेषण","chart_summary":"सांख्यिकीय सारांश",
        "chart_top_insights":"शीर्ष अंतर्दृष्टि","chart_download_csv":"⬇️ CSV डाउनलोड करें",
    },
    "bn": {
        "title":"Nova AI","subtitle":"বিশ্বের সবচেয়ে স্মার্ট AI — ছবি দেখে, অ্যাপ তৈরি করে, ডেটা ভিজ্যুয়ালাইজ করে।",
        "badge":"লাইভ · বিনামূল্যে · সীমাহীন · ভিশন AI","chat_placeholder":"যেকোনো কিছু জিজ্ঞাসা করুন — এখানে টাইপ করুন বা 🖼️ ছবি / 📄 ফাইল / 📊 CSV ক্লিক করুন…",
        "clear":"🗑️ মুছুন","msgs":"বার্তা","msgp":"বার্তা","hero_q":"আজ আপনি কী করতে চান?",
        "cat_vision":"ভিশন AI","cat_vision_ex":"যেকোনো ছবি আপলোড করুন\nAI পড়ে ও বিশ্লেষণ করে",
        "cat_games":"গেমস","cat_games_ex":"Snake · Tetris\nChess · 2048",
        "cat_apps":"অ্যাপস","cat_apps_ex":"Dashboard · Todo\nই-কমার্স",
        "cat_code":"কোড","cat_code_ex":"Python · JS · Java\nC++ · Go · Rust",
        "cat_files":"ফাইলস","cat_files_ex":"CSV · JSON · কোড\nAI বিশ্লেষণ করে",
        "cat_charts":"চার্ট ও ডেটা","cat_charts_ex":"CSV আপলোড করুন\nচার্ট স্বয়ংক্রিয়ভাবে তৈরি\nAI অন্তর্দৃষ্টি",
        "cat_live":"লাইভ ডেটা","cat_live_ex":"ক্রিকেট · শেয়ার\nআবহাওয়া · সংবাদ",
        "img_btn":"🖼️ ছবি","img_btn_done":"🖼️ ✓",
        "file_btn":"📄 ফাইল","file_btn_done":"📄 ✓",
        "csv_btn":"📊 CSV","csv_btn_done":"📊 ✓",
        "help_btn":"❓ সাহায্য","settings":"⚙️ মডেল সেটিংস","temperature":"তাপমাত্রা","max_length":"সর্বোচ্চ দৈর্ঘ্য",
        "ai_mode":"🎭 AI মোড","quick_tools":"🛠️ দ্রুত সরঞ্জাম",
        "currency":"💱 মুদ্রা","units":"📐 একক","calculator":"🔢 ক্যালকুলেটর","qr_code":"📱 QR কোড",
        "export":"💾 রপ্তানি","no_msgs":"এখনো কোনো বার্তা নেই।",
        "convert_btn":"রূপান্তর করুন 💱","calc_btn":"গণনা করুন 🔢","unit_btn":"রূপান্তর করুন 📐","qr_btn":"QR তৈরি করুন",
        "download_md":"📝 MD","download_json":"📊 JSON",
        "img_upload_title":"👁️ ভিশন AI-এর জন্য ছবি আপলোড করুন","img_upload_hint":"সমর্থিত: JPG, PNG, GIF, BMP, WebP, TIFF",
        "file_upload_title":"📁 বিশ্লেষণের জন্য ফাইল আপলোড করুন","file_upload_hint":"সমর্থিত: TXT, CSV, JSON, Python, JS",
        "csv_upload_title":"📊 ডেটা ভিজ্যুয়ালাইজেশনের জন্য CSV আপলোড করুন","csv_upload_hint":"যেকোনো CSV ফাইল আপলোড করুন — Nova AI স্বয়ংক্রিয়ভাবে চার্ট তৈরি করবে",
        "img_ready":"প্রস্তুত · নিচে আপনার প্রশ্ন টাইপ করুন ↓","file_ready":"এই ফাইল সম্পর্কে যেকোনো কিছু জিজ্ঞাসা করুন",
        "csv_ready":"CSV লোড হয়েছে · চার্ট স্বয়ংক্রিয়ভাবে তৈরি!",
        "analyzing":"👁️ ছবি বিশ্লেষণ হচ্ছে…","searching":"🔍 অনুসন্ধান হচ্ছে…",
        "fetching_weather":"🌤️ আবহাওয়া আনা হচ্ছে…","fetching_stock":"📈 ডেটা আনা হচ্ছে",
        "fetching_sports":"🏏 লাইভ স্পোর্টস ডেটা আনা হচ্ছে…","fetching_news":"📰 সংবাদ আনা হচ্ছে…",
        "fetching_rate":"💱 বিনিময় হার আনা হচ্ছে…","reading_url":"🌐 পড়া হচ্ছে",
        "running_code":"⚙️ চালানো হচ্ছে","run_btn":"▶ চালান",
        "live_preview":"🖥️ প্রিভিউ","live_game":"🎮 লাইভ গেম!","live_app":"🚀 লাইভ অ্যাপ",
        "live_software":"⚙️ লাইভ সফটওয়্যার","live_design":"✨ লাইভ ডিজাইন",
        "download":"⬇️ ডাউনলোড","example_q":"💡 উদাহরণ প্রশ্ন:","ex1":"এই ছবিতে কী আছে?",
        "ex2":"টেক্সট পড়ুন","ex3":"এই গণিত সমাধান করুন","ex4":"এই কোড বুঝিয়ে দিন","ex5":"এই চার্ট বিশ্লেষণ করুন",
        "unit_placeholder":"যেমন: ১০০ কিমি থেকে মাইল","calc_placeholder":"যেমন: sqrt(144)",
        "qr_placeholder":"টেক্সট বা URL","amount":"পরিমাণ","from_curr":"থেকে","to_curr":"তে",
        "no_results":"কোনো ফলাফল নেই।","stat_memory":"🧠 মেমোরি","stat_vision":"👁️ ভিশন AI",
        "stat_sports":"🏏 লাইভ স্পোর্টস","stat_games":"🎮 গেমস ও অ্যাপস",
        "stat_files":"📁 ফাইলস ও URLs","stat_live":"💱 লাইভ ডেটা","stat_charts":"📊 ডেটা ভিজ",
        "language_label":"🌍 ভাষা","sys_prompt_lang":"বাংলায় উত্তর দিন।",
        "chart_title":"📊 স্বয়ংক্রিয় চার্ট","chart_overview":"📋 ডেটাসেট ওভারভিউ","chart_ai_insights":"🤖 AI ডেটা অন্তর্দৃষ্টি",
        "chart_rows":"সারি","chart_cols":"কলাম","chart_numeric":"সংখ্যাসূচক কলাম",
        "chart_categorical":"শ্রেণীবদ্ধ কলাম","chart_missing":"অনুপস্থিত মান",
        "chart_ask":"এই ডেটা সম্পর্কে AI-কে জিজ্ঞাসা করুন…","chart_generating":"📊 চার্ট তৈরি হচ্ছে…",
        "chart_analyzing":"🤖 AI ডেটা বিশ্লেষণ করছে…","chart_types":"চার্ট ধরন",
        "chart_select_x":"X-অক্ষ","chart_select_y":"Y-অক্ষ","chart_select_color":"রঙ দ্বারা",
        "chart_custom":"🎨 কাস্টম চার্ট বিল্ডার",
        "chart_bar":"বার","chart_line":"লাইন","chart_scatter":"স্ক্যাটার","chart_pie":"পাই",
        "chart_histogram":"হিস্টোগ্রাম","chart_box":"বক্স","chart_heatmap":"হিটম্যাপ",
        "chart_area":"এরিয়া","chart_violin":"ভায়োলিন","chart_sunburst":"সানবার্স্ট",
        "chart_generate":"চার্ট তৈরি করুন","chart_correlation":"পারস্পরিক সম্পর্ক ম্যাট্রিক্স",
        "chart_distribution":"বিতরণ বিশ্লেষণ","chart_summary":"পরিসংখ্যান সারসংক্ষেপ",
        "chart_top_insights":"শীর্ষ অন্তর্দৃষ্টি","chart_download_csv":"⬇️ CSV ডাউনলোড করুন",
    },
    "es": {
        "title":"Nova AI","subtitle":"La IA más inteligente — ve imágenes, crea apps, visualiza datos en vivo.",
        "badge":"EN VIVO · GRATIS · ILIMITADO · IA DE VISIÓN","chat_placeholder":"Pregunta lo que quieras — escribe aquí o haz clic en 🖼️ Imagen / 📄 Archivo / 📊 CSV…",
        "clear":"🗑️ Borrar","msgs":"mensaje","msgp":"mensajes","hero_q":"¿Qué quieres hacer hoy?",
        "cat_vision":"IA de Visión","cat_vision_ex":"Sube cualquier imagen\nIA lee y analiza",
        "cat_games":"Juegos","cat_games_ex":"Snake · Tetris\nAjedrez · 2048",
        "cat_apps":"Aplicaciones","cat_apps_ex":"Dashboard · Todo\nE-commerce",
        "cat_code":"Código","cat_code_ex":"Python · JS · Java\nC++ · Go · Rust",
        "cat_files":"Archivos","cat_files_ex":"CSV · JSON · Código\nIA lo analiza",
        "cat_charts":"Gráficos y Datos","cat_charts_ex":"Sube CSV\nGráficos automáticos\nAnálisis IA",
        "cat_live":"Datos en Vivo","cat_live_ex":"Cricket · Bolsa\nClima · Noticias",
        "img_btn":"🖼️ Imagen","img_btn_done":"🖼️ ✓",
        "file_btn":"📄 Archivo","file_btn_done":"📄 ✓",
        "csv_btn":"📊 CSV","csv_btn_done":"📊 ✓",
        "help_btn":"❓ Ayuda","settings":"⚙️ Ajustes","temperature":"Temperatura","max_length":"Longitud máx.",
        "ai_mode":"🎭 Modo IA","quick_tools":"🛠️ Herramientas",
        "currency":"💱 Divisa","units":"📐 Unidades","calculator":"🔢 Calculadora","qr_code":"📱 Código QR",
        "export":"💾 Exportar","no_msgs":"Aún no hay mensajes.",
        "convert_btn":"Convertir 💱","calc_btn":"Calcular 🔢","unit_btn":"Convertir 📐","qr_btn":"Generar QR",
        "download_md":"📝 MD","download_json":"📊 JSON",
        "img_upload_title":"👁️ Subir imagen para IA de Visión","img_upload_hint":"Soporta: JPG, PNG, GIF, BMP, WebP, TIFF",
        "file_upload_title":"📁 Subir archivo para análisis","file_upload_hint":"Soporta: TXT, CSV, JSON, Python, JS",
        "csv_upload_title":"📊 Subir CSV para Visualización de Datos","csv_upload_hint":"Sube cualquier CSV — Nova AI genera gráficos automáticamente",
        "img_ready":"Listo · Escribe tu pregunta abajo ↓","file_ready":"Pregúntame sobre este archivo",
        "csv_ready":"¡CSV cargado · Gráficos generados automáticamente!",
        "analyzing":"👁️ Analizando imagen…","searching":"🔍 Buscando…",
        "fetching_weather":"🌤️ Obteniendo clima…","fetching_stock":"📈 Obteniendo",
        "fetching_sports":"🏏 Obteniendo datos deportivos…","fetching_news":"📰 Obteniendo noticias…",
        "fetching_rate":"💱 Obteniendo tasas…","reading_url":"🌐 Leyendo",
        "running_code":"⚙️ Ejecutando","run_btn":"▶ Ejecutar",
        "live_preview":"🖥️ Vista previa","live_game":"🎮 ¡Juego en Vivo!","live_app":"🚀 App en Vivo",
        "live_software":"⚙️ Software en Vivo","live_design":"✨ Diseño en Vivo",
        "download":"⬇️ Descargar","example_q":"💡 Ejemplos:","ex1":"¿Qué hay en esta imagen?",
        "ex2":"Lee el texto","ex3":"Resuelve esta matemática","ex4":"Explica este código","ex5":"Analiza este gráfico",
        "unit_placeholder":"ej. 100 km a millas","calc_placeholder":"ej. sqrt(144)",
        "qr_placeholder":"Texto o URL","amount":"Cantidad","from_curr":"De","to_curr":"A",
        "no_results":"Sin resultados.","stat_memory":"🧠 Memoria","stat_vision":"👁️ Visión IA",
        "stat_sports":"🏏 Deportes","stat_games":"🎮 Juegos y Apps",
        "stat_files":"📁 Archivos y URLs","stat_live":"💱 Datos en Vivo","stat_charts":"📊 Visualización",
        "language_label":"🌍 Idioma","sys_prompt_lang":"Responde en español.",
        "chart_title":"📊 Gráficos Automáticos","chart_overview":"📋 Resumen del Dataset","chart_ai_insights":"🤖 Análisis IA",
        "chart_rows":"filas","chart_cols":"columnas","chart_numeric":"Columnas numéricas",
        "chart_categorical":"Columnas categóricas","chart_missing":"Valores faltantes",
        "chart_ask":"Pregunta a la IA sobre estos datos…","chart_generating":"📊 Generando gráficos…",
        "chart_analyzing":"🤖 IA analizando datos…","chart_types":"Tipos de gráfico",
        "chart_select_x":"Eje X","chart_select_y":"Eje Y","chart_select_color":"Color por",
        "chart_custom":"🎨 Constructor de Gráficos",
        "chart_bar":"Barras","chart_line":"Línea","chart_scatter":"Dispersión","chart_pie":"Tarta",
        "chart_histogram":"Histograma","chart_box":"Caja","chart_heatmap":"Mapa de calor",
        "chart_area":"Área","chart_violin":"Violín","chart_sunburst":"Sol",
        "chart_generate":"Generar Gráfico","chart_correlation":"Matriz de Correlación",
        "chart_distribution":"Análisis de Distribución","chart_summary":"Resumen Estadístico",
        "chart_top_insights":"Principales Insights","chart_download_csv":"⬇️ Descargar CSV",
    },
}
# Fill remaining languages with English fallback
for _lc in ["fr","de","ja","zh","ar","ru","pt","ko"]:
    if _lc not in UI_TEXT:
        UI_TEXT[_lc] = UI_TEXT["en"].copy()
UI_TEXT["fr"].update({"sys_prompt_lang":"Répondez en français.","badge":"EN DIRECT · GRATUIT · ILLIMITÉ · IA VISION"})
UI_TEXT["de"].update({"sys_prompt_lang":"Antworten Sie auf Deutsch.","badge":"LIVE · KOSTENLOS · UNBEGRENZT · VISION KI"})
UI_TEXT["ja"].update({"sys_prompt_lang":"日本語で答えてください。","badge":"ライブ · 無料 · 無制限 · ビジョンAI"})
UI_TEXT["zh"].update({"sys_prompt_lang":"请用中文回答。","badge":"实时 · 免费 · 无限 · 视觉AI"})
UI_TEXT["ar"].update({"sys_prompt_lang":"أجب باللغة العربية.","badge":"مباشر · مجاني · غير محدود · رؤية AI"})
UI_TEXT["ru"].update({"sys_prompt_lang":"Отвечайте на русском языке.","badge":"LIVE · БЕСПЛАТНО · БЕЗЛИМИТНО · VISION AI"})
UI_TEXT["pt"].update({"sys_prompt_lang":"Responda em português.","badge":"AO VIVO · GRÁTIS · ILIMITADO · IA DE VISÃO"})
UI_TEXT["ko"].update({"sys_prompt_lang":"한국어로 답변해 주세요.","badge":"실시간 · 무료 · 무제한 · 비전 AI"})

def T(key: str) -> str:
    lang_code = st.session_state.get("lang_code", "en")
    return UI_TEXT.get(lang_code, UI_TEXT["en"]).get(key, UI_TEXT["en"].get(key, key))

def is_rtl() -> bool:
    return st.session_state.get("lang_code", "en") == "ar"

st.set_page_config(page_title="Nova AI", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

rtl_css = "body,[data-testid='stAppViewContainer']{direction:rtl!important;text-align:right!important;}[data-testid='stChatInput']{direction:rtl!important;}[data-testid='stSidebar']{direction:rtl!important;}" if is_rtl() else ""

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&family=Noto+Sans+Devanagari:wght@400;500&family=Noto+Sans+Bengali:wght@400;500&family=Noto+Sans+Arabic:wght@400;500&display=swap');
:root{{--bg:#0a0c10;--surface:#111318;--surface2:#1a1d24;--border:#232730;--accent:#00e5ff;--text:#e2e8f0;--muted:#64748b;--user-bg:#131b2e;--green:#10b981;--purple:#7c3aed;--orange:#f59e0b;--red:#ef4444;--pink:#ec4899;--radius:14px;}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
html,body,[data-testid="stAppViewContainer"]{{background:var(--bg)!important;color:var(--text)!important;font-family:'DM Sans','Noto Sans Devanagari','Noto Sans Bengali','Noto Sans Arabic',sans-serif!important;}}
[data-testid="stHeader"],[data-testid="stToolbar"],.stDeployButton,#MainMenu,footer{{display:none!important;}}
::-webkit-scrollbar{{width:4px;}}::-webkit-scrollbar-track{{background:var(--bg);}}::-webkit-scrollbar-thumb{{background:var(--border);border-radius:4px;}}
[data-testid="stAppViewContainer"]>.main>.block-container{{max-width:960px!important;padding:0 1.5rem 10rem!important;margin:0 auto!important;}}
[data-testid="stSidebar"]{{background:var(--surface)!important;border-right:1px solid var(--border)!important;}}
[data-testid="stSidebar"] *{{color:var(--text)!important;}}
[data-testid="stSidebar"] .stSelectbox>div,[data-testid="stSidebar"] .stTextInput>div>div{{background:var(--surface2)!important;border-color:var(--border)!important;}}
[data-testid="stSidebar"] label{{color:var(--muted)!important;font-size:12px!important;}}
[data-testid="stSidebar"] h3{{color:var(--accent)!important;font-family:'Space Mono',monospace!important;font-size:13px!important;margin:.8rem 0 .4rem!important;}}
[data-testid="stSidebar"] hr{{border-color:var(--border)!important;}}
[data-testid="stSidebar"] .stButton>button{{width:100%!important;background:var(--surface2)!important;border:1px solid var(--border)!important;color:var(--muted)!important;border-radius:8px!important;font-size:12px!important;}}
[data-testid="stSidebar"] .stButton>button:hover{{border-color:var(--accent)!important;color:var(--accent)!important;}}
[data-testid="stSidebar"] .stDownloadButton>button{{width:100%!important;background:rgba(0,229,255,.08)!important;border:1px solid rgba(0,229,255,.25)!important;color:var(--accent)!important;border-radius:8px!important;font-size:12px!important;}}
[data-testid="stSidebar"] .stExpander{{background:var(--surface2)!important;border:1px solid var(--border)!important;border-radius:10px!important;margin-bottom:.4rem!important;}}
.hero{{text-align:center;padding:2.5rem 1rem 1.5rem;position:relative;}}
.hero::before{{content:'';position:absolute;top:0;left:50%;transform:translateX(-50%);width:600px;height:300px;background:radial-gradient(ellipse at center,rgba(0,229,255,.07) 0%,transparent 70%);pointer-events:none;}}
.hero-badge{{display:inline-flex;align-items:center;gap:6px;background:rgba(0,229,255,.08);border:1px solid rgba(0,229,255,.2);border-radius:999px;padding:4px 14px;font-family:'Space Mono',monospace;font-size:11px;color:var(--accent);letter-spacing:.05em;margin-bottom:1rem;}}
.hero-badge::before{{content:'●';font-size:8px;animation:pulse 2s infinite;}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
.hero h1{{font-family:'Space Mono',monospace!important;font-size:clamp(1.8rem,4vw,2.6rem)!important;font-weight:700!important;color:#fff!important;line-height:1.15!important;letter-spacing:-.02em;margin-bottom:.5rem!important;}}
.hero h1 span{{color:var(--accent);}}
.hero p{{font-size:.95rem;color:var(--muted);font-weight:300;max-width:480px;margin:0 auto;}}
.divider{{height:1px;background:linear-gradient(90deg,transparent,var(--border),transparent);margin:1.2rem 0;}}
.stats-row{{display:flex;gap:.6rem;margin:1rem 0 1.5rem;justify-content:center;flex-wrap:wrap;}}
.stat-pill{{display:flex;align-items:center;gap:6px;background:var(--surface);border:1px solid var(--border);border-radius:999px;padding:5px 12px;font-size:12px;color:var(--muted);}}
.stat-pill .dot{{width:6px;height:6px;border-radius:50%;}}
.dot-green{{background:var(--green);box-shadow:0 0 5px var(--green);}}.dot-blue{{background:var(--accent);box-shadow:0 0 5px var(--accent);}}.dot-purple{{background:var(--purple);box-shadow:0 0 5px var(--purple);}}.dot-orange{{background:var(--orange);box-shadow:0 0 5px var(--orange);}}.dot-pink{{background:var(--pink);box-shadow:0 0 5px var(--pink);}}
[data-testid="stChatMessage"]{{background:transparent!important;border:none!important;padding:0!important;}}
[data-testid="stChatMessage"]>div{{background:transparent!important;}}
[data-testid="stChatMessageContent"]{{background:transparent!important;}}
.stChatMessage{{border-radius:var(--radius)!important;padding:1rem 1.2rem!important;border:1px solid var(--border)!important;margin-bottom:.6rem!important;background:var(--surface)!important;animation:fadeUp .25s ease;}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}
.stChatMessage:has([data-testid="chatAvatarIcon-user"]){{background:var(--user-bg)!important;border-color:rgba(0,229,255,.15)!important;}}
pre,code{{font-family:'Space Mono',monospace!important;font-size:13px!important;}}
pre{{background:#0d1117!important;border:1px solid var(--border)!important;border-left:3px solid var(--accent)!important;border-radius:10px!important;padding:1rem 1.2rem!important;overflow-x:auto!important;}}
code:not(pre code){{background:rgba(0,229,255,.08)!important;color:var(--accent)!important;border-radius:5px!important;padding:2px 6px!important;font-size:12.5px!important;}}
[data-testid="stChatInputContainer"]{{position:fixed!important;bottom:0!important;left:50%!important;transform:translateX(-50%)!important;width:100%!important;max-width:960px!important;padding:0.5rem 1.5rem 1.2rem!important;background:linear-gradient(to top,var(--bg) 80%,transparent)!important;backdrop-filter:blur(12px);z-index:999!important;}}
[data-testid="stChatInput"]{{background:var(--surface2)!important;border:1px solid var(--border)!important;border-radius:12px!important;color:var(--text)!important;font-size:15px!important;}}
[data-testid="stChatInput"]:focus{{border-color:var(--accent)!important;box-shadow:0 0 0 3px rgba(0,229,255,.1)!important;outline:none!important;}}
[data-testid="stChatInputSubmitButton"] button{{background:var(--accent)!important;border:none!important;border-radius:8px!important;color:#000!important;font-weight:600!important;}}
.badge{{display:inline-flex;align-items:center;gap:5px;border-radius:6px;padding:3px 10px;font-size:11px;margin-bottom:.5rem;}}
.badge-green{{background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.25);color:var(--green);}}
.badge-red{{background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.3);color:#fca5a5;}}
.badge-purple{{background:rgba(124,58,237,.08);border:1px solid rgba(124,58,237,.3);color:#a78bfa;}}
.badge-orange{{background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.3);color:var(--orange);}}
.badge-blue{{background:rgba(0,229,255,.08);border:1px solid rgba(0,229,255,.25);color:var(--accent);}}
.badge-pink{{background:rgba(236,72,153,.08);border:1px solid rgba(236,72,153,.3);color:var(--pink);}}
.badge-teal{{background:rgba(20,184,166,.08);border:1px solid rgba(20,184,166,.3);color:#2dd4bf;}}
.output-box{{background:#0d1117;border:1px solid var(--border);border-left:3px solid var(--green);border-radius:10px;padding:.8rem 1.2rem;font-family:'Space Mono',monospace;font-size:13px;color:#a3e635;margin-top:.5rem;white-space:pre-wrap;}}
.error-box{{background:#1a0a0a;border:1px solid #7f1d1d;border-left:3px solid var(--red);border-radius:10px;padding:.8rem 1.2rem;font-family:'Space Mono',monospace;font-size:13px;color:#fca5a5;margin-top:.5rem;white-space:pre-wrap;}}
.result-box{{background:linear-gradient(135deg,#0d1117,#111827);border:1px solid var(--border);border-radius:10px;padding:.8rem 1.2rem;font-size:14px;color:var(--text);margin:.5rem 0;}}
.result-box.orange{{border-left:3px solid var(--orange);}}.result-box.green{{border-left:3px solid var(--green);}}
.btn-download{{display:inline-flex;align-items:center;gap:5px;background:rgba(0,229,255,.1);border:1px solid rgba(0,229,255,.3);color:var(--accent);padding:6px 14px;border-radius:8px;text-decoration:none;font-size:12px;font-weight:500;margin-top:.5rem;}}
.stButton>button{{background:var(--surface2)!important;border:1px solid var(--border)!important;color:var(--muted)!important;border-radius:8px!important;font-size:13px!important;font-weight:500!important;padding:.4rem 1rem!important;transition:all .2s!important;}}
.stButton>button:hover{{border-color:var(--accent)!important;color:var(--accent)!important;background:rgba(0,229,255,.06)!important;}}
.category-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:.8rem;margin:1.2rem 0;}}
.category-card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1rem;text-align:center;transition:border-color .2s,transform .2s;}}
.category-card:hover{{border-color:var(--accent);transform:translateY(-2px);}}
.category-icon{{font-size:1.6rem;margin-bottom:.4rem;}}.category-title{{font-size:12.5px;font-weight:600;color:#94a3b8;margin-bottom:.2rem;}}.category-examples{{font-size:11px;color:var(--muted);line-height:1.6;}}
.chat-image{{max-width:360px;max-height:280px;border-radius:12px;border:1px solid var(--border);margin-bottom:8px;display:block;object-fit:cover;}}

/* ── DATA VIZ STYLES ── */
.viz-container{{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:1.5rem;margin:1rem 0;}}
.viz-header{{display:flex;align-items:center;gap:10px;margin-bottom:1rem;}}
.viz-title{{font-family:'Space Mono',monospace;font-size:14px;color:var(--accent);font-weight:700;}}
.viz-subtitle{{font-size:12px;color:var(--muted);}}
.metric-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:.8rem;margin:1rem 0;}}
.metric-card{{background:var(--surface2);border:1px solid var(--border);border-radius:12px;padding:1rem;text-align:center;transition:border-color .2s;}}
.metric-card:hover{{border-color:var(--accent);}}
.metric-value{{font-family:'Space Mono',monospace;font-size:1.4rem;font-weight:700;color:var(--accent);}}
.metric-label{{font-size:11px;color:var(--muted);margin-top:.3rem;}}
.insight-card{{background:linear-gradient(135deg,rgba(0,229,255,.05),rgba(124,58,237,.05));border:1px solid rgba(0,229,255,.15);border-radius:12px;padding:1rem 1.2rem;margin:.4rem 0;}}
.insight-icon{{font-size:1.1rem;margin-right:.4rem;}}
.insight-text{{font-size:13px;color:var(--text);line-height:1.6;}}
.chart-tab{{display:inline-flex;align-items:center;gap:5px;background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:5px 12px;font-size:12px;color:var(--muted);cursor:pointer;margin:.2rem;transition:all .2s;}}
.chart-tab:hover,.chart-tab.active{{border-color:var(--accent);color:var(--accent);background:rgba(0,229,255,.06);}}
.data-table-wrap{{background:#0d1117;border:1px solid var(--border);border-radius:10px;overflow:hidden;margin-top:.8rem;}}
.csv-drop-zone{{background:linear-gradient(135deg,rgba(0,229,255,.04),rgba(124,58,237,.04));border:2px dashed rgba(0,229,255,.25);border-radius:16px;padding:2rem;text-align:center;margin:1rem 0;transition:border-color .3s;}}
.csv-drop-zone:hover{{border-color:var(--accent);}}
.csv-icon{{font-size:2.5rem;margin-bottom:.5rem;}}
.csv-hint{{font-size:12px;color:var(--muted);margin-top:.4rem;}}
.lang-selector-wrap{{display:flex;align-items:center;gap:8px;background:rgba(0,229,255,.05);border:1px solid rgba(0,229,255,.15);border-radius:12px;padding:8px 12px;margin-bottom:8px;}}
{rtl_css}
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
#  ████████  DATA VISUALIZATION ENGINE  ████████
# ══════════════════════════════════════════════════════════════════════════════

PLOTLY_THEME = dict(
    template   = "plotly_dark",
    paper_bgcolor = "#111318",
    plot_bgcolor  = "#0d1117",
    font_color    = "#e2e8f0",
    font_family   = "DM Sans, sans-serif",
    colorway   = ["#00e5ff","#7c3aed","#10b981","#f59e0b","#ec4899",
                  "#3b82f6","#ef4444","#a78bfa","#34d399","#fbbf24"],
)

def apply_theme(fig):
    """Apply Nova dark theme to any Plotly figure."""
    fig.update_layout(
        template      = "plotly_dark",
        paper_bgcolor = PLOTLY_THEME["paper_bgcolor"],
        plot_bgcolor  = PLOTLY_THEME["plot_bgcolor"],
        font          = dict(color=PLOTLY_THEME["font_color"], family=PLOTLY_THEME["font_family"]),
        margin        = dict(l=40, r=40, t=60, b=40),
        legend        = dict(bgcolor="rgba(0,0,0,0)", bordercolor="#232730"),
        hoverlabel    = dict(bgcolor="#1a1d24", bordercolor="#232730", font_color="#e2e8f0"),
    )
    fig.update_xaxes(gridcolor="#232730", zerolinecolor="#232730")
    fig.update_yaxes(gridcolor="#232730", zerolinecolor="#232730")
    return fig

def parse_csv(uploaded_file) -> pd.DataFrame | None:
    """Robust CSV parser — tries multiple encodings & separators."""
    uploaded_file.seek(0)
    raw = uploaded_file.read()
    for enc in ["utf-8","latin-1","cp1252","utf-16"]:
        try:
            text = raw.decode(enc)
            for sep in [",",";","\t","|"]:
                try:
                    df = pd.read_csv(io.StringIO(text), sep=sep, engine="python")
                    if len(df.columns) > 1:
                        # Clean column names
                        df.columns = [str(c).strip() for c in df.columns]
                        # Auto-convert numeric columns
                        for col in df.columns:
                            try:
                                df[col] = pd.to_numeric(df[col].astype(str).str.replace(",",""), errors="ignore")
                            except: pass
                        return df
                except: pass
        except: pass
    return None

def get_col_types(df: pd.DataFrame):
    """Returns (numeric_cols, categorical_cols, datetime_cols)."""
    num  = df.select_dtypes(include=np.number).columns.tolist()
    cat  = df.select_dtypes(include=["object","category","bool"]).columns.tolist()
    # Try detecting datetime
    dt_cols = []
    for c in cat[:]:
        try:
            pd.to_datetime(df[c], infer_datetime_format=True)
            dt_cols.append(c)
        except: pass
    return num, cat, dt_cols

def smart_insights(df: pd.DataFrame, num_cols, cat_cols) -> list[str]:
    """Generate automatic statistical insights."""
    insights = []
    # Shape
    insights.append(f"📐 Dataset has **{len(df):,}** rows and **{len(df.columns)}** columns.")
    # Missing
    missing = df.isnull().sum().sum()
    if missing > 0:
        pct = missing / (df.shape[0]*df.shape[1]) * 100
        insights.append(f"⚠️ **{missing:,}** missing values detected ({pct:.1f}% of data).")
    else:
        insights.append("✅ No missing values — dataset is complete.")
    # Numeric insights
    for col in num_cols[:4]:
        s = df[col].dropna()
        if len(s) == 0: continue
        skew = s.skew()
        skew_label = "right-skewed" if skew > 0.5 else "left-skewed" if skew < -0.5 else "normally distributed"
        insights.append(f"📊 **{col}**: mean={s.mean():.2f}, std={s.std():.2f}, range=[{s.min():.2f}, {s.max():.2f}] — {skew_label}.")
    # Categorical insights
    for col in cat_cols[:3]:
        vc = df[col].value_counts()
        if len(vc) > 0:
            top_val = vc.index[0]
            top_pct = vc.iloc[0] / len(df) * 100
            insights.append(f"🏷️ **{col}**: {df[col].nunique()} unique values. Most common: **'{top_val}'** ({top_pct:.1f}%).")
    # Correlation
    if len(num_cols) >= 2:
        corr = df[num_cols].corr()
        pairs = []
        for i in range(len(num_cols)):
            for j in range(i+1, len(num_cols)):
                v = corr.iloc[i,j]
                if abs(v) > 0.6:
                    pairs.append((num_cols[i], num_cols[j], v))
        if pairs:
            pairs.sort(key=lambda x: abs(x[2]), reverse=True)
            a,b,v = pairs[0]
            direction = "positively" if v > 0 else "negatively"
            insights.append(f"🔗 **{a}** and **{b}** are strongly {direction} correlated (r={v:.2f}).")
    return insights

def auto_charts(df: pd.DataFrame, num_cols, cat_cols, filename="data") -> list:
    """Auto-generate the most useful charts based on data types."""
    charts = []

    # ── 1. Distribution of first numeric col ──────────────────────────────
    if num_cols:
        col = num_cols[0]
        fig = px.histogram(df, x=col, nbins=30,
                           title=f"Distribution of {col}",
                           color_discrete_sequence=["#00e5ff"])
        fig.update_traces(marker_line_color="#232730", marker_line_width=1)
        charts.append(("histogram", f"📊 Distribution — {col}", fig))

    # ── 2. Top categories bar chart ────────────────────────────────────────
    if cat_cols and num_cols:
        cat, num = cat_cols[0], num_cols[0]
        if df[cat].nunique() <= 30:
            grp = df.groupby(cat)[num].mean().nlargest(15).reset_index()
            fig = px.bar(grp, x=cat, y=num,
                         title=f"Average {num} by {cat}",
                         color=num,
                         color_continuous_scale="Teal")
            fig.update_layout(xaxis_tickangle=-35)
            charts.append(("bar", f"📊 Bar — {num} by {cat}", fig))

    # ── 3. Scatter / relationship ──────────────────────────────────────────
    if len(num_cols) >= 2:
        x, y = num_cols[0], num_cols[1]
        color_col = cat_cols[0] if cat_cols and df[cat_cols[0]].nunique() <= 12 else None
        fig = px.scatter(df, x=x, y=y, color=color_col,
                         title=f"{x} vs {y}",
                         opacity=0.75,
                         trendline="ols" if len(df) < 5000 else None,
                         color_discrete_sequence=PLOTLY_THEME["colorway"])
        charts.append(("scatter", f"📊 Scatter — {x} vs {y}", fig))

    # ── 4. Pie / donut for top category ───────────────────────────────────
    if cat_cols:
        cat = cat_cols[0]
        vc = df[cat].value_counts().nlargest(8)
        fig = px.pie(values=vc.values, names=vc.index,
                     title=f"Composition of {cat}",
                     hole=0.4,
                     color_discrete_sequence=PLOTLY_THEME["colorway"])
        fig.update_traces(textposition="inside", textinfo="percent+label")
        charts.append(("pie", f"🥧 Pie — {cat}", fig))

    # ── 5. Line chart (time or index) ──────────────────────────────────────
    if num_cols:
        col = num_cols[0]
        fig = px.line(df.reset_index(), x="index", y=col,
                      title=f"Trend of {col}",
                      color_discrete_sequence=["#10b981"])
        fig.update_traces(line_width=2)
        charts.append(("line", f"📈 Trend — {col}", fig))

    # ── 6. Box plot — spread analysis ──────────────────────────────────────
    if num_cols:
        cols_to_plot = num_cols[:6]
        df_melt = df[cols_to_plot].melt(var_name="Column", value_name="Value")
        fig = px.box(df_melt, x="Column", y="Value",
                     title="Distribution Spread (Box Plot)",
                     color="Column",
                     color_discrete_sequence=PLOTLY_THEME["colorway"])
        charts.append(("box", "📦 Box Plot — All Numeric", fig))

    # ── 7. Correlation heatmap ─────────────────────────────────────────────
    if len(num_cols) >= 3:
        corr = df[num_cols[:12]].corr().round(2)
        fig = px.imshow(corr,
                        text_auto=True,
                        aspect="auto",
                        title="Correlation Heatmap",
                        color_continuous_scale="RdBu_r",
                        zmin=-1, zmax=1)
        charts.append(("heatmap", "🔥 Correlation Heatmap", fig))

    # ── 8. Area chart ──────────────────────────────────────────────────────
    if len(num_cols) >= 2:
        cols = num_cols[:3]
        df_sample = df[cols].head(200)
        df_melt = df_sample.reset_index().melt(id_vars="index", var_name="Series", value_name="Value")
        fig = px.area(df_melt, x="index", y="Value", color="Series",
                      title="Area Chart — Numeric Trends",
                      color_discrete_sequence=PLOTLY_THEME["colorway"])
        charts.append(("area", "📉 Area — Multi-Series", fig))

    # Apply theme to all
    for i, (ctype, label, fig) in enumerate(charts):
        charts[i] = (ctype, label, apply_theme(fig))

    return charts

def build_custom_chart(df: pd.DataFrame, chart_type: str,
                       x_col: str, y_col: str, color_col: str | None) -> go.Figure | None:
    """Build a user-specified custom chart."""
    try:
        kwargs = dict(data_frame=df, x=x_col, title=f"{chart_type.title()}: {x_col} vs {y_col}",
                      color_discrete_sequence=PLOTLY_THEME["colorway"])
        if color_col and color_col != "None": kwargs["color"] = color_col

        if chart_type == "bar":
            fig = px.bar(df, x=x_col, y=y_col, **{k:v for k,v in kwargs.items() if k not in ["data_frame","x","title","color_discrete_sequence"]},
                         data_frame=df, title=kwargs["title"],
                         color_discrete_sequence=kwargs["color_discrete_sequence"])
        elif chart_type == "line":
            fig = px.line(df, x=x_col, y=y_col,
                          title=kwargs["title"],
                          color_discrete_sequence=kwargs["color_discrete_sequence"])
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x_col, y=y_col,
                             color=kwargs.get("color"),
                             title=kwargs["title"],
                             color_discrete_sequence=kwargs["color_discrete_sequence"],
                             opacity=0.75)
        elif chart_type == "area":
            fig = px.area(df, x=x_col, y=y_col,
                          title=kwargs["title"],
                          color_discrete_sequence=kwargs["color_discrete_sequence"])
        elif chart_type == "histogram":
            fig = px.histogram(df, x=x_col, nbins=30,
                               title=f"Distribution of {x_col}",
                               color_discrete_sequence=["#00e5ff"])
        elif chart_type == "box":
            fig = px.box(df, x=x_col if x_col != y_col else None, y=y_col,
                         color=kwargs.get("color"),
                         title=kwargs["title"],
                         color_discrete_sequence=kwargs["color_discrete_sequence"])
        elif chart_type == "violin":
            fig = px.violin(df, x=x_col if x_col != y_col else None, y=y_col,
                            color=kwargs.get("color"),
                            title=kwargs["title"],
                            box=True,
                            color_discrete_sequence=kwargs["color_discrete_sequence"])
        elif chart_type == "pie":
            vc = df[x_col].value_counts().nlargest(10)
            fig = px.pie(values=vc.values, names=vc.index,
                         title=f"Composition of {x_col}",
                         hole=0.4,
                         color_discrete_sequence=PLOTLY_THEME["colorway"])
        elif chart_type == "sunburst":
            if color_col and color_col != "None":
                fig = px.sunburst(df, path=[x_col, color_col], values=y_col if y_col in df.select_dtypes(include=np.number).columns.tolist() else None,
                                  title=kwargs["title"],
                                  color_discrete_sequence=PLOTLY_THEME["colorway"])
            else:
                vc = df[x_col].value_counts().nlargest(15)
                fig = px.sunburst(dict(names=vc.index.tolist(), parents=[""]*len(vc), values=vc.values.tolist()),
                                  names="names", parents="parents", values="values",
                                  title=f"Sunburst of {x_col}")
        else:
            return None
        return apply_theme(fig)
    except Exception as e:
        st.error(f"Chart error: {e}")
        return None

def render_data_viz_panel(df: pd.DataFrame, filename: str = "data.csv"):
    """Full data visualization panel rendered inline."""
    num_cols, cat_cols, dt_cols = get_col_types(df)

    st.markdown(f'<div class="badge badge-teal">📊 {T("chart_title")} · {filename}</div>', unsafe_allow_html=True)

    # ── Metric overview ────────────────────────────────────────────────────
    st.markdown(f"#### {T('chart_overview')}")
    metrics = [
        (f"{len(df):,}", T("chart_rows")),
        (str(len(df.columns)), T("chart_cols")),
        (str(len(num_cols)), T("chart_numeric")),
        (str(len(cat_cols)), T("chart_categorical")),
        (str(df.isnull().sum().sum()), T("chart_missing")),
        (f"{df.memory_usage(deep=True).sum()/1024:.1f} KB", "Memory"),
    ]
    cols = st.columns(len(metrics))
    for i, (val, label) in enumerate(metrics):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Data preview table ─────────────────────────────────────────────────
    with st.expander("📋 Preview Data (first 20 rows)", expanded=False):
        st.dataframe(
            df.head(20),
            use_container_width=True,
            hide_index=False,
        )
        # Statistical summary
        if num_cols:
            st.markdown("**📐 Statistical Summary**")
            st.dataframe(df[num_cols].describe().round(3), use_container_width=True)

    # ── AI Smart Insights ──────────────────────────────────────────────────
    st.markdown(f"#### {T('chart_ai_insights')}")
    insights = smart_insights(df, num_cols, cat_cols)
    for ins in insights:
        st.markdown(f"""
        <div class="insight-card">
            <span class="insight-text">{ins}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Auto-generated charts ──────────────────────────────────────────────
    st.markdown(f"#### {T('chart_title')}")

    with st.spinner(T("chart_generating")):
        charts = auto_charts(df, num_cols, cat_cols, filename)

    if charts:
        # Show charts in 2-column grid
        for i in range(0, len(charts), 2):
            c1, c2 = st.columns(2)
            with c1:
                _, label, fig = charts[i]
                st.markdown(f"<div style='font-size:12px;color:var(--muted);margin-bottom:4px'>{label}</div>", unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":True,"displaylogo":False})
            if i+1 < len(charts):
                with c2:
                    _, label, fig = charts[i+1]
                    st.markdown(f"<div style='font-size:12px;color:var(--muted);margin-bottom:4px'>{label}</div>", unsafe_allow_html=True)
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":True,"displaylogo":False})
    else:
        st.info("⚠️ Could not auto-generate charts. Try adding more numeric columns.")

    # ── Custom Chart Builder ────────────────────────────────────────────────
    st.markdown(f"#### {T('chart_custom')}")

    all_cols = df.columns.tolist()
    chart_types = {
        T("chart_bar"):"bar", T("chart_line"):"line", T("chart_scatter"):"scatter",
        T("chart_area"):"area", T("chart_histogram"):"histogram",
        T("chart_box"):"box", T("chart_violin"):"violin",
        T("chart_pie"):"pie", T("chart_sunburst"):"sunburst",
    }

    cb1, cb2, cb3, cb4, cb5 = st.columns([2,2,2,2,1])
    with cb1:
        chosen_type = st.selectbox(T("chart_types"), list(chart_types.keys()), key="cv_type")
    with cb2:
        x_col = st.selectbox(T("chart_select_x"), all_cols, key="cv_x")
    with cb3:
        y_default = num_cols[0] if num_cols else all_cols[0]
        y_col = st.selectbox(T("chart_select_y"), all_cols,
                             index=all_cols.index(y_default) if y_default in all_cols else 0,
                             key="cv_y")
    with cb4:
        color_opts = ["None"] + cat_cols
        color_col = st.selectbox(T("chart_select_color"), color_opts, key="cv_color")
    with cb5:
        st.markdown("<br>", unsafe_allow_html=True)
        gen_chart = st.button(T("chart_generate"), key="cv_gen", use_container_width=True)

    if gen_chart:
        cc = None if color_col == "None" else color_col
        custom_fig = build_custom_chart(df, chart_types[chosen_type], x_col, y_col, cc)
        if custom_fig:
            st.plotly_chart(custom_fig, use_container_width=True, config={"displayModeBar":True,"displaylogo":False})

    # ── Download processed CSV ─────────────────────────────────────────────
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label    = T("chart_download_csv"),
        data     = csv_bytes,
        file_name= f"nova_processed_{filename}",
        mime     = "text/csv",
        key      = "dl_csv_processed",
    )

def get_csv_ai_analysis(df: pd.DataFrame, question: str) -> str:
    """Ask AI about the loaded CSV data."""
    num_cols, cat_cols, _ = get_col_types(df)
    stats = df.describe(include="all").to_string()
    sample = df.head(10).to_string()
    corr = df[num_cols].corr().round(2).to_string() if len(num_cols) >= 2 else "N/A"
    context = (
        f"Dataset: {len(df)} rows × {len(df.columns)} columns\n"
        f"Columns: {list(df.columns)}\n"
        f"Numeric cols: {num_cols}\nCategorical cols: {cat_cols}\n\n"
        f"Statistical Summary:\n{stats}\n\n"
        f"Correlation Matrix:\n{corr}\n\n"
        f"Sample Data (first 10 rows):\n{sample}\n\n"
        f"Missing values per column:\n{df.isnull().sum().to_dict()}\n"
    )
    lang_instruction = T("sys_prompt_lang")
    messages = [
        {"role":"system","content":(
            f"You are Nova AI, an expert data analyst. {lang_instruction} "
            "Analyze the dataset provided and give clear, insightful answers. "
            "Use bullet points, bold key numbers, and be specific with statistics. "
            "Suggest visualizations when appropriate."
        )},
        {"role":"user","content":f"Dataset info:\n{context}\n\nQuestion: {question}"}
    ]
    return stream_response(messages, max_tokens=1024, temperature=0.2)

def is_csv_analysis_query(q: str) -> bool:
    """Detect if user is asking about a loaded CSV."""
    if not st.session_state.get("csv_df") is not None: return False
    keywords = ["data","csv","chart","graph","plot","column","row","average","mean",
                "max","min","correlation","trend","distribution","analyze","analyse",
                "insight","show me","tell me","what","how many","which","compare"]
    return any(k in q.lower() for k in keywords)

# ══════════════════════════════════════════════════════════════════════════════
#  IMAGE PROCESSING
# ══════════════════════════════════════════════════════════════════════════════
def image_to_base64(uploaded_file) -> tuple:
    try:
        uploaded_file.seek(0)
        img  = Image.open(uploaded_file)
        fmt  = img.format or "PNG"
        mime = f"image/{fmt.lower()}"
        if mime == "image/jpg": mime = "image/jpeg"
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
    except:
        return None, None, 0, 0

def get_vision_prompt(user_text: str) -> str:
    q = user_text.lower()
    if any(k in q for k in ["read","text","ocr","extract text","what does it say","written","transcribe"]):
        return f"Read and transcribe ALL text visible in this image exactly. Then answer: {user_text}"
    elif any(k in q for k in ["solve","calculate","math","equation","problem","formula"]):
        return f"Solve the math problem shown in this image. Show step-by-step working. {user_text}"
    elif any(k in q for k in ["code","program","script","debug","error","fix","bug"]):
        return f"Read the code in this image exactly. Explain what it does and identify any issues. {user_text}"
    elif any(k in q for k in ["chart","graph","table","data","plot","diagram","statistics"]):
        return f"Analyze this chart/graph/table in detail. Extract all data, trends, and insights. {user_text}"
    elif any(k in q for k in ["ui","design","website","app","interface","layout"]):
        return f"Analyze this UI/UX design. Describe layout, design choices, and suggest improvements. {user_text}"
    elif any(k in q for k in ["document","invoice","receipt","form","certificate","id","card"]):
        return f"Extract all information from this document carefully. {user_text}"
    else:
        return (
            "Analyze this image comprehensively:\n1. Describe everything in detail\n"
            "2. Read any visible text\n3. Identify objects, colors, patterns\n"
            f"Also answer: {user_text if user_text.strip() else 'What is in this image?'}"
        )

def analyze_image_stream(b64: str, mime: str, user_prompt: str) -> str:
    placeholder = st.empty()
    full        = ""
    lang_instruction = T("sys_prompt_lang")
    try:
        stream = client.chat.completions.create(
            model    = VISION_MODEL,
            messages = [
                {"role":"system","content":(
                    f"You are Nova AI with powerful vision. Created by Samiran. "
                    f"Analyze images with exceptional accuracy. {lang_instruction}"
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
#  STREAMING TEXT
# ══════════════════════════════════════════════════════════════════════════════
def stream_response(messages: list, max_tokens: int = 4096, temperature: float = 0.25) -> str:
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
    "🤖 Default":"","💻 Coder":"CODER MODE: Focus on perfect production-ready code.",
    "🎨 Creative":"CREATIVE MODE: Be imaginative and expressive.",
    "📊 Analyst":"ANALYST MODE: Be data-driven, precise, use tables.",
    "🎓 Teacher":"TEACHER MODE: Explain step by step with examples.",
    "✍️ Writer":"WRITER MODE: Clear, engaging, polished writing.",
    "📊 Data Scientist":"DATA SCIENCE MODE: Expert in statistics, ML, data analysis, visualization. Suggest Python code with pandas/plotly.",
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
    "f1":"F1 race","boxing":"boxing","mma":"MMA UFC","ufc":"UFC","olympics":"Olympics",
}
IPL_TEAMS = ["csk","mi","rcb","kkr","srh","pbks","dc","gt","lsg","rr",
             "chennai","mumbai","bangalore","kolkata","hyderabad",
             "punjab","delhi","gujarat","lucknow","rajasthan"]

LANGUAGE_MAP = {
    "python":("python","3.10.0"),"javascript":("javascript","18.15.0"),"js":("javascript","18.15.0"),
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
    sw = {"what","is","the","weather","report","temperature","forecast","today","current","now","like","how","give","me","show","humidity","climate","condition","a","an"}
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
    return (any(a in ql for a in ["stock","share price","stock price","price of","market price","trading at","crypto","bitcoin","ethereum","sensex","nifty","nasdaq","dow jones","coin price"]) or
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
    actions=["score","result","match","game","live","standings","winner","champion","playoff","final","tournament","who won","playing today","which team","schedule"]
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
                       headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},timeout=10)
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
        safe={"sin":math.sin,"cos":math.cos,"tan":math.tan,"asin":math.asin,"acos":math.acos,"atan":math.atan,
              "log":math.log10,"ln":math.log,"log2":math.log2,"sqrt":math.sqrt,"exp":math.exp,"abs":abs,
              "pi":math.pi,"e":math.e,"ceil":math.ceil,"floor":math.floor,"round":round,"pow":math.pow,"factorial":math.factorial}
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
    units=["km","miles","meters","feet","cm","inches","kg","pounds","grams","celsius","fahrenheit","kelvin","liters","gallons","mph","kmh","gb","mb","tb"]
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
    return {"game":T("live_game"),"app":T("live_app"),"software":T("live_software"),
            "design":T("live_design"),"code":"💻 Writing world-class code…","general":"✨ Thinking…"}.get(ct,"✨ Thinking…")

def get_system_prompt(ct):
    mode=st.session_state.get("ai_mode","🤖 Default")
    mode_extra=MODE_PROMPTS.get(mode,""); td=today_str()
    lang_instruction = T("sys_prompt_lang")
    base=(f"You are Nova AI — world's BEST AI assistant with vision and data analysis, created by Samiran. "
          f"Today: {td}. If asked who made you: 'Nova AI, created by Samiran.' "
          f"Never mention Meta, Llama, OpenAI, Groq. Full conversation memory. "
          f"NEVER write partial code. ALWAYS complete implementations. "
          f"Do NOT generate images — you can ANALYZE images but not create them. "
          f"{lang_instruction} {mode_extra}\n\n"
          f"LIVE DATA: When real-time data provided, use as ABSOLUTE TRUTH. Today is {td}.\n\n")
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
    ("ai_mode","🤖 Default"),("uploaded_file_content",None),("uploaded_file_name",None),
    ("pending_image_b64",None),("pending_image_mime",None),("pending_image_name",None),
    ("show_image_uploader",False),("show_file_uploader",False),("show_csv_uploader",False),
    ("lang_code","en"),("lang_name","🌐 English"),
    ("csv_df",None),("csv_filename",None),("csv_analyzed",False),
]:
    if key not in st.session_state: st.session_state[key]=default

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1.2rem 0 .8rem'>
        <div style='font-size:1.4rem;font-weight:700;font-family:Space Mono,monospace;color:#00e5ff'>✨ Nova AI</div>
        <div style='font-size:11px;color:#64748b;margin-top:.3rem'>Created by Samiran · v5.1</div>
    </div>""", unsafe_allow_html=True)
    st.divider()

    # ── Language ──────────────────────────────────────────────────────────
    st.markdown(f"### {T('language_label')}")
    st.markdown(f"""
    <div class="lang-selector-wrap">
        <span style="font-size:18px">{st.session_state['lang_name'].split()[0]}</span>
        <span style="font-size:13px;color:#00e5ff;font-weight:500">{st.session_state['lang_name']}</span>
    </div>""", unsafe_allow_html=True)

    lang_choice = st.selectbox("Language",list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state["lang_name"]),
        label_visibility="collapsed",key="lang_select")
    if lang_choice != st.session_state["lang_name"]:
        st.session_state["lang_name"]=lang_choice
        st.session_state["lang_code"]=LANGUAGES[lang_choice]
        st.rerun()

    lang_keys=list(LANGUAGES.keys())
    cols=st.columns(4)
    for i,lk in enumerate(lang_keys):
        with cols[i%4]:
            if st.button(lk.split()[0],key=f"lf_{LANGUAGES[lk]}",help=lk,use_container_width=True):
                st.session_state["lang_name"]=lk
                st.session_state["lang_code"]=LANGUAGES[lk]
                st.rerun()
    st.divider()

    # ── Settings ──────────────────────────────────────────────────────────
    st.markdown(f"### {T('settings')}")
    st.session_state["temperature"]=st.slider(T("temperature"),0.0,1.0,value=st.session_state["temperature"],step=0.05)
    st.session_state["max_tokens"]=st.select_slider(T("max_length"),options=[512,1024,2048,4096,8192],value=st.session_state["max_tokens"])
    st.divider()

    st.markdown(f"### {T('ai_mode')}")
    st.session_state["ai_mode"]=st.selectbox("Mode",list(MODE_PROMPTS.keys()),index=0,label_visibility="collapsed")
    st.divider()

    # ── CSV Quick Upload in Sidebar ────────────────────────────────────────
    st.markdown("### 📊 Quick CSV Upload")
    sidebar_csv = st.file_uploader("Drop CSV here",type=["csv"],key="sidebar_csv",label_visibility="collapsed")
    if sidebar_csv:
        df_tmp = parse_csv(sidebar_csv)
        if df_tmp is not None:
            st.session_state["csv_df"]       = df_tmp
            st.session_state["csv_filename"] = sidebar_csv.name
            st.session_state["csv_analyzed"] = False
            st.success(f"✅ {sidebar_csv.name} ({len(df_tmp):,} rows)")
        else:
            st.error("❌ Could not parse CSV")
    if st.session_state.get("csv_df") is not None:
        df_info = st.session_state["csv_df"]
        st.markdown(f"""
        <div style='background:rgba(0,229,255,.06);border:1px solid rgba(0,229,255,.2);
                    border-radius:10px;padding:8px 12px;margin-top:4px;'>
            <div style='font-size:12px;color:#00e5ff;font-weight:600'>📊 {st.session_state['csv_filename']}</div>
            <div style='font-size:11px;color:#64748b'>{len(df_info):,} rows · {len(df_info.columns)} cols</div>
        </div>""", unsafe_allow_html=True)
        if st.button("🗑️ Clear CSV",key="clear_csv_sb"):
            st.session_state["csv_df"]=None; st.session_state["csv_filename"]=None
            st.session_state["csv_analyzed"]=False; st.rerun()
    st.divider()

    # ── Quick Tools ────────────────────────────────────────────────────────
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
            res=convert_unit(uin); st.markdown(res if res else "⚠️ Try: '100 km to miles'")

    with st.expander(T("calculator")):
        cin=st.text_input(T("calc_placeholder"),key="sb_cin")
        if st.button(T("calc_btn"),key="sb_calc"):
            res=solve_math(cin)
            if res: st.markdown(f"**= {res}**")
            else: st.warning("Could not evaluate.")

    with st.expander(T("qr_code")):
        qin=st.text_input(T("qr_placeholder"),key="sb_qin")
        if st.button(T("qr_btn"),key="sb_qr") and qin:
            url=qr_url(qin); st.image(url,width=180); st.markdown(f"[⬇️ Download]({url})")

    st.divider()
    st.markdown(f"### {T('export')}")
    if st.session_state["messages"]:
        ca,cb=st.columns(2)
        ts=datetime.now().strftime("%Y%m%d_%H%M")
        with ca: st.download_button(T("download_md"),data=export_md(),file_name=f"nova_{ts}.md",mime="text/markdown",use_container_width=True)
        with cb: st.download_button(T("download_json"),data=export_json_chat(),file_name=f"nova_{ts}.json",mime="application/json",use_container_width=True)
    else: st.caption(T("no_msgs"))
    st.divider()
    st.markdown(f"<div style='text-align:center;font-size:10px;color:#374151'>Nova AI · Samiran · v5.1<br>{datetime.now().strftime('%B %Y')}</div>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero">
    <div class="hero-badge">{T('badge')}</div>
    <h1>Nova<span> AI</span></h1>
    <p>{T('subtitle')}</p>
</div>
<div class="stats-row">
    <div class="stat-pill"><span class="dot dot-purple"></span>{T('stat_memory')}</div>
    <div class="stat-pill"><span class="dot dot-pink"></span>{T('stat_vision')}</div>
    <div class="stat-pill"><span class="dot dot-blue"></span>{T('stat_sports')}</div>
    <div class="stat-pill"><span class="dot dot-orange"></span>{T('stat_games')}</div>
    <div class="stat-pill"><span class="dot dot-green"></span>{T('stat_files')}</div>
    <div class="stat-pill"><span class="dot dot-green"></span>{T('stat_live')}</div>
    <div class="stat-pill"><span class="dot dot-blue"></span>{T('stat_charts')}</div>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

col1,col2,col3=st.columns([5,1,1])
with col2:
    count=len([m for m in st.session_state.messages if m["role"]=="user"])
    label=f"{count} {T('msgp') if count!=1 else T('msgs')}"
    st.markdown(f"<p style='text-align:right;color:var(--muted);font-size:12px;padding-top:.5rem'>{label}</p>",unsafe_allow_html=True)
with col3:
    if st.button(T("clear")): st.session_state.messages=[]; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  CSV VISUALIZATION PANEL — shown above chat when CSV is loaded
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.get("csv_df") is not None and not st.session_state.get("csv_analyzed"):
    df   = st.session_state["csv_df"]
    fname= st.session_state.get("csv_filename","data.csv")
    render_data_viz_panel(df, fname)
    st.session_state["csv_analyzed"] = True
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
elif st.session_state.get("csv_df") is not None and st.session_state.get("csv_analyzed"):
    # Show compact toolbar for loaded CSV
    df   = st.session_state["csv_df"]
    fname= st.session_state.get("csv_filename","data.csv")
    with st.expander(f"📊 {fname} — {len(df):,} rows · Click to re-open charts", expanded=False):
        render_data_viz_panel(df, fname)

# ══════════════════════════════════════════════════════════════════════════════
#  CHAT HISTORY
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.messages:
    st.markdown(f"""
    <div style="text-align:center;padding:1rem 1rem .5rem">
        <div style="font-size:2rem;margin-bottom:.5rem">✨</div>
        <p style="font-size:.95rem;font-weight:600;color:#94a3b8;margin-bottom:1rem">{T('hero_q')}</p>
    </div>
    <div class="category-grid">
        <div class="category-card"><div class="category-icon">👁️</div><div class="category-title">{T('cat_vision')}</div><div class="category-examples">{T('cat_vision_ex')}</div></div>
        <div class="category-card"><div class="category-icon">📊</div><div class="category-title">{T('cat_charts')}</div><div class="category-examples">{T('cat_charts_ex')}</div></div>
        <div class="category-card"><div class="category-icon">🎮</div><div class="category-title">{T('cat_games')}</div><div class="category-examples">{T('cat_games_ex')}</div></div>
        <div class="category-card"><div class="category-icon">🚀</div><div class="category-title">{T('cat_apps')}</div><div class="category-examples">{T('cat_apps_ex')}</div></div>
        <div class="category-card"><div class="category-icon">💻</div><div class="category-title">{T('cat_code')}</div><div class="category-examples">{T('cat_code_ex')}</div></div>
        <div class="category-card"><div class="category-icon">🌐</div><div class="category-title">{T('cat_live')}</div><div class="category-examples">{T('cat_live_ex')}</div></div>
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

# ══════════════════════════════════════════════════════════════════════════════
#  PENDING PREVIEWS
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.get("pending_image_b64"):
    fname=st.session_state.get("pending_image_name","image")
    try:
        img_bytes=base64.b64decode(st.session_state["pending_image_b64"])
        ci,cinfo,cx=st.columns([1,5,1])
        with ci: st.image(Image.open(io.BytesIO(img_bytes)),width=56)
        with cinfo:
            st.markdown(f"<div style='padding-top:8px'><div style='font-size:13px;color:#e2e8f0;font-weight:500'>🖼️ {fname}</div><div style='font-size:11px;color:#64748b'>{T('img_ready')}</div></div>",unsafe_allow_html=True)
        with cx:
            if st.button("✕",key="clr_img"):
                st.session_state["pending_image_b64"]=None; st.session_state["pending_image_mime"]=None; st.session_state["pending_image_name"]=None; st.rerun()
    except: pass

if st.session_state.get("uploaded_file_content"):
    fname=st.session_state.get("uploaded_file_name","file")
    cfi,cfx=st.columns([8,1])
    with cfi: st.markdown(f'<div class="badge badge-purple">📁 {fname} — {T("file_ready")}</div>',unsafe_allow_html=True)
    with cfx:
        if st.button("✕",key="clr_file"):
            st.session_state["uploaded_file_content"]=None; st.session_state["uploaded_file_name"]=None; st.rerun()

if st.session_state.get("csv_df") is not None:
    fname=st.session_state.get("csv_filename","data.csv")
    df=st.session_state["csv_df"]
    ccsv,ccsvx=st.columns([8,1])
    with ccsv:
        st.markdown(f'<div class="badge badge-teal">📊 {fname} · {len(df):,} rows · {len(df.columns)} cols — {T("chart_ask").replace("…","")}</div>',unsafe_allow_html=True)
    with ccsvx:
        if st.button("✕",key="clr_csv2"):
            st.session_state["csv_df"]=None; st.session_state["csv_filename"]=None; st.session_state["csv_analyzed"]=False; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  UPLOAD TOOLBAR
# ══════════════════════════════════════════════════════════════════════════════
tb1,tb2,tb3,tb4,tb5=st.columns([1,1,1,1,5])

with tb1:
    img_lbl=T("img_btn_done") if st.session_state.get("pending_image_b64") else T("img_btn")
    if st.button(img_lbl,key="tog_img",help="Upload image"):
        st.session_state["show_image_uploader"]=not st.session_state["show_image_uploader"]
        st.session_state["show_file_uploader"]=False; st.session_state["show_csv_uploader"]=False; st.rerun()

with tb2:
    file_lbl=T("file_btn_done") if st.session_state.get("uploaded_file_content") else T("file_btn")
    if st.button(file_lbl,key="tog_file",help="Upload file"):
        st.session_state["show_file_uploader"]=not st.session_state["show_file_uploader"]
        st.session_state["show_image_uploader"]=False; st.session_state["show_csv_uploader"]=False; st.rerun()

with tb3:
    csv_lbl=T("csv_btn_done") if st.session_state.get("csv_df") is not None else T("csv_btn")
    if st.button(csv_lbl,key="tog_csv",help="Upload CSV for charts"):
        st.session_state["show_csv_uploader"]=not st.session_state["show_csv_uploader"]
        st.session_state["show_image_uploader"]=False; st.session_state["show_file_uploader"]=False; st.rerun()

with tb4:
    if st.button(T("help_btn"),key="show_help"):
        st.session_state["show_image_uploader"]=False; st.session_state["show_file_uploader"]=False; st.session_state["show_csv_uploader"]=False

# ── Image uploader panel ───────────────────────────────────────────────────────
if st.session_state.get("show_image_uploader"):
    st.markdown(f"""
    <div style='background:#1a1d24;border:1px solid #232730;border-radius:14px;padding:1.2rem;margin-bottom:.5rem;'>
        <div style='font-size:13px;color:#00e5ff;font-weight:600;margin-bottom:.5rem'>{T('img_upload_title')}</div>
        <div style='font-size:11px;color:#64748b;margin-bottom:.8rem'>{T('img_upload_hint')}</div>
    </div>""", unsafe_allow_html=True)
    img_file=st.file_uploader("img",type=["jpg","jpeg","png","gif","bmp","webp","tiff"],key="main_img",label_visibility="collapsed")
    if img_file:
        b64,mime,w,h=image_to_base64(img_file)
        if b64:
            st.session_state["pending_image_b64"]=b64; st.session_state["pending_image_mime"]=mime
            st.session_state["pending_image_name"]=img_file.name; st.session_state["show_image_uploader"]=False
            cp,ci2=st.columns([1,2])
            with cp: st.image(Image.open(io.BytesIO(base64.b64decode(b64))),width=120)
            with ci2: st.success(f"✅ {img_file.name}"); st.caption(f"{w}×{h}px · {mime}"); st.info(T("img_ready"))
        else: st.error("❌ Could not process image.")
    st.markdown(f"""<div style='margin-top:.8rem'><div style='font-size:11px;color:#64748b;margin-bottom:.4rem'>{T('example_q')}</div>
    <div style='display:flex;flex-wrap:wrap;gap:6px'>
        {''.join(f"<span style='background:#1a1d24;border:1px solid #232730;border-radius:999px;padding:3px 10px;font-size:11px;color:#94a3b8'>{T(k)}</span>" for k in ['ex1','ex2','ex3','ex4','ex5'])}
    </div></div>""", unsafe_allow_html=True)

# ── File uploader panel ────────────────────────────────────────────────────────
if st.session_state.get("show_file_uploader"):
    st.markdown(f"""
    <div style='background:#1a1d24;border:1px solid #232730;border-radius:14px;padding:1.2rem;margin-bottom:.5rem;'>
        <div style='font-size:13px;color:#a78bfa;font-weight:600;margin-bottom:.5rem'>{T('file_upload_title')}</div>
        <div style='font-size:11px;color:#64748b;margin-bottom:.8rem'>{T('file_upload_hint')}</div>
    </div>""", unsafe_allow_html=True)
    doc_file=st.file_uploader("doc",type=["txt","csv","json","py","js","ts","html","css","java","cpp","c","md","rs","go"],key="main_doc",label_visibility="collapsed")
    if doc_file:
        content=read_uploaded_file(doc_file)
        st.session_state["uploaded_file_content"]=content; st.session_state["uploaded_file_name"]=doc_file.name
        st.session_state["show_file_uploader"]=False; st.success(f"✅ {doc_file.name}"); st.info(T("file_ready"))

# ── CSV uploader panel ─────────────────────────────────────────────────────────
if st.session_state.get("show_csv_uploader"):
    st.markdown(f"""
    <div style='background:#1a1d24;border:1px solid rgba(0,229,255,.2);border-radius:14px;padding:1.5rem;margin-bottom:.5rem;'>
        <div style='font-size:14px;color:#00e5ff;font-weight:700;margin-bottom:.5rem'>{T('csv_upload_title')}</div>
        <div style='font-size:12px;color:#64748b;margin-bottom:1rem'>{T('csv_upload_hint')}</div>
        <div style='display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:1rem;'>
            {"".join(f"<div style='background:rgba(0,229,255,.06);border:1px solid rgba(0,229,255,.15);border-radius:8px;padding:6px;text-align:center;font-size:11px;color:#94a3b8'>✅ {t}</div>" for t in ['Bar Charts','Line Charts','Scatter Plots','Pie Charts','Heatmaps','Box Plots','Histograms','Area Charts'])}
        </div>
    </div>""", unsafe_allow_html=True)

    csv_file=st.file_uploader("csv",type=["csv"],key="main_csv_up",label_visibility="collapsed")
    if csv_file:
        with st.spinner(T("chart_generating")):
            df_parsed=parse_csv(csv_file)
        if df_parsed is not None:
            st.session_state["csv_df"]       = df_parsed
            st.session_state["csv_filename"] = csv_file.name
            st.session_state["csv_analyzed"] = False
            st.session_state["show_csv_uploader"]=False
            st.success(f"✅ {csv_file.name} — {len(df_parsed):,} rows × {len(df_parsed.columns)} columns loaded!")
            st.info(T("csv_ready"))
            st.rerun()
        else:
            st.error("❌ Could not parse this CSV. Check the format and try again.")

    # Sample CSV download
    sample_csv = """Name,Age,Salary,Department,City,Experience,Rating
Alice,28,75000,Engineering,New York,5,4.2
Bob,34,95000,Marketing,London,10,3.8
Carol,22,55000,Design,Paris,2,4.7
David,45,120000,Engineering,Tokyo,20,4.1
Eve,31,88000,Marketing,New York,8,4.5
Frank,27,62000,Design,London,3,3.9
Grace,38,105000,Engineering,Paris,15,4.6
Henry,29,79000,Marketing,Tokyo,6,4.0
"""
    st.download_button("⬇️ Download Sample CSV",data=sample_csv,file_name="sample_data.csv",mime="text/csv",key="dl_sample")

# ══════════════════════════════════════════════════════════════════════════════
#  CHAT INPUT
# ══════════════════════════════════════════════════════════════════════════════
if prompt := st.chat_input(T("chat_placeholder")):

    has_image = bool(st.session_state.get("pending_image_b64"))
    has_file  = bool(st.session_state.get("uploaded_file_content"))
    has_csv   = st.session_state.get("csv_df") is not None

    user_msg={"role":"user","content":prompt,"meta":""}
    if has_image:
        user_msg["image_b64"] =st.session_state["pending_image_b64"]
        user_msg["image_mime"]=st.session_state["pending_image_mime"]
        user_msg["image_name"]=st.session_state["pending_image_name"]
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

        # ── 🖼️ IMAGE ─────────────────────────────────────────────────────
        if has_image:
            b64=st.session_state["pending_image_b64"]; mime=st.session_state["pending_image_mime"]
            name=st.session_state.get("pending_image_name","image")
            meta=f'<div class="badge badge-pink">👁️ Vision AI · {name}</div>'
            st.markdown(meta,unsafe_allow_html=True)
            with st.spinner(T("analyzing")):
                response=analyze_image_stream(b64,mime,get_vision_prompt(prompt))
            st.session_state["pending_image_b64"]=None; st.session_state["pending_image_mime"]=None; st.session_state["pending_image_name"]=None

        # ── 📊 CSV DATA QUESTION ──────────────────────────────────────────
        elif has_csv and is_csv_analysis_query(prompt):
            df=st.session_state["csv_df"]; fname=st.session_state.get("csv_filename","data.csv")
            meta=f'<div class="badge badge-teal">📊 Data Analysis · {fname}</div>'
            st.markdown(meta,unsafe_allow_html=True)

            # Check if user wants a specific chart
            ql=prompt.lower()
            chart_requested=None
            if any(k in ql for k in ["bar chart","bar graph","bar plot"]): chart_requested="bar"
            elif any(k in ql for k in ["line chart","line graph","trend"]): chart_requested="line"
            elif any(k in ql for k in ["scatter","scatter plot","scatter chart"]): chart_requested="scatter"
            elif any(k in ql for k in ["pie chart","pie graph","donut"]): chart_requested="pie"
            elif any(k in ql for k in ["histogram","distribution"]): chart_requested="histogram"
            elif any(k in ql for k in ["box plot","box chart","boxplot"]): chart_requested="box"
            elif any(k in ql for k in ["heatmap","heat map","correlation"]): chart_requested="heatmap"
            elif any(k in ql for k in ["area chart","area graph"]): chart_requested="area"

            if chart_requested:
                num_cols,cat_cols,_=get_col_types(df)
                x_col=cat_cols[0] if cat_cols else df.columns[0]
                y_col=num_cols[0] if num_cols else df.columns[0]
                fig=build_custom_chart(df,chart_requested,x_col,y_col,None)
                if fig:
                    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":True,"displaylogo":False})

            with st.spinner(T("chart_analyzing")):
                response=get_csv_ai_analysis(df,prompt)

        # ── QR ────────────────────────────────────────────────────────────
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
                msgs=build_messages(f"Answer to '{prompt}' is {result}. Explain briefly.")
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
            st.session_state["uploaded_file_content"]=None; st.session_state["uploaded_file_name"]=None

        if not response and is_stock_query(prompt):
            symbol,dname=extract_stock_symbol(prompt)
            if symbol:
                with st.spinner(f"{T('fetching_stock')} {dname}…"): sd=get_stock(symbol,dname)
                if "failed" not in sd.lower():
                    L=dict(l.split(": ",1) for l in sd.strip().splitlines() if ": " in l)
                    meta='<div class="badge badge-green">📈 Live · Yahoo Finance</div>'
                    st.markdown(meta,unsafe_allow_html=True)
                    response=(f"### 📈 {L.get('Name',dname)}\n_{L.get('Exchange','')} · {L.get('Market','')}_\n\n"
                              f"| Detail | Value |\n|--------|-------|\n"
                              f"| 💰 Price | **{L.get('Price','N/A')}** |\n| 📊 Change | {L.get('Change','N/A')} |\n"
                              f"| 📈 Day High | {L.get('Day High','N/A')} |\n| 📉 Day Low | {L.get('Day Low','N/A')} |\n"
                              f"| 🔢 Volume | {L.get('Volume','N/A')} |\n\n_Delayed ~15 min_")
                    st.markdown(response)

        if not response and is_sports_query(prompt):
            with st.spinner(T("fetching_sports")):
                cricket=fetch_live_cricket(); sport_term="general"
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
                response=(f"### 🌍 {L.get('City',city)}\n\n| Detail | Value |\n|--------|-------|\n"
                          f"| 🌡️ Temperature | {L.get('Temperature','N/A')} |\n| 🌤️ Condition | {L.get('Condition','N/A')} |\n"
                          f"| 💧 Humidity | {L.get('Humidity','N/A')} |\n| 💨 Wind Speed | {L.get('Wind Speed','N/A')} |\n"
                          f"| 👁️ Visibility | {L.get('Visibility','N/A')} |\n| ☀️ UV Index | {L.get('UV Index','N/A')} |")
                st.markdown(response)
            else:
                response=f"❌ Could not fetch weather for **{city}**."; st.markdown(response)

        if not response:
            ct=classify_creation(prompt); search_results=""; searched=False
            if needs_search(prompt):
                with st.spinner(T("searching")):
                    search_results=web_search(prompt); facts=get_current_facts(prompt)
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
                            plabels={"game":T("live_game"),"app":T("live_app"),"software":T("live_software"),"design":T("live_design")}
                            st.markdown(f"### {plabels.get(ct,T('live_preview'))}")
                            h=650 if ct in ("game","app","software") else 520
                            st.components.v1.html(html_src,height=h,scrolling=True)
                            b64_html=base64.b64encode(html_src.encode()).decode()
                            fname={"game":"nova_game.html","app":"nova_app.html","software":"nova_software.html","design":"nova_design.html"}.get(ct,"nova_ai.html")
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
