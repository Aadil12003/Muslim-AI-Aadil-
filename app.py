import json
import os
import re
import random
from html import escape
from datetime import datetime

import requests
import streamlit as st

# ==========================================
# PAGE SETUP & PREMIUM STYLING
# ==========================================
st.set_page_config(page_title="Muslim AI by Aadil", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,400&family=Scheherazade+New:wght@400;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0a0a0a !important; color: #e0e0e0 !important; }
.stApp { background-color: #0a0a0a; background-image: radial-gradient(circle at 50% 0%, #1a1a1a 0%, #0a0a0a 70%); }
h1, h2, h3, .serif-text { font-family: 'Playfair Display', serif; color: #D4AF37 !important; font-weight: 600; letter-spacing: 0.5px; }

.premium-card { background-color: #121212; border: 1px solid #2a2a2a; border-radius: 12px; padding: 28px; margin-bottom: 24px; word-break: break-word; box-shadow: 0 4px 20px rgba(0,0,0,0.4); transition: transform 0.2s ease, border-color 0.2s ease; }
.premium-card:hover { border-color: #D4AF37; transform: translateY(-2px); }
.name-card { text-align: center; padding: 20px; border: 1px solid #2a2a2a; border-radius: 8px; background: linear-gradient(145deg, #121212, #0a0a0a); transition: border-color 0.2s ease; }
.name-card:hover { border-color: #D4AF37; }

.hero { text-align: center; padding: 60px 20px 40px 20px; margin-bottom: 40px; border-bottom: 1px solid #2a2a2a; background: linear-gradient(180deg, rgba(212, 175, 55, 0.05) 0%, rgba(10, 10, 10, 0) 100%); }
.bismillah { font-family: 'Scheherazade New', serif; font-size: 36px; color: #D4AF37; margin-bottom: 16px; text-shadow: 0 2px 10px rgba(212, 175, 55, 0.2); }
.title { font-size: 42px; font-weight: 700; margin-bottom: 8px; font-family: 'Playfair Display', serif; color: #ffffff; }
.subtitle { font-size: 16px; color: #a0a0a0; font-weight: 300; letter-spacing: 1px; }

.arabic { font-family: 'Scheherazade New', serif; font-size: 34px; direction: rtl; text-align: right; margin-bottom: 16px; line-height: 1.8; color: #D4AF37; }
.section-title { font-family: 'Playfair Display', serif; font-size: 24px; color: #D4AF37; margin: 40px 0 20px 0; padding-bottom: 10px; border-bottom: 1px solid #2a2a2a; }
.info-box { background-color: rgba(212, 175, 55, 0.05); border-left: 3px solid #D4AF37; border-radius: 4px; padding: 16px 20px; font-size: 15px; margin-bottom: 24px; color: #cccccc; }
.accent { color: #D4AF37 !important; font-weight: 600; }
.muted { color: #888888 !important; font-size: 0.9em; font-weight: 300; }

[data-testid="stSidebar"] { background-color: #0f0f0f !important; border-right: 1px solid #2a2a2a; }
input, textarea { background-color: #1a1a1a !important; border: 1px solid #333 !important; color: #fff !important; border-radius: 8px !important; }
input:focus, textarea:focus { border-color: #D4AF37 !important; box-shadow: 0 0 0 1px #D4AF37 !important; }
.stButton > button { background-color: #1a1a1a; color: #D4AF37; border: 1px solid #D4AF37; border-radius: 8px; transition: all 0.3s ease; }
.stButton > button:hover { background-color: #D4AF37; color: #000; }
.creator-footer { text-align: center; padding: 30px 10px; margin-top: auto; font-family: 'Playfair Display', serif; color: #D4AF37; border-top: 1px solid #2a2a2a; font-size: 18px; letter-spacing: 1px; }
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# CONFIGURATION & API SETUP
# ==========================================
try:
    NVIDIA_API_KEY = st.secrets["NVIDIA_API_KEY"]
except Exception:
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "").strip()

if not NVIDIA_API_KEY:
    st.error("Missing NVIDIA_API_KEY. Please add it to your Streamlit Cloud Secrets.")
    st.stop()

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "meta/llama-4-maverick-17b-128e-instruct"

SYSTEM_PROMPT = """You are an Islamic AI Assistant. Respond only with authentic Quran, Sahih Hadith, and recognized classical scholarship (like Ibn Kathir).
- Do NOT fabricate references.
- Return ONLY valid JSON.
{
  "direct_answer": "concise answer or full narrative text",
  "quran_evidence": [{"arabic": "", "translation": "", "reference": "", "explanation": ""}],
  "hadith_evidence": [{"text": "", "arabic": "", "source": "", "authenticity": "Sahih", "note": ""}],
  "scholarly_opinions": [{"madhab": "", "opinion": "", "source": ""}],
  "dua": {"title": "", "arabic": "", "transliteration": "", "meaning": "", "reference": "", "source_url": ""},
  "duas": [],
  "ikhtilaf": "Yes or No",
  "conclusion": "summary",
  "consult_scholar": "Yes or No",
  "source_notice": "",
  "language_detected": "English"
}"""

# ==========================================
# DATA SETS
# ==========================================
SURAH_NAMES = ["Al-Fatiha","Al-Baqarah","Al-Imran","An-Nisa","Al-Maidah","Al-Anam","Al-Araf","Al-Anfal","At-Tawbah","Yunus","Hud","Yusuf","Ar-Rad","Ibrahim","Al-Hijr","An-Nahl","Al-Isra","Al-Kahf","Maryam","Ta-Ha","Al-Anbiya","Al-Hajj","Al-Muminun","An-Nur","Al-Furqan","Ash-Shuara","An-Naml","Al-Qasas","Al-Ankabut","Ar-Rum","Luqman","As-Sajdah","Al-Ahzab","Saba","Fatir","Ya-Sin","As-Saffat","Sad","Az-Zumar","Ghafir","Fussilat","Ash-Shura","Az-Zukhruf","Ad-Dukhan","Al-Jathiyah","Al-Ahqaf","Muhammad","Al-Fath","Al-Hujurat","Qaf","Adh-Dhariyat","At-Tur","An-Najm","Al-Qamar","Ar-Rahman","Al-Waqiah","Al-Hadid","Al-Mujadila","Al-Hashr","Al-Mumtahanah","As-Saf","Al-Jumuah","Al-Munafiqun","At-Taghabun","At-Talaq","At-Tahrim","Al-Mulk","Al-Qalam","Al-Haqqah","Al-Maarij","Nuh","Al-Jinn","Al-Muzzammil","Al-Muddaththir","Al-Qiyamah","Al-Insan","Al-Mursalat","An-Naba","An-Naziat","Abasa","At-Takwir","Al-Infitar","Al-Mutaffifin","Al-Inshiqaq","Al-Buruj","At-Tariq","Al-Ala","Al-Ghashiyah","Al-Fajr","Al-Balad","Ash-Shams","Al-Layl","Ad-Duhaa","Ash-Sharh","At-Tin","Al-Alaq","Al-Qadr","Al-Bayyinah","Az-Zalzalah","Al-Adiyat","Al-Qariah","At-Takathur","Al-Asr","Al-Humazah","Al-Fil","Quraysh","Al-Maun","Al-Kawthar","Al-Kafirun","An-Nasr","Al-Masad","Al-Ikhlas","Al-Falaq","An-Nas"]

DUA_CATEGORIES = {
    "Quranic Rabbana Duas": [
        {"title": "For Good in This World and the Hereafter", "arabic": "رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً وَفِي الْآخِرَةِ حَسَنَةً وَقِنَا عَذَابَ النَّارِ", "transliteration": "Rabbana atina fid-dunya hasanatan wa fil 'akhirati hasanatan waqina 'adhaban-nar", "meaning": "Our Lord, give us in this world [that which is] good and in the Hereafter [that which is] good and protect us from the punishment of the Fire.", "reference": "Quran 2:201"}
    ],
    "Morning Adhkar": [
        {"title": "Sayyidul Istighfar", "arabic": "اللَّهُمَّ أَنْتَ رَبِّي لَا إِلَهَ إِلَّا أَنْتَ، خَلَقْتَنِي وَأَنَا عَبْدُكَ", "transliteration": "Allahumma anta rabbi la ilaha illa anta, khalaqtani wa ana abduk", "meaning": "O Allah, You are my Lord; none has the right to be worshipped except You. You created me and I am Your servant.", "reference": "Bukhari 6306"}
    ]
}

HADITH_40 = [
    {"number": 1, "arabic": "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ", "text": "Actions are judged by intentions.", "source": "Sahih al-Bukhari 1"},
    {"number": 2, "arabic": "الدِّينُ النَّصِيحَةُ", "text": "Religion is sincere advice.", "source": "Sahih Muslim 55"},
    {"number": 3, "arabic": "لاَ تَغْضَبْ", "text": "Do not become angry.", "source": "Sahih al-Bukhari 6116"},
    {"number": 4, "arabic": "وَالْكَلِمَةُ الطَّيِّبَةُ صَدَقَةٌ", "text": "A good word is charity.", "source": "Sahih Muslim 1009"},
    {"number": 5, "arabic": "يَسِّرُوا وَلاَ تُعَسِّرُوا", "text": "Make things easy and do not make them difficult.", "source": "Sahih al-Bukhari 69"}
]

# The 99 Names of Allah (First 33 for brevity, format: Arabic|Transliteration|Meaning)
NAMES_RAW = "الرَّحْمَن|Ar-Rahman|The Entirely Merciful,الرَّحِيم|Ar-Rahim|The Especially Merciful,الْمَلِك|Al-Malik|The Sovereign,الْقُدُّوس|Al-Quddus|The Most Holy,السَّلاَم|As-Salam|The Source of Peace,الْمُؤْمِن|Al-Mu'min|The Guarantor,الْمُهَيْمِن|Al-Muhaymin|The Guardian,الْعَزِيز|Al-Aziz|The Almighty,الْجَبَّار|Al-Jabbar|The Compeller,الْمُتَكَبِّر|Al-Mutakabbir|The Supreme,الْخَالِق|Al-Khaliq|The Creator,الْبَارِئ|Al-Bari'|The Evolver,الْمُصَوِّر|Al-Musawwir|The Fashioner,الْغَفَّار|Al-Ghaffar|The Repeatedly Forgiving,الْقَهَّار|Al-Qahhar|The Subduer,الْوَهَّاب|Al-Wahhab|The Bestower,الرَّزَّاق|Ar-Razzaq|The Provider,الْفَتَّاح|Al-Fattah|The Opener,الْعَلِيم|Al-Aleem|The Knowing,الْقَابِض|Al-Qabid|The Withholder,الْبَاسِط|Al-Basit|The Extender,الْخَافِض|Al-Khafid|The Abaser,الرَّافِع|Ar-Rafi'|The Exalter,الْمُعِزّ|Al-Mu'izz|The Honorer,الْمُذِلّ|Al-Mudhill|The Dishonorer,السَّمِيع|As-Sami'|The Hearing,الْبَصِير|Al-Basir|The Seeing,الْحَكَم|Al-Hakam|The Judge,الْعَدْل|Al-Adl|The Just,اللَّطِيف|Al-Latif|The Subtle One,الْخَبِير|Al-Khabir|The Acquainted,الْحَلِيم|Al-Haleem|The Forbearing,الْعَظِيم|Al-Azeem|The Magnificent"
NAMES_99 = [name.split('|') for name in NAMES_RAW.split(',')]

DYNAMIC_PROPHETS = ["Prophet Adam (as)", "Prophet Nuh (as)", "Prophet Ibrahim (as)", "Prophet Yusuf (as)", "Prophet Musa (as)", "Prophet Isa (as)", "Prophet Muhammad (ﷺ)"]
DYNAMIC_STORIES = ["People of the Cave (Ashab al-Kahf)", "Musa and Al-Khidr", "The Men of the Elephant", "Qarun (Korah)"]
TIBB_TOPICS = ["Black Seed (Habbatul Barakah)", "Honey", "Cupping (Hijama)", "Dates (Ajwa)", "Olive Oil", "Siwak (Miswak)"]

# ==========================================
# STATE MANAGEMENT
# ==========================================
if "messages" not in st.session_state: st.session_state.messages = []
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "loaded_surah_number" not in st.session_state: st.session_state.loaded_surah_number = None
if "daily_inspo" not in st.session_state: st.session_state.daily_inspo = random.choice(HADITH_40)

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def safe_html(value): return escape("" if value is None else str(value))
def contains_any(text, terms): return any(term in text for term in terms)

def normalize_result(result):
    if not isinstance(result, dict): result = {}
    return {
        "direct_answer": str(result.get("direct_answer", "")).strip(),
        "quran_evidence": result.get("quran_evidence", []) if isinstance(result.get("quran_evidence", []), list) else [],
        "hadith_evidence": result.get("hadith_evidence", []) if isinstance(result.get("hadith_evidence", []), list) else [],
        "scholarly_opinions": result.get("scholarly_opinions", []) if isinstance(result.get("scholarly_opinions", []), list) else [],
        "conclusion": str(result.get("conclusion", "")).strip(),
        "source_notice": str(result.get("source_notice", "")).strip(),
    }

def call_api(user_message, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for item in history[-3:]:
        messages.append({"role": "user", "content": item["user"]})
        messages.append({"role": "assistant", "content": item["assistant"]})
    messages.append({"role": "user", "content": user_message})
    headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Accept": "application/json", "Content-Type": "application/json"}
    payload = {"model": MODEL, "messages": messages, "max_tokens": 2000, "temperature": 0.2, "stream": False}
    response = requests.post(API_URL, headers=headers, json=payload, timeout=45)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def parse_response(raw):
    try:
        cleaned = re.sub(r"```json|```", "", raw).strip()
        start = cleaned.find("{"); end = cleaned.rfind("}") + 1
        if start != -1 and end > start: cleaned = cleaned[start:end]
        return normalize_result(json.loads(cleaned))
    except Exception: return normalize_result({"direct_answer": raw})

@st.cache_data(ttl=3600)
def fetch_quran_surah(surah_number):
    try:
        res = requests.get(f"https://api.alquran.cloud/v1/surah/{surah_number}/editions/quran-uthmani,en.asad", timeout=15)
        return res.json()["data"] if res.status_code == 200 else None
    except Exception: return None

@st.cache_data(ttl=3600)
def fetch_prayer_times(city, country):
    try:
        res = requests.get(f"http://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=2", timeout=10)
        return res.json()["data"] if res.status_code == 200 else None
    except Exception: return None

def format_chat_for_export():
    out = "Muslim AI - Chat Transcript\n" + "="*30 + "\n\n"
    for m in st.session_state.messages:
        role = "YOU" if m["role"] == "user" else "MUSLIM AI"
        out += f"{role}:\n{m['content']}\n\n" + "-"*30 + "\n\n"
    return out

def render_response(result):
    result = normalize_result(result)
    formatted_answer = safe_html(result["direct_answer"]).replace('\n', '<br>')
    st.markdown(f'<div class="premium-card"><strong class="accent" style="font-size:20px;">Response</strong><br><br><span style="line-height:1.7; font-size:16px;">{formatted_answer}</span></div>', unsafe_allow_html=True)

    if result["quran_evidence"]:
        st.markdown('<div class="section-title">Quranic Evidence</div>', unsafe_allow_html=True)
        for verse in result["quran_evidence"]:
            st.markdown(f'<div class="premium-card"><div class="arabic">{safe_html(verse.get("arabic", ""))}</div><div style="font-size:16px; margin-bottom:12px;">{safe_html(verse.get("translation", ""))}</div><strong class="accent">{safe_html(verse.get("reference", ""))}</strong></div>', unsafe_allow_html=True)

    if result["hadith_evidence"]:
        st.markdown('<div class="section-title">Hadith Evidence</div>', unsafe_allow_html=True)
        for h in result["hadith_evidence"]:
            st.markdown(f'<div class="premium-card"><div class="arabic">{safe_html(h.get("arabic", ""))}</div><div style="font-size:16px;">{safe_html(h.get("text", ""))}</div><br><span class="muted">Source: {safe_html(h.get("source", ""))}</span></div>', unsafe_allow_html=True)

# ==========================================
# UI LAYOUT & SIDEBAR
# ==========================================
st.markdown(
    '<div class="hero"><div class="bismillah">بِسْمِ اللَّهِ الرَّحْمٰنِ الرَّحِيمِ</div>'
    '<div class="title">Muslim AI</div>'
    '<div class="subtitle">Complete Islamic Toolkit • Grounded in Authentic Scholarship</div></div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown('<div style="text-align:center;"><h2 style="color:#D4AF37; margin-bottom:5px;">Muslim AI</h2><div style="color:#888; font-size:14px; text-transform:uppercase;">Knowledge & Reflection</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Daily Inspiration Widget
    st.markdown('<div style="background:#121212; padding:15px; border-radius:8px; border:1px solid #D4AF37;"><h4 style="margin-top:0; color:#D4AF37; font-size:14px; text-transform:uppercase;">✨ Daily Inspiration</h4>'
                f'<div class="arabic" style="font-size:24px; text-align:center;">{st.session_state.daily_inspo["arabic"]}</div>'
                f'<div style="font-size:13px; font-style:italic; margin-bottom:10px; color:#ddd;">"{st.session_state.daily_inspo["text"]}"</div>'
                f'<div style="font-size:11px; color:#D4AF37;">- {st.session_state.daily_inspo["source"]}</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.chat_history = []; st.session_state.messages = []; st.rerun()
        
    st.markdown('<div class="creator-footer">Created by Aadil Rather</div>', unsafe_allow_html=True)

# ==========================================
# MAIN TABS
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🤖 AI Chat", "📖 Quran & Dua", "🕌 Prayer & Zakat", "📚 Hadith & Names", "📜 Deep Knowledge"])

with tab1: # AI CHAT
    st.download_button("📥 Download Chat Transcript", data=format_chat_for_export(), file_name=f"Muslim_AI_Chat_{datetime.now().strftime('%Y%m%d')}.txt", mime="text/plain")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                try: render_response(json.loads(msg["content"]))
                except Exception: st.markdown(msg["content"])
            else: st.markdown(f'<div style="font-size:16px;">{msg["content"]}</div>', unsafe_allow_html=True)

    user_input = st.chat_input("Ask your Islamic question...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"): st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Consulting authentic sources..."):
                try:
                    raw = call_api(user_input, st.session_state.chat_history)
                    result = parse_response(raw)
                    render_response(result)
                    st.session_state.messages.append({"role": "assistant", "content": json.dumps(result, ensure_ascii=False)})
                    st.session_state.chat_history.append({"user": user_input, "assistant": result.get("direct_answer", "")})
                except Exception as e: st.error("Error processing request.")

with tab2: # QURAN & DUA
    st.markdown('<div class="section-title" style="margin-top:0;">The Holy Quran</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        selected_surah = st.selectbox("Select Surah", [f"{i + 1}. {name}" for i, name in enumerate(SURAH_NAMES)])
        if st.button("Read Surah", type="primary", use_container_width=True): st.session_state.loaded_surah_number = int(selected_surah.split(".")[0])
    with col2:
        if st.session_state.loaded_surah_number:
            surah_data = fetch_quran_surah(st.session_state.loaded_surah_number)
            if surah_data:
                ar, en = surah_data[0], surah_data[1]
                st.markdown(f'<div class="arabic" style="font-size:40px; text-align:center; margin-bottom:40px;">{safe_html(ar.get("name", ""))}</div>', unsafe_allow_html=True)
                for i, ayah in enumerate(ar.get("ayahs", [])):
                    eng_text = en.get("ayahs", [])[i].get("text", "") if i < len(en.get("ayahs", [])) else ""
                    st.markdown(f'<div class="premium-card"><div class="muted" style="color:#D4AF37 !important;">AYAH {ayah.get("numberInSurah")}</div><div class="arabic">{safe_html(ayah.get("text"))}</div><div style="font-size:16px; color:#ccc;">{safe_html(eng_text)}</div></div>', unsafe_allow_html=True)

with tab3: # PRAYER & ZAKAT
    st.markdown('<div class="section-title" style="margin-top:0;">Live Prayer Times</div>', unsafe_allow_html=True)
    pc1, pc2 = st.columns(2)
    with pc1: city = st.text_input("City", value="Mecca")
    with pc2: country = st.text_input("Country", value="Saudi Arabia")
    
    if st.button("Get Timings", type="primary"):
        times_data = fetch_prayer_times(city, country)
        if times_data:
            timings = times_data["timings"]
            date_hijri = times_data["date"]["hijri"]
            st.markdown(f'<div class="info-box" style="text-align:center; font-size:18px;"><strong class="accent">{date_hijri["day"]} {date_hijri["month"]["en"]} {date_hijri["year"]} AH</strong></div>', unsafe_allow_html=True)
            cols = st.columns(6)
            prayers = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
            for i, p in enumerate(prayers):
                cols[i].markdown(f'<div class="name-card"><strong class="accent">{p}</strong><br><span style="font-size:18px;">{timings[p]}</span></div>', unsafe_allow_html=True)
        else: st.error("Could not fetch times. Check city/country spelling.")

    st.markdown('<div class="section-title">Zakat Calculator (2.5%)</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Enter your assets. If your net wealth is above the Nisab threshold, your Zakat is 2.5%.</div>', unsafe_allow_html=True)
    zc1, zc2, zc3 = st.columns(3)
    with zc1: cash = st.number_input("Cash & Savings ($)", min_value=0.0)
    with zc2: gold = st.number_input("Value of Gold/Silver ($)", min_value=0.0)
    with zc3: debt = st.number_input("Short-term Debts ($)", min_value=0.0)
    
    net_wealth = (cash + gold) - debt
    zakat = net_wealth * 0.025 if net_wealth > 0 else 0.0
    st.markdown(f'<div class="premium-card" style="text-align:center;"><h3>Estimated Zakat Due: <span style="color:#D4AF37;">${zakat:,.2f}</span></h3></div>', unsafe_allow_html=True)

with tab4: # HADITH & NAMES
    st.markdown('<div class="section-title" style="margin-top:0;">The 99 Names of Allah (Asma-ul-Husna)</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for i, name_data in enumerate(NAMES_99):
        cols[i % 3].markdown(f'<div class="name-card"><div class="arabic" style="font-size:28px; text-align:center; margin-bottom:5px;">{name_data[0]}</div><strong style="color:#D4AF37; font-size:18px;">{name_data[1]}</strong><br><span style="color:#aaa; font-size:14px;">{name_data[2]}</span></div>', unsafe_allow_html=True)

with tab5: # DEEP KNOWLEDGE (AI Generated)
    st.markdown('<div class="section-title" style="margin-top:0;">Dynamic Islamic Sciences</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Select a topic. The AI will generate a comprehensive, authentic profile based on classical sources.</div>', unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('### Prophetic History (Seerah/Stories)')
        selected_story = st.selectbox("Select a Prophet or Event", DYNAMIC_PROPHETS + DYNAMIC_STORIES)
        if st.button("Generate History Profile", use_container_width=True):
            with st.spinner(f"Extracting authentic history for {selected_story}..."):
                prompt = f"Provide a complete, multi-paragraph, highly detailed profile of '{selected_story}'. Base it strictly on Quran and authentic Ahadith/Tafseer. Detail the motives, major events, and moral legacy."
                raw = call_api(prompt, [])
                render_response(parse_response(raw))
                
    with col_b:
        st.markdown('### Prophetic Medicine (Tibb al-Nabawi)')
        selected_tibb = st.selectbox("Select a Remedy", TIBB_TOPICS)
        if st.button("Generate Medicine Profile", use_container_width=True):
            with st.spinner(f"Extracting authentic knowledge on {selected_tibb}..."):
                prompt = f"Provide a comprehensive overview of '{selected_tibb}' in Islam. Cite authentic Hadith mentioning it, and explain its spiritual and physical benefits according to Prophetic Medicine (Tibb al-Nabawi)."
                raw = call_api(prompt, [])
                render_response(parse_response(raw))
