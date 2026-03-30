import os
import json
import re
from html import escape

import requests
import streamlit as st

st.set_page_config(
    page_title="Muslim AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Scheherazade+New:wght@400;700&display=swap');

:root {
    --bg-1: #071019;
    --bg-2: #0c1d2b;
    --bg-3: #14293d;
    --gold: #d8b55a;
    --gold-soft: rgba(216, 181, 90, 0.18);
    --emerald: #39b97a;
    --emerald-soft: rgba(57, 185, 122, 0.18);
    --sky: #57a9ff;
    --sky-soft: rgba(87, 169, 255, 0.18);
    --warn: #f0ad4e;
    --warn-soft: rgba(240, 173, 78, 0.18);
    --danger: #d9665b;
    --text: #edf4fb;
    --muted: #b6c7d8;
    --card: rgba(13, 28, 42, 0.88);
    --card-2: rgba(16, 35, 52, 0.92);
    --line: rgba(216, 181, 90, 0.24);
    --shadow: 0 12px 38px rgba(0, 0, 0, 0.28);
}

html, body, .stApp {
    background:
        radial-gradient(circle at 12% 10%, rgba(216, 181, 90, 0.10), transparent 22%),
        radial-gradient(circle at 88% 14%, rgba(87, 169, 255, 0.08), transparent 18%),
        linear-gradient(145deg, var(--bg-1) 0%, var(--bg-2) 45%, var(--bg-3) 100%);
    color: var(--text);
}

@keyframes fadeRise {
    from { opacity: 0; transform: translateY(14px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes floatGlow {
    0% { transform: translateY(0px); box-shadow: 0 0 0 rgba(216,181,90,0); }
    50% { transform: translateY(-3px); box-shadow: 0 10px 26px rgba(216,181,90,0.08); }
    100% { transform: translateY(0px); box-shadow: 0 0 0 rgba(216,181,90,0); }
}

@keyframes shimmer {
    0% { background-position: -220px 0; }
    100% { background-position: 220px 0; }
}

.hero-shell {
    animation: fadeRise 0.55s ease both;
    position: relative;
    overflow: hidden;
    background:
        linear-gradient(135deg, rgba(15, 31, 47, 0.96), rgba(10, 23, 35, 0.96)),
        radial-gradient(circle at top right, rgba(216,181,90,0.08), transparent 32%);
    border: 1px solid var(--line);
    border-radius: 22px;
    padding: 20px 22px;
    margin: 8px 0 18px 0;
    box-shadow: var(--shadow);
}

.hero-shell::before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.045), transparent);
    background-size: 220px 100%;
    animation: shimmer 5.2s linear infinite;
    pointer-events: none;
}

.hero-bismillah {
    font-family: 'Scheherazade New', serif;
    font-size: 40px;
    color: #f0d589;
    text-align: center;
    direction: rtl;
    line-height: 1.7;
}

.hero-title {
    font-family: 'Amiri', serif;
    text-align: center;
    font-size: 44px;
    color: var(--gold);
    margin-top: 6px;
    margin-bottom: 4px;
    letter-spacing: 0.4px;
}

.hero-subtitle {
    text-align: center;
    color: var(--muted);
    font-size: 15px;
    margin-bottom: 14px;
}

.pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
}

.pill {
    display: inline-block;
    padding: 6px 11px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.15px;
    animation: floatGlow 4s ease-in-out infinite;
}

.pill.ok {
    background: var(--emerald-soft);
    color: #aef0cb;
    border: 1px solid rgba(57,185,122,0.35);
}

.pill.info {
    background: var(--sky-soft);
    color: #bfdeff;
    border: 1px solid rgba(87,169,255,0.34);
}

.pill.warn {
    background: var(--warn-soft);
    color: #ffe0ab;
    border: 1px solid rgba(240,173,78,0.34);
}

.panel, .answer-card, .quran-card, .hadith-card, .blocked-card, .scholar-card, .dua-card, .reader-card, .warning-card {
    animation: fadeRise 0.42s ease both;
    box-shadow: var(--shadow);
}

.panel {
    background: linear-gradient(135deg, rgba(14, 27, 40, 0.94), rgba(11, 21, 32, 0.94));
    border: 1px solid rgba(216,181,90,0.16);
    border-radius: 16px;
    padding: 14px;
    color: var(--text);
    margin-bottom: 14px;
}

.panel-title {
    color: var(--gold);
    font-weight: 700;
    margin-bottom: 8px;
}

.panel-note {
    color: var(--muted);
    font-size: 12px;
    line-height: 1.6;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
    margin: 10px 0 14px 0;
}

.metric-card {
    background: linear-gradient(135deg, rgba(16, 33, 48, 0.95), rgba(12, 25, 37, 0.95));
    border: 1px solid rgba(216,181,90,0.12);
    border-radius: 14px;
    padding: 12px;
}

.metric-value {
    font-size: 24px;
    font-weight: 700;
    color: var(--gold);
}

.metric-label {
    font-size: 12px;
    color: var(--muted);
    line-height: 1.45;
}

.section-title {
    font-size: 20px;
    font-weight: 700;
    color: var(--gold);
    margin: 18px 0 10px 0;
    padding-bottom: 5px;
    border-bottom: 1px solid rgba(216,181,90,0.24);
}

.answer-card {
    background: linear-gradient(135deg, rgba(18, 38, 57, 0.96), rgba(24, 49, 73, 0.96));
    border-left: 4px solid var(--gold);
    border-radius: 16px;
    padding: 18px;
    color: var(--text);
    line-height: 1.85;
    margin: 12px 0;
}

.quran-card {
    background: linear-gradient(135deg, rgba(13, 38, 27, 0.96), rgba(18, 54, 37, 0.96));
    border-left: 4px solid var(--emerald);
    border-radius: 16px;
    padding: 18px;
    color: var(--text);
    margin: 10px 0;
    border: 1px solid rgba(57,185,122,0.22);
}

.hadith-card {
    background: linear-gradient(135deg, rgba(14, 31, 47, 0.96), rgba(18, 42, 63, 0.96));
    border-left: 4px solid var(--sky);
    border-radius: 16px;
    padding: 18px;
    color: var(--text);
    margin: 10px 0;
    border: 1px solid rgba(87,169,255,0.18);
}

.blocked-card {
    background: linear-gradient(135deg, rgba(45, 33, 12, 0.96), rgba(58, 40, 12, 0.96));
    border-left: 4px solid var(--warn);
    border-radius: 16px;
    padding: 18px;
    color: #fff0cf;
    margin: 10px 0;
    border: 1px solid rgba(240,173,78,0.22);
}

.scholar-card {
    background: linear-gradient(135deg, rgba(38, 24, 11, 0.96), rgba(53, 34, 16, 0.96));
    border-left: 4px solid var(--gold);
    border-radius: 16px;
    padding: 16px;
    color: var(--text);
    margin: 10px 0;
}

.dua-card {
    background: linear-gradient(135deg, rgba(27, 15, 43, 0.96), rgba(39, 21, 60, 0.96));
    border: 1px solid rgba(168, 122, 219, 0.26);
    border-radius: 18px;
    padding: 20px;
    color: var(--text);
    margin: 10px 0;
    text-align: center;
}

.reader-card {
    background: linear-gradient(135deg, rgba(14, 30, 21, 0.96), rgba(17, 41, 29, 0.96));
    border: 1px solid rgba(57,185,122,0.20);
    border-radius: 16px;
    padding: 18px;
    color: var(--text);
    margin: 8px 0;
}

.warning-card {
    background: linear-gradient(135deg, rgba(55, 17, 17, 0.96), rgba(68, 20, 20, 0.96));
    border-left: 4px solid var(--danger);
    border-radius: 16px;
    padding: 16px;
    color: #ffe0dd;
    margin: 12px 0;
}

.arabic-text {
    font-family: 'Scheherazade New', 'Amiri', serif;
    font-size: 30px;
    font-weight: 700;
    direction: rtl;
    text-align: right;
    color: #f0d589;
    line-height: 2.35;
    margin: 10px 0;
}

.translation-text {
    color: #cde0d1;
    font-style: italic;
    line-height: 1.8;
    margin-top: 8px;
}

.label-line {
    color: #d9e6f2;
    font-size: 13px;
    margin-top: 8px;
}

.badge-sahih, .badge-hasan, .badge-weak {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
}

.badge-sahih {
    background: #2ea76d;
    color: white;
}

.badge-hasan {
    background: #d7952e;
    color: white;
}

.badge-weak {
    background: #c25757;
    color: white;
}

.small-note {
    font-size: 12px;
    color: var(--muted);
    line-height: 1.65;
}

.center-note {
    text-align: center;
    color: var(--muted);
    font-size: 12px;
    margin-top: 6px;
}

@media (max-width: 900px) {
    .metric-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}
</style>
""",
    unsafe_allow_html=True,
)

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "meta/llama-4-maverick-17b-128e-instruct"
REQUEST_TIMEOUT = 45

CANONICAL_HADITH_TEXTS = {
    "Bukhari|6324": {
        "collection": "Bukhari",
        "collection_full": "Sahih al-Bukhari",
        "reference": "6324",
        "reference_label": "Bukhari 6324",
        "source_label": "Sahih al-Bukhari 6324",
        "source_url": "https://sunnah.com/bukhari:6324",
        "authenticity": "Sahih",
        "topic": "Before Sleep",
        "narrator": "Hudhayfah (RA)",
        "arabic": "بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا",
        "transliteration": "Bismika Allahumma amutu wa ahya",
        "meaning": "In Your name, O Allah, I die and I live.",
        "hadith_text": "Whenever the Prophet intended to go to bed, he would say: 'Bismika Allahumma amutu wa ahya.'",
    },
    "Bukhari|6306": {
        "collection": "Bukhari",
        "collection_full": "Sahih al-Bukhari",
        "reference": "6306",
        "reference_label": "Bukhari 6306",
        "source_label": "Sahih al-Bukhari 6306",
        "source_url": "https://sunnah.com/bukhari:6306",
        "authenticity": "Sahih",
        "topic": "Forgiveness",
        "narrator": "Shaddad ibn Aws (RA)",
        "arabic": "اللَّهُمَّ أَنْتَ رَبِّي لَا إِلَهَ إِلَّا أَنْتَ، خَلَقْتَنِي وَأَنَا عَبْدُكَ، وَأَنَا عَلَى عَهْدِكَ وَوَعْدِكَ مَا اسْتَطَعْتُ، أَعُوذُ بِكَ مِنْ شَرِّ مَا صَنَعْتُ، أَبُوءُ لَكَ بِنِعْمَتِكَ عَلَيَّ، وَأَبُوءُ بِذَنْبِي، فَاغْفِرْ لِي، فَإِنَّهُ لَا يَغْفِرُ الذُّنُوبَ إِلَّا أَنْتَ",
        "transliteration": "Allahumma anta rabbi la ilaha illa anta, khalaqtani wa ana abduka, wa ana ala ahdika wa wadika mastata'tu, a'udhu bika min sharri ma sana'tu, abu'u laka bini'matika alayya, wa abu'u bidhanbi, faghfir li, fa inn
