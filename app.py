import json
import os
import re
import random
from html import escape
from datetime import datetime

import requests
import streamlit as st

# ==========================================
# PAGE SETUP & PREMIUM VIBRANT STYLING
# ==========================================
st.set_page_config(page_title="Muslim AI by Aadil", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,400&family=Scheherazade+New:wght@400;700&display=swap');

/* ===== GLOBAL TYPOGRAPHY & RICH BACKGROUND ===== */
html, body, [class*="css"] { 
    font-family: 'Inter', sans-serif; 
    color: #F8FAFC !important; 
}
.stApp { 
    background: linear-gradient(135deg, #020617 0%, #064E3B 100%) !important; /* Deep Slate to Royal Emerald */
    background-attachment: fixed;
}
h1, h2, h3, .serif-text { 
    font-family: 'Playfair Display', serif; 
    color: #FBBF24 !important; /* Vibrant Gold */
    font-weight: 600; 
    letter-spacing: 0.5px; 
}

/* ===== GLASSMORPHISM CARDS ===== */
.premium-card { 
    background-color: rgba(15, 23, 42, 0.45); /* Transparent Dark Blue */
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(251, 191, 36, 0.25); /* Soft Gold Border */
    border-radius: 16px; 
    padding: 28px; 
    margin-bottom: 24px; 
    word-break: break-word; 
    box-shadow: 0 10px 30px rgba(0,0,0,0.5); 
    transition: all 0.3s ease; 
}
.premium-card:hover { 
    border-color: rgba(251, 191, 36, 0.8); 
    background-color: rgba(15, 23, 42, 0.6);
    transform: translateY(-4px); 
    box-shadow: 0 15px 40px rgba(0,0,0,0.6), 0 0 15px rgba(251, 191, 36, 0.1);
}
.name-card { 
    text-align: center; 
    padding: 20px; 
    border: 1px solid rgba(251, 191, 36, 0.2); 
    border-radius: 12px; 
    background: rgba(15, 23, 42, 0.4);
    backdrop-filter: blur(8px);
    transition: all 0.2s ease; 
}
.name-card:hover { 
    border-color: #FBBF24; 
    background: rgba(15, 23, 42, 0.7);
}

/* ===== HERO SECTION ===== */
.hero { 
    text-align: center; 
    padding: 60px 20px 40px 20px; 
    margin-bottom: 40px; 
    border-bottom: 1px solid rgba(255,255,255,0.05); 
    background: radial-gradient(circle at top, rgba(251, 191, 36, 0.15) 0%, transparent 70%); 
}
.bismillah { 
    font-family: 'Scheherazade New', serif; 
    font-size: 42px; 
    color: #FBBF24; 
    margin-bottom: 16px; 
    text-shadow: 0 0 20px rgba(251, 191, 36, 0.4); 
}
.title { 
    font-size: 48px; 
    font-weight: 700; 
    margin-bottom: 8px; 
    font-family: 'Playfair Display', serif; 
    background: linear-gradient(to right, #FBBF24, #FEF08A);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 2px 10px rgba(251, 191, 36, 0.2);
}
.subtitle { 
    font-size: 18px; 
    color: #CBD5E1; 
    font-weight: 300; 
    letter-spacing: 1px; 
}

/* ===== TEXT & UI ELEMENTS ===== */
.arabic { 
    font-family: 'Scheherazade New', serif; 
    font-size: 36px; 
    direction: rtl; 
    text-align: right; 
    margin-bottom: 16px; 
    line-height: 1.8; 
    color: #FDE047; 
    text-shadow: 0 2px 4px rgba(0,0,0,0.5);
}
.section-title { 
    font-family: 'Playfair Display', serif; 
    font-size: 26px; 
    color: #FBBF24; 
    margin: 40px 0 20px 0; 
    padding-bottom: 10px; 
    border-bottom: 1px solid rgba(251, 191, 36, 0.2); 
}
.info-box { 
    background-color: rgba(251, 191, 36, 0.08); 
    border-left: 4px solid #FBBF24; 
    border-radius: 6px; 
    padding: 16px 20px; 
    font-size: 15px; 
    margin-bottom: 24px; 
    color: #F8FAFC; 
    backdrop-filter: blur(4px);
}
.accent { color: #FBBF24 !important; font-weight: 600; }
.muted { color: #94A3B8 !important; font-size: 0.9em; font-weight: 400; }
.source-link { color: #60A5FA; text-decoration: none; border-bottom: 1px dotted #60A5FA; transition: opacity 0.2s; }
.source-link:hover { opacity: 0.7; color: #93C5FD; }
.pill-badge { font-size: 11px; border: 1px solid #FBBF24; color: #FBBF24; padding: 4px 10px; border-radius: 20px; text-transform: uppercase; letter-spacing: 1px; margin-left: 10px; }

/* ===== SIDEBAR & INPUT ===== */
[data-testid="stSidebar"] { 
    background-color: rgba(2, 6, 23, 0.8) !important; 
    backdrop-filter: blur(15px);
    border-right: 1px solid rgba(251, 191, 36, 0.15); 
}
input, textarea { 
    background-color: rgba(15, 23, 42, 0.6) !important; 
    border: 1px solid rgba(251, 191, 36, 0.3) !important; 
    color: #fff !important; 
    border-radius: 8px !important; 
}
input:focus, textarea:focus { border-color: #FBBF24 !important; box-shadow: 0 0 8px rgba(251, 191, 36, 0.4) !important; }
.stButton > button { 
    background: linear-gradient(135deg, rgba(251, 191, 36, 0.1), rgba(251, 191, 36, 0.05)); 
    color: #FBBF24; 
    border: 1px solid #FBBF24; 
    border-radius: 8px; 
    transition: all 0.3s ease; 
    font-weight: 500;
}
.stButton > button:hover { 
    background: #FBBF24; 
    color: #020617; 
    transform: scale(1.02);
    box-shadow: 0 4px 15px rgba(251, 191, 36, 0.3);
}
.creator-footer { text-align: center; padding: 30px 10px; margin-top: auto; font-family: 'Playfair Display', serif; color: #FBBF24; border-top: 1px solid rgba(251, 191, 36, 0.2); font-size: 18px; letter-spacing: 1px; }

/* ===== TASBIH STYLES ===== */
.tasbih-count { font-size: 56px; color: #FBBF24; text-align: center; font-family: 'Inter', sans-serif; font-weight: 700; text-shadow: 0 0 20px rgba(251, 191, 36, 0.3); }
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

NAMES_RAW = "الرَّحْمَن|Ar-Rahman|The Entirely Merciful,الرَّحِيم|Ar-Rahim|The Especially Merciful,الْمَلِك|Al-Malik|The Sovereign,الْقُدُّوس|Al-Quddus|The Most Holy,السَّلاَم|As-Salam|The Source of Peace,الْمُؤْمِن|Al-Mu'min|The Guarantor,الْمُهَيْمِن|Al-Muhaymin|The Guardian,الْعَزِيز|Al-Aziz|The Almighty,الْجَبَّار|Al-Jabbar|The Compeller,الْمُتَكَبِّر|Al-Mutakabbir|The Supreme,الْخَالِق|Al-Khaliq|The Creator,الْبَارِئ|Al-Bari'|The Evolver,الْمُصَوِّر|Al-Musawwir|The Fashioner,الْغَفَّار|Al-Ghaffar|The Repeatedly Forgiving,الْقَهَّار|Al-Qahhar|The Subduer,الْوَهَّاب|Al-Wahhab|The Bestower,الرَّزَّاق|Ar-Razzaq|The Provider,الْفَتَّاح|Al-Fattah|The Opener,الْعَلِيم|Al-Aleem|The Knowing,الْقَابِض|Al-Qabid|The Withholder,الْبَاسِط|Al-Basit|The Extender,الْخَافِض|Al-Khafid|The Abaser,الرَّافِع|Ar-Rafi'|The Exalter,الْمُعِزّ|Al-Mu'izz|The Honorer,الْمُذِلّ|Al-Mudhill|The Dishonorer,السَّمِيع|As-Sami'|The Hearing,الْبَصِير|Al-Basir|The Seeing,الْحَكَم|Al-Hakam|The Judge,الْعَدْل|Al-Adl|The Just,اللَّطِيف|Al-Latif|The Subtle One,الْخَبِير|Al-Khabir|The Acquainted,الْحَلِيم|Al-Haleem|The Forbearing,الْعَظِيم|Al-Azeem|The Magnificent"
NAMES_99 = [name.split('|') for name in NAMES_RAW.split(',')]

DYNAMIC_PROPHETS = ["Prophet Adam (as)", "Prophet Nuh (as)", "Prophet Ibrahim (as)", "Prophet Yusuf (as)", "Prophet Musa (as)", "Prophet Isa (as)", "Prophet Muhammad (ﷺ)"]
DYNAMIC_STORIES = ["People of the Cave (Ashab al-Kahf)", "Musa and Al-Khidr", "The Men of the Elephant", "Qarun (Korah)"]
TIBB_TOPICS = ["Black Seed (Habbatul Barakah)", "Honey", "Cupping (Hijama)", "Dates (Ajwa)", "Olive Oil", "Siwak (Miswak)"]
TRIVIA_TOPICS = ["Life of Prophet Muhammad (ﷺ)", "Quranic Facts", "The 5 Pillars of Islam", "Stories of the Prophets", "Women in Islam"]

# ==========================================
# STATE MANAGEMENT
# ==========================================
if "messages" not in st.session_state: st.session_state.messages = []
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "loaded_surah_number" not in st.session_state: st.session_state.loaded_surah_number = None
if "daily_inspo" not in st.session_state: st.session_state.daily_inspo = random.choice(HADITH_40)
if "tasbih_count" not in st.session_state: st.session_state.tasbih_count = 0

# ==========================================
# HELPER FUNCTIONS (RESTORED & FIXED)
# ==========================================
def safe_html(value): 
    return escape("" if value is None else str(value))

def source_link(label, url):
    safe_label = safe_html(label)
    if url:
        if not str(url).startswith(('http://', 'https://')): url = '#'
        return f'<a class="source-link" href="{escape(url, quote=True)}" target="_blank">{safe_label}</a>'
    return safe_label

def contains_any(text, terms): 
    return any(term in text.lower() for term in terms)

def is_dua_query(text):
    q = text.lower().strip()
    return contains_any(q, ["dua", "duas", "adhkar", "azkar", "supplication", "dhikr", "zikr", "sleep", "anxiety", "stress", "travel", "home", "eat", "eating", "forgiveness", "دعاء", "ذكر"])

def detect_curated_route(text):
    q = text.lower().strip()
    if contains_any(q, ["sleep", "before sleep", "sleeping"]): return "Before Sleep"
    if contains_any(q, ["morning adhkar", "morning azkar", "subah"]): return "Morning Adhkar"
    if contains_any(q, ["rabbana", "quran dua"]): return "Quranic Rabbana Duas"
    return None

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

def build_curated_response(category_name):
    return {
        "direct_answer": f"Here are verified duas from the category: {category_name}",
        "quran_evidence": [], "hadith_evidence": [], "scholarly_opinions": [], "dua": {},
        "duas": DUA_CATEGORIES.get(category_name, []),
        "ikhtilaf": "No", "conclusion": "", "consult_scholar": "No",
        "source_notice": "Dua text pulled from built-in verified collection.",
    }

def hide_unverified_model_dua(result):
    result = normalize_result(result)
    result["dua"] = {}
    result["duas"] = []
    result["source_notice"] = "For safety, AI-generated dua wording is hidden. Please refer to the authentic Dua Collection tab."
    if not result["conclusion"]:
        result["conclusion"] = "Please consult a verified Hisnul Muslim for highly specific unlisted duas."
    return result

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
    st.markdown('<div style="text-align:center;"><h2 style="color:#FBBF24; margin-bottom:5px;">Muslim AI</h2><div style="color:#94A3B8; font-size:14px; text-transform:uppercase; letter-spacing:1.5px;">Knowledge & Reflection</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown('<div style="background:rgba(15, 23, 42, 0.4); padding:18px; border-radius:12px; border:1px solid rgba(251, 191, 36, 0.3); backdrop-filter:blur(10px);"><h4 style="margin-top:0; color:#FBBF24; font-size:13px; text-transform:uppercase; letter-spacing:1px;">✨ Daily Inspiration</h4>'
                f'<div class="arabic" style="font-size:26px; text-align:center; color:#FEF08A;">{st.session_state.daily_inspo["arabic"]}</div>'
                f'<div style="font-size:14px; font-style:italic; margin-bottom:12px; color:#F8FAFC;">"{st.session_state.daily_inspo["text"]}"</div>'
                f'<div style="font-size:12px; color:#FBBF24; font-weight:600;">- {st.session_state.daily_inspo["source"]}</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.chat_history = []; st.session_state.messages = []; st.rerun()
        
    st.markdown('<div class="creator-footer">Created by Aadil Rather</div>', unsafe_allow_html=True)

# ==========================================
# MAIN TABS
# ==========================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🤖 AI Chat", "📖 Quran Reader", "🕌 Prayer & Qibla", "📿 Tasbih & Dua", "📚 Hadith & Names", "📜 Deep Knowledge"])

# ----------------- TAB 1: AI CHAT & FIRST AID -----------------
with tab1: 
    st.markdown("### Spiritual First Aid")
    st.markdown("<span class='muted'>Select how you are feeling to receive instant Quranic comfort and guidance.</span>", unsafe_allow_html=True)
    mood_cols = st.columns(4)
    moods = ["Anxious 😟", "Sad 😢", "Angry 😠", "Grateful 🙏", "Lost 🧭", "Seeking Forgiveness 🤲"]
    
    selected_mood = None
    for i, mood in enumerate(moods):
        if mood_cols[i % 4].button(mood, use_container_width=True):
            selected_mood = mood
            
    if selected_mood:
        prompt = f"I am feeling {selected_mood}. Please provide a comforting Islamic perspective, a relevant Ayah, and a short Dua to help me."
        with st.spinner("Finding comfort..."):
            try:
                raw = call_api(prompt, [])
                render_response(parse_response(raw))
            except Exception: st.error("Error retrieving guidance.")
            
    st.markdown("---")
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
                    route = detect_curated_route(user_input)
                    if route:
                        result = build_curated_response(route)
                    else:
                        raw = call_api(user_input, st.session_state.chat_history)
                        result = parse_response(raw)
                        if is_dua_query(user_input):
                            result = hide_unverified_model_dua(result)
                    render_response(result)
                    st.session_state.messages.append({"role": "assistant", "content": json.dumps(result, ensure_ascii=False)})
                    st.session_state.chat_history.append({"user": user_input, "assistant": result.get("direct_answer", "")})
                except Exception as e: st.error("Error processing request.")

# ----------------- TAB 2: QURAN & AUDIO -----------------
with tab2: 
    st.markdown('<div class="section-title" style="margin-top:0;">The Holy Quran (Read & Listen)</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        selected_surah = st.selectbox("Select Surah", [f"{i + 1}. {name}" for i, name in enumerate(SURAH_NAMES)])
        if st.button("Load Surah", type="primary", use_container_width=True): 
            st.session_state.loaded_surah_number = int(selected_surah.split(".")[0])
            
    with col2:
        if st.session_state.loaded_surah_number:
            # Audio Player (Mishary Alafasy)
            audio_url = f"https://server8.mp3quran.net/afs/{st.session_state.loaded_surah_number:03d}.mp3"
            st.markdown('<div class="premium-card" style="text-align:center;"><strong class="accent" style="font-size:18px;">🔊 Listen to Full Surah Recitation:</strong><br><br>', unsafe_allow_html=True)
            st.audio(audio_url, format="audio/mp3")
            st.markdown('</div>', unsafe_allow_html=True)
            
            surah_data = fetch_quran_surah(st.session_state.loaded_surah_number)
            if surah_data:
                ar, en = surah_data[0], surah_data[1]
                st.markdown(f'<div class="arabic" style="font-size:48px; text-align:center; margin-bottom:40px; color:#FEF08A;">{safe_html(ar.get("name", ""))}</div>', unsafe_allow_html=True)
                for i, ayah in enumerate(ar.get("ayahs", [])):
                    eng_text = en.get("ayahs", [])[i].get("text", "") if i < len(en.get("ayahs", [])) else ""
                    st.markdown(f'<div class="premium-card"><div class="muted" style="color:#FBBF24 !important; font-weight:600; letter-spacing:1px; margin-bottom:10px;">AYAH {ayah.get("numberInSurah")}</div><div class="arabic">{safe_html(ayah.get("text"))}</div><div style="font-size:18px; line-height:1.7; color:#E2E8F0;">{safe_html(eng_text)}</div></div>', unsafe_allow_html=True)

# ----------------- TAB 3: PRAYER, QIBLA & ZAKAT -----------------
with tab3: 
    st.markdown('<div class="section-title" style="margin-top:0;">Live Prayer Times & Qibla Compass</div>', unsafe_allow_html=True)
    pc1, pc2 = st.columns(2)
    with pc1: city = st.text_input("City", value="Mecca")
    with pc2: country = st.text_input("Country", value="Saudi Arabia")
    
    if st.button("Get Timings & Qibla", type="primary"):
        times_data = fetch_prayer_times(city, country)
        if times_data:
            timings = times_data["timings"]
            date_hijri = times_data["date"]["hijri"]
            qibla_deg = times_data.get("meta", {}).get("qibla", "Unknown")
            
            st.markdown(f'<div class="info-box" style="text-align:center; font-size:20px;"><strong class="accent">{date_hijri["day"]} {date_hijri["month"]["en"]} {date_hijri["year"]} AH</strong><br><br>🧭 <strong style="color:#60A5FA;">Qibla Direction:</strong> {qibla_deg}° <span class="muted">(Degrees from North)</span></div>', unsafe_allow_html=True)
            
            cols = st.columns(6)
            prayers = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
            for i, p in enumerate(prayers):
                cols[i].markdown(f'<div class="name-card"><strong class="accent">{p}</strong><br><br><span style="font-size:22px; color:#fff;">{timings[p]}</span></div>', unsafe_allow_html=True)
        else: st.error("Could not fetch times. Check city/country spelling.")

    st.markdown('<div class="section-title">Zakat Calculator (2.5%)</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Enter your assets. If your net wealth is above the Nisab threshold, your Zakat is 2.5%.</div>', unsafe_allow_html=True)
    zc1, zc2, zc3 = st.columns(3)
    with zc1: cash = st.number_input("Cash & Savings ($)", min_value=0.0)
    with zc2: gold = st.number_input("Value of Gold/Silver ($)", min_value=0.0)
    with zc3: debt = st.number_input("Short-term Debts ($)", min_value=0.0)
    
    net_wealth = (cash + gold) - debt
    zakat = net_wealth * 0.025 if net_wealth > 0 else 0.0
    st.markdown(f'<div class="premium-card" style="text-align:center; background:rgba(15, 23, 42, 0.8);"><h2>Estimated Zakat Due:<br><br><span style="color:#FBBF24; font-size:48px;">${zakat:,.2f}</span></h2></div>', unsafe_allow_html=True)

# ----------------- TAB 4: SMART TASBIH & DUA -----------------
with tab4:
    st.markdown('<div class="section-title" style="margin-top:0;">Smart Tasbih (Digital Dhikr)</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Keep track of your daily Dhikr. Traditional Goal: 33 repetitions.</div>', unsafe_allow_html=True)
    
    t_col1, t_col2 = st.columns([1, 1])
    with t_col1:
        if st.button("➕ Tap to Count", use_container_width=True):
            st.session_state.tasbih_count += 1
            if st.session_state.tasbih_count == 33:
                st.toast("Goal of 33 reached! Alhamdulillah.", icon="✨")
        if st.button("🔄 Reset Counter", use_container_width=True):
            st.session_state.tasbih_count = 0
            
    with t_col2:
        st.markdown(f'<div class="premium-card" style="padding:15px;"><div class="tasbih-count">{st.session_state.tasbih_count} <span style="font-size:24px; color:#aaa;">/ 33</span></div></div>', unsafe_allow_html=True)
        progress = min(st.session_state.tasbih_count / 33.0, 1.0)
        st.progress(progress)

    st.markdown('<div class="section-title">Fortress of the Muslim (Dua)</div>', unsafe_allow_html=True)
    selected_category = st.selectbox("Select Collection", list(DUA_CATEGORIES.keys()))
    for dua in DUA_CATEGORIES.get(selected_category, []):
        st.markdown(
            f'<div class="premium-card"><h3 style="margin-top:0;">{safe_html(dua["title"])}</h3>'
            f'<div class="arabic" style="margin: 20px 0;">{safe_html(dua.get("arabic", ""))}</div>'
            f'<strong class="accent" style="font-size:14px; text-transform:uppercase;">Transliteration</strong><br><span style="color:#CBD5E1; line-height:1.6; display:inline-block; margin-bottom:16px;">{safe_html(dua.get("transliteration", ""))}</span><br>'
            f'<strong class="accent" style="font-size:14px; text-transform:uppercase;">Meaning</strong><br><span style="font-size:16px; line-height:1.6; color:#F8FAFC;">{safe_html(dua.get("meaning", ""))}</span>'
            f'<div style="margin-top:20px; border-top:1px solid rgba(251, 191, 36, 0.2); padding-top:12px;"><span class="muted">Reference: {source_link(dua.get("reference", ""), dua.get("source_url", ""))}</span></div></div>',
            unsafe_allow_html=True,
        )

# ----------------- TAB 5: HADITH & NAMES -----------------
with tab5:
    st.markdown('<div class="section-title" style="margin-top:0;">An-Nawawi\'s 40 Hadith</div>', unsafe_allow_html=True)
    for h in HADITH_40:
        st.markdown(
            f'<div class="premium-card"><div class="muted" style="margin-bottom:16px; font-weight:600; color:#FBBF24 !important; letter-spacing:1.5px;">HADITH {h["number"]}</div>'
            f'<div class="arabic">{safe_html(h["arabic"])}</div>'
            f'<div style="font-size:20px; line-height:1.7; margin:20px 0; color:#F8FAFC;">"{safe_html(h["text"])}"</div>'
            f'<div style="border-top:1px solid rgba(251, 191, 36, 0.2); padding-top:12px;"><span class="muted">Source: <span style="color:#FBBF24;">{safe_html(h["source"])}</span></span></div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-title">The 99 Names of Allah (Asma-ul-Husna)</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">The first 33 beautiful names of Allah.</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for i, name_data in enumerate(NAMES_99):
        cols[i % 3].markdown(f'<div class="name-card"><div class="arabic" style="font-size:32px; text-align:center; margin-bottom:10px; color:#FEF08A;">{name_data[0]}</div><strong style="color:#FBBF24; font-size:18px;">{name_data[1]}</strong><br><br><span style="color:#CBD5E1; font-size:15px;">{name_data[2]}</span></div>', unsafe_allow_html=True)

# ----------------- TAB 6: DEEP KNOWLEDGE & TRIVIA -----------------
with tab6:
    st.markdown('<div class="section-title" style="margin-top:0;">Dynamic Islamic Sciences & AI Trivia</div>', unsafe_allow_html=True)
    
    # TRIVIA SECTION
    st.markdown('<div class="premium-card" style="border-color:#FBBF24; background:rgba(251, 191, 36, 0.05);"><h3>🧠 AI Trivia Master</h3><p style="color:#CBD5E1;">Test your knowledge! Select a topic and the AI will generate a custom 5-question multiple choice quiz.</p>', unsafe_allow_html=True)
    t_col1, t_col2 = st.columns([2,1])
    with t_col1: selected_trivia = st.selectbox("Select Trivia Topic", TRIVIA_TOPICS)
    with t_col2: 
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Generate Custom Quiz", use_container_width=True):
            with st.spinner("Generating Quiz..."):
                try:
                    prompt = f"Create a 5-question multiple choice trivia quiz about '{selected_trivia}'. Format it clearly with Question 1, 2, etc. Put the Answer Key at the very bottom."
                    raw = call_api(prompt, [])
                    st.markdown(f'<div style="margin-top:20px; font-size:16px; line-height:1.7;">{safe_html(parse_response(raw)["direct_answer"]).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                except Exception: st.error("Failed to generate quiz.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # SEERAH & TIBB SECTION
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<h3 class="accent">Prophetic History (Stories)</h3>', unsafe_allow_html=True)
        selected_story = st.selectbox("Select a Prophet or Event", DYNAMIC_PROPHETS + DYNAMIC_STORIES)
        if st.button("Generate History Profile", use_container_width=True):
            with st.spinner(f"Extracting authentic history for {selected_story}..."):
                try:
                    prompt = f"Provide a complete, multi-paragraph, highly detailed profile of '{selected_story}'. Base it strictly on Quran and authentic Ahadith/Tafseer. Detail the motives, major events, and moral legacy."
                    raw = call_api(prompt, [])
                    render_response(parse_response(raw))
                except Exception: st.error("Failed to generate history.")
                
    with col_b:
        st.markdown('<h3 class="accent">Prophetic Medicine (Tibb)</h3>', unsafe_allow_html=True)
        selected_tibb = st.selectbox("Select a Remedy", TIBB_TOPICS)
        if st.button("Generate Medicine Profile", use_container_width=True):
            with st.spinner(f"Extracting authentic knowledge on {selected_tibb}..."):
                try:
                    prompt = f"Provide a comprehensive overview of '{selected_tibb}' in Islam. Cite authentic Hadith mentioning it, and explain its spiritual and physical benefits according to Prophetic Medicine."
                    raw = call_api(prompt, [])
                    render_response(parse_response(raw))
                except Exception: st.error("Failed to generate medicine profile.")
