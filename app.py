import os
import json
import re
from html import escape

import requests
import streamlit as st

st.set_page_config(
    page_title="Muslim AI",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Scheherazade+New:wght@400;700&family=Manrope:wght@400;500;600;700&display=swap');

:root {
    --bg-1: #061019;
    --bg-2: #0d1e2b;
    --bg-3: #153147;
    --gold-1: #d7bb69;
    --gold-2: #f2d78f;
    --mint-1: #a4e0bd;
    --mint-2: #2ca36d;
    --blue-1: #9bd1ff;
    --blue-2: #3091db;
    --text-1: #eef4fb;
    --text-2: #c8d5e2;
    --text-3: #97aabd;
    --line: rgba(215, 187, 105, 0.18);
    --ok: #27ae60;
    --warn: #f39c12;
    --danger: #e74c3c;
}

html, body, [class*="css"] {
    font-family: 'Manrope', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 15% 10%, rgba(215, 187, 105, 0.12), transparent 18%),
        radial-gradient(circle at 85% 18%, rgba(49, 145, 219, 0.10), transparent 20%),
        radial-gradient(circle at 50% 80%, rgba(44, 163, 109, 0.07), transparent 24%),
        linear-gradient(135deg, var(--bg-1) 0%, var(--bg-2) 48%, var(--bg-3) 100%);
    color: var(--text-1);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(8, 16, 24, 0.98), rgba(12, 24, 36, 0.98));
    border-right: 1px solid rgba(215, 187, 105, 0.12);
}

section[data-testid="stSidebar"] .stButton button {
    border-radius: 14px;
    border: 1px solid rgba(215, 187, 105, 0.24);
    background: linear-gradient(135deg, rgba(19, 33, 47, 0.95), rgba(13, 24, 36, 0.95));
    color: var(--text-1);
    transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
}
section[data-testid="stSidebar"] .stButton button:hover {
    transform: translateY(-1px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.22);
    border-color: rgba(242, 215, 143, 0.45);
}

.block-container {
    padding-top: 1.4rem;
    padding-bottom: 2rem;
}

@keyframes riseFade {
    0% { opacity: 0; transform: translateY(10px); }
    100% { opacity: 1; transform: translateY(0); }
}

@keyframes glowPulse {
    0%, 100% { box-shadow: 0 0 0 rgba(215, 187, 105, 0); }
    50% { box-shadow: 0 0 24px rgba(215, 187, 105, 0.10); }
}

@keyframes drift {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-4px); }
}

.hero-shell {
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(215, 187, 105, 0.24);
    border-radius: 22px;
    padding: 22px 20px 18px 20px;
    background:
        linear-gradient(135deg, rgba(11, 21, 31, 0.96), rgba(17, 34, 48, 0.94)),
        radial-gradient(circle at top right, rgba(215, 187, 105, 0.10), transparent 30%);
    animation: riseFade 500ms ease both, glowPulse 7s ease-in-out infinite;
}
.hero-shell::before {
    content: "";
    position: absolute;
    top: -50px;
    right: -30px;
    width: 170px;
    height: 170px;
    border-radius: 999px;
    background: radial-gradient(circle, rgba(242, 215, 143, 0.12), transparent 68%);
    animation: drift 8s ease-in-out infinite;
}
.hero-bismillah {
    font-family: 'Scheherazade New', serif;
    font-size: 40px;
    color: var(--gold-2);
    direction: rtl;
    text-align: center;
    line-height: 1.7;
    margin-bottom: 2px;
}
.hero-title {
    font-family: 'Amiri', serif;
    font-size: 44px;
    color: var(--gold-2);
    text-align: center;
    margin-bottom: 4px;
}
.hero-subtitle {
    text-align: center;
    color: var(--text-2);
    font-size: 15px;
    line-height: 1.7;
    margin-bottom: 14px;
}
.hero-badges {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
}

.verify-pill {
    display: inline-block;
    padding: 6px 11px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
}
.verify-ok {
    background: rgba(39, 174, 96, 0.16);
    border: 1px solid rgba(39, 174, 96, 0.34);
    color: #a5e4ba;
}
.verify-warn {
    background: rgba(243, 156, 18, 0.16);
    border: 1px solid rgba(243, 156, 18, 0.34);
    color: #ffd391;
}
.verify-info {
    background: rgba(52, 152, 219, 0.16);
    border: 1px solid rgba(52, 152, 219, 0.34);
    color: #aad9ff;
}

.panel,
.metric-card,
.answer-card,
.quran-card,
.hadith-card,
.pending-card,
.dua-card,
.info-box,
.warning-card,
.registry-card,
.source-card,
.scholar-card,
.quran-ayah {
    animation: riseFade 430ms ease both;
}

.panel {
    background: linear-gradient(135deg, rgba(14, 27, 39, 0.96), rgba(18, 35, 49, 0.94));
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 14px 16px;
    color: var(--text-1);
    margin-bottom: 12px;
}
.panel-title {
    color: var(--gold-2);
    font-weight: 700;
    margin-bottom: 8px;
}
.small-note {
    color: var(--text-3);
    font-size: 12px;
    line-height: 1.65;
}

.metric-row {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
    margin: 12px 0 16px 0;
}
.metric-card {
    background: linear-gradient(135deg, rgba(15, 29, 43, 0.96), rgba(10, 23, 34, 0.96));
    border: 1px solid rgba(215, 187, 105, 0.14);
    border-radius: 16px;
    padding: 14px;
}
.metric-value {
    color: var(--gold-2);
    font-size: 24px;
    font-weight: 700;
    line-height: 1.1;
}
.metric-label {
    color: var(--text-3);
    font-size: 12px;
    margin-top: 4px;
}

.answer-card {
    background: linear-gradient(135deg, rgba(21, 37, 53, 0.96), rgba(19, 49, 71, 0.96));
    border-left: 4px solid var(--gold-1);
    border-radius: 18px;
    padding: 20px;
    color: var(--text-1);
    line-height: 1.9;
    margin: 12px 0;
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.18);
}
.quran-card,
.quran-ayah {
    background: linear-gradient(135deg, rgba(13, 36, 22, 0.96), rgba(20, 53, 33, 0.96));
    border: 1px solid rgba(46, 171, 104, 0.42);
    border-left: 4px solid #2ecc71;
    border-radius: 18px;
    padding: 18px;
    color: var(--text-1);
    margin: 10px 0;
}
.hadith-card {
    background: linear-gradient(135deg, rgba(13, 28, 42, 0.96), rgba(19, 45, 69, 0.96));
    border: 1px solid rgba(52, 152, 219, 0.40);
    border-left: 4px solid #3498db;
    border-radius: 18px;
    padding: 18px;
    color: var(--text-1);
    margin: 10px 0;
}
.pending-card {
    background: linear-gradient(135deg, rgba(43, 30, 10, 0.96), rgba(60, 41, 12, 0.96));
    border: 1px solid rgba(243, 156, 18, 0.42);
    border-left: 4px solid var(--warn);
    border-radius: 18px;
    padding: 18px;
    color: #fff1cf;
    margin: 10px 0;
}
.dua-card {
    background:
        linear-gradient(135deg, rgba(22, 16, 42, 0.97), rgba(33, 24, 59, 0.97)),
        radial-gradient(circle at top right, rgba(205, 168, 255, 0.08), transparent 30%);
    border: 1px solid rgba(184, 130, 255, 0.34);
    border-radius: 20px;
    padding: 22px;
    text-align: center;
    color: var(--text-1);
    margin: 10px 0;
}
.registry-card,
.source-card {
    background: linear-gradient(135deg, rgba(16, 28, 40, 0.96), rgba(13, 21, 31, 0.96));
    border: 1px solid rgba(215, 187, 105, 0.15);
    border-radius: 16px;
    padding: 16px;
    color: var(--text-1);
    margin: 10px 0;
}
.scholar-card {
    background: linear-gradient(135deg, rgba(38, 28, 14, 0.96), rgba(52, 35, 16, 0.96));
    border-left: 4px solid var(--gold-1);
    border-radius: 14px;
    padding: 14px;
    color: var(--text-1);
    margin: 10px 0;
}
.info-box {
    background: linear-gradient(135deg, rgba(14, 27, 39, 0.96), rgba(18, 35, 49, 0.96));
    border: 1px solid var(--line);
    border-radius: 15px;
    padding: 14px;
    color: var(--text-2);
    margin: 10px 0;
}
.warning-card {
    background: linear-gradient(135deg, rgba(42, 14, 14, 0.95), rgba(58, 20, 20, 0.95));
    border-left: 4px solid var(--danger);
    border-radius: 14px;
    padding: 14px;
    color: #f6d8d8;
    margin: 12px 0;
}
.section-title {
    color: var(--gold-2);
    font-size: 20px;
    font-weight: 700;
    margin: 18px 0 10px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(215, 187, 105, 0.28);
}
.arabic-text {
    font-family: 'Scheherazade New', serif;
    font-size: 29px;
    line-height: 2.25;
    direction: rtl;
    text-align: right;
    color: var(--gold-2);
    margin: 10px 0 6px 0;
}
.arabic-translation {
    color: #d0e3d5;
    font-style: italic;
    line-height: 1.8;
    margin-top: 8px;
}
.meta-line {
    color: var(--text-3);
    font-size: 12px;
    line-height: 1.6;
    margin-top: 8px;
}
.badge-sahih,
.badge-hasan,
.badge-weak {
    color: white;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
}
.badge-sahih { background: #27ae60; }
.badge-hasan { background: #f39c12; }
.badge-weak { background: #e74c3c; }

.source-link {
    color: var(--blue-1);
    text-decoration: none;
    font-weight: 700;
}
.source-link:hover {
    color: #e7f5ff;
    text-decoration: underline;
}

@media (max-width: 900px) {
    .metric-row {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (prefers-reduced-motion: reduce) {
    .hero-shell,
    .panel,
    .metric-card,
    .answer-card,
    .quran-card,
    .hadith-card,
    .pending-card,
    .dua-card,
    .info-box,
    .warning-card,
    .registry-card,
    .source-card,
    .scholar-card,
    .quran-ayah {
        animation: none !important;
    }
}
</style>
""", unsafe_allow_html=True)

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "meta/llama-4-maverick-17b-128e-instruct"
REQUEST_TIMEOUT = 45

SURAH_NAMES = [
    "Al-Fatihah", "Al-Baqarah", "Ali 'Imran", "An-Nisa", "Al-Ma'idah", "Al-An'am",
    "Al-A'raf", "Al-Anfal", "At-Tawbah", "Yunus", "Hud", "Yusuf", "Ar-Ra'd",
    "Ibrahim", "Al-Hijr", "An-Nahl", "Al-Isra", "Al-Kahf", "Maryam", "Ta-Ha",
    "Al-Anbiya", "Al-Hajj", "Al-Mu'minun", "An-Nur", "Al-Furqan", "Ash-Shu'ara",
    "An-Naml", "Al-Qasas", "Al-'Ankabut", "Ar-Rum", "Luqman", "As-Sajdah",
    "Al-Ahzab", "Saba", "Fatir", "Ya-Sin", "As-Saffat", "Sad", "Az-Zumar",
    "Ghafir", "Fussilat", "Ash-Shura", "Az-Zukhruf", "Ad-Dukhan", "Al-Jathiyah",
    "Al-Ahqaf", "Muhammad", "Al-Fath", "Al-Hujurat", "Qaf", "Adh-Dhariyat",
    "At-Tur", "An-Najm", "Al-Qamar", "Ar-Rahman", "Al-Waqi'ah", "Al-Hadid",
    "Al-Mujadilah", "Al-Hashr", "Al-Mumtahanah", "As-Saff", "Al-Jumu'ah",
    "Al-Munafiqun", "At-Taghabun", "At-Talaq", "At-Tahrim", "Al-Mulk", "Al-Qalam",
    "Al-Haqqah", "Al-Ma'arij", "Nuh", "Al-Jinn", "Al-Muzzammil", "Al-Muddaththir",
    "Al-Qiyamah", "Al-Insan", "Al-Mursalat", "An-Naba", "An-Nazi'at", "'Abasa",
    "At-Takwir", "Al-Infitar", "Al-Mutaffifin", "Al-Inshiqaq", "Al-Buruj", "At-Tariq",
    "Al-A'la", "Al-Ghashiyah", "Al-Fajr", "Al-Balad", "Ash-Shams", "Al-Layl",
    "Ad-Duhaa", "Ash-Sharh", "At-Tin", "Al-'Alaq", "Al-Qadr", "Al-Bayyinah",
    "Az-Zalzalah", "Al-'Adiyat", "Al-Qari'ah", "At-Takathur", "Al-'Asr", "Al-Humazah",
    "Al-Fil", "Quraysh", "Al-Ma'un", "Al-Kawthar", "Al-Kafirun", "An-Nasr",
    "Al-Masad", "Al-Ikhlas", "Al-Falaq", "An-Nas",
]
SURAH_NAME_BY_NUMBER = {index + 1: name for index, name in enumerate(SURAH_NAMES)}

# Exact text lives only here.
CANONICAL_HADITH_SOURCES = {
    "Bukhari|6306": {
        "collection": "Bukhari",
        "collection_full": "Sahih al-Bukhari",
        "reference": "6306",
        "reference_label": "Bukhari 6306",
        "source_label": "Sahih al-Bukhari 6306",
        "authenticity": "Sahih",
        "source_url": "https://sunnah.com/bukhari:6306",
        "narrator": "Shaddad bin Aws (RA)",
        "hadith_text_en": (
            "The most superior way of asking forgiveness from Allah is to say this supplication. "
            "Whoever says it during the day with firm faith and dies before evening, or says it at night "
            "with firm faith and dies before morning, will be from the people of Paradise."
        ),
        "hadith_text_ar": (
            "سَيِّدُ الاِسْتِغْفَارِ أَنْ تَقُولَ اللَّهُمَّ أَنْتَ رَبِّي، لاَ إِلَهَ إِلاَّ أَنْتَ، "
            "خَلَقْتَنِي وَأَنَا عَبْدُكَ، وَأَنَا عَلَى عَهْدِكَ وَوَعْدِكَ مَا اسْتَطَعْتُ، "
            "أَعُوذُ بِكَ مِنْ شَرِّ مَا صَنَعْتُ، أَبُوءُ لَكَ بِنِعْمَتِكَ عَلَيَّ، "
            "وَأَبُوءُ بِذَنْبِي، فَاغْفِرْ لِي، فَإِنَّهُ لاَ يَغْفِرُ الذُّنُوبَ إِلاَّ أَنْتَ"
        ),
        "invocation_arabic": (
            "اللَّهُمَّ أَنْتَ رَبِّي، لاَ إِلَهَ إِلاَّ أَنْتَ، خَلَقْتَنِي وَأَنَا عَبْدُكَ، "
            "وَأَنَا عَلَى عَهْدِكَ وَوَعْدِكَ مَا اسْتَطَعْتُ، أَعُوذُ بِكَ مِنْ شَرِّ مَا صَنَعْتُ، "
            "أَبُوءُ لَكَ بِنِعْمَتِكَ عَلَيَّ، وَأَبُوءُ بِذَنْبِي، فَاغْفِرْ لِي، "
            "فَإِنَّهُ لاَ يَغْفِرُ الذُّنُوبَ إِلاَّ أَنْتَ"
        ),
        "transliteration": (
            "Allahumma anta Rabbi, la ilaha illa anta, khalaqtani wa ana 'abduka, "
            "wa ana 'ala 'ahdika wa wa'dika mastata'tu, a'udhu bika min sharri ma sana'tu, "
            "abu'u laka bini'matika 'alayya, wa abu'u bidh-dhanbi, faghfir li, "
            "fa innahu la yaghfirudh-dhunuba illa anta."
        ),
        "meaning": (
            "O Allah, You are my Lord. There is no deity except You. You created me and I am Your servant. "
            "I remain faithful to Your covenant and promise as much as I can. I seek refuge in You from the evil "
            "of what I have done. I acknowledge Your favor upon me and I acknowledge my sin, so forgive me, "
            "for none forgives sins except You."
        ),
        "display_note": "Verified from one canonical source record.",
    },
    "Bukhari|6314": {
        "collection": "Bukhari",
        "collection_full": "Sahih al-Bukhari",
        "reference": "6314",
        "reference_label": "Bukhari 6314",
        "source_label": "Sahih al-Bukhari 6314",
        "authenticity": "Sahih",
        "source_url": "https://sunnah.com/bukhari:6314",
        "narrator": "Hudhayfah (RA)",
        "hadith_text_en": "When the Prophet went to bed at night, he would place his hand under his cheek and say this supplication.",
        "hadith_text_ar": "اللَّهُمَّ بِاسْمِكَ أَمُوتُ وَأَحْيَا",
        "invocation_arabic": "اللَّهُمَّ بِاسْمِكَ أَمُوتُ وَأَحْيَا",
        "transliteration": "Allahumma bismika amutu wa ahya.",
        "meaning": "O Allah, in Your name I die and I live.",
        "display_note": "An authentic bedtime variant. The app keeps it separate from Bukhari 6324 so variants do not get mixed.",
    },
    "Bukhari|6324": {
        "collection": "Bukhari",
        "collection_full": "Sahih al-Bukhari",
        "reference": "6324",
        "reference_label": "Bukhari 6324",
        "source_label": "Sahih al-Bukhari 6324",
        "authenticity": "Sahih",
        "source_url": "https://sunnah.com/bukhari:6324",
        "narrator": "Hudhayfah (RA)",
        "hadith_text_en": "Whenever the Prophet intended to go to bed, he would say this supplication.",
        "hadith_text_ar": "بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا",
        "invocation_arabic": "بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا",
        "transliteration": "Bismika Allahumma amutu wa ahya.",
        "meaning": "In Your name, O Allah, I die and I live.",
        "display_note": "This is the app's primary short bedtime dua source.",
    },
    "Tirmidhi|1858": {
        "collection": "Tirmidhi",
        "collection_full": "Jami at-Tirmidhi",
        "reference": "1858",
        "reference_label": "Tirmidhi 1858",
        "source_label": "Jami at-Tirmidhi 1858",
        "authenticity": "Hasan",
        "source_url": "https://sunnah.com/tirmidhi:1858",
        "narrator": "Aishah (RA)",
        "hadith_text_en": (
            "When one of you eats food, let him say Bismillah. If he forgets in the beginning, "
            "let him say: Bismillahi fi awwalihi wa akhirihi."
        ),
        "hadith_text_ar": (
            "إِذَا أَكَلَ أَحَدُكُمْ طَعَامًا فَلْيَقُلْ بِسْمِ اللَّهِ فَإِنْ نَسِيَ فِي أَوَّلِهِ "
            "فَلْيَقُلْ بِسْمِ اللَّهِ فِي أَوَّلِهِ وَآخِرِهِ"
        ),
        "invocation_arabic": "بِسْمِ اللَّهِ",
        "transliteration": "Bismillah.",
        "meaning": "In the name of Allah.",
        "alternate_arabic": "بِسْمِ اللَّهِ فِي أَوَّلِهِ وَآخِرِهِ",
        "alternate_transliteration": "Bismillahi fi awwalihi wa akhirihi.",
        "alternate_meaning": "In the name of Allah, at its beginning and at its end.",
        "display_note": "If you forgot at the start, use the alternate phrase shown below the card.",
    },
}

DUA_LIBRARY = {
    "sleep_short_dua": {
        "type": "hadith_source",
        "title": "Short Bedtime Dua",
        "category": "Before Sleep",
        "source_key": "Bukhari|6324",
    },
    "ayat_al_kursi_sleep": {
        "type": "quran_reference",
        "title": "Ayat al-Kursi Before Sleep",
        "category": "Before Sleep",
        "surah": 2,
        "ayah_start": 255,
        "ayah_end": 255,
        "explanation": "Displayed by live Qur'an reference instead of being typed manually.",
    },
    "morning_sayyidul_istighfar": {
        "type": "hadith_source",
        "title": "Sayyidul Istighfar",
        "category": "Morning Starter",
        "source_key": "Bukhari|6306",
    },
    "before_eating_bismillah": {
        "type": "hadith_source",
        "title": "Before Eating",
        "category": "Eating",
        "source_key": "Tirmidhi|1858",
    },
}

DUA_CATEGORIES = {
    "Before Sleep": ["sleep_short_dua", "ayat_al_kursi_sleep"],
    "Morning Starter": ["morning_sayyidul_istighfar"],
    "Eating": ["before_eating_bismillah"],
}

ALLOWED_DUA_IDS = ", ".join(sorted(DUA_LIBRARY.keys()))

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

DUA MODE:
If the user asks for a dua, return only one or more dua_ids from this verified list:
{ALLOWED_DUA_IDS}

IKHTILAF HANDLING:
- If valid scholarly disagreement exists, set ikhtilaf to Yes
- Present major valid views neutrally
- Mention madhab when relevant

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
      "explanation": "brief explanation"
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
        value = st.secrets.get("NVIDIA_API_KEY", "")
    except Exception:
        value = ""
    return (value or os.getenv("NVIDIA_API_KEY", "")).strip()


def safe_html(value):
    return escape("" if value is None else str(value)).replace("\n", "<br>")


def html_link(label, url):
    return f'<a class="source-link" href="{escape(url, quote=True)}" target="_blank">{safe_html(label)}</a>'


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
    }
    return mapping.get(raw, "")


def extract_reference_number(value):
    match = re.search(r"\d+", str(value or ""))
    return match.group(0) if match else ""


def contains_any(text, phrases):
    return any(phrase in text for phrase in phrases)


def detect_curated_route(user_input):
    q = re.sub(r"\s+", " ", user_input.lower().strip())

    if contains_any(q, [
        "dua to fall asleep", "sleep dua", "dua before sleep", "before sleep",
        "before sleeping", "dua for sleep", "sleeping dua", "fall asleep",
        "sleep", "neend", "sona", "sone se pehle",
    ]):
        return "before_sleep"

    if contains_any(q, [
        "morning dua", "morning adhkar", "morning azkar", "morning remembrance",
        "sayyidul istighfar", "forgiveness dua", "istighfar",
    ]):
        return "morning_starter"

    if contains_any(q, [
        "dua before eating", "before eating", "food dua", "eating dua",
        "khane se pehle", "khana khane",
    ]):
        return "before_eating"

    return None


def validate_registries():
    required_fields = [
        "collection", "collection_full", "reference", "reference_label",
        "source_label", "authenticity", "source_url", "hadith_text_en",
        "invocation_arabic", "transliteration", "meaning",
    ]
    seen = set()

    for source_key, source in CANONICAL_HADITH_SOURCES.items():
        for field in required_fields:
            if not str(source.get(field, "")).strip():
                raise ValueError(f"Missing {field} in {source_key}")

        expected_key = f"{source['collection']}|{source['reference']}"
        if source_key != expected_key:
            raise ValueError(f"Source key mismatch: {source_key}")

        ref_pair = (source["collection"], source["reference"])
        if ref_pair in seen:
            raise ValueError(f"Duplicate canonical source: {source_key}")
        seen.add(ref_pair)

    for dua_id, item in DUA_LIBRARY.items():
        if item.get("type") not in {"hadith_source", "quran_reference"}:
            raise ValueError(f"Invalid dua type in {dua_id}")

        if item["type"] == "hadith_source":
            source_key = item.get("source_key", "")
            if source_key not in CANONICAL_HADITH_SOURCES:
                raise ValueError(f"{dua_id} references missing source {source_key}")

            forbidden_fields = {"arabic", "transliteration", "meaning", "reference"}
            if forbidden_fields.intersection(item.keys()):
                raise ValueError(
                    f"{dua_id} stores exact text directly. Keep exact text only in CANONICAL_HADITH_SOURCES."
                )

        if item["type"] == "quran_reference":
            if not as_int(item.get("surah")) or not as_int(item.get("ayah_start")):
                raise ValueError(f"Invalid Qur'an reference in {dua_id}")

    for category, item_ids in DUA_CATEGORIES.items():
        if not item_ids:
            raise ValueError(f"Empty dua category: {category}")
        for item_id in item_ids:
            if item_id not in DUA_LIBRARY:
                raise ValueError(f"Unknown dua id {item_id} in category {category}")


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_surah_editions(surah_number):
    try:
        response = requests.get(
            f"https://api.alquran.cloud/v1/surah/{surah_number}/editions/quran-uthmani,en.asad",
            timeout=20,
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
    seen = set()

    for ref in quran_refs:
        surah = as_int(ref.get("surah"))
        ayah_start = as_int(ref.get("ayah_start"))
        ayah_end = as_int(ref.get("ayah_end", ref.get("ayah_start")))
        title = str(ref.get("title", "")).strip()
        explanation = str(ref.get("explanation", "")).strip()

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

        dedupe_key = (surah, ayah_start, ayah_end)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

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

        arabic_text = " ".join(
            f'{item.get("text", "")} ﴿{item.get("numberInSurah", "")}﴾'
            for item in arabic_ayahs
        ).strip()
        translation = " ".join(item.get("text", "") for item in english_ayahs).strip()

        reference_label = (
            f'{SURAH_NAME_BY_NUMBER.get(surah, f"Surah {surah}")} {ayah_start}'
            if ayah_start == ayah_end
            else f'{SURAH_NAME_BY_NUMBER.get(surah, f"Surah {surah}")} {ayah_start}-{ayah_end}'
        )

        verified.append({
            "title": title,
            "arabic": arabic_text,
            "translation": translation,
            "reference": reference_label,
            "explanation": explanation,
            "verified": True,
        })

    return verified


def hadith_record_for_source(source_key, why_relevant=""):
    source = CANONICAL_HADITH_SOURCES[source_key]
    return {
        "collection": source["collection"],
        "collection_full": source["collection_full"],
        "reference_label": source["reference_label"],
        "source_label": source["source_label"],
        "source_url": source["source_url"],
        "authenticity": source["authenticity"],
        "arabic": source.get("hadith_text_ar", source["invocation_arabic"]),
        "text": source["hadith_text_en"],
        "narrator": source.get("narrator", ""),
        "why_relevant": why_relevant,
        "verified": True,
    }


def build_dua_card(item_id):
    item = DUA_LIBRARY[item_id]
    if item["type"] != "hadith_source":
        return None

    source = CANONICAL_HADITH_SOURCES[item["source_key"]]
    return {
        "title": item["title"],
        "arabic": source["invocation_arabic"],
        "transliteration": source["transliteration"],
        "meaning": source["meaning"],
        "reference_label": source["source_label"],
        "source_url": source["source_url"],
        "authenticity": source["authenticity"],
        "note": source.get("display_note", ""),
        "alternate_arabic": source.get("alternate_arabic", ""),
        "alternate_transliteration": source.get("alternate_transliteration", ""),
        "alternate_meaning": source.get("alternate_meaning", ""),
    }


def quran_ref_from_library_item(item_id):
    item = DUA_LIBRARY[item_id]
    if item["type"] != "quran_reference":
        return None
    return {
        "surah": item["surah"],
        "ayah_start": item["ayah_start"],
        "ayah_end": item["ayah_end"],
        "title": item["title"],
        "explanation": item.get("explanation", ""),
    }


def expand_dua_ids(dua_ids):
    dua_cards = []
    quran_refs = []

    for dua_id in dua_ids:
        if dua_id not in DUA_LIBRARY:
            continue
        item = DUA_LIBRARY[dua_id]
        if item["type"] == "hadith_source":
            card = build_dua_card(dua_id)
            if card:
                dua_cards.append(card)
        elif item["type"] == "quran_reference":
            ref = quran_ref_from_library_item(dua_id)
            if ref:
                quran_refs.append(ref)

    return dua_cards, quran_refs


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
        "language_detected": "English",
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
            if surah and ayah_start:
                result["quran_references"].append({
                    "surah": surah,
                    "ayah_start": ayah_start,
                    "ayah_end": ayah_end or ayah_start,
                    "title": str(item.get("title", "")).strip(),
                    "explanation": str(item.get("explanation", "")).strip(),
                })

    hadith_refs = data.get("hadith_references", [])
    if isinstance(hadith_refs, list):
        for item in hadith_refs[:6]:
            if not isinstance(item, dict):
                continue
            result["hadith_references"].append({
                "collection": str(item.get("collection", "")).strip(),
                "reference": str(item.get("reference", "")).strip(),
                "authenticity": normalize_authenticity(item.get("authenticity", "")),
                "why_relevant": str(item.get("why_relevant", "")).strip(),
            })

    scholarly = data.get("scholarly_opinions", [])
    if isinstance(scholarly, list):
        for item in scholarly[:6]:
            if not isinstance(item, dict):
                continue
            result["scholarly_opinions"].append({
                "madhab": str(item.get("madhab", "")).strip(),
                "opinion": str(item.get("opinion", "")).strip(),
                "source": str(item.get("source", "")).strip(),
            })

    dua_ids = data.get("dua_ids", [])
    if isinstance(dua_ids, list):
        seen = set()
        for item in dua_ids[:4]:
            dua_id = str(item).strip()
            if dua_id in DUA_LIBRARY and dua_id not in seen:
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


def call_api(user_message, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for item in history[-4:]:
        messages.append({"role": "user", "content": item["user"]})
        messages.append({"role": "assistant", "content": item["assistant"]})
    messages.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 1600,
        "temperature": 0.1,
        "stream": False,
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


def verify_hadith_references(hadith_refs):
    verified = []
    blocked = []
    seen = set()

    for ref in hadith_refs:
        collection = canonical_collection(ref.get("collection", ""))
        number = extract_reference_number(ref.get("reference", ""))
        if not collection or not number:
            continue

        source_key = f"{collection}|{number}"
        if source_key in seen:
            continue
        seen.add(source_key)

        if source_key in CANONICAL_HADITH_SOURCES:
            verified.append(hadith_record_for_source(source_key, ref.get("why_relevant", "")))
        else:
            blocked.append({
                "collection_full": {
                    "Bukhari": "Sahih al-Bukhari",
                    "Muslim": "Sahih Muslim",
                    "Abu Dawood": "Sunan Abu Dawood",
                    "Tirmidhi": "Jami at-Tirmidhi",
                }.get(collection, collection),
                "reference_label": f"{collection} {number}",
                "authenticity": normalize_authenticity(ref.get("authenticity", "")),
                "why_relevant": ref.get("why_relevant", ""),
                "note": "This hadith wording is hidden because it is not yet in the canonical source registry.",
            })

    return verified, blocked


def build_curated_response(route, user_input):
    if route == "before_sleep":
        quran_evidence = verify_quran_references([quran_ref_from_library_item("ayat_al_kursi_sleep")])
        return {
            "response_mode": "curated",
            "direct_answer": (
                "The short verified bedtime dua is shown below. This app intentionally uses one canonical "
                "Bukhari wording so authentic variants do not get mixed together."
            ),
            "quran_evidence": quran_evidence,
            "hadith_evidence": [hadith_record_for_source("Bukhari|6324", "This is the short bedtime supplication.")],
            "blocked_hadith": [],
            "scholarly_opinions": [],
            "dua_cards": [build_dua_card("sleep_short_dua")],
            "ikhtilaf": "No",
            "conclusion": "For a simple bedtime routine, use the short dua below and, if you wish, recite Ayat al-Kursi.",
            "consult_scholar": "No",
            "language_detected": "English",
        }

    if route == "morning_starter":
        return {
            "response_mode": "curated",
            "direct_answer": "A verified morning supplication is shown below from the app's canonical source registry.",
            "quran_evidence": [],
            "hadith_evidence": [hadith_record_for_source("Bukhari|6306", "This is a verified morning supplication for forgiveness.")],
            "blocked_hadith": [],
            "scholarly_opinions": [],
            "dua_cards": [build_dua_card("morning_sayyidul_istighfar")],
            "ikhtilaf": "No",
            "conclusion": "This is a safe verified morning starter dua.",
            "consult_scholar": "No",
            "language_detected": "English",
        }

    if route == "before_eating":
        return {
            "response_mode": "curated",
            "direct_answer": "Say Bismillah before eating. If you forgot at the beginning, the verified alternate phrase is shown below the card.",
            "quran_evidence": [],
            "hadith_evidence": [hadith_record_for_source("Tirmidhi|1858", "This hadith teaches what to say before eating.")],
            "blocked_hadith": [],
            "scholarly_opinions": [],
            "dua_cards": [build_dua_card("before_eating_bismillah")],
            "ikhtilaf": "No",
            "conclusion": "Keep it simple: say Bismillah before eating.",
            "consult_scholar": "No",
            "language_detected": "English",
        }

    return None


def build_verified_result(model_result):
    dua_cards, quran_from_dua_ids = expand_dua_ids(model_result.get("dua_ids", []))
    quran_evidence = verify_quran_references(list(model_result.get("quran_references", [])) + quran_from_dua_ids)
    hadith_evidence, blocked_hadith = verify_hadith_references(model_result.get("hadith_references", []))

    return {
        "response_mode": "verified_references",
        "direct_answer": model_result.get("direct_answer", "").strip() or "No strong authentic evidence found",
        "quran_evidence": quran_evidence,
        "hadith_evidence": hadith_evidence,
        "blocked_hadith": blocked_hadith,
        "scholarly_opinions": model_result.get("scholarly_opinions", []),
        "dua_cards": dua_cards,
        "ikhtilaf": model_result.get("ikhtilaf", "No"),
        "conclusion": model_result.get("conclusion", "").strip(),
        "consult_scholar": model_result.get("consult_scholar", "No"),
        "language_detected": model_result.get("language_detected", "English"),
    }


def render_metric_row(result):
    cards = [
        ("Verified Qur'an Items", len(result.get("quran_evidence", []))),
        ("Verified Hadith Sources", len(result.get("hadith_evidence", []))),
        ("Blocked Unverified Hadiths", len(result.get("blocked_hadith", []))),
        ("Canonical Dua Cards", len(result.get("dua_cards", []))),
    ]
    html = "".join(
        f'<div class="metric-card"><div class="metric-value">{count}</div><div class="metric-label">{safe_html(label)}</div></div>'
        for label, count in cards
    )
    st.markdown(f'<div class="metric-row">{html}</div>', unsafe_allow_html=True)


def render_quran_block(item):
    title = f'<div class="meta-line" style="margin-bottom:6px;color:#a4e0bd;">{safe_html(item.get("title", ""))}</div>' if item.get("title") else ""
    st.markdown(
        f'<div class="quran-card">'
        f'<span class="verify-pill verify-ok">Live Qur&apos;an reference</span>'
        f'{title}'
        f'<div class="arabic-text">{safe_html(item.get("arabic", ""))}</div>'
        f'<div class="arabic-translation">{safe_html(item.get("translation", ""))}</div>'
        f'<div class="meta-line"><strong>Reference:</strong> {safe_html(item.get("reference", ""))}</div>'
        f'<div class="meta-line">{safe_html(item.get("explanation", ""))}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_hadith_block(item):
    auth = item.get("authenticity", "")
    badge_class = "badge-sahih" if auth == "Sahih" else "badge-hasan" if auth == "Hasan" else "badge-weak"
    narrator = f'<div class="meta-line"><strong>Narrator:</strong> {safe_html(item.get("narrator", ""))}</div>' if item.get("narrator") else ""
    why = f'<div class="meta-line"><strong>Why relevant:</strong> {safe_html(item.get("why_relevant", ""))}</div>' if item.get("why_relevant") else ""
    link = html_link(item.get("source_label", ""), item.get("source_url", ""))

    st.markdown(
        f'<div class="hadith-card">'
        f'<span class="verify-pill verify-ok">Canonical source match</span><br><br>'
        f'<div><strong>{link}</strong> <span class="{badge_class}">{safe_html(auth)}</span></div>'
        f'<div class="arabic-text">{safe_html(item.get("arabic", ""))}</div>'
        f'<div style="line-height:1.85;">{safe_html(item.get("text", ""))}</div>'
        f'{narrator}'
        f'{why}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_blocked_hadith_block(item):
    auth = item.get("authenticity", "")
    badge_html = ""
    if auth:
        badge_class = "badge-sahih" if auth == "Sahih" else "badge-hasan" if auth == "Hasan" else "badge-weak"
        badge_html = f' <span class="{badge_class}">{safe_html(auth)}</span>'

    why = f'<div class="meta-line"><strong>Why relevant:</strong> {safe_html(item.get("why_relevant", ""))}</div>' if item.get("why_relevant") else ""

    st.markdown(
        f'<div class="pending-card">'
        f'<span class="verify-pill verify-warn">Text hidden until canonical verification</span><br><br>'
        f'<div><strong>Suggested reference:</strong> {safe_html(item.get("collection_full", ""))} - {safe_html(item.get("reference_label", ""))}{badge_html}</div>'
        f'<div class="meta-line">{safe_html(item.get("note", ""))}</div>'
        f'{why}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_dua_card(card):
    source_link = html_link(card.get("reference_label", ""), card.get("source_url", ""))
    alt_block = ""
    if card.get("alternate_arabic"):
        alt_block = (
            f'<div class="meta-line" style="margin-top:12px;"><strong>If forgotten at the beginning:</strong></div>'
            f'<div class="arabic-text" style="font-size:24px;">{safe_html(card.get("alternate_arabic", ""))}</div>'
            f'<div>{safe_html(card.get("alternate_transliteration", ""))}</div>'
            f'<div class="meta-line">{safe_html(card.get("alternate_meaning", ""))}</div>'
        )

    st.markdown(
        f'<div class="dua-card">'
        f'<span class="verify-pill verify-ok">Canonical dua card</span><br><br>'
        f'<div style="font-size:18px;font-weight:700;color:#f2d78f;">{safe_html(card.get("title", ""))}</div>'
        f'<div class="arabic-text">{safe_html(card.get("arabic", ""))}</div>'
        f'<div><strong style="color:#cfb2ff;">Transliteration:</strong><br>{safe_html(card.get("transliteration", ""))}</div>'
        f'<div style="margin-top:12px;"><strong style="color:#f2d78f;">Meaning:</strong><br>{safe_html(card.get("meaning", ""))}</div>'
        f'<div class="meta-line" style="margin-top:12px;"><strong>Verified source:</strong> {source_link}</div>'
        f'<div class="meta-line">{safe_html(card.get("note", ""))}</div>'
        f'{alt_block}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_registry_card(source_key, source):
    link = html_link(source["source_label"], source["source_url"])
    auth = source["authenticity"]
    badge_class = "badge-sahih" if auth == "Sahih" else "badge-hasan" if auth == "Hasan" else "badge-weak"
    alt_block = ""
    if source.get("alternate_arabic"):
        alt_block = (
            f'<div class="meta-line" style="margin-top:10px;"><strong>Alternate phrase in same source:</strong></div>'
            f'<div class="arabic-text" style="font-size:24px;">{safe_html(source.get("alternate_arabic", ""))}</div>'
        )

    st.markdown(
        f'<div class="source-card">'
        f'<div><strong>{link}</strong> <span class="{badge_class}">{safe_html(auth)}</span></div>'
        f'<div class="meta-line"><strong>Registry key:</strong> {safe_html(source_key)}</div>'
        f'<div class="meta-line"><strong>Narrator:</strong> {safe_html(source.get("narrator", ""))}</div>'
        f'<div class="arabic-text">{safe_html(source.get("invocation_arabic", ""))}</div>'
        f'<div><strong>Transliteration:</strong> {safe_html(source.get("transliteration", ""))}</div>'
        f'<div class="meta-line">{safe_html(source.get("meaning", ""))}</div>'
        f'{alt_block}'
        f'<div class="meta-line" style="margin-top:10px;">{safe_html(source.get("display_note", ""))}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_response(result):
    render_metric_row(result)

    if result.get("response_mode") == "curated":
        st.markdown(
            '<div class="info-box"><span class="verify-pill verify-ok">Curated verified mode</span> This answer came from the locked local registry and live Qur&apos;an references, not from model-written source text.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="info-box"><span class="verify-pill verify-info">Reference verification mode</span> The model suggested references, then the app verified Qur&apos;an items and filtered Hadith through the canonical registry.</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<div class="answer-card"><strong style="color:#f2d78f;">Direct Answer</strong><br><br>{safe_html(result.get("direct_answer", ""))}</div>',
        unsafe_allow_html=True,
    )

    if result.get("quran_evidence"):
        st.markdown('<div class="section-title">Verified Qur&apos;an Evidence</div>', unsafe_allow_html=True)
        for item in result["quran_evidence"]:
            render_quran_block(item)

    if result.get("hadith_evidence"):
        st.markdown('<div class="section-title">Verified Hadith Evidence</div>', unsafe_allow_html=True)
        for item in result["hadith_evidence"]:
            render_hadith_block(item)

    if result.get("blocked_hadith"):
        with st.expander(f"Suggested Hadith References Not Yet In Canonical Registry ({len(result['blocked_hadith'])})"):
            for item in result["blocked_hadith"]:
                render_blocked_hadith_block(item)

    if result.get("scholarly_opinions"):
        st.markdown('<div class="section-title">Scholarly View Summary</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="info-box">This section is an AI summary of recognized scholarly views. Verify detailed fatwa wording directly for personal rulings.</div>',
            unsafe_allow_html=True,
        )
        if result.get("ikhtilaf") == "Yes":
            st.markdown(
                '<div class="info-box">There is a difference of opinion among scholars on this matter.</div>',
                unsafe_allow_html=True,
            )
        for opinion in result["scholarly_opinions"]:
            st.markdown(
                f'<div class="scholar-card"><strong style="color:#f2d78f;">{safe_html(opinion.get("madhab", "General"))}:</strong> {safe_html(opinion.get("opinion", ""))}<br><div class="meta-line"><strong>Source label:</strong> {safe_html(opinion.get("source", ""))}</div></div>',
                unsafe_allow_html=True,
            )

    if result.get("dua_cards"):
        st.markdown('<div class="section-title">Verified Dua Cards</div>', unsafe_allow_html=True)
        for card in result["dua_cards"]:
            render_dua_card(card)

    if result.get("conclusion"):
        st.markdown('<div class="section-title">Conclusion</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="answer-card">{safe_html(result["conclusion"])}</div>', unsafe_allow_html=True)

    if result.get("consult_scholar") == "Yes":
        st.markdown(
            '<div class="warning-card">This matter may require a qualified Islamic scholar for a personal ruling. Please consult a trusted scholar before acting on the answer.</div>',
            unsafe_allow_html=True,
        )


validate_registries()

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

st.markdown("""
<div class="hero-shell">
    <div class="hero-bismillah">بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ</div>
    <div class="hero-title">Muslim AI</div>
    <div class="hero-subtitle">
        Evidence-first Islamic answers with locked canonical dua text,
        live Qur'an verification, and safe filtering for any Hadith not yet added to the canonical registry.
    </div>
    <div class="hero-badges">
        <span class="verify-pill verify-ok">Exact dua text exists in one registry only</span>
        <span class="verify-pill verify-ok">Qur'an text is fetched by reference</span>
        <span class="verify-pill verify-warn">Unverified Hadith wording stays hidden</span>
        <span class="verify-pill verify-info">CSS-only motion for safe Streamlit deployment</span>
    </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(
        f'<div class="panel"><div class="panel-title">Registry Lock</div><div class="small-note">Canonical source records: <strong>{len(CANONICAL_HADITH_SOURCES)}</strong><br>Canonical dua cards: <strong>{len(DUA_LIBRARY)}</strong><br><br>Future exact Arabic should be added only once inside the canonical registry. Startup validation will fail if duplicate raw text is typed outside it.</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="panel"><div class="panel-title">Verification Policy</div><div class="small-note">Common duas use curated verified cards. Qur&apos;an is always fetched by reference. Hadith wording appears only if its reference exists in the local canonical registry.</div></div>',
        unsafe_allow_html=True,
    )

    topics = [
        "dua to fall asleep",
        "give me a morning dua",
        "dua before eating",
        "what is the ruling on missing Fajr prayer?",
        "is music halal or haram?",
        "what is tawakkul in Islam?",
    ]
    st.markdown('<div class="panel"><div class="panel-title">Quick Topics</div></div>', unsafe_allow_html=True)
    for topic in topics:
        if st.button(topic, use_container_width=True, key=f"topic_{topic}"):
            st.session_state.quick_question = topic

    st.markdown(
        '<div class="panel"><div class="panel-title">Languages</div><div class="small-note">Ask in English, Urdu, Hindi, or Arabic.</div></div>',
        unsafe_allow_html=True,
    )

    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.messages = []
        st.session_state.quick_question = ""
        st.rerun()

tab1, tab2, tab3, tab4 = st.tabs([
    "AI Assistant",
    "Qur'an Reader",
    "Verified Dua Library",
    "Canonical Source Registry",
])

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

                    stored = json.dumps(final_result, ensure_ascii=False)
                    st.session_state.messages.append({"role": "assistant", "content": stored})

                    summary = final_result.get("direct_answer", "").strip()
                    if final_result.get("conclusion"):
                        summary = f"{summary} Conclusion: {final_result['conclusion']}".strip()

                    st.session_state.chat_history.append({
                        "user": user_input,
                        "assistant": summary or "No strong authentic evidence found",
                    })

                except Exception as exc:
                    error_msg = f"Error: {exc}. Please try again."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

with tab2:
    st.markdown('<div class="section-title">Qur&apos;an Reader</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="info-box">Arabic and English are fetched live from the Qur&apos;an API, so verses are not typed manually in the app.</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 2])

    with col1:
        surah_options = [f"{index + 1}. {name}" for index, name in enumerate(SURAH_NAMES)]
        selected_surah = st.selectbox("Select Surah", surah_options)
        surah_number = int(selected_surah.split(".")[0])

        st.markdown(
            f'<div class="info-box"><strong style="color:#f2d78f;">Selected:</strong> {safe_html(selected_surah)}</div>',
            unsafe_allow_html=True,
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
                    '<div class="info-box"><span class="verify-pill verify-ok">Live Qur&apos;an source loaded</span></div>',
                    unsafe_allow_html=True,
                )

                for i, ayah in enumerate(arabic_edition.get("ayahs", [])):
                    arabic = ayah.get("text", "")
                    english = english_ayahs[i].get("text", "") if i < len(english_ayahs) else ""
                    ayah_number = ayah.get("numberInSurah", i + 1)

                    st.markdown(
                        f'<div class="quran-ayah">'
                        f'<div class="meta-line"><strong>Ayah {ayah_number}</strong></div>'
                        f'<div class="arabic-text">{safe_html(arabic)} ﴿{ayah_number}﴾</div>'
                        f'<div class="arabic-translation">{safe_html(english)}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.error("Could not load the Surah right now. Please try again.")
        else:
            st.info("Select a Surah and click Load Surah.")

with tab3:
    st.markdown('<div class="section-title">Verified Dua Library</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="info-box">This library is intentionally small and locked. Exact Arabic appears only when a source is manually verified and added to the canonical registry.</div>',
        unsafe_allow_html=True,
    )

    selected_category = st.selectbox("Select Category", list(DUA_CATEGORIES.keys()))
    for item_id in DUA_CATEGORIES[selected_category]:
        item = DUA_LIBRARY[item_id]
        if item["type"] == "hadith_source":
            render_dua_card(build_dua_card(item_id))
        else:
            refs = verify_quran_references([quran_ref_from_library_item(item_id)])
            for ref in refs:
                render_quran_block(ref)

with tab4:
    st.markdown('<div class="section-title">Canonical Source Registry</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="info-box">These are the only local Hadith records allowed to display exact wording in the app. If a reference is not here, the app hides its text until you verify and add it here first.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="registry-card"><strong style="color:#f2d78f;">How future safety works</strong><div class="meta-line">1. Add one exact source record here.<br>2. Reference it from the dua library by source key only.<br>3. Let startup validation block duplicate raw text in other places.</div></div>',
        unsafe_allow_html=True,
    )

    for source_key in sorted(CANONICAL_HADITH_SOURCES.keys()):
        render_registry_card(source_key, CANONICAL_HADITH_SOURCES[source_key])
