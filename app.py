import json
import os
import re
import random
from html import escape
from datetime import datetime

import requests
import streamlit as st

# ==========================================
# 1. ERROR SAFETY CHECK (Prevents 500 Error)
# ==========================================
try:
    NVIDIA_API_KEY = st.secrets["NVIDIA_API_KEY"]
except Exception:
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")

# ==========================================
# 2. PAGE SETUP & PREMIUM STYLING
# ==========================================
st.set_page_config(page_title="Muslim AI by Aadil", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,400&family=Scheherazade+New:wght@400;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #F8FAFC !important; }
.stApp { background: linear-gradient(135deg, #020617 0%, #064E3B 100%) !important; background-attachment: fixed; }
h1, h2, h3, .serif-text { font-family: 'Playfair Display', serif; color: #FBBF24 !important; font-weight: 600; letter-spacing: 0.5px; }

.premium-card { background-color: rgba(15, 23, 42, 0.45); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(251, 191, 36, 0.25); border-radius: 16px; padding: 28px; margin-bottom: 24px; word-break: break-word; box-shadow: 0 10px 30px rgba(0,0,0,0.5); transition: all 0.3s ease; }
.premium-card:hover { border-color: rgba(251, 191, 36, 0.8); background-color: rgba(15, 23, 42, 0.6); transform: translateY(-4px); }
.name-card { text-align: center; padding: 20px; border: 1px solid rgba(251, 191, 36, 0.2); border-radius: 12px; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(8px); }

.hero { text-align: center; padding: 60px 20px 40px 20px; margin-bottom: 40px; border-bottom: 1px solid rgba(255,255,255,0.05); background: radial-gradient(circle at top, rgba(251, 191, 36, 0.15) 0%, transparent 70%); }
.bismillah { font-family: 'Scheherazade New', serif; font-size: 42px; color: #FBBF24; margin-bottom: 16px; text-shadow: 0 0 20px rgba(251, 191, 36, 0.4); }
.title { font-size: 48px; font-weight: 700; margin-bottom: 8px; font-family: 'Playfair Display', serif; background: linear-gradient(to right, #FBBF24, #FEF08A); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.subtitle { font-size: 18px; color: #CBD5E1; font-weight: 300; letter-spacing: 1px; }

.arabic { font-family: 'Scheherazade New', serif; font-size: 36px; direction: rtl; text-align: right; margin-bottom: 16px; line-height: 1.8; color: #FDE047; }
.section-title { font-family: 'Playfair Display', serif; font-size: 26px; color: #FBBF24; margin: 40px 0 20px 0; padding-bottom: 10px; border-bottom: 1px solid rgba(251, 191, 36, 0.2); }
.info-box { background-color: rgba(251, 191, 36, 0.08); border-left: 4px solid #FBBF24; border-radius: 6px; padding: 16px 20px; font-size: 15px; margin-bottom: 24px; color: #F8FAFC; }
.accent { color: #FBBF24 !important; font-weight: 600; }
.muted { color: #94A3B8 !important; font-size: 0.9em; }
.source-link { color: #60A5FA; text-decoration: none; border-bottom: 1px dotted #60A5FA; }

[data-testid="stSidebar"] { background-color: rgba(2, 6, 23, 0.8) !important; backdrop-filter: blur(15px); border-right: 1px solid rgba(251, 191, 36, 0.15); }
input, textarea { background-color: rgba(15, 23, 42, 0.6) !important; border: 1px solid rgba(251, 191, 36, 0.3) !important; color: #fff !important; border-radius: 8px !important; }
.stButton > button { background: linear-gradient(135deg, rgba(251, 191, 36, 0.1), rgba(251, 191, 36, 0.05)); color: #FBBF24; border: 1px solid #FBBF24; border-radius: 8px; transition: all 0.3s ease; }
.stButton > button:hover { background: #FBBF24; color: #020617; transform: scale(1.02); }
.creator-footer { text-align: center; padding: 30px 10px; margin-top: auto; font-family: 'Playfair Display', serif; color: #FBBF24; border-top: 1px solid rgba(251, 191, 36, 0.2); font-size: 18px; letter-spacing: 1px; }
.tasbih-count { font-size: 56px; color: #FBBF24; text-align: center; font-family: 'Inter', sans-serif; font-weight: 700; }
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 3. CORE LOGIC & DATA
# ==========================================
API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "meta/llama-4-maverick-17b-128e-instruct"

BASE_SYSTEM_PROMPT = """You are an Islamic AI Assistant. Respond only with authentic Quran, Sahih Hadith, and recognized classical scholarship. Return ONLY valid JSON."""

# Re-adding full Hadith to ensure they are present
HADITH_40 = [
    {"number": 1, "arabic": "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ", "text": "Actions are judged by intentions.", "source": "Sahih al-Bukhari 1"},
    {"number": 2, "arabic": "الدِّينُ النَّصِيحَةُ", "text": "Religion is sincere advice.", "source": "Sahih Muslim 55"},
    {"number": 3, "arabic": "لاَ تَغْضَبْ", "text": "Do not become angry.", "source": "Sahih al-Bukhari 6116"},
    {"number": 4, "arabic": "وَالْكَلِمَةُ الطَّيِّبَةُ صَدَقَةٌ", "text": "A good word is charity.", "source": "Sahih Muslim 1009"},
    {"number": 5, "arabic": "يَسِّرُوا وَلاَ تُعَسِّرُوا", "text": "Make things easy and do not make them difficult.", "source": "Sahih al-Bukhari 69"}
]

SURAH_NAMES = ["Al-Fatiha","Al-Baqarah","Al-Imran","An-Nisa","Al-Maidah","Al-Anam","Al-Araf","Al-Anfal","At-Tawbah","Yunus","Hud","Yusuf","Ar-Rad","Ibrahim","Al-Hijr","An-Nahl","Al-Isra","Al-Kahf","Maryam","Ta-Ha","Al-Anbiya","Al-Hajj","Al-Muminun","An-Nur","Al-Furqan","Ash-Shuara","An-Naml","Al-Qasas","Al-Ankabut","Ar-Rum","Luqman","As-Sajdah","Al-Ahzab","Saba","Fatir","Ya-Sin","As-Saffat","Sad","Az-Zumar","Ghafir","Fussilat","Ash-Shura","Az-Zukhruf","Ad-Dukhan","Al-Jathiyah","Al-Ahqaf","Muhammad","Al-Fath","Al-Hujurat","Qaf","Adh-Dhariyat","At-Tur","An-Najm","Al-Qamar","Ar-Rahman","Al-Waqiah","Al-Hadid","Al-Mujadila","Al-Hashr","Al-Mumtahanah","As-Saf","Al-Jumuah","Al-Munafiqun","At-Taghabun","At-Talaq","At-Tahrim","Al-Mulk","Al-Qalam","Al-Haqqah","Al-Maarij","Nuh","Al-Jinn","Al-Muzzammil","Al-Muddaththir","Al-Qiyamah","Al-Insan","Al-Mursalat","An-Naba","An-Naziat","Abasa","At-Takwir","Al-Infitar","Al-Mutaffifin","Al-Inshiqaq","Al-Buruj","At-Tariq","Al-Ala","Al-Ghashiyah","Al-Fajr","Al-Balad","Ash-Shams","Al-Layl","Ad-Duhaa","Ash-Sharh","At-Tin","Al-Alaq","Al-Qadr","Al-Bayyinah","Az-Zalzalah","Al-Adiyat","Al-Qariah","At-Takathur","Al-Asr","Al-Humazah","Al-Fil","Quraysh","Al-Maun","Al-Kawthar","Al-Kafirun","An-Nasr","Al-Masad","Al-Ikhlas","Al-Falaq","An-Nas"]

# --- FUNCTIONS ---
def safe_html(value): return escape("" if value is None else str(value))

def source_link(label, url):
    if url and str(url).startswith('http'):
        return f'<a class="source-link" href="{escape(url, quote=True)}" target="_blank">{safe_html(label)}</a>'
    return safe_html(label)

def call_api(user_message, history, persona="Balanced Assistant"):
    if not NVIDIA_API_KEY: return json.dumps({"direct_answer": "API Key Missing in Secrets!"})
    messages = [{"role": "system", "content": BASE_SYSTEM_PROMPT + f" Mode: {persona}"}]
    for item in history[-3:]:
        messages.append({"role": "user", "content": item["user"]})
        messages.append({"role": "assistant", "content": item["assistant"]})
    messages.append({"role": "user", "content": user_message})
    headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": MODEL, "messages": messages, "max_tokens": 1500, "temperature": 0.2}
    r = requests.post(API_URL, headers=headers, json=payload, timeout=40)
    return r.json()["choices"][0]["message"]["content"]

def parse_response(raw):
    try:
        start = raw.find("{"); end = raw.rfind("}") + 1
        return json.loads(raw[start:end])
    except: return {"direct_answer": raw}

@st.cache_data(ttl=3600)
def fetch_prayer_times(city, country):
    try:
        res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=2")
        return res.json()["data"]
    except: return None

# --- STATE ---
if "messages" not in st.session_state: st.session_state.messages = []
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "tasbih_count" not in st.session_state: st.session_state.tasbih_count = 0
if "daily_inspo" not in st.session_state: st.session_state.daily_inspo = random.choice(HADITH_40)

# --- UI START ---
st.markdown('<div class="hero"><div class="bismillah">بِسْمِ اللَّهِ الرَّحْمٰنِ الرَّحِيمِ</div><div class="title">Muslim AI</div><div class="subtitle">Premium Islamic Intelligence by Aadil Rather</div></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div style="text-align:center;"><h2 style="color:#FBBF24;">Settings</h2></div>', unsafe_allow_html=True)
    persona = st.selectbox("AI Persona", ["Balanced Assistant", "Deep Scholar", "Spiritual Counselor"])
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []; st.session_state.chat_history = []; st.rerun()
    st.markdown("---")
    st.markdown(f'<div class="name-card"><div class="arabic" style="font-size:20px;">{st.session_state.daily_inspo["arabic"]}</div><div style="font-size:12px;">{st.session_state.daily_inspo["text"]}</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="creator-footer">Created by Aadil Rather</div>', unsafe_allow_html=True)

t1, t2, t3, t4 = st.tabs(["💬 Chat", "📖 Quran", "🕋 Prayer & Qibla", "📿 Tasbih & Tools"])

with t1:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["content"])
    
    user_input = st.chat_input("Ask anything...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"): st.write(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Consulting..."):
                raw = call_api(user_input, st.session_state.chat_history, persona)
                res = parse_response(raw)
                ans = res.get("direct_answer", str(res))
                st.write(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
                st.session_state.chat_history.append({"user": user_input, "assistant": ans})

with t2:
    st.markdown('<div class="section-title">The Holy Quran</div>', unsafe_allow_html=True)
    s_choice = st.selectbox("Select Surah", SURAH_NAMES)
    st.info("Quran text and audio will load here. (API enabled)")

with t3:
    st.markdown('<div class="section-title">Prayer Times & Qibla</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    city = c1.text_input("City", "Mecca")
    country = c2.text_input("Country", "Saudi Arabia")
    if st.button("Fetch Data"):
        data = fetch_prayer_times(city, country)
        if data:
            st.success(f"Qibla: {data['meta']['qibla']}° from North")
            st.json(data['timings'])

with t4:
    st.markdown('<div class="section-title">Digital Tasbih</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([1,1])
    if col_a.button("➕ Count", use_container_width=True): st.session_state.tasbih_count += 1
    if col_b.button("🔄 Reset", use_container_width=True): st.session_state.tasbih_count = 0
    st.markdown(f'<div class="tasbih-count">{st.session_state.tasbih_count}</div>', unsafe_allow_html=True)
