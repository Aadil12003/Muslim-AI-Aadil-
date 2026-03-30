import os
import json
import re
from html import escape

import requests
import streamlit as st

st.set_page_config(page_title="Muslim AI", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Scheherazade+New:wght@400;700&display=swap');

body {
    background:
        radial-gradient(circle at top right, rgba(201,168,76,0.14), transparent 28%),
        linear-gradient(135deg, #09111b 0%, #102032 45%, #13283d 100%);
}
.main-header {
    font-size: 42px;
    font-weight: 700;
    color: #d6b65c;
    text-align: center;
    padding: 14px 0 6px 0;
    text-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    font-family: 'Amiri', serif;
    border-bottom: 2px solid rgba(214,182,92,0.45);
    margin-bottom: 8px;
}
.bismillah {
    font-family: 'Scheherazade New', serif;
    font-size: 38px;
    color: #e4c873;
    text-align: center;
    direction: rtl;
    margin: 8px 0 4px 0;
    line-height: 2;
}
.sub-header {
    font-size: 16px;
    color: #b8c7d6;
    text-align: center;
    margin-bottom: 18px;
}
.trust-banner {
    background: linear-gradient(135deg, rgba(14,28,42,0.92), rgba(20,38,56,0.92));
    border: 1px solid rgba(214,182,92,0.35);
    border-radius: 14px;
    padding: 14px 16px;
    margin: 6px 0 20px 0;
    color: #d7e3ef;
    box-shadow: 0 6px 24px rgba(0,0,0,0.22);
}
.banner-title {
    color: #e4c873;
    font-weight: 700;
    margin-bottom: 8px;
}
.pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.verify-pill {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.2px;
}
.verify-ok {
    background: rgba(39,174,96,0.18);
    border: 1px solid rgba(39,174,96,0.35);
    color: #9ee2b5;
}
.verify-warn {
    background: rgba(243,156,18,0.18);
    border: 1px solid rgba(243,156,18,0.35);
    color: #ffd28a;
}
.verify-info {
    background: rgba(52,152,219,0.18);
    border: 1px solid rgba(52,152,219,0.35);
    color: #a8d8ff;
}
.metric-row {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
    margin: 10px 0 14px 0;
}
.metric-card {
    background: linear-gradient(135deg, rgba(18,31,46,0.92), rgba(14,24,36,0.92));
    border: 1px solid rgba(214,182,92,0.18);
    border-radius: 12px;
    padding: 12px;
    color: #d7e3ef;
}
.metric-value {
    font-size: 24px;
    font-weight: 700;
    color: #e4c873;
    line-height: 1.1;
}
.metric-label {
    font-size: 12px;
    color: #a9bbcd;
    margin-top: 4px;
}
.answer-card {
    background: linear-gradient(135deg, #132536, #1b3349);
    border-left: 4px solid #d6b65c;
    padding: 20px;
    border-radius: 14px;
    margin: 14px 0;
    line-height: 1.9;
    color: #edf3f8;
    box-shadow: 0 5px 18px rgba(0,0,0,0.28);
}
.quran-card {
    background: linear-gradient(135deg, #0f2619, #173725);
    border: 1px solid #2d8e5d;
    border-left: 4px solid #2ecc71;
    padding: 20px;
    border-radius: 14px;
    margin: 10px 0;
    box-shadow: 0 5px 18px rgba(0,0,0,0.22);
    color: #edf3f8;
}
.hadith-card {
    background: linear-gradient(135deg, #102133, #17324d);
    border: 1px solid #2e7bb8;
    border-left: 4px solid #3498db;
    padding: 18px;
    border-radius: 14px;
    margin: 10px 0;
    color: #edf3f8;
    box-shadow: 0 5px 18px rgba(0,0,0,0.22);
}
.pending-card {
    background: linear-gradient(135deg, #2a210f, #35270f);
    border: 1px solid #b5811b;
    border-left: 4px solid #f39c12;
    padding: 18px;
    border-radius: 14px;
    margin: 10px 0;
    color: #fff2d6;
    box-shadow: 0 5px 18px rgba(0,0,0,0.22);
}
.scholar-card {
    background: linear-gradient(135deg, #26180c, #3a2716);
    border-left: 4px solid #d6b65c;
    padding: 15px;
    border-radius: 12px;
    margin: 10px 0;
    color: #edf3f8;
}
.warning-card {
    background: linear-gradient(135deg, #2a0e0e, #3d1616);
    border-left: 4px solid #e74c3c;
    padding: 15px;
    border-radius: 12px;
    margin: 12px 0;
    color: #f5dddd;
}
.dua-card {
    background: linear-gradient(135deg, #1a1131, #2a1945);
    border: 1px solid rgba(142,68,173,0.65);
    padding: 24px;
    border-radius: 14px;
    margin: 10px 0;
    text-align: center;
    color: #edf3f8;
    box-shadow: 0 5px 20px rgba(84,35,111,0.25);
}
.arabic-text {
    font-family: 'Scheherazade New', 'Amiri', serif;
    font-size: 28px;
    font-weight: 700;
    color: #e4c873;
    direction: rtl;
    text-align: right;
    margin: 10px 0;
    line-height: 2.4;
}
.arabic-translation {
    color: #c6dfcc;
    font-style: italic;
    margin: 8px 0;
    line-height: 1.8;
}
.quran-ref {
    color: #75d69b;
    font-weight: 700;
    font-size: 14px;
}
.section-title {
    font-size: 20px;
    font-weight: 700;
    color: #e4c873;
    margin: 20px 0 10px 0;
    border-bottom: 1px solid rgba(214,182,92,0.38);
    padding-bottom: 5px;
}
.quran-ayah {
    background: linear-gradient(135deg, #112718, #183626);
    border: 1px solid #2e8a5f;
    padding: 20px;
    border-radius: 14px;
    margin: 8px 0;
    color: #edf3f8;
}
.info-box {
    background: linear-gradient(135deg, #0f1e2f, #16283a);
    border: 1px solid rgba(214,182,92,0.35);
    padding: 15px;
    border-radius: 12px;
    color: #dde8f1;
    margin: 10px 0;
}
.panel {
    background: linear-gradient(135deg, rgba(18,31,46,0.95), rgba(14,24,36,0.95));
    border: 1px solid rgba(214,182,92,0.2);
    padding: 14px;
    border-radius: 14px;
    color: #d7e3ef;
    margin-bottom: 14px;
}
.panel-title {
    color: #e4c873;
    font-weight: 700;
    margin-bottom: 10px;
}
.small-note {
    font-size: 12px;
    color: #aebfd0;
}
.badge-sahih {
    background: #27ae60;
    color: white;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
}
.badge-hasan {
    background: #f39c12;
    color: white;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
}
.badge-weak {
    background: #e74c3c;
    color: white;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
}
@media (max-width: 900px) {
    .metric-row {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}
</style>
""", unsafe_allow_html=True)

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "meta/llama-4-maverick-17b-128e-instruct"
REQUEST_TIMEOUT = 45

QURAN_SURAHS = [
    (1, "Al-Fatiha", 7), (2, "Al-Baqarah", 286), (3, "Al-Imran", 200),
    (4, "An-Nisa", 176), (5, "Al-Maidah", 120), (6, "Al-Anam", 165),
    (7, "Al-Araf", 206), (8, "Al-Anfal", 75), (9, "At-Tawbah", 129),
    (10, "Yunus", 109), (11, "Hud", 123), (12, "Yusuf", 111),
    (13, "Ar-Rad", 43), (14, "Ibrahim", 52), (15, "Al-Hijr", 99),
    (16, "An-Nahl", 128), (17, "Al-Isra", 111), (18, "Al-Kahf", 110),
    (19, "Maryam", 98), (20, "Ta-Ha", 135), (21, "Al-Anbiya", 112),
    (22, "Al-Hajj", 78), (23, "Al-Muminun", 118), (24, "An-Nur", 64),
    (25, "Al-Furqan", 77), (26, "Ash-Shuara", 227), (27, "An-Naml", 93),
    (28, "Al-Qasas", 88), (29, "Al-Ankabut", 69), (30, "Ar-Rum", 60),
    (31, "Luqman", 34), (32, "As-Sajdah", 30), (33, "Al-Ahzab", 73),
    (34, "Saba", 54), (35, "Fatir", 45), (36, "Ya-Sin", 83),
    (37, "As-Saffat", 182), (38, "Sad", 88), (39, "Az-Zumar", 75),
    (40, "Ghafir", 85), (41, "Fussilat", 54), (42, "Ash-Shura", 53),
    (43, "Az-Zukhruf", 89), (44, "Ad-Dukhan", 59), (45, "Al-Jathiyah", 37),
    (46, "Al-Ahqaf", 35), (47, "Muhammad", 38), (48, "Al-Fath", 29),
    (49, "Al-Hujurat", 18), (50, "Qaf", 45), (51, "Adh-Dhariyat", 60),
    (52, "At-Tur", 49), (53, "An-Najm", 62), (54, "Al-Qamar", 55),
    (55, "Ar-Rahman", 78), (56, "Al-Waqiah", 96), (57, "Al-Hadid", 29),
    (58, "Al-Mujadila", 22), (59, "Al-Hashr", 24), (60, "Al-Mumtahanah", 13),
    (61, "As-Saf", 14), (62, "Al-Jumuah", 11), (63, "Al-Munafiqun", 11),
    (64, "At-Taghabun", 18), (65, "At-Talaq", 12), (66, "At-Tahrim", 12),
    (67, "Al-Mulk", 30), (68, "Al-Qalam", 52), (69, "Al-Haqqah", 52),
    (70, "Al-Maarij", 44), (71, "Nuh", 28), (72, "Al-Jinn", 28),
    (73, "Al-Muzzammil", 20), (74, "Al-Muddaththir", 56), (75, "Al-Qiyamah", 40),
    (76, "Al-Insan", 31), (77, "Al-Mursalat", 50), (78, "An-Naba", 40),
    (79, "An-Naziat", 46), (80, "Abasa", 42), (81, "At-Takwir", 29),
    (82, "Al-Infitar", 19), (83, "Al-Mutaffifin", 36), (84, "Al-Inshiqaq", 25),
    (85, "Al-Buruj", 22), (86, "At-Tariq", 17), (87, "Al-Ala", 19),
    (88, "Al-Ghashiyah", 26), (89, "Al-Fajr", 30), (90, "Al-Balad", 20),
    (91, "Ash-Shams", 15), (92, "Al-Layl", 21), (93, "Ad-Duhaa", 11),
    (94, "Ash-Sharh", 8), (95, "At-Tin", 8), (96, "Al-Alaq", 19),
    (97, "Al-Qadr", 5), (98, "Al-Bayyinah", 8), (99, "Az-Zalzalah", 8),
    (100, "Al-Adiyat", 11), (101, "Al-Qariah", 11), (102, "At-Takathur", 8),
    (103, "Al-Asr", 3), (104, "Al-Humazah", 9), (105, "Al-Fil", 5),
    (106, "Quraysh", 4), (107, "Al-Maun", 7), (108, "Al-Kawthar", 3),
    (109, "Al-Kafirun", 6), (110, "An-Nasr", 3), (111, "Al-Masad", 5),
    (112, "Al-Ikhlas", 4), (113, "Al-Falaq", 5), (114, "An-Nas", 6)
]
SURAH_NAME_BY_NUMBER = {num: name for num, name, _ in QURAN_SURAHS}

VERIFIED_DUA_LIBRARY = {
    "morning_remembrance": {
        "title": "Morning Remembrance",
        "arabic": "أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ، لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ",
        "transliteration": "Asbahna wa asbahal mulku lillah, walhamdu lillah, la ilaha illallah wahdahu la sharika lah",
        "meaning": "We have entered the morning and the whole kingdom belongs to Allah. All praise is for Allah. None has the right to be worshipped except Allah alone with no partner.",
        "reference": "Abu Dawood 4/317",
        "category": "Morning Adhkar"
    },
    "sayyidul_istighfar_morning": {
        "title": "Sayyidul Istighfar",
        "arabic": "اللَّهُمَّ أَنْتَ رَبِّي لَا إِلَهَ إِلَّا أَنْتَ، خَلَقْتَنِي وَأَنَا عَبْدُكَ",
        "transliteration": "Allahumma anta rabbi la ilaha illa anta, khalaqtani wa ana abduk",
        "meaning": "O Allah, You are my Lord. None has the right to be worshipped except You. You created me and I am Your servant.",
        "reference": "Sahih al-Bukhari 6306",
        "category": "Morning Adhkar"
    },
    "evening_remembrance": {
        "title": "Evening Remembrance",
        "arabic": "أَمْسَيْنَا وَأَمْسَى الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ، لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ",
        "transliteration": "Amsayna wa amsal mulku lillah, walhamdu lillah, la ilaha illallah wahdahu la sharika lah",
        "meaning": "We have entered the evening and the whole kingdom belongs to Allah. All praise is for Allah. None has the right to be worshipped except Allah alone with no partner.",
        "reference": "Abu Dawood 4/317",
        "category": "Evening Adhkar"
    },
    "dua_before_sleep": {
        "title": "Dua Before Sleeping",
        "arabic": "بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا",
        "transliteration": "Bismika Allahumma amootu wa ahya",
        "meaning": "In Your name, O Allah, I die and I live.",
        "reference": "Sahih al-Bukhari 6324",
        "category": "Before Sleep"
    },
    "entering_home": {
        "title": "Dua for Entering Home",
        "arabic": "اللَّهُمَّ إِنِّي أَسْأَلُكَ خَيْرَ الْمَوْلَجِ وَخَيْرَ الْمَخْرَجِ",
        "transliteration": "Allahumma inni as'aluka khayral mawlaji wa khayral makhraji",
        "meaning": "O Allah, I ask You for the good of the entrance and the good of the exit.",
        "reference": "Abu Dawood 5096",
        "category": "Entering Home"
    },
    "before_eating": {
        "title": "Before Eating",
        "arabic": "بِسْمِ اللَّهِ",
        "transliteration": "Bismillah",
        "meaning": "In the name of Allah.",
        "reference": "Abu Dawood, Tirmidhi",
        "category": "Eating and Drinking"
    },
    "after_eating": {
        "title": "After Eating",
        "arabic": "الْحَمْدُ لِلَّهِ الَّذِي أَطْعَمَنَا وَسَقَانَا وَجَعَلَنَا مُسْلِمِينَ",
        "transliteration": "Alhamdu lillahil ladhi at'amana wa saqana wa ja'alana muslimin",
        "meaning": "All praise is for Allah who fed us, gave us drink, and made us Muslims.",
        "reference": "Abu Dawood 3850",
        "category": "Eating and Drinking"
    },
    "anxiety_distress": {
        "title": "Dua for Anxiety and Distress",
        "arabic": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ",
        "transliteration": "Allahumma inni a'udhu bika minal hammi wal hazan",
        "meaning": "O Allah, I seek refuge in You from worry and grief.",
        "reference": "Sahih al-Bukhari 2893",
        "category": "Anxiety and Distress"
    },
    "travel_dua": {
        "title": "Travel Supplication",
        "arabic": "سُبْحَانَ الَّذِي سَخَّرَ لَنَا هَذَا وَمَا كُنَّا لَهُ مُقْرِنِينَ",
        "transliteration": "Subhanal ladhi sakhkhara lana hadha wa ma kunna lahu muqrinin",
        "meaning": "Glory be to Him who has subjected this to us, and we could never have it by our own efforts.",
        "reference": "Qur'an 43:13, Abu Dawood 2602",
        "category": "Travel"
    },
    "forgiveness_dua": {
        "title": "Seeking Forgiveness",
        "arabic": "رَبِّ اغْفِرْ لِي وَتُبْ عَلَيَّ إِنَّكَ أَنْتَ التَّوَّابُ الرَّحِيمُ",
        "transliteration": "Rabbighfir li wa tub alayya innaka antat tawwabur rahim",
        "meaning": "My Lord, forgive me and accept my repentance. Indeed You are the Oft-Returning, the Most Merciful.",
        "reference": "Abu Dawood, Ibn Majah",
        "category": "For Forgiveness"
    }
}

DUA_CATEGORIES = {
    "Morning Adhkar": ["morning_remembrance", "sayyidul_istighfar_morning"],
    "Evening Adhkar": ["evening_remembrance"],
    "Before Sleep": ["dua_before_sleep"],
    "Entering Home": ["entering_home"],
    "Eating and Drinking": ["before_eating", "after_eating"],
    "Anxiety and Distress": ["anxiety_distress"],
    "Travel": ["travel_dua"],
    "For Forgiveness": ["forgiveness_dua"]
}

VERIFIED_HADITH_DB = {
    "Bukhari|1": {
        "collection": "Bukhari",
        "collection_full": "Sahih al-Bukhari",
        "reference": "1",
        "reference_label": "Bukhari 1",
        "authenticity": "Sahih",
        "arabic": "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ",
        "text": "Actions are judged by intentions, and every person will get the reward according to what he intended.",
        "narrator": "Umar ibn al-Khattab (RA)",
        "topic": "Intentions"
    },
    "Bukhari|8": {
        "collection": "Bukhari",
        "collection_full": "Sahih al-Bukhari",
        "reference": "8",
        "reference_label": "Bukhari 8",
        "authenticity": "Sahih",
        "arabic": "بُنِيَ الإِسْلَامُ عَلَى خَمْسٍ",
        "text": "Islam has been built upon five things: the testimony that there is no god but Allah and that Muhammad is the Messenger of Allah, establishing prayer, giving zakah, performing pilgrimage to the House, and fasting in Ramadan.",
        "narrator": "Ibn Umar (RA)",
        "topic": "Foundations of Islam"
    },
    "Muslim|684": {
        "collection": "Muslim",
        "collection_full": "Sahih Muslim",
        "reference": "684",
        "reference_label": "Muslim 684",
        "authenticity": "Sahih",
        "arabic": "",
        "text": "Whoever forgets a prayer or sleeps through it, its expiation is that he should pray it when he remembers it.",
        "narrator": "",
        "topic": "Missed Prayer"
    },
    "Bukhari|1933": {
        "collection": "Bukhari",
        "collection_full": "Sahih al-Bukhari",
        "reference": "1933",
        "reference_label": "Bukhari 1933",
        "authenticity": "Sahih",
        "arabic": "",
        "text": "If somebody eats or drinks forgetfully, then he should complete his fast, for what he has eaten or drunk has been given to him by Allah.",
        "narrator": "Abu Hurairah (RA)",
        "topic": "Fasting"
    },
    "Muslim|1155": {
        "collection": "Muslim",
        "collection_full": "Sahih Muslim",
        "reference": "1155",
        "reference_label": "Muslim 1155",
        "authenticity": "Sahih",
        "arabic": "",
        "text": "If somebody eats or drinks forgetfully while fasting, let him complete his fast, for it is Allah who fed him and gave him drink.",
        "narrator": "Abu Hurairah (RA)",
        "topic": "Fasting"
    },
    "Tirmidhi|2344": {
        "collection": "Tirmidhi",
        "collection_full": "Jami at-Tirmidhi",
        "reference": "2344",
        "reference_label": "Tirmidhi 2344",
        "authenticity": "Hasan",
        "arabic": "",
        "text": "If you were to rely upon Allah with the reliance due to Him, He would provide for you as He provides for the birds: they leave in the morning with empty stomachs and return full.",
        "narrator": "Umar ibn al-Khattab (RA)",
        "topic": "Tawakkul"
    },
    "Bukhari|6324": {
        "collection": "Bukhari",
        "collection_full": "Sahih al-Bukhari",
        "reference": "6324",
        "reference_label": "Bukhari 6324",
        "authenticity": "Sahih",
        "arabic": "بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا",
        "text": "When the Prophet went to bed, he would say: In Your name, O Allah, I die and I live.",
        "narrator": "Hudhayfah ibn al-Yaman (RA)",
        "topic": "Before Sleep"
    }
}

HADITH_LIBRARY_GROUPS = {
    "Foundations": ["Bukhari|1", "Bukhari|8"],
    "Prayer": ["Muslim|684"],
    "Fasting": ["Bukhari|1933", "Muslim|1155"],
    "Tawakkul": ["Tirmidhi|2344"],
    "Before Sleep": ["Bukhari|6324"]
}

DUA_ID_LIST = ", ".join(sorted(VERIFIED_DUA_LIBRARY.keys()))

SYSTEM_PROMPT = f"""
You are an advanced Islamic AI Assistant designed to provide accurate, source-based, and respectful answers strictly grounded in authentic Islamic knowledge.

CORE OBJECTIVE:
Provide answers based ONLY on:
1. Qur'an
2. Authentic Hadith
3. Recognized scholarly fatwa summaries

AUTHORIZED SOURCES ONLY:
- Qur'an with Surah and Ayah numbers
- Sahih al-Bukhari
- Sahih Muslim
- Sunan Abu Dawood
- Jami at-Tirmidhi
- IslamQA
- Dar al-Ifta al-Misriyyah

STRICT RULES:
- Never fabricate Qur'an or Hadith
- Never give rulings without evidence
- Never rely on random sites
- If unsure, say exactly: No strong authentic evidence found
- For sensitive matters like marriage, finance, health, or personal rulings, set consult_scholar to Yes

VERY IMPORTANT OUTPUT SAFETY:
- Do NOT return Qur'an Arabic text
- Do NOT return Qur'an translations
- Do NOT return Hadith text
- Do NOT return Arabic Hadith
- Do NOT return free-written dua Arabic
- Return references only so the application can verify before display
- If you are not confident in an exact Qur'an or Hadith reference, leave it out

IKHTILAF HANDLING:
- If valid scholarly disagreement exists, set ikhtilaf to Yes
- Present major valid views neutrally
- Mention madhab when relevant
- Do not force one opinion unless the user explicitly asks for the strongest view

DUA MODE:
If the user asks for dua, return only one or more dua_ids from this verified list:
{DUA_ID_LIST}

LANGUAGES:
- Default English
- Support Urdu, Hindi, Arabic
- If the user writes in Urdu, Hindi, or Arabic, answer direct_answer, scholarly_opinions, and conclusion in that language

RESPONSE FORMAT:
{{
  "direct_answer": "clear concise answer",
  "quran_references": [
    {{
      "surah": 2,
      "ayah_start": 255,
      "ayah_end": 255,
      "explanation": "brief explanation of relevance"
    }}
  ],
  "hadith_references": [
    {{
      "collection": "Bukhari or Muslim or Abu Dawood or Tirmidhi",
      "reference": "exact hadith number only",
      "authenticity": "Sahih or Hasan or Weak",
      "why_relevant": "brief relevance note"
    }}
  ],
  "scholarly_opinions": [
    {{
      "madhab": "Hanafi or Shafii or Maliki or Hanbali or General",
      "opinion": "brief view summary",
      "source": "IslamQA or Dar al-Ifta al-Misriyyah or General classical fiqh"
    }}
  ],
  "dua_ids": ["one_or_more_verified_dua_ids"],
  "ikhtilaf": "Yes or No",
  "conclusion": "neutral summary",
  "consult_scholar": "Yes or No",
  "language_detected": "English or Urdu or Arabic or Hindi"
}}

Return ONLY valid JSON.
""".strip()


def get_api_key():
    try:
        key = st.secrets.get("NVIDIA_API_KEY", "")
    except Exception:
        key = ""
    return (key or os.getenv("NVIDIA_API_KEY", "")).strip()


def safe_html(value):
    return escape("" if value is None else str(value)).replace("\n", "<br>")


def as_int(value):
    try:
        return int(str(value).strip())
    except Exception:
        return None


def normalize_authenticity(value):
    text = str(value or "").strip().lower()
    if text == "sahih":
        return "Sahih"
    if text == "hasan":
        return "Hasan"
    if text == "weak":
        return "Weak"
    return ""


def canonical_collection(name):
    raw = re.sub(r"[^a-z]", "", str(name or "").lower())
    mapping = {
        "bukhari": "Bukhari",
        "sahihbukhari": "Bukhari",
        "sahihalbukhari": "Bukhari",
        "muslim": "Muslim",
        "sahihmuslim": "Muslim",
        "abudawood": "Abu Dawood",
        "abudawud": "Abu Dawood",
        "sunanabudawood": "Abu Dawood",
        "sunanabudawud": "Abu Dawood",
        "tirmidhi": "Tirmidhi",
        "tirmizi": "Tirmidhi",
        "jamitirmidhi": "Tirmidhi",
        "jamiattirmidhi": "Tirmidhi",
        "jamialtirmidhi": "Tirmidhi"
    }
    return mapping.get(raw, "")


def extract_reference_number(value):
    match = re.search(r"\d+", str(value or ""))
    return match.group(0) if match else ""


def detect_input_language(text):
    if re.search(r"[\u0900-\u097F]", text):
        return "Hindi"
    if re.search(r"[ٹڈڑںےھ]", text):
        return "Urdu"
    if re.search(r"[\u0600-\u06FF]", text):
        return "Arabic"
    return "English"


def contains_any(text, phrases):
    return any(phrase in text for phrase in phrases)


def detect_curated_route(user_input):
    q = re.sub(r"\s+", " ", user_input.lower().strip())

    if contains_any(q, [
        "fall asleep", "dua to fall asleep", "sleep dua", "dua before sleep",
        "before sleep", "before sleeping", "dua for sleep", "sleeping dua",
        "sleep", "sone se pehle", "neend", "sona", "sonay"
    ]):
        return "before_sleep"

    if contains_any(q, [
        "morning adhkar", "morning azkar", "morning dua", "morning remembrance",
        "subah", "after fajr"
    ]):
        return "morning"

    if contains_any(q, [
        "evening adhkar", "evening azkar", "evening dua", "shaam", "after maghrib"
    ]):
        return "evening"

    if contains_any(q, [
        "anxiety", "stress", "distress", "worry", "worried", "tension", "gham", "pareshani"
    ]):
        return "anxiety"

    if contains_any(q, [
        "travel", "journey", "safar", "trip"
    ]):
        return "travel"

    if contains_any(q, [
        "enter home", "entering home", "ghar mein dakhil", "home dua"
    ]):
        return "entering_home"

    return None


def empty_model_result():
    return {
        "direct_answer": "",
        "quran_references": [],
        "hadith_references": [],
        "scholarly_opinions": [],
        "dua_ids": [],
        "ikhtilaf": "No",
        "conclusion": "",
        "consult_scholar": "No",
        "language_detected": "English"
    }


def normalize_model_result(data):
    result = empty_model_result()

    if not isinstance(data, dict):
        return result

    result["direct_answer"] = str(data.get("direct_answer", "")).strip()
    result["conclusion"] = str(data.get("conclusion", "")).strip()
    result["language_detected"] = str(data.get("language_detected", "English")).strip() or "English"
    result["ikhtilaf"] = "Yes" if str(data.get("ikhtilaf", "")).strip().lower() == "yes" else "No"
    result["consult_scholar"] = "Yes" if str(data.get("consult_scholar", "")).strip().lower() == "yes" else "No"

    quran_refs = data.get("quran_references", [])
    if isinstance(quran_refs, list):
        for item in quran_refs[:5]:
            if not isinstance(item, dict):
                continue
            surah = as_int(item.get("surah"))
            ayah_start = as_int(item.get("ayah_start"))
            ayah_end = as_int(item.get("ayah_end", item.get("ayah_start")))
            explanation = str(item.get("explanation", "")).strip()
            if surah and ayah_start:
                result["quran_references"].append({
                    "surah": surah,
                    "ayah_start": ayah_start,
                    "ayah_end": ayah_end or ayah_start,
                    "explanation": explanation
                })

    hadith_refs = data.get("hadith_references", [])
    if isinstance(hadith_refs, list):
        for item in hadith_refs[:5]:
            if not isinstance(item, dict):
                continue
            result["hadith_references"].append({
                "collection": str(item.get("collection", "")).strip(),
                "reference": str(item.get("reference", "")).strip(),
                "authenticity": normalize_authenticity(item.get("authenticity", "")),
                "why_relevant": str(item.get("why_relevant", "")).strip()
            })

    scholarly = data.get("scholarly_opinions", [])
    if isinstance(scholarly, list):
        for item in scholarly[:6]:
            if not isinstance(item, dict):
                continue
            result["scholarly_opinions"].append({
                "madhab": str(item.get("madhab", "")).strip(),
                "opinion": str(item.get("opinion", "")).strip(),
                "source": str(item.get("source", "")).strip()
            })

    dua_ids = data.get("dua_ids", [])
    if isinstance(dua_ids, list):
        seen = set()
        for item in dua_ids[:4]:
            dua_id = str(item).strip()
            if dua_id and dua_id in VERIFIED_DUA_LIBRARY and dua_id not in seen:
                seen.add(dua_id)
                result["dua_ids"].append(dua_id)

    return result


def parse_response(raw):
    cleaned = re.sub(r"```json|```", "", raw).strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)

    if not match:
        fallback = empty_model_result()
        fallback["direct_answer"] = raw.strip() or "No strong authentic evidence found"
        fallback["conclusion"] = "The model response was not valid JSON."
        return fallback

    try:
        return normalize_model_result(json.loads(match.group(0)))
    except Exception:
        fallback = empty_model_result()
        fallback["direct_answer"] = raw.strip() or "No strong authentic evidence found"
        fallback["conclusion"] = "The model response could not be parsed."
        return fallback


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_surah_editions(surah_number):
    try:
        response = requests.get(
            f"https://api.alquran.cloud/v1/surah/{surah_number}/editions/quran-uthmani,en.asad",
            timeout=20
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("status") == "OK" and isinstance(payload.get("data"), list):
            return payload["data"]
        return None
    except Exception:
        return None


def get_edition_by_identifier(editions, identifier_substring, fallback_index=0):
    if not editions:
        return None
    for edition in editions:
        identifier = str(edition.get("edition", {}).get("identifier", "")).lower()
        if identifier_substring in identifier:
            return edition
    if len(editions) > fallback_index:
        return editions[fallback_index]
    return editions[0]


def verify_quran_references(quran_refs):
    verified = []

    for ref in quran_refs:
        surah = as_int(ref.get("surah"))
        ayah_start = as_int(ref.get("ayah_start"))
        ayah_end = as_int(ref.get("ayah_end"))

        if not surah or not ayah_start:
            continue
        if surah < 1 or surah > 114:
            continue

        if not ayah_end:
            ayah_end = ayah_start
        if ayah_end < ayah_start:
            ayah_start, ayah_end = ayah_end, ayah_start
        if ayah_end - ayah_start > 4:
            ayah_end = ayah_start + 4

        data = fetch_surah_editions(surah)
        if not data:
            continue

        arabic_edition = get_edition_by_identifier(data, "quran-uthmani", 0)
        english_edition = get_edition_by_identifier(data, "en.", 1)

        arabic_ayahs = []
        english_ayahs = []

        for ayah in arabic_edition.get("ayahs", []):
            number = ayah.get("numberInSurah")
            if ayah_start <= number <= ayah_end:
                arabic_ayahs.append(ayah)

        for ayah in english_edition.get("ayahs", []):
            number = ayah.get("numberInSurah")
            if ayah_start <= number <= ayah_end:
                english_ayahs.append(ayah)

        if not arabic_ayahs:
            continue

        arabic_text = " ".join(f'{item.get("text", "")} ﴿{item.get("numberInSurah", "")}﴾' for item in arabic_ayahs).strip()
        translation = " ".join(item.get("text", "") for item in english_ayahs).strip()

        reference_label = (
            f'{SURAH_NAME_BY_NUMBER.get(surah, f"Surah {surah}")} {ayah_start}'
            if ayah_start == ayah_end
            else f'{SURAH_NAME_BY_NUMBER.get(surah, f"Surah {surah}")} {ayah_start}-{ayah_end}'
        )

        verified.append({
            "arabic": arabic_text,
            "translation": translation,
            "reference": reference_label,
            "explanation": ref.get("explanation", ""),
            "verified": True
        })

    return verified


def verify_hadith_references(hadith_refs):
    verified = []
    seen = set()

    for ref in hadith_refs:
        collection = canonical_collection(ref.get("collection", ""))
        number = extract_reference_number(ref.get("reference", ""))
        if not collection or not number:
            continue

        key = f"{collection}|{number}"
        if key in seen:
            continue
        seen.add(key)

        local_record = VERIFIED_HADITH_DB.get(key)
        if local_record:
            item = dict(local_record)
            item["verified"] = True
            item["why_relevant"] = ref.get("why_relevant", "")
            verified.append(item)
        else:
            verified.append({
                "collection": collection,
                "collection_full": {
                    "Bukhari": "Sahih al-Bukhari",
                    "Muslim": "Sahih Muslim",
                    "Abu Dawood": "Sunan Abu Dawood",
                    "Tirmidhi": "Jami at-Tirmidhi"
                }.get(collection, collection),
                "reference": number,
                "reference_label": f"{collection} {number}",
                "authenticity": normalize_authenticity(ref.get("authenticity", "")),
                "arabic": "",
                "text": "",
                "narrator": "",
                "topic": "",
                "why_relevant": ref.get("why_relevant", ""),
                "verified": False,
                "note": "Hadith text was withheld because this reference is not yet in the local verified hadith registry."
            })

    return verified


def curated_hadith_entry(key, why_relevant=""):
    item = dict(VERIFIED_HADITH_DB[key])
    item["verified"] = True
    item["why_relevant"] = why_relevant
    return item


def build_curated_response(route, user_input):
    language = detect_input_language(user_input)

    if route == "before_sleep":
        return {
            "response_mode": "curated",
            "direct_answer": "For falling asleep, start with the short bedtime dua shown below. Ayat al-Kursi is also recommended before sleeping.",
            "quran_evidence": verify_quran_references([
                {
                    "surah": 2,
                    "ayah_start": 255,
                    "ayah_end": 255,
                    "explanation": "Ayat al-Kursi is an established bedtime recitation."
                }
            ]),
            "hadith_evidence": [
                curated_hadith_entry("Bukhari|6324", "This is the short bedtime dua taught by the Prophet.")
            ],
            "scholarly_opinions": [],
            "dua_items": [VERIFIED_DUA_LIBRARY["dua_before_sleep"]],
            "ikhtilaf": "No",
            "conclusion": "For a simple bedtime practice, read the short bedtime dua and, if you can, also recite Ayat al-Kursi.",
            "consult_scholar": "No",
            "language_detected": language
        }

    if route == "morning":
        return {
            "response_mode": "curated",
            "direct_answer": "Here are verified morning adhkar from the built-in library.",
            "quran_evidence": [],
            "hadith_evidence": [],
            "scholarly_opinions": [],
            "dua_items": [
                VERIFIED_DUA_LIBRARY["morning_remembrance"],
                VERIFIED_DUA_LIBRARY["sayyidul_istighfar_morning"]
            ],
            "ikhtilaf": "No",
            "conclusion": "These are good morning adhkar to begin with.",
            "consult_scholar": "No",
            "language_detected": language
        }

    if route == "evening":
        return {
            "response_mode": "curated",
            "direct_answer": "Here is a verified evening remembrance from the built-in library.",
            "quran_evidence": [],
            "hadith_evidence": [],
            "scholarly_opinions": [],
            "dua_items": [VERIFIED_DUA_LIBRARY["evening_remembrance"]],
            "ikhtilaf": "No",
            "conclusion": "Recite this in the evening as part of your adhkar.",
            "consult_scholar": "No",
            "language_detected": language
        }

    if route == "anxiety":
        return {
            "response_mode": "curated",
            "direct_answer": "A verified dua for anxiety and distress is shown below.",
            "quran_evidence": [],
            "hadith_evidence": [],
            "scholarly_opinions": [],
            "dua_items": [VERIFIED_DUA_LIBRARY["anxiety_distress"]],
            "ikhtilaf": "No",
            "conclusion": "Read this dua regularly with sincerity and trust in Allah.",
            "consult_scholar": "No",
            "language_detected": language
        }

    if route == "travel":
        return {
            "response_mode": "curated",
            "direct_answer": "A verified travel supplication is shown below.",
            "quran_evidence": verify_quran_references([
                {
                    "surah": 43,
                    "ayah_start": 13,
                    "ayah_end": 13,
                    "explanation": "This verse forms part of the travel supplication."
                }
            ]),
            "hadith_evidence": [],
            "scholarly_opinions": [],
            "dua_items": [VERIFIED_DUA_LIBRARY["travel_dua"]],
            "ikhtilaf": "No",
            "conclusion": "Recite this when beginning your journey.",
            "consult_scholar": "No",
            "language_detected": language
        }

    if route == "entering_home":
        return {
            "response_mode": "curated",
            "direct_answer": "A verified dua for entering the home is shown below.",
            "quran_evidence": [],
            "hadith_evidence": [],
            "scholarly_opinions": [],
            "dua_items": [VERIFIED_DUA_LIBRARY["entering_home"]],
            "ikhtilaf": "No",
            "conclusion": "Use this dua when entering your home.",
            "consult_scholar": "No",
            "language_detected": language
        }

    return None


def build_verified_result(model_result):
    return {
        "response_mode": "model_verified",
        "direct_answer": model_result.get("direct_answer", "").strip() or "No strong authentic evidence found",
        "quran_evidence": verify_quran_references(model_result.get("quran_references", [])),
        "hadith_evidence": verify_hadith_references(model_result.get("hadith_references", [])),
        "scholarly_opinions": model_result.get("scholarly_opinions", []),
        "dua_items": [VERIFIED_DUA_LIBRARY[item] for item in model_result.get("dua_ids", []) if item in VERIFIED_DUA_LIBRARY],
        "ikhtilaf": model_result.get("ikhtilaf", "No"),
        "conclusion": model_result.get("conclusion", "").strip(),
        "consult_scholar": model_result.get("consult_scholar", "No"),
        "language_detected": model_result.get("language_detected", "English")
    }


def call_api(user_message, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for item in history[-4:]:
        messages.append({"role": "user", "content": item["user"]})
        messages.append({"role": "assistant", "content": item["assistant"]})

    messages.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 1600,
        "temperature": 0.1,
        "stream": False
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"API request failed: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError("API returned invalid JSON.") from exc

    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError(f"API error: {json.dumps(data)[:500]}")

    content = choices[0].get("message", {}).get("content", "").strip()
    if not content:
        raise RuntimeError("Empty response from API")

    return content


def render_metric_row(result):
    verified_quran = len(result.get("quran_evidence", []))
    verified_hadith = len([item for item in result.get("hadith_evidence", []) if item.get("verified")])
    blocked_hadith = len([item for item in result.get("hadith_evidence", []) if not item.get("verified")])
    verified_duas = len(result.get("dua_items", []))

    cards = [
        f'<div class="metric-card"><div class="metric-value">{verified_quran}</div><div class="metric-label">Verified Qur\'an References</div></div>',
        f'<div class="metric-card"><div class="metric-value">{verified_hadith}</div><div class="metric-label">Verified Hadith Entries</div></div>',
        f'<div class="metric-card"><div class="metric-value">{blocked_hadith}</div><div class="metric-label">Blocked Unverified Hadith Texts</div></div>',
        f'<div class="metric-card"><div class="metric-value">{verified_duas}</div><div class="metric-label">Verified Duas Shown</div></div>',
    ]
    st.markdown(f'<div class="metric-row">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_response(result):
    render_metric_row(result)

    if result.get("response_mode") == "curated":
        st.markdown(
            '<div class="info-box"><span class="verify-pill verify-ok">Curated verified answer</span> This answer came directly from the built-in verified dua and Qur\'an workflow, not from model-written source text.</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="info-box"><span class="verify-pill verify-info">Verified reference mode</span> The model suggested references, then the app verified Qur\'an references and filtered Hadith before display.</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        f'<div class="answer-card"><strong style="color:#e4c873;">Direct Answer</strong><br><br>{safe_html(result.get("direct_answer", ""))}</div>',
        unsafe_allow_html=True
    )

    quran = result.get("quran_evidence", [])
    if quran:
        st.markdown('<div class="section-title">Verified Qur\'an Evidence</div>', unsafe_allow_html=True)
        for verse in quran:
            st.markdown(
                f'<div class="quran-card">'
                f'<span class="verify-pill verify-ok">Verified by live Qur\'an reference</span>'
                f'<div class="arabic-text">{safe_html(verse.get("arabic", ""))}</div>'
                f'<div class="arabic-translation">{safe_html(verse.get("translation", ""))}</div>'
                f'<span class="quran-ref">{safe_html(verse.get("reference", ""))}</span><br><br>'
                f'<em style="color:#bcd7c2;">{safe_html(verse.get("explanation", ""))}</em>'
                f'</div>',
                unsafe_allow_html=True
            )

    hadith = result.get("hadith_evidence", [])
    verified_hadith = [item for item in hadith if item.get("verified")]
    blocked_hadith = [item for item in hadith if not item.get("verified")]

    if verified_hadith:
        st.markdown('<div class="section-title">Verified Hadith Evidence</div>', unsafe_allow_html=True)
        for item in verified_hadith:
            auth = item.get("authenticity", "")
            badge_class = "badge-sahih" if auth == "Sahih" else "badge-hasan" if auth == "Hasan" else "badge-weak"
            arabic_block = f'<div class="arabic-text">{safe_html(item.get("arabic", ""))}</div>' if item.get("arabic") else ""
            narrator_line = f'<br><small style="color:#aac3d9;">Narrator: {safe_html(item.get("narrator", ""))}</small>' if item.get("narrator") else ""
            why_line = f'<br><small style="color:#bcd7ea;">Why relevant: {safe_html(item.get("why_relevant", ""))}</small>' if item.get("why_relevant") else ""

            st.markdown(
                f'<div class="hadith-card">'
                f'<span class="verify-pill verify-ok">Verified from local hadith registry</span><br><br>'
                f'{arabic_block}'
                f'<strong>{safe_html(item.get("text", ""))}</strong><br><br>'
                f'<strong>Source:</strong> {safe_html(item.get("collection_full", ""))} - {safe_html(item.get("reference_label", ""))} '
                f'<span class="{badge_class}">{safe_html(auth)}</span>'
                f'{narrator_line}'
                f'{why_line}'
                f'</div>',
                unsafe_allow_html=True
            )

    if blocked_hadith:
        with st.expander(f"Suggested Hadith References Not Yet Verified ({len(blocked_hadith)})"):
            for item in blocked_hadith:
                auth = item.get("authenticity", "")
                badge_class = "badge-sahih" if auth == "Sahih" else "badge-hasan" if auth == "Hasan" else "badge-weak"
                auth_label = f'<span class="{badge_class}">{safe_html(auth)}</span>' if auth else ""
                why_line = f'<br><small style="color:#ffe1a3;">Why relevant: {safe_html(item.get("why_relevant", ""))}</small>' if item.get("why_relevant") else ""

                st.markdown(
                    f'<div class="pending-card">'
                    f'<span class="verify-pill verify-warn">Text blocked until locally verified</span><br><br>'
                    f'<strong>Reference suggested:</strong> {safe_html(item.get("collection_full", ""))} - {safe_html(item.get("reference_label", ""))} {auth_label}<br>'
                    f'<small>{safe_html(item.get("note", ""))}</small>'
                    f'{why_line}'
                    f'</div>',
                    unsafe_allow_html=True
                )

    scholarly = result.get("scholarly_opinions", [])
    if scholarly:
        st.markdown('<div class="section-title">Scholarly View Summary</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">This section is an AI summary of recognized scholarly views. Verify detailed fatwa wording directly for personal rulings.</div>',
            unsafe_allow_html=True
        )
        if result.get("ikhtilaf") == "Yes":
            st.markdown(
                '<div class="info-box">There is a difference of opinion among scholars on this matter.</div>',
                unsafe_allow_html=True
            )
        for opinion in scholarly:
            st.markdown(
                f'<div class="scholar-card">'
                f'<strong style="color:#e4c873;">{safe_html(opinion.get("madhab", "General"))}:</strong> '
                f'{safe_html(opinion.get("opinion", ""))}<br>'
                f'<small style="color:#c9d5e0;">Source label: {safe_html(opinion.get("source", ""))}</small>'
                f'</div>',
                unsafe_allow_html=True
            )

    dua_items = result.get("dua_items", [])
    if dua_items:
        st.markdown('<div class="section-title">Verified Dua</div>', unsafe_allow_html=True)
        for dua in dua_items:
            st.markdown(
                f'<div class="dua-card">'
                f'<span class="verify-pill verify-ok">Loaded from verified dua library</span><br><br>'
                f'<strong style="color:#e4c873; font-size:18px;">{safe_html(dua.get("title", ""))}</strong>'
                f'<div class="arabic-text">{safe_html(dua.get("arabic", ""))}</div>'
                f'<strong style="color:#cda8ff;">Transliteration:</strong><br>{safe_html(dua.get("transliteration", ""))}<br><br>'
                f'<strong style="color:#e4c873;">Meaning:</strong><br>{safe_html(dua.get("meaning", ""))}<br><br>'
                f'<small style="color:#d2b3ff;">Reference: {safe_html(dua.get("reference", ""))}</small>'
                f'</div>',
                unsafe_allow_html=True
            )

    conclusion = result.get("conclusion", "")
    if conclusion:
        st.markdown('<div class="section-title">Conclusion</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="answer-card">{safe_html(conclusion)}</div>', unsafe_allow_html=True)

    if result.get("consult_scholar") == "Yes":
        st.markdown(
            '<div class="warning-card">This matter may require a qualified Islamic scholar for a personal ruling. Please consult a trusted scholar before acting on the answer.</div>',
            unsafe_allow_html=True
        )


NVIDIA_API_KEY = get_api_key()
if not NVIDIA_API_KEY:
    st.error("Missing NVIDIA_API_KEY. Add it in Streamlit Cloud secrets.")
    st.code('NVIDIA_API_KEY = "your-new-api-key"', language="toml")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "quick_question" not in st.session_state:
    st.session_state.quick_question = ""
if "loaded_surah_number" not in st.session_state:
    st.session_state.loaded_surah_number = None

st.markdown('<div class="bismillah">بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</div>', unsafe_allow_html=True)
st.markdown('<div class="main-header">Muslim AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Evidence-first Islamic answers with verified Qur\'an display, curated dua answers, and blocked unverified hadith text</div>', unsafe_allow_html=True)

st.markdown("""
<div class="trust-banner">
    <div class="banner-title">Integrity Mode</div>
    <div class="pill-row">
        <span class="verify-pill verify-ok">Common dua queries use curated verified answers</span>
        <span class="verify-pill verify-ok">Qur'an text is fetched by reference before display</span>
        <span class="verify-pill verify-ok">Duas are shown only from the local verified library</span>
        <span class="verify-pill verify-warn">Unverified hadith wording is hidden</span>
    </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(
        '<div class="panel"><div class="panel-title">Verification Rules</div><div class="pill-row"><span class="verify-pill verify-ok">Curated Dua Mode</span><span class="verify-pill verify-ok">Verified Qur\'an</span><span class="verify-pill verify-warn">Blocked unverified Hadith text</span></div><div class="small-note" style="margin-top:10px;">This is designed to stop mixed ayahs, invented Arabic, and wrongly quoted hadith wording from being shown as fact.</div></div>',
        unsafe_allow_html=True
    )

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
        "Dua for entering home"
    ]

    st.markdown('<div class="panel"><div class="panel-title">Quick Topics</div></div>', unsafe_allow_html=True)
    for topic in topics:
        if st.button(topic, use_container_width=True, key=f"topic_{topic}"):
            st.session_state.quick_question = topic

    st.markdown('<div class="panel"><div class="panel-title">Languages</div><div class="small-note">Ask in English, Urdu, Hindi, or Arabic.</div></div>', unsafe_allow_html=True)

    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.messages = []
        st.session_state.quick_question = ""
        st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(["AI Assistant", "Qur'an Reader", "Dua Collection", "Verified Hadith Library"])

with tab1:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                try:
                    parsed = json.loads(msg["content"])
                    render_response(parsed)
                except Exception:
                    st.markdown(msg["content"])
            else:
                st.markdown(msg["content"])

    quick_q = st.session_state.get("quick_question", "")
    if quick_q:
        st.session_state.quick_question = ""
        user_input = quick_q
    else:
        user_input = st.chat_input("Ask your Islamic question in English, Urdu, Hindi, or Arabic...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Checking references and preparing a verified answer..."):
                try:
                    route = detect_curated_route(user_input)
                    if route:
                        final_result = build_curated_response(route, user_input)
                    else:
                        raw = call_api(user_input, st.session_state.chat_history)
                        model_result = parse_response(raw)
                        final_result = build_verified_result(model_result)

                    render_response(final_result)

                    assistant_store = json.dumps(final_result, ensure_ascii=False)
                    st.session_state.messages.append({"role": "assistant", "content": assistant_store})

                    summary = final_result.get("direct_answer", "").strip()
                    if final_result.get("conclusion"):
                        summary = f"{summary} Conclusion: {final_result.get('conclusion')}".strip()

                    st.session_state.chat_history.append({
                        "user": user_input,
                        "assistant": summary or "No strong authentic evidence found"
                    })

                except Exception as e:
                    error_msg = f"Error: {str(e)}. Please try again."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

with tab2:
    st.markdown('<div class="section-title">Qur\'an Reader</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Select any Surah to read verified Arabic text and English translation directly from the Qur\'an API.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        surah_options = [f"{num}. {name} ({verses} verses)" for num, name, verses in QURAN_SURAHS]
        selected_surah = st.selectbox("Select Surah", surah_options)
        surah_number = int(selected_surah.split(".")[0])
        surah_info = QURAN_SURAHS[surah_number - 1]

        st.markdown(
            f'<div class="info-box"><strong style="color:#e4c873;">Surah {surah_info[0]}: {safe_html(surah_info[1])}</strong><br>Total Ayahs: {surah_info[2]}</div>',
            unsafe_allow_html=True
        )

        if st.button("Load Surah", type="primary", use_container_width=True):
            st.session_state.loaded_surah_number = surah_number

    with col2:
        current_surah_number = st.session_state.loaded_surah_number
        if current_surah_number:
            surah_data = fetch_surah_editions(current_surah_number)
            if surah_data:
                arabic_edition = get_edition_by_identifier(surah_data, "quran-uthmani", 0)
                english_edition = get_edition_by_identifier(surah_data, "en.", 1)
                english_ayahs = english_edition.get("ayahs", [])

                st.markdown(
                    f'<div class="info-box"><span class="verify-pill verify-ok">Verified live Qur\'an text</span></div>',
                    unsafe_allow_html=True
                )
                st.markdown(f'<div class="bismillah">{safe_html(arabic_edition.get("name", ""))}</div>', unsafe_allow_html=True)

                for i, ayah in enumerate(arabic_edition.get("ayahs", [])):
                    arabic = ayah.get("text", "")
                    english = english_ayahs[i].get("text", "") if i < len(english_ayahs) else ""
                    ayah_number = ayah.get("numberInSurah", i + 1)

                    st.markdown(
                        f'<div class="quran-ayah">'
                        f'<span style="color:#e4c873; font-size:12px;">Ayah {ayah_number}</span>'
                        f'<div class="arabic-text">{safe_html(arabic)} ﴿{ayah_number}﴾</div>'
                        f'<div class="arabic-translation">{safe_html(english)}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.error("Could not load the Surah right now. Please try again.")
        else:
            st.info("Select a Surah and click Load Surah.")

with tab3:
    st.markdown('<div class="section-title">Verified Dua Collection</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">These duas come only from the local verified dua library used by the assistant.</div>', unsafe_allow_html=True)

    selected_category = st.selectbox("Select Category", list(DUA_CATEGORIES.keys()))
    dua_ids = DUA_CATEGORIES.get(selected_category, [])

    for dua_id in dua_ids:
        dua = VERIFIED_DUA_LIBRARY[dua_id]
        st.markdown(
            f'<div class="dua-card">'
            f'<span class="verify-pill verify-ok">Verified dua library</span><br><br>'
            f'<strong style="color:#e4c873; font-size:16px;">{safe_html(dua["title"])}</strong><br>'
            f'<div class="arabic-text">{safe_html(dua["arabic"])}</div><br>'
            f'<strong style="color:#cda8ff;">Transliteration:</strong><br><em>{safe_html(dua["transliteration"])}</em><br><br>'
            f'<strong style="color:#e4c873;">Meaning:</strong><br>{safe_html(dua["meaning"])}<br><br>'
            f'<small style="color:#d2b3ff;">Reference: {safe_html(dua["reference"])}</small>'
            f'</div>',
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section-title">Verified Hadith Library</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Only hadith entries stored in this local verified registry can appear with full wording in the AI Assistant tab.</div>', unsafe_allow_html=True)

    selected_group = st.selectbox("Select Group", list(HADITH_LIBRARY_GROUPS.keys()))
    hadith_keys = HADITH_LIBRARY_GROUPS.get(selected_group, [])

    for key in hadith_keys:
        hadith = VERIFIED_HADITH_DB[key]
        auth = hadith.get("authenticity", "")
        badge_class = "badge-sahih" if auth == "Sahih" else "badge-hasan" if auth == "Hasan" else "badge-weak"
        arabic_block = f'<div class="arabic-text">{safe_html(hadith.get("arabic", ""))}</div><br>' if hadith.get("arabic") else ""

        st.markdown(
            f'<div class="hadith-card">'
            f'<span class="verify-pill verify-ok">Verified local entry</span><br><br>'
            f'<span style="color:#e4c873; font-size:13px; font-weight:700;">{safe_html(hadith.get("reference_label", ""))}</span> '
            f'<span class="{badge_class}">{safe_html(auth)}</span>'
            f'{arabic_block}'
            f'<strong>{safe_html(hadith.get("text", ""))}</strong><br><br>'
            f'<small style="color:#aac3d9;">Collection: {safe_html(hadith.get("collection_full", ""))}</small><br>'
            f'<small style="color:#aac3d9;">Narrator: {safe_html(hadith.get("narrator", ""))}</small><br>'
            f'<small style="color:#aac3d9;">Topic: {safe_html(hadith.get("topic", ""))}</small>'
            f'</div>',
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        '<div class="warning-card">If the model suggests a hadith reference that is not in this verified registry, the app will show the reference only inside a collapsed section and hide the hadith text.</div>',
        unsafe_allow_html=True
    )
