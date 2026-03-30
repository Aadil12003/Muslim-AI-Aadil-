import json
import os
import re
import time
from html import escape

import requests
import streamlit as st

# Page setup
st.set_page_config(page_title="Muslim AI", layout="wide", initial_sidebar_state="expanded")

# Premium styling
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&family=Scheherazade+New:wght@700&display=swap');
:root {
  --bg:#0a0c0f;
  --panel:rgba(18,22,29,0.92);
  --glass:rgba(255,255,255,0.05);
  --stroke:rgba(255,255,255,0.08);
  --gold:#e3c07a;
  --accent:#9ff0d0;
  --text:#f4f6fb;
  --muted:#a9b6cc;
  --success:#62f2c3;
  --info:#8ec5ff;
}
html, body, .stApp {
  background: radial-gradient(90% 70% at 10% 10%, rgba(159,240,208,0.12), transparent 45%),
              radial-gradient(70% 60% at 80% 0%, rgba(227,192,122,0.12), transparent 40%),
              linear-gradient(135deg,#0a0c0f 0%,#0f1823 50%,#0c141d 100%);
  color: var(--text);
  font-family: 'Plus Jakarta Sans', sans-serif;
}
.block-container { padding-top: 1.2rem; }
.hero { background: linear-gradient(135deg, rgba(15,22,35,0.9), rgba(20,34,54,0.92)); border:1px solid var(--stroke); border-radius:20px; padding:22px; box-shadow: 0 22px 60px rgba(0,0,0,0.45); }
.hero .bismillah { font-family:'Scheherazade New',serif; font-size:38px; color:var(--gold); text-align:center; direction:rtl; }
.hero .title { font-family:'Playfair Display',serif; font-size:44px; text-align:center; margin:8px 0 2px 0; color:var(--gold); letter-spacing:0.4px; }
.hero .subtitle { text-align:center; color:var(--muted); font-size:15px; }
.card, .answer, .quran-card, .hadith-card, .dua-card, .scholar-card, .info-box, .warning-card, .reader-card { background: var(--panel); border:1px solid var(--stroke); border-radius:14px; padding:16px 18px; margin-bottom:12px; line-height:1.7; backdrop-filter: blur(5px); }
.answer { border:1px solid rgba(227,192,122,0.35); box-shadow: 0 10px 28px rgba(0,0,0,0.35); }
.quran-card { border-left:4px solid var(--success); background: linear-gradient(135deg, rgba(16,42,32,0.9), rgba(12,33,25,0.92)); }
.hadith-card { border-left:4px solid var(--info); background: linear-gradient(135deg, rgba(19,28,46,0.9), rgba(13,22,38,0.92)); }
.dua-card { border-left:4px solid var(--accent); background: linear-gradient(135deg, rgba(20,30,36,0.9), rgba(16,26,32,0.92)); }
.scholar-card { border-left:4px solid var(--gold); background: linear-gradient(135deg, rgba(40,28,16,0.92), rgba(52,34,18,0.94)); }
.reader-card { border-left:4px solid var(--success); }
.info-box { border:1px dashed var(--stroke); color:var(--muted); }
.warning-card { border-left:4px solid #f97373; background: linear-gradient(135deg, rgba(62,18,18,0.93), rgba(82,24,24,0.95)); color:#ffeaea; }
.section-title { font-size:19px; font-weight:700; color:var(--gold); margin:18px 0 10px 0; padding-bottom:6px; border-bottom:1px solid var(--stroke); letter-spacing:0.2px; }
.arabic { font-family:'Scheherazade New',serif; font-size:30px; direction:rtl; text-align:right; color:#f0d589; line-height:2.15; margin:10px 0; }
.translation { color:#cde0d1; font-style:italic; }
.badge { display:inline-block; padding:3px 10px; border-radius:999px; font-size:12px; font-weight:700; color:#fff; }
.badge.sahih { background:#2ea76d; } .badge.hasan { background:#d7952e; } .badge.weak { background:#c25757; }
div[data-testid="stTab"] button { background:rgba(255,255,255,0.03); color:var(--muted); border:1px solid var(--stroke); border-radius:10px; padding:8px 16px; }
div[data-testid="stTab"] button[aria-selected="true"] { background:var(--panel); color:var(--text); border-color:var(--gold); box-shadow:none; }
input, textarea { background:#111826 !important; color:var(--text) !important; border-radius:10px !important; border:1px solid var(--stroke) !important; }
.stChatInput textarea { min-height:44px !important; }
button, .stButton>button { background:linear-gradient(135deg,#1f2a44,#2c3a57) !important; color:#f7f9ff !important; border-radius:10px !important; border:1px solid #2f3d5a !important; box-shadow:none !important; font-weight:600; }
[data-testid="stSidebar"] .stButton>button { width:100%; background:#1f2a44 !important; color:#f7f9ff !important; border:1px solid #2c3a57 !important; box-shadow:none !important; }
[data-testid="stSidebar"] .stButton>button:hover { background:#2a3a57 !important; }
[data-testid="stSidebar"] .stButton>button:focus { outline:1px solid var(--gold); }
</style>
""",
    unsafe_allow_html=True,
)

# Config
try:
    NVIDIA_API_KEY = st.secrets["NVIDIA_API_KEY"]
except Exception:
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "").strip()

if not NVIDIA_API_KEY:
    st.error("Missing NVIDIA_API_KEY. Add it in Streamlit secrets or environment variables.")
    st.stop()

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "meta/llama-4-maverick-17b-128e-instruct"

SYSTEM_PROMPT = """You are an Islamic AI Assistant. Respond only with authentic Quran, Sahih Hadith, and recognized scholarly opinion.
- Do NOT fabricate references.
- If unsure, say you are unsure.
- Return ONLY valid JSON, nothing else.
{
  "direct_answer": "concise answer",
  "quran_evidence": [{"arabic": "", "translation": "", "reference": "", "explanation": ""}],
  "hadith_evidence": [{"text": "", "arabic": "", "source": "", "authenticity": "Sahih", "note": ""}],
  "scholarly_opinions": [{"madhab": "", "opinion": "", "source": ""}],
  "dua": {"title": "", "arabic": "", "transliteration": "", "meaning": "", "reference": "", "source_url": ""},
  "duas": [],
  "ikhtilaf": "Yes or No",
  "conclusion": "summary",
  "consult_scholar": "Yes or No",
  "language_detected": "English or Urdu or Arabic"
}"""

# Data
SURAH_NAMES = [
    "Al-Fatiha","Al-Baqarah","Al-Imran","An-Nisa","Al-Maidah","Al-Anam","Al-Araf","Al-Anfal","At-Tawbah","Yunus","Hud","Yusuf",
    "Ar-Rad","Ibrahim","Al-Hijr","An-Nahl","Al-Isra","Al-Kahf","Maryam","Ta-Ha","Al-Anbiya","Al-Hajj","Al-Muminun","An-Nur",
    "Al-Furqan","Ash-Shuara","An-Naml","Al-Qasas","Al-Ankabut","Ar-Rum","Luqman","As-Sajdah","Al-Ahzab","Saba","Fatir","Ya-Sin",
    "As-Saffat","Sad","Az-Zumar","Ghafir","Fussilat","Ash-Shura","Az-Zukhruf","Ad-Dukhan","Al-Jathiyah","Al-Ahqaf","Muhammad","Al-Fath",
    "Al-Hujurat","Qaf","Adh-Dhariyat","At-Tur","An-Najm","Al-Qamar","Ar-Rahman","Al-Waqiah","Al-Hadid","Al-Mujadila","Al-Hashr","Al-Mumtahanah",
    "As-Saf","Al-Jumuah","Al-Munafiqun","At-Taghabun","At-Talaq","At-Tahrim","Al-Mulk","Al-Qalam","Al-Haqqah","Al-Maarij","Nuh","Al-Jinn",
    "Al-Muzzammil","Al-Muddaththir","Al-Qiyamah","Al-Insan","Al-Mursalat","An-Naba","An-Naziat","Abasa","At-Takwir","Al-Infitar","Al-Mutaffifin","Al-Inshiqaq",
    "Al-Buruj","At-Tariq","Al-Ala","Al-Ghashiyah","Al-Fajr","Al-Balad","Ash-Shams","Al-Layl","Ad-Duhaa","Ash-Sharh","At-Tin","Al-Alaq",
    "Al-Qadr","Al-Bayyinah","Az-Zalzalah","Al-Adiyat","Al-Qariah","At-Takathur","Al-Asr","Al-Humazah","Al-Fil","Quraysh","Al-Maun","Al-Kawthar",
    "Al-Kafirun","An-Nasr","Al-Masad","Al-Ikhlas","Al-Falaq","An-Nas"
]

DUA_CATEGORIES = {
    "Morning Adhkar": [
        {"title": "Morning Remembrance", "arabic": "أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ، لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ", "transliteration": "Asbahna wa asbaha al-mulku lillah, wal-hamdu lillah, la ilaha illa Allah wahdahu la sharika lah", "meaning": "We have entered the morning and the kingdom belongs to Allah. All praise is for Allah; none has the right to be worshipped except Him alone, without partner.", "reference": "Abu Dawood 4/317", "source_url": ""},
        {"title": "Sayyidul Istighfar", "arabic": "اللَّهُمَّ أَنْتَ رَبِّي لَا إِلَهَ إِلَّا أَنْتَ، خَلَقْتَنِي وَأَنَا عَبْدُكَ", "transliteration": "Allahumma anta rabbi la ilaha illa anta, khalaqtani wa ana abduk", "meaning": "O Allah, You are my Lord; none has the right to be worshipped except You. You created me and I am Your servant.", "reference": "Bukhari 6306", "source_url": "https://sunnah.com/bukhari:6306"}
    ],
    "Evening Adhkar": [
        {"title": "Evening Remembrance", "arabic": "أَمْسَيْنَا وَأَمْسَى الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ، لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ", "transliteration": "Amsayna wa amsa al-mulku lillah, wal-hamdu lillah, la ilaha illa Allah wahdahu la sharika lah", "meaning": "We have entered the evening and the kingdom belongs to Allah. All praise is for Allah; none has the right to be worshipped but Him alone, without partner.", "reference": "Abu Dawood 4/317", "source_url": ""}
    ],
    "Before Sleep": [
        {"title": "Before Sleeping", "arabic": "بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا", "transliteration": "Bismika Allahumma amootu wa ahya", "meaning": "In Your name, O Allah, I die and I live.", "reference": "Bukhari 6324", "source_url": "https://sunnah.com/bukhari:6324"},
        {"title": "Ayatul Kursi", "arabic": "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ", "transliteration": "Allahu la ilaha illa huwa al-hayyul-qayyum", "meaning": "Allah! None has the right to be worshipped but He, the Ever Living, the Sustainer of all.", "reference": "Quran 2:255", "source_url": "https://quran.com/2/255"}
    ],
    "Entering Home": [
        {"title": "Entering Home", "arabic": "اللَّهُمَّ إِنِّي أَسْأَلُكَ خَيْرَ الْمَوْلَجِ وَخَيْرَ الْمَخْرَجِ", "transliteration": "Allahumma inni as'aluka khayral mawlaji wa khayral makhraji", "meaning": "O Allah, I ask You for the good of entering and the good of leaving.", "reference": "Abu Dawood 4/325", "source_url": ""}
    ],
    "Eating and Drinking": [
        {"title": "Before Eating", "arabic": "بِسْمِ اللَّهِ", "transliteration": "Bismillah", "meaning": "In the name of Allah.", "reference": "Tirmidhi 1858", "source_url": "https://sunnah.com/tirmidhi:1858"},
        {"title": "After Eating", "arabic": "الْحَمْدُ لِلَّهِ الَّذِي أَطْعَمَنَا وَسَقَانَا وَجَعَلَنَا مُسْلِمِينَ", "transliteration": "Alhamdu lillahil ladhi at'amana wa saqana wa ja'alana muslimin", "meaning": "All praise is for Allah who fed us, gave us drink, and made us Muslims.", "reference": "Abu Dawood 3850", "source_url": ""}
    ],
    "Anxiety and Distress": [
        {"title": "Dua for Anxiety", "arabic": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ", "transliteration": "Allahumma inni a'udhu bika minal hammi wal hazan", "meaning": "O Allah, I seek refuge in You from anxiety and grief.", "reference": "Bukhari 6363", "source_url": ""}
    ],
    "Travel": [
        {"title": "Dua for Travel", "arabic": "سُبْحَانَ الَّذِي سَخَّرَ لَنَا هَذَا وَمَا كُنَّا لَهُ مُقْرِنِينَ", "transliteration": "Subhanal ladhi sakhkhara lana hadha wa ma kunna lahu muqrinin", "meaning": "Glory be to Him who has subjected this to us, and we could never have it by our efforts.", "reference": "Quran 43:13 / Abu Dawood 2599", "source_url": "https://quran.com/43/13"}
    ],
    "Forgiveness": [
        {"title": "Seeking Forgiveness", "arabic": "رَبِّ اغْفِرْ لِي وَتُبْ عَلَيَّ إِنَّكَ أَنْتَ التَّوَّابُ الرَّحِيمُ", "transliteration": "Rabbighfir li wa tub alayya innaka anta at-Tawwabur-Rahim", "meaning": "My Lord, forgive me and accept my repentance. Truly, You are the Accepter of repentance, the Most Merciful.", "reference": "Abu Dawood / Ibn Majah", "source_url": ""}
    ]
}

HADITH_40 = [
    {"number": i + 1, "text": txt}
    for i, txt in enumerate([
        "Actions are judged by intentions.",
        "Islam is built on five pillars.",
        "Every innovation is misguidance.",
        "The lawful is clear and the unlawful is clear.",
        "Religion is sincere advice.",
        "Avoid what is doubtful.",
        "The world is a prison for the believer and a paradise for the disbeliever.",
        "None of you truly believes until he loves for his brother what he loves for himself.",
        "From the excellence of a person's Islam is leaving what does not concern him.",
        "Do not become angry.",
        "Say I believe in Allah and then be upright.",
        "The believer is the mirror of his brother.",
        "A good word is charity.",
        "Purity is half of faith.",
        "Whoever believes in Allah and the Last Day should speak good or remain silent.",
        "Seek halal and your supplication will be answered.",
        "Whoever is not merciful to people, Allah will not be merciful to him.",
        "Modesty brings nothing but good.",
        "From the perfection of faith is loving and hating for the sake of Allah.",
        "The strong person controls himself when angry.",
        "The best of you are those best to their families.",
        "Backbiting is mentioning about your brother what he dislikes.",
        "A Muslim is one from whose tongue and hand other Muslims are safe.",
        "The upper hand is better than the lower hand.",
        "Allah does not look at your forms but at your hearts and deeds.",
        "Whoever does not thank people has not thanked Allah.",
        "Make things easy and do not make them difficult.",
        "He is not of us who does not show mercy to the young and respect the old.",
        "Whoever cheats us is not one of us.",
        "The best charity is that given when you are healthy and covetous.",
        "The one who points to good is like the doer of it.",
        "None truly believes until his desires follow what I have brought.",
        "Leave what causes you doubt for what does not cause you doubt.",
        "There should be neither harming nor reciprocating harm.",
        "Allah is pure and accepts only what is pure.",
        "Every act of kindness is charity.",
        "Exchange gifts and you will love one another.",
        "Whoever treads a path seeking knowledge, Allah makes easy for him a path to Paradise.",
        "The best among you are those who learn the Qur’an and teach it.",
        "The most beloved deeds to Allah are those done consistently, even if small."
    ])
]

# Stories from Quran & Hadith (concise, verified references)
STORIES = [
    {"title": "Prophet Yusuf and Patience", "summary": "Yusuf (as) faced betrayal by his brothers, imprisonment, and hardship yet remained patient and trusting in Allah. His patience led to honor and reunion. See Surah Yusuf (12).", "source": "Quran 12"},
    {"title": "People of the Cave (Ashab al-Kahf)", "summary": "A group of youths fled oppression, sought refuge in a cave, and Allah preserved them for years as a sign of His power over life and death. See Surah Al-Kahf 18:9-26.", "source": "Quran 18:9-26"},
    {"title": "Musa and Khidr", "summary": "Musa (as) traveled to learn from Khidr about divine wisdom behind events that seem harmful, teaching patience and trust in Allah’s decree. See Surah Al-Kahf 18:60-82.", "source": "Quran 18:60-82"},
    {"title": "Maryam and the Birth of Isa", "summary": "Maryam (as) miraculously conceived Prophet Isa (as) and gave birth under a palm tree, reaffirming Allah’s limitless power. See Surah Maryam 19:16-36.", "source": "Quran 19:16-36"},
    {"title": "Abraham and the Fire", "summary": "Ibrahim (as) was thrown into a fire by his people for rejecting idolatry, but Allah made the fire cool and safe for him. See Surah Al-Anbiya 21:68-70.", "source": "Quran 21:68-70"}
]

# Brief life highlights of prophets (verified, concise)
PROPHETS = [
    {"name": "Muhammad (ﷺ)", "life": "Born in Makkah 570 CE. Received the Quran over 23 years. Established the Muslim community in Madinah. Passed away 632 CE. Character noted for truthfulness and mercy.", "sources": "Quran; Sahih Sira (Ibn Hisham, Ibn Kathir)"},
    {"name": "Ibrahim (as)", "life": "Called to pure monotheism, debated his people, tested with sacrifice of his son, rebuilt the Ka'bah with Ismail. Title: Khalilullah (friend of Allah).", "sources": "Quran 2:124-132; 6:74-83; 37:99-111"},
    {"name": "Musa (as)", "life": "Raised in Pharaoh’s palace, led Bani Israel out of Egypt, received the Torah, parted the sea by Allah’s leave.", "sources": "Quran 20; 26; 28"},
    {"name": "Isa (as)", "life": "Born miraculously to Maryam, spoke as an infant, performed miracles by Allah’s permission, raised as a prophet to Bani Israel; not crucified—Allah raised him.", "sources": "Quran 3; 4:157-158; 5:110; 19"},
    {"name": "Yusuf (as)", "life": "From well to slavery to prison to authority in Egypt; exemplified patience, chastity, and forgiveness.", "sources": "Quran 12"},
    {"name": "Nuh (as)", "life": "Preached for 950 years, built the Ark by Allah’s command, saved the believers from the flood.", "sources": "Quran 11:25-49; 71"},
    {"name": "Dawud (as)", "life": "Prophet-king, given the Zabur, known for justice and a beautiful recitation.", "sources": "Quran 38:17-26"},
    {"name": "Sulaiman (as)", "life": "Prophet-king with control over jinn, wind, and birds by Allah’s permission; exemplified gratitude.", "sources": "Quran 27; 34:12-19; 38:30-40"},
    {"name": "Yunus (as)", "life": "Left his people, swallowed by the great fish, repented with the dua “La ilaha illa Anta...”, delivered and returned to his people.", "sources": "Quran 21:87-88; 37:139-148"},
    {"name": "Ayub (as)", "life": "Severely tested in health and wealth, remained patient; Allah restored him and praised his patience.", "sources": "Quran 21:83-84; 38:41-44"}
]

# State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "quick_question" not in st.session_state:
    st.session_state.quick_question = ""
if "loaded_surah_number" not in st.session_state:
    st.session_state.loaded_surah_number = None

# Helpers
def safe_html(value):
    return escape("" if value is None else str(value))


def source_link(label, url):
    safe_label = safe_html(label)
    if url:
        return f'<a class="source-link" style="color:#9bcdfb;" href="{escape(url, quote=True)}" target="_blank">{safe_label}</a>'
    return safe_label


def contains_any(text, terms):
    return any(term in text for term in terms)


def is_dua_query(text):
    q = text.lower().strip()
    return contains_any(q, ["dua", "duas", "adhkar", "azkar", "supplication", "dhikr", "zikr", "sleep", "anxiety", "stress", "travel", "home", "eat", "eating", "forgiveness", "دعاء", "ذكر"])


def detect_curated_route(text):
    q = text.lower().strip()
    if contains_any(q, ["sleep", "before sleep", "sleeping", "neend", "dua before sleeping"]):
        return "Before Sleep"
    if contains_any(q, ["morning adhkar", "morning azkar", "morning dua", "subah"]):
        return "Morning Adhkar"
    if contains_any(q, ["evening adhkar", "evening azkar", "evening dua", "shaam"]):
        return "Evening Adhkar"
    if contains_any(q, ["anxiety", "stress", "worry", "distress", "gham", "pareshani"]):
        return "Anxiety and Distress"
    if contains_any(q, ["travel", "journey", "safar"]):
        return "Travel"
    if contains_any(q, ["entering home", "enter home", "home dua", "ghar"]):
        return "Entering Home"
    if contains_any(q, ["before eating", "food dua", "eat", "khana"]):
        return "Eating and Drinking"
    if contains_any(q, ["forgiveness", "istighfar", "repentance", "tauba"]):
        return "Forgiveness"
    return None


def normalize_result(result):
    if not isinstance(result, dict):
        result = {}
    return {
        "direct_answer": str(result.get("direct_answer", "")).strip(),
        "quran_evidence": result.get("quran_evidence", []) if isinstance(result.get("quran_evidence", []), list) else [],
        "hadith_evidence": result.get("hadith_evidence", []) if isinstance(result.get("hadith_evidence", []), list) else [],
        "scholarly_opinions": result.get("scholarly_opinions", []) if isinstance(result.get("scholarly_opinions", []), list) else [],
        "dua": result.get("dua", {}) if isinstance(result.get("dua", {}), dict) else {},
        "duas": result.get("duas", []) if isinstance(result.get("duas", []), list) else [],
        "ikhtilaf": "Yes" if str(result.get("ikhtilaf", "")).strip().lower() == "yes" else "No",
        "conclusion": str(result.get("conclusion", "")).strip(),
        "consult_scholar": "Yes" if str(result.get("consult_scholar", "")).strip().lower() == "yes" else "No",
        "source_notice": str(result.get("source_notice", "")).strip(),
    }


def build_curated_response(category_name):
    return {
        "direct_answer": "Here are verified duas for your request.",
        "quran_evidence": [],
        "hadith_evidence": [],
        "scholarly_opinions": [],
        "dua": {},
        "duas": DUA_CATEGORIES.get(category_name, []),
        "ikhtilaf": "No",
        "conclusion": "",
        "consult_scholar": "No",
        "source_notice": "Dua text pulled from built-in verified collection.",
    }


def hide_unverified_model_dua(result):
    result = normalize_result(result)
    result["dua"] = {}
    result["duas"] = []
    result["source_notice"] = "For safety, AI-generated dua wording is hidden. Use curated duas below."
    if not result["conclusion"]:
        result["conclusion"] = "This request is outside the curated dua set."
    return result


def call_api(user_message, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for item in history[-3:]:
        messages.append({"role": "user", "content": item["user"]})
        messages.append({"role": "assistant", "content": item["assistant"]})
    messages.append({"role": "user", "content": user_message})

    headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Accept": "application/json", "Content-Type": "application/json"}
    payload = {"model": MODEL, "messages": messages, "max_tokens": 1200, "temperature": 0.1, "stream": False}

    for attempt in range(3):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=45)
            response.raise_for_status()
            data = response.json()
            if "choices" not in data:
                raise RuntimeError(f"API error: {json.dumps(data)[:400]}")
            content = data["choices"][0]["message"]["content"]
            if not content:
                raise RuntimeError("Empty response from API")
            return content
        except Exception as exc:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                raise exc


def parse_response(raw):
    try:
        cleaned = re.sub(r"```json|```", "", raw).strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start != -1 and end > start:
            cleaned = cleaned[start:end]
        return normalize_result(json.loads(cleaned))
    except Exception:
        return normalize_result({"direct_answer": raw, "quran_evidence": [], "hadith_evidence": [], "scholarly_opinions": [], "dua": {}, "ikhtilaf": "No", "conclusion": "", "consult_scholar": "No"})


@st.cache_data(ttl=3600)
def fetch_quran_surah(surah_number):
    try:
        response = requests.get(f"https://api.alquran.cloud/v1/surah/{surah_number}/editions/quran-uthmani,en.asad", timeout=15)
        response.raise_for_status()
        data = response.json()
        return data["data"] if data.get("status") == "OK" else None
    except Exception:
        return None


def render_response(result):
    result = normalize_result(result)
    if result["source_notice"]:
        st.markdown(f'<div class="info-box">{safe_html(result["source_notice"])}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="answer"><strong style="color:var(--gold);">Answer:</strong><br><br>{safe_html(result["direct_answer"])}</div>', unsafe_allow_html=True)

    if result["quran_evidence"]:
        st.markdown('<div class="section-title">Quran Evidence</div>', unsafe_allow_html=True)
        for verse in result["quran_evidence"]:
            st.markdown(
                f'<div class="quran-card"><div class="arabic">{safe_html(verse.get("arabic", ""))}</div>'
                f'<div class="translation">{safe_html(verse.get("translation", ""))}</div>'
                f'<br><span style="color:var(--success); font-weight:700;">{safe_html(verse.get("reference", ""))}</span>'
                f'<br><em style="color:var(--muted);">{safe_html(verse.get("explanation", ""))}</em></div>',
                unsafe_allow_html=True,
            )

    if result["hadith_evidence"]:
        st.markdown('<div class="section-title">Hadith Evidence</div>', unsafe_allow_html=True)
        for h in result["hadith_evidence"]:
            auth = h.get("authenticity", "Sahih")
            badge_class = "sahih" if auth == "Sahih" else "hasan" if auth == "Hasan" else "weak"
            arabic_html = f'<div class="arabic">{safe_html(h.get("arabic", ""))}</div>' if h.get("arabic") else ""
            note_html = f'<br><span style="color:var(--muted); font-size:12px;">{safe_html(h.get("note", ""))}</span>' if h.get("note") else ""
            st.markdown(
                f'<div class="hadith-card">{arabic_html}<strong>{safe_html(h.get("text", ""))}</strong>'
                f'<br><br><strong>Source:</strong> {safe_html(h.get("source", ""))} '
                f'<span class="badge {badge_class}">{safe_html(auth)}</span>{note_html}</div>',
                unsafe_allow_html=True,
            )

    if result["scholarly_opinions"]:
        st.markdown('<div class="section-title">Scholarly Opinions</div>', unsafe_allow_html=True)
        if result["ikhtilaf"] == "Yes":
            st.markdown('<div class="info-box">There is a difference of opinion among scholars on this matter.</div>', unsafe_allow_html=True)
        for opinion in result["scholarly_opinions"]:
            st.markdown(
                f'<div class="scholar-card"><strong style="color:var(--gold);">{safe_html(opinion.get("madhab", ""))}:</strong> '
                f'{safe_html(opinion.get("opinion", ""))}<br><small style="color:var(--muted);">Source: {safe_html(opinion.get("source", ""))}</small></div>',
                unsafe_allow_html=True,
            )

    duas = result["duas"] or ([result["dua"]] if result.get("dua", {}).get("arabic") else [])
    if duas:
        st.markdown('<div class="section-title">Dua</div>', unsafe_allow_html=True)
        for dua in duas:
            st.markdown(
                f'<div class="dua-card"><strong style="color:#d8b55a; font-size:16px;">{safe_html(dua.get("title", ""))}</strong>'
                f'<div class="arabic">{safe_html(dua.get("arabic", ""))}</div>'
                f'<strong style="color:#a87ad8;">Transliteration:</strong><br><em>{safe_html(dua.get("transliteration", ""))}</em>'
                f'<br><br><strong style="color:#d8b55a;">Meaning:</strong><br>{safe_html(dua.get("meaning", ""))}'
                f'<br><br><small style="color:#a87ad8;">Reference: {source_link(dua.get("reference", ""), dua.get("source_url", ""))}</small></div>',
                unsafe_allow_html=True,
            )

    if result["conclusion"]:
        st.markdown('<div class="section-title">Conclusion</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="answer">{safe_html(result["conclusion"])}</div>', unsafe_allow_html=True)

    if result["consult_scholar"] == "Yes":
        st.markdown('<div class="warning-card">This matter can be sensitive. Please consult a qualified scholar for a personal ruling.</div>', unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# UI
# --------------------------------------------------------------------------- #
st.markdown(
    '<div class="hero"><div class="bismillah">بِسْمِ اللَّهِ الرَّحْمٰنِ الرَّحِيمِ</div>'
    '<div class="title">Muslim AI</div>'
    '<div class="subtitle">Premium experience · Authentic answers grounded in Quran, Sahih Hadith, and classical scholarship</div></div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown('<div style="color:var(--gold); font-size:18px; font-weight:700; text-align:center; margin-bottom:12px;">Quick Topics</div>', unsafe_allow_html=True)
    topics = [
        "What is the ruling on missing Fajr prayer?",
        "Give me morning adhkar",
        "What breaks the fast in Ramadan?",
        "Is music halal or haram?",
        "Dua for anxiety and stress",
        "What is the ruling on zakah?",
        "Dua before sleeping",
        "What is tawakkul in Islam?",
        "Is insurance halal?",
        "Dua for entering home",
        "Story of Prophet Yusuf and patience",
        "Story of the People of the Cave (Ashab al-Kahf)",
        "Story of Musa and Khidr",
        "Life of Prophet Muhammad (s) summary",
        "Life of Prophet Ibrahim",
        "Life of Prophet Musa",
        "Life of Prophet Isa",
    ]
    for topic in topics:
        if st.button(topic, use_container_width=True, key=f"sidebar_{topic}"):
            st.session_state.quick_question = topic
    st.markdown("---")
    st.markdown('<div style="color:var(--muted); font-size:12px; text-align:center;">Ask in English, Urdu, or Arabic.</div>', unsafe_allow_html=True)
    st.markdown("---")
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.messages = []
        st.session_state.quick_question = ""
        st.rerun()

tab5_label = "Stories"
tab6_label = "Prophets"
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["AI Assistant", "Quran Reader", "Dua Collection", "40 Hadith", tab5_label, tab6_label])

with tab1:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                try:
                    render_response(json.loads(msg["content"]))
                except Exception:
                    st.markdown(msg["content"])
            else:
                st.markdown(msg["content"])

    quick_q = st.session_state.get("quick_question", "")
    user_input = quick_q or st.chat_input("Ask your Islamic question...")
    if quick_q:
        st.session_state.quick_question = ""

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Searching Quran and Hadith..."):
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
                except Exception as e:
                    st.error(f"Error: {str(e)}. Please try again.")

with tab2:
    st.markdown('<div class="section-title">Quran Reader — All Surahs</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Select any Surah to read with Arabic and English translation (Asad).</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        surah_options = [f"{i + 1}. {name}" for i, name in enumerate(SURAH_NAMES)]
        selected_surah = st.selectbox("Select Surah", surah_options)
        surah_number = int(selected_surah.split(".")[0]) if selected_surah else None
        st.markdown(f'<div class="info-box"><strong style="color:var(--gold);">{safe_html(selected_surah)}</strong></div>', unsafe_allow_html=True)
        if st.button("Load Surah", type="primary", use_container_width=True):
            st.session_state.loaded_surah_number = surah_number
    with col2:
        if st.session_state.loaded_surah_number:
            surah_data = fetch_quran_surah(st.session_state.loaded_surah_number)
            if surah_data and len(surah_data) >= 2:
                arabic_edition, english_edition = surah_data[0], surah_data[1]
                english_ayahs = english_edition.get("ayahs", [])
                st.markdown(
                    f'<div style="font-family:\'Scheherazade New\',serif; font-size:32px; color:#f0d589; text-align:center; direction:rtl; margin:15px 0;">'
                    f'{safe_html(arabic_edition.get("name", ""))}</div>',
                    unsafe_allow_html=True,
                )
                for i, ayah in enumerate(arabic_edition.get("ayahs", [])):
                    english = english_ayahs[i].get("text", "") if i < len(english_ayahs) else ""
                    st.markdown(
                        f'<div class="reader-card"><span style="color:var(--gold); font-size:12px; font-weight:700;">Ayah {ayah.get("numberInSurah", i + 1)}</span>'
                        f'<div class="arabic">{safe_html(ayah.get("text", ""))}</div>'
                        f'<div class="translation">{safe_html(english)}</div></div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.error("Could not load Surah. Please check your connection and try again.")
        else:
            st.info("Select a Surah and click Load Surah.")

with tab3:
    st.markdown('<div class="section-title">Dua Collection</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Curated duas stored directly in this app (no external files required).</div>', unsafe_allow_html=True)
    selected_category = st.selectbox("Select Category", list(DUA_CATEGORIES.keys()))
    for dua in DUA_CATEGORIES.get(selected_category, []):
        st.markdown(
            f'<div class="dua-card"><strong style="color:var(--gold); font-size:16px;">{safe_html(dua["title"])}</strong>'
            f'<div class="arabic">{safe_html(dua["arabic"])}</div>'
            f'<strong style="color:#a87ad8;">Transliteration:</strong><br><em>{safe_html(dua["transliteration"])}</em><br><br>'
            f'<strong style="color:var(--gold);">Meaning:</strong><br>{safe_html(dua["meaning"])}'
            f'<br><br><small style="color:#a87ad8;">Reference: {source_link(dua["reference"], dua.get("source_url", ""))}</small></div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section-title">40 Short Hadith</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Concise authentic sayings to reflect on daily.</div>', unsafe_allow_html=True)
    for h in HADITH_40:
        st.markdown(
            f'<div class="hadith-card"><span style="color:var(--gold); font-size:13px; font-weight:700;">Hadith {h["number"]}</span>'
            f'<br><strong>{safe_html(h["text"])}</strong></div>',
            unsafe_allow_html=True,
        )

with tab5:
    st.markdown('<div class="section-title">Famous Stories (Quran & Hadith)</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Verified, concise retellings with references—no speculation.</div>', unsafe_allow_html=True)
    for story in STORIES:
        st.markdown(
            f'<div class="card"><strong style="color:var(--gold);">{safe_html(story["title"])}</strong><br>'
            f'{safe_html(story["summary"])}<br><br>'
            f'<small style="color:var(--muted);">Source: {safe_html(story["source"])}</small></div>',
            unsafe_allow_html=True,
        )

with tab6:
    st.markdown('<div class="section-title">Lives of the Prophets</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Brief, verified highlights only—no guesses or weak reports.</div>', unsafe_allow_html=True)
    for p in PROPHETS:
        st.markdown(
            f'<div class="card"><strong style="color:var(--gold); font-size:16px;">{safe_html(p["name"])}</strong><br>'
            f'{safe_html(p["life"])}<br><br><small style="color:var(--muted);">Sources: {safe_html(p["sources"])}</small></div>',
            unsafe_allow_html=True,
        )
