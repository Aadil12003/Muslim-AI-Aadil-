import json
import os
import re
import time
from html import escape

import requests
import streamlit as st

# Page setup
st.set_page_config(page_title="Muslim AI by Aadil", layout="wide", initial_sidebar_state="expanded")

# Premium Dark & Gold Styling
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,400&family=Scheherazade+New:wght@400;700&display=swap');

/* ===== GLOBAL TYPOGRAPHY & BACKGROUND ===== */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0a0a0a !important;
    color: #e0e0e0 !important;
}

.stApp {
    background-color: #0a0a0a;
    background-image: radial-gradient(circle at 50% 0%, #1a1a1a 0%, #0a0a0a 70%);
}

/* ===== HEADINGS ===== */
h1, h2, h3, .serif-text {
    font-family: 'Playfair Display', serif;
    color: #D4AF37 !important; /* Premium Gold */
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* ===== CLEAN CARD CONTAINER ===== */
.premium-card {
    background-color: #121212;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 28px;
    margin-bottom: 24px;
    word-break: break-word;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.premium-card:hover {
    border-color: #D4AF37;
    transform: translateY(-2px);
}

/* ===== HERO ===== */
.hero {
    text-align: center;
    padding: 60px 20px 40px 20px;
    margin-bottom: 40px;
    border-bottom: 1px solid #2a2a2a;
    background: linear-gradient(180deg, rgba(212, 175, 55, 0.05) 0%, rgba(10, 10, 10, 0) 100%);
}
.bismillah {
    font-family: 'Scheherazade New', serif;
    font-size: 36px;
    color: #D4AF37;
    margin-bottom: 16px;
    text-shadow: 0 2px 10px rgba(212, 175, 55, 0.2);
}
.title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 8px;
    font-family: 'Playfair Display', serif;
    color: #ffffff;
}
.subtitle {
    font-size: 16px;
    color: #a0a0a0;
    font-weight: 300;
    letter-spacing: 1px;
}

/* ===== ARABIC TEXT ===== */
.arabic {
    font-family: 'Scheherazade New', serif;
    font-size: 34px;
    direction: rtl;
    text-align: right;
    margin-bottom: 16px;
    line-height: 1.8;
    color: #D4AF37;
}

/* ===== UI ELEMENTS ===== */
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 24px;
    color: #D4AF37;
    margin: 40px 0 20px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid #2a2a2a;
}
.info-box {
    background-color: rgba(212, 175, 55, 0.05);
    border-left: 3px solid #D4AF37;
    border-radius: 4px;
    padding: 16px 20px;
    font-size: 15px;
    margin-bottom: 24px;
    color: #cccccc;
}
.accent { color: #D4AF37 !important; font-weight: 600; }
.muted { color: #888888 !important; font-size: 0.9em; font-weight: 300; }
.source-link {
    color: #D4AF37;
    text-decoration: none;
    border-bottom: 1px dotted #D4AF37;
    transition: opacity 0.2s;
}
.source-link:hover { opacity: 0.7; }

/* ===== LABELS & BADGES ===== */
.pill-badge {
    font-size: 11px;
    border: 1px solid #D4AF37;
    color: #D4AF37;
    padding: 4px 10px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-left: 10px;
}

/* ===== SIDEBAR & INPUT ===== */
[data-testid="stSidebar"] {
    background-color: #0f0f0f !important;
    border-right: 1px solid #2a2a2a;
}
input, textarea {
    background-color: #1a1a1a !important;
    border: 1px solid #333 !important;
    color: #fff !important;
    border-radius: 8px !important;
}
input:focus, textarea:focus {
    border-color: #D4AF37 !important;
    box-shadow: 0 0 0 1px #D4AF37 !important;
}
.stButton > button {
    background-color: #1a1a1a;
    color: #D4AF37;
    border: 1px solid #D4AF37;
    border-radius: 8px;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    background-color: #D4AF37;
    color: #000;
}
.creator-footer {
    text-align: center;
    padding: 30px 10px;
    margin-top: auto;
    font-family: 'Playfair Display', serif;
    color: #D4AF37;
    border-top: 1px solid #2a2a2a;
    font-size: 18px;
    letter-spacing: 1px;
}
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

SYSTEM_PROMPT = """You are an Islamic AI Assistant. Respond only with authentic Quran, Sahih Hadith, and recognized classical scholarship (like Ibn Kathir).
- Do NOT fabricate references.
- If generating a story, provide a deep, comprehensive, multi-paragraph narrative detailing the motives and profound morals.
- Return ONLY valid JSON.
{
  "direct_answer": "concise answer or full story text",
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

# Data Sets
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
    "Quranic Rabbana Duas": [
        {"title": "For Good in This World and the Hereafter", "arabic": "رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً وَفِي الْآخِرَةِ حَسَنَةً وَقِنَا عَذَابَ النَّارِ", "transliteration": "Rabbana atina fid-dunya hasanatan wa fil 'akhirati hasanatan waqina 'adhaban-nar", "meaning": "Our Lord, give us in this world [that which is] good and in the Hereafter [that which is] good and protect us from the punishment of the Fire.", "reference": "Quran 2:201", "source_url": "https://quran.com/2/201"},
        {"title": "For Patience and Victory", "arabic": "رَبَّنَا أَفْرِغْ عَلَيْنَا صَبْرًا وَثَبِّتْ أَقْدَامَنَا وَانصُرْنَا عَلَى الْقَوْمِ الْكَافِرِينَ", "transliteration": "Rabbana afrigh 'alayna sabran wa thabbit aqdamana wansurna 'alal-qawmil-kafirin", "meaning": "Our Lord, pour upon us patience and plant firmly our feet and give us victory over the disbelieving people.", "reference": "Quran 2:250", "source_url": "https://quran.com/2/250"},
        {"title": "For Forgiveness and Avoiding Burden", "arabic": "رَبَّنَا لَا تُؤَاخِذْنَا إِن نَّسِينَا أَوْ أَخْطَأْنَا ۚ رَبَّنَا وَلَا تَحْمِلْ عَلَيْنَا إِصْرًا كَمَا حَمَلْتَهُ عَلَى الَّذِينَ مِن قَبْلِنَا", "transliteration": "Rabbana la tuakhidhna in nasina aw akhta'na. Rabbana wa la tahmil 'alayna isran kama hamaltahu 'alal-ladhina min qablina", "meaning": "Our Lord, do not impose blame upon us if we have forgotten or erred. Our Lord, and lay not upon us a burden like that which You laid upon those before us.", "reference": "Quran 2:286", "source_url": "https://quran.com/2/286"},
        {"title": "For Guidance of the Heart", "arabic": "رَبَّنَا لَا تُزِغْ قُلُوبَنَا بَعْدَ إِذْ هَدَيْتَنَا وَهَبْ لَنَا مِن لَّدُنكَ رَحْمَةً ۚ إِنَّكَ أَنتَ الْوَهَّابُ", "transliteration": "Rabbana la tuzigh quloobana ba'da idh hadaytana wa hab lana min ladunka rahmatan innaka antal-Wahhab", "meaning": "Our Lord, let not our hearts deviate after You have guided us and grant us from Yourself mercy. Indeed, You are the Bestower.", "reference": "Quran 3:8", "source_url": "https://quran.com/3/8"},
        {"title": "Seeking Forgiveness of Sins", "arabic": "رَبَّنَا إِنَّنَا آمَنَّا فَاغْفِرْ لَنَا ذُنُوبَنَا وَقِنَا عَذَابَ النَّارِ", "transliteration": "Rabbana innana amanna faghfir lana dhunubana waqina 'adhaban-nar", "meaning": "Our Lord, indeed we have believed, so forgive us our sins and protect us from the punishment of the Fire.", "reference": "Quran 3:16", "source_url": "https://quran.com/3/16"},
        {"title": "To Be Among the Witnesses of Truth", "arabic": "رَبَّنَا آمَنَّا بِمَا أَنزَلْتَ وَاتَّبَعْنَا الرَّسُولَ فَاكْتُبْنَا مَعَ الشَّاهِدِينَ", "transliteration": "Rabbana amanna bima anzalta wattaba'nar-rasula faktubna ma'ash-shahidin", "meaning": "Our Lord, we have believed in what You revealed and have followed the messenger, so register us among the witnesses.", "reference": "Quran 3:53", "source_url": "https://quran.com/3/53"},
        {"title": "For Forgiveness of Excesses", "arabic": "رَبَّنَا اغْفِرْ لَنَا ذُنُوبَنَا وَإِسْرَافَنَا فِي أَمْرِنَا وَثَبِّتْ أَقْدَامَنَا وَانصُرْنَا عَلَى الْقَوْمِ الْكَافِرِينَ", "transliteration": "Rabbana-ghfir lana dhunubana wa israfana fi amrina wa thabbit aqdamana wansurna 'alal-qawmil-kafirin", "meaning": "Our Lord, forgive us our sins and the excess in our affairs and plant firmly our feet and give us victory over the disbelieving people.", "reference": "Quran 3:147", "source_url": "https://quran.com/3/147"},
        {"title": "Contemplation of Creation", "arabic": "رَبَّنَا مَا خَلَقْتَ هَٰذَا بَاطِلًا سُبْحَانَكَ فَقِنَا عَذَابَ النَّارِ", "transliteration": "Rabbana ma khalaqta hadha batilan subhanaka faqina 'adhaban-nar", "meaning": "Our Lord, You did not create this aimlessly; exalted are You [above such a thing]; then protect us from the punishment of the Fire.", "reference": "Quran 3:191", "source_url": "https://quran.com/3/191"},
        {"title": "For Fulfilling Promises", "arabic": "رَبَّنَا وَآتِنَا مَا وَعَدتَّنَا عَلَىٰ رُسُلِكَ وَلَا تُخْزِنَا يَوْمَ الْقِيَامَةِ ۗ إِنَّكَ لَا تُخْلِفُ الْمِيعَادَ", "transliteration": "Rabbana wa atina ma wa'adtana 'ala rusulika wa la tukhzina yawmal-qiyamati innaka la tukhliful-mi'ad", "meaning": "Our Lord, and grant us what You promised us through Your messengers and do not disgrace us on the Day of Resurrection. Indeed, You do not fail in [Your] promise.", "reference": "Quran 3:194", "source_url": "https://quran.com/3/194"},
        {"title": "Dua of Adam and Hawa (Repentance)", "arabic": "رَبَّنَا ظَلَمْنَا أَنفُسَنَا وَإِن لَّمْ تَغْفِرْ لَنَا وَتَرْحَمْنَا لَنَكُونَنَّ مِنَ الْخَاسِرِينَ", "transliteration": "Rabbana zalamna anfusana wa in lam taghfir lana wa tarhamna lanakunanna minal-khasirin", "meaning": "Our Lord, we have wronged ourselves, and if You do not forgive us and have mercy upon us, we will surely be among the losers.", "reference": "Quran 7:23", "source_url": "https://quran.com/7/23"},
        {"title": "Protection from Wrongdoers", "arabic": "رَبَّنَا لَا تَجْعَلْنَا مَعَ الْقَوْمِ الظَّالِمِينَ", "transliteration": "Rabbana la taj'alna ma'al-qawmiz-zalimin", "meaning": "Our Lord, do not place us with the wrongdoing people.", "reference": "Quran 7:47", "source_url": "https://quran.com/7/47"},
        {"title": "Dua for Just Judgement", "arabic": "رَبَّنَا افْتَحْ بَيْنَنَا وَبَيْنَ قَوْمِنَا بِالْحَقِّ وَأَنتَ خَيْرُ الْفَاتِحِينَ", "transliteration": "Rabbana-ftah baynana wa bayna qawmina bil-haqqi wa anta khayrul-fatihin", "meaning": "Our Lord, decide between us and our people in truth, and You are the best of those who give decision.", "reference": "Quran 7:89", "source_url": "https://quran.com/7/89"},
        {"title": "For Reliance on Allah", "arabic": "رَبَّنَا عَلَيْكَ تَوَكَّلْنَا وَإِلَيْكَ أَنَبْنَا وَإِلَيْكَ الْمَصِيرُ", "transliteration": "Rabbana 'alayka tawakkalna wa ilayka anabna wa ilaykal-masir", "meaning": "Our Lord, upon You we have relied, and to You we have returned, and to You is the destination.", "reference": "Quran 60:4", "source_url": "https://quran.com/60/4"},
        {"title": "For Mercy and Right Guidance", "arabic": "رَبَّنَا آتِنَا مِن لَّدُنكَ رَحْمَةً وَهَيِّئْ لَنَا مِنْ أَمْرِنَا رَشَدًا", "transliteration": "Rabbana atina min ladunka rahmatan wa hayyi' lana min amrina rashada", "meaning": "Our Lord, grant us from Yourself mercy and prepare for us from our affair right guidance.", "reference": "Quran 18:10", "source_url": "https://quran.com/18/10"},
        {"title": "Protection from Hellfire", "arabic": "رَبَّنَا اصْرِفْ عَنَّا عَذَابَ جَهَنَّمَ ۖ إِنَّ عَذَابَهَا كَانَ غَرَامًا", "transliteration": "Rabbana-srif 'anna 'adhaba jahannama inna 'adhabaha kana gharama", "meaning": "Our Lord, avert from us the punishment of Hell. Indeed, its punishment is ever adhering.", "reference": "Quran 25:65", "source_url": "https://quran.com/25/65"},
        {"title": "For Righteous Spouses and Offspring", "arabic": "رَبَّنَا هَبْ لَنَا مِنْ أَزْوَاجِنَا وَذُرِّيَّاتِنَا قُرَّةَ أَعْيُنٍ وَاجْعَلْنَا لِلْمُتَّقِينَ إِمَامًا", "transliteration": "Rabbana hab lana min azwajina wa dhurriyyatina qurrata a'yunin waj'alna lil-muttaqina imama", "meaning": "Our Lord, grant us from among our wives and offspring comfort to our eyes and make us an example for the righteous.", "reference": "Quran 25:74", "source_url": "https://quran.com/25/74"},
        {"title": "For Perfecting Our Light", "arabic": "رَبَّنَا أَتْمِمْ لَنَا نُورَنَا وَاغْفِرْ لَنَا ۖ إِنَّكَ عَلَىٰ كُلِّ شَيْءٍ قَدِيرٌ", "transliteration": "Rabbana atmim lana nurana waghfir lana innaka 'ala kulli shay'in qadir", "meaning": "Our Lord, perfect for us our light and forgive us. Indeed, You are over all things competent.", "reference": "Quran 66:8", "source_url": "https://quran.com/66/8"}
    ],
    "Morning Adhkar": [
        {"title": "Sayyidul Istighfar", "arabic": "اللَّهُمَّ أَنْتَ رَبِّي لَا إِلَهَ إِلَّا أَنْتَ، خَلَقْتَنِي وَأَنَا عَبْدُكَ", "transliteration": "Allahumma anta rabbi la ilaha illa anta, khalaqtani wa ana abduk", "meaning": "O Allah, You are my Lord; none has the right to be worshipped except You. You created me and I am Your servant.", "reference": "Bukhari 6306", "source_url": "https://sunnah.com/bukhari:6306"}
    ],
    "Before Sleep": [
        {"title": "Before Sleeping", "arabic": "بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا", "transliteration": "Bismika Allahumma amootu wa ahya", "meaning": "In Your name, O Allah, I die and I live.", "reference": "Bukhari 6324", "source_url": "https://sunnah.com/bukhari:6324"},
        {"title": "Ayatul Kursi", "arabic": "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ", "transliteration": "Allahu la ilaha illa huwa al-hayyul-qayyum", "meaning": "Allah! None has the right to be worshipped but He, the Ever Living, the Sustainer of all.", "reference": "Quran 2:255", "source_url": "https://quran.com/2/255"}
    ]
}

HADITH_40 = [
    {"number": 1, "arabic": "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ، وَإِنَّمَا لِكُلِّ امْرِئٍ مَا نَوَى", "text": "Actions are judged by intentions, and everyone will get what they intended.", "source": "Sahih al-Bukhari 1, Sahih Muslim 1907"},
    {"number": 2, "arabic": "بُنِيَ الإِسْلاَمُ عَلَى خَمْسٍ", "text": "Islam is built on five pillars...", "source": "Sahih al-Bukhari 8, Sahih Muslim 16"},
    {"number": 3, "arabic": "مَنْ أَحْدَثَ فِي أَمْرِنَا هَذَا مَا لَيْسَ فِيهِ فَهُوَ رَدٌّ", "text": "Whoever introduces into this matter of ours that which is not of it, it is rejected.", "source": "Sahih al-Bukhari 2697, Sahih Muslim 1718"},
    {"number": 4, "arabic": "الْحَلاَلُ بَيِّنٌ وَالْحَرَامُ بَيِّنٌ", "text": "The lawful is clear and the unlawful is clear, and between them are doubtful matters.", "source": "Sahih al-Bukhari 52, Sahih Muslim 1599"},
    {"number": 5, "arabic": "الدِّينُ النَّصِيحَةُ", "text": "Religion is sincere advice.", "source": "Sahih Muslim 55"},
    {"number": 6, "arabic": "دَعْ مَا يَرِيبُكَ إِلَى مَا لاَ يَرِيبُكَ", "text": "Leave that which makes you doubt for that which does not make you doubt.", "source": "Jami` at-Tirmidhi 2518 (Hasan Sahih)"},
    {"number": 7, "arabic": "الدُّنْيَا سِجْنُ الْمُؤْمِنِ وَجَنَّةُ الْكَافِرِ", "text": "The world is a prison for the believer and a paradise for the disbeliever.", "source": "Sahih Muslim 2956"},
    {"number": 8, "arabic": "لاَ يُؤْمِنُ أَحَدُكُمْ حَتَّى يُحِبَّ لأَخِيهِ مَا يُحِبُّ لِنَفْسِهِ", "text": "None of you truly believes until he loves for his brother what he loves for himself.", "source": "Sahih al-Bukhari 13, Sahih Muslim 45"},
    {"number": 9, "arabic": "مِنْ حُسْنِ إِسْلاَمِ الْمَرْءِ تَرْكُهُ مَا لاَ يَعْنِيهِ", "text": "From the excellence of a person's Islam is leaving what does not concern him.", "source": "Sunan Ibn Majah 3976, Tirmidhi (Hasan)"},
    {"number": 10, "arabic": "لاَ تَغْضَبْ", "text": "Do not become angry.", "source": "Sahih al-Bukhari 6116"},
    {"number": 11, "arabic": "قُلْ آمَنْتُ بِاللَّهِ ثُمَّ اسْتَقِمْ", "text": "Say, 'I believe in Allah,' and then remain steadfast.", "source": "Sahih Muslim 38"},
    {"number": 12, "arabic": "الْمُؤْمِنُ مِرْآةُ الْمُؤْمِنِ", "text": "The believer is the mirror of his brother.", "source": "Sunan Abi Dawud 4918 (Hasan)"},
    {"number": 13, "arabic": "وَالْكَلِمَةُ الطَّيِّبَةُ صَدَقَةٌ", "text": "A good word is charity.", "source": "Sahih al-Bukhari 2989, Sahih Muslim 1009"},
    {"number": 14, "arabic": "الطُّهُورُ شَطْرُ الإِيمَانِ", "text": "Purity is half of faith.", "source": "Sahih Muslim 223"},
    {"number": 15, "arabic": "مَنْ كَانَ يُؤْمِنُ بِاللَّهِ وَالْيَوْمِ الآخِرِ فَلْيَقُلْ خَيْرًا أَوْ لِيَصْمُتْ", "text": "Whoever believes in Allah and the Last Day should speak good or remain silent.", "source": "Sahih al-Bukhari 6018, Sahih Muslim 47"},
    {"number": 16, "arabic": "مَنْ لاَ يَرْحَمُ لاَ يُرْحَمُ", "text": "Whoever is not merciful to people, Allah will not be merciful to him.", "source": "Sahih al-Bukhari 6013, Sahih Muslim 2318"},
    {"number": 17, "arabic": "الْحَيَاءُ لاَ يَأْتِي إِلاَّ بِخَيْرٍ", "text": "Modesty brings nothing but good.", "source": "Sahih al-Bukhari 6117, Sahih Muslim 37"},
    {"number": 18, "arabic": "لَيْسَ الشَّدِيدُ بِالصُّرْعَةِ، إِنَّمَا الشَّدِيدُ الَّذِي يَمْلِكُ نَفْسَهُ عِنْدَ الْغَضَبِ", "text": "The strong person is not the good wrestler. The strong person is the one who controls himself when angry.", "source": "Sahih al-Bukhari 6114, Sahih Muslim 2609"},
    {"number": 19, "arabic": "خَيْرُكُمْ خَيْرُكُمْ لأَهْلِهِ", "text": "The best of you are those who are best to their families.", "source": "Sunan Ibn Majah 1977 (Sahih)"},
    {"number": 20, "arabic": "الْمُسْلِمُ مَنْ سَلِمَ الْمُسْلِمُونَ مِنْ لِسَانِهِ وَيَدِهِ", "text": "A Muslim is the one from whose tongue and hand other Muslims are safe.", "source": "Sahih al-Bukhari 10, Sahih Muslim 40"},
    {"number": 21, "arabic": "الْيَدُ الْعُلْيَا خَيْرٌ مِنَ الْيَدِ السُّفْلَى", "text": "The upper hand (giving) is better than the lower hand (receiving).", "source": "Sahih al-Bukhari 1429, Sahih Muslim 1033"},
    {"number": 22, "arabic": "إِنَّ اللَّهَ لاَ يَنْظُرُ إِلَى صُوَرِكُمْ وَأَمْوَالِكُمْ، وَلَكِنْ يَنْظُرُ إِلَى قُلُوبِكُمْ وَأَعْمَالِكُمْ", "text": "Allah does not look at your forms or your wealth, but He looks at your hearts and your deeds.", "source": "Sahih Muslim 2564"},
    {"number": 23, "arabic": "مَنْ لَمْ يَشْكُرِ النَّاسَ لَمْ يَشْكُرِ اللَّهَ", "text": "Whoever does not thank people has not thanked Allah.", "source": "Sunan Abi Dawud 4811 (Sahih)"},
    {"number": 24, "arabic": "يَسِّرُوا وَلاَ تُعَسِّرُوا", "text": "Make things easy and do not make them difficult.", "source": "Sahih al-Bukhari 69, Sahih Muslim 1732"},
    {"number": 25, "arabic": "لَيْسَ مِنَّا مَنْ لَمْ يَرْحَمْ صَغِيرَنَا وَيُوَقِّرْ كَبِيرَنَا", "text": "He is not of us who does not show mercy to our young ones and respect our old ones.", "source": "Jami` at-Tirmidhi 1919 (Sahih)"},
    {"number": 26, "arabic": "مَنْ غَشَّنَا فَلَيْسَ مِنَّا", "text": "Whoever cheats us is not one of us.", "source": "Sahih Muslim 101"},
    {"number": 27, "arabic": "الدَّالُّ عَلَى الْخَيْرِ كَفَاعِلِهِ", "text": "The one who guides to good is like the one who does it.", "source": "Jami` at-Tirmidhi 2670 (Sahih)"},
    {"number": 28, "arabic": "لاَ ضَرَرَ وَلاَ ضِرَارَ", "text": "There should be neither harming nor reciprocating harm.", "source": "Sunan Ibn Majah 2340 (Hasan)"},
    {"number": 29, "arabic": "إِنَّ اللَّهَ طَيِّبٌ لاَ يَقْبَلُ إِلاَّ طَيِّبًا", "text": "Indeed Allah is pure and He accepts only what is pure.", "source": "Sahih Muslim 1015"},
    {"number": 30, "arabic": "كُلُّ مَعْرُوفٍ صَدَقَةٌ", "text": "Every act of goodness is charity.", "source": "Sahih al-Bukhari 6021, Sahih Muslim 1005"},
    {"number": 31, "arabic": "تَهَادَوْا تَحَابُّوا", "text": "Exchange gifts, as that will lead to increasing your love to one another.", "source": "Al-Adab Al-Mufrad 594 (Hasan)"},
    {"number": 32, "arabic": "مَنْ سَلَكَ طَرِيقًا يَلْتَمِسُ فِيهِ عِلْمًا سَهَّلَ اللَّهُ لَهُ بِهِ طَرِيقًا إِلَى الْجَنَّةِ", "text": "Whoever treads a path seeking knowledge, Allah makes easy for him a path to Paradise.", "source": "Sahih Muslim 2699"},
    {"number": 33, "arabic": "خَيْرُكُمْ مَنْ تَعَلَّمَ الْقُرْآنَ وَعَلَّمَهُ", "text": "The best among you are those who learn the Qur'an and teach it.", "source": "Sahih al-Bukhari 5027"},
    {"number": 34, "arabic": "أَحَبُّ الأَعْمَالِ إِلَى اللَّهِ تَعَالَى أَدْوَمُهَا وَإِنْ قَلَّ", "text": "The most beloved of deeds to Allah are those that are most consistent, even if it is small.", "source": "Sahih al-Bukhari 6464, Sahih Muslim 783"},
    {"number": 35, "arabic": "اتَّقِ اللَّهَ حَيْثُمَا كُنْتَ", "text": "Fear Allah wherever you are.", "source": "Jami` at-Tirmidhi 1987 (Hasan)"},
    {"number": 36, "arabic": "احْفَظِ اللَّهَ يَحْفَظْكَ", "text": "Be mindful of Allah and He will protect you.", "source": "Jami` at-Tirmidhi 2516 (Hasan Sahih)"},
    {"number": 37, "arabic": "إِذَا سَأَلْتَ فَاسْأَلِ اللَّهَ", "text": "If you ask, ask of Allah; if you seek help, seek help from Allah.", "source": "Jami` at-Tirmidhi 2516 (Hasan Sahih)"},
    {"number": 38, "arabic": "الْبِرُّ حُسْنُ الْخُلُقِ", "text": "Righteousness is good character.", "source": "Sahih Muslim 2553"},
    {"number": 39, "arabic": "الصَّلاَةُ نُورٌ، وَالصَّدَقَةُ بُرْهَانٌ، وَالصَّبْرُ ضِيَاءٌ", "text": "Prayer is light, charity is a proof, and patience is illumination.", "source": "Sahih Muslim 223"},
    {"number": 40, "arabic": "مَنْ حَسُنَ إِسْلاَمُهُ تَرَكَ مَا لاَ يَعْنِيهِ", "text": "Part of the perfection of a person's Islam is his leaving that which is of no concern to him.", "source": "Jami` at-Tirmidhi 2317 (Hasan)"}
]

DYNAMIC_PROPHETS = [
    "Prophet Adam (as)", "Prophet Nuh (as)", "Prophet Ibrahim (as)", 
    "Prophet Yusuf (as)", "Prophet Musa (as)", "Prophet Dawud (as)", 
    "Prophet Sulaiman (as)", "Prophet Yunus (as)", "Prophet Isa (as)", 
    "Prophet Muhammad (ﷺ)"
]

DYNAMIC_STORIES = [
    "People of the Cave (Ashab al-Kahf)",
    "The Story of Musa and Al-Khidr",
    "The Men of the Elephant (Ashab al-Fil)",
    "The Story of Qarun (Korah)",
    "The Believer of Pharaoh's Court"
]

# State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "loaded_surah_number" not in st.session_state:
    st.session_state.loaded_surah_number = None

# Helpers
def safe_html(value):
    return escape("" if value is None else str(value))

def source_link(label, url):
    safe_label = safe_html(label)
    if url:
        if not str(url).startswith(('http://', 'https://')): url = '#'
        return f'<a class="source-link" href="{escape(url, quote=True)}" target="_blank">{safe_label}</a>'
    return safe_label

def contains_any(text, terms):
    return any(term in text for term in terms)

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
    def is_yes(val):
        if isinstance(val, bool): return val
        return str(val).strip().lower() == "yes"

    return {
        "direct_answer": str(result.get("direct_answer", "")).strip(),
        "quran_evidence": result.get("quran_evidence", []) if isinstance(result.get("quran_evidence", []), list) else [],
        "hadith_evidence": result.get("hadith_evidence", []) if isinstance(result.get("hadith_evidence", []), list) else [],
        "scholarly_opinions": result.get("scholarly_opinions", []) if isinstance(result.get("scholarly_opinions", []), list) else [],
        "dua": result.get("dua", {}) if isinstance(result.get("dua", {}), dict) else {},
        "duas": result.get("duas", []) if isinstance(result.get("duas", []), list) else [],
        "ikhtilaf": "Yes" if is_yes(result.get("ikhtilaf")) else "No",
        "conclusion": str(result.get("conclusion", "")).strip(),
        "consult_scholar": "Yes" if is_yes(result.get("consult_scholar")) else "No",
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

    for attempt in range(3):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=45)
            response.raise_for_status()
            data = response.json()
            if "choices" not in data:
                raise RuntimeError(f"API error: {json.dumps(data)[:400]}")
            return data["choices"][0]["message"]["content"]
        except Exception as exc:
            if attempt < 2: time.sleep(2 ** attempt)
            else: raise exc

def parse_response(raw):
    try:
        cleaned = re.sub(r"```json|```", "", raw).strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start != -1 and end > start:
            cleaned = cleaned[start:end]
        return normalize_result(json.loads(cleaned))
    except Exception:
        return normalize_result({"direct_answer": raw})

@st.cache_data(ttl=3600)
def fetch_quran_surah(surah_number):
    try:
        response = requests.get(f"https://api.alquran.cloud/v1/surah/{surah_number}/editions/quran-uthmani,en.asad", timeout=15)
        response.raise_for_status()
        data = response.json()
        return data["data"] if data.get("status") == "OK" else None
    except Exception: return None

def render_response(result):
    result = normalize_result(result)

    if result["source_notice"]:
        st.markdown(f'<div class="info-box">{safe_html(result["source_notice"])}</div>', unsafe_allow_html=True)

    formatted_answer = safe_html(result["direct_answer"]).replace('\n', '<br>')
    st.markdown(f'<div class="premium-card"><strong class="accent" style="font-family:\'Playfair Display\',serif; font-size:20px;">Answer</strong><br><br><span style="line-height:1.7; font-size:16px;">{formatted_answer}</span></div>', unsafe_allow_html=True)

    if result["quran_evidence"]:
        st.markdown('<div class="section-title">Quranic Evidence</div>', unsafe_allow_html=True)
        for verse in result["quran_evidence"]:
            st.markdown(
                f'<div class="premium-card"><div class="arabic">{safe_html(verse.get("arabic", ""))}</div>'
                f'<div style="font-size:16px; line-height:1.6; margin-bottom:12px;">{safe_html(verse.get("translation", ""))}</div>'
                f'<strong class="accent">{safe_html(verse.get("reference", ""))}</strong>'
                f'<br><span class="muted">{safe_html(verse.get("explanation", ""))}</span></div>',
                unsafe_allow_html=True,
            )

    if result["hadith_evidence"]:
        st.markdown('<div class="section-title">Hadith Evidence</div>', unsafe_allow_html=True)
        for h in result["hadith_evidence"]:
            auth = h.get("authenticity", "Sahih")
            arabic_html = f'<div class="arabic">{safe_html(h.get("arabic", ""))}</div>' if h.get("arabic") else ""
            note_html = f'<br><br><span class="muted">{safe_html(h.get("note", ""))}</span>' if h.get("note") else ""
            st.markdown(
                f'<div class="premium-card">{arabic_html}<div style="font-size:16px; line-height:1.6;">{safe_html(h.get("text", ""))}</div>'
                f'<br><span class="muted">Source: {safe_html(h.get("source", ""))}</span> '
                f'<span class="pill-badge">{safe_html(auth)}</span>{note_html}</div>',
                unsafe_allow_html=True,
            )

    if result["scholarly_opinions"]:
        st.markdown('<div class="section-title">Scholarly Viewpoints</div>', unsafe_allow_html=True)
        if result["ikhtilaf"] == "Yes":
            st.markdown('<div class="info-box">There is a recognized difference of opinion (Ikhtilaf) among classical scholars on this issue.</div>', unsafe_allow_html=True)
        for opinion in result["scholarly_opinions"]:
            st.markdown(
                f'<div class="premium-card"><strong class="accent">{safe_html(opinion.get("madhab", ""))}:</strong> '
                f'<span style="line-height:1.6;">{safe_html(opinion.get("opinion", ""))}</span><br><br><span class="muted">Source: {safe_html(opinion.get("source", ""))}</span></div>',
                unsafe_allow_html=True,
            )

    duas = result["duas"] or ([result["dua"]] if result.get("dua", {}).get("arabic") else [])
    if duas:
        st.markdown('<div class="section-title">Supplication (Dua)</div>', unsafe_allow_html=True)
        for dua in duas:
            st.markdown(
                f'<div class="premium-card"><strong class="accent" style="font-size: 1.2em; font-family:\'Playfair Display\',serif;">{safe_html(dua.get("title", ""))}</strong>'
                f'<div class="arabic" style="margin-top:16px;">{safe_html(dua.get("arabic", ""))}</div>'
                f'<strong class="accent" style="font-size:14px;">Transliteration</strong><br><span style="color:#cccccc; line-height:1.6;">{safe_html(dua.get("transliteration", ""))}</span>'
                f'<br><br><strong class="accent" style="font-size:14px;">Meaning</strong><br><span style="line-height:1.6;">{safe_html(dua.get("meaning", ""))}</span>'
                f'<br><br><span class="muted">Reference: {source_link(dua.get("reference", ""), dua.get("source_url", ""))}</span></div>',
                unsafe_allow_html=True,
            )

    if result["conclusion"]:
        st.markdown('<div class="section-title">Conclusion</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="premium-card" style="line-height:1.6;">{safe_html(result["conclusion"])}</div>', unsafe_allow_html=True)

    if result["consult_scholar"] == "Yes":
        st.markdown('<div style="background-color:rgba(212, 175, 55, 0.1); border-left:3px solid #D4AF37; padding:16px; color:#D4AF37; margin-bottom:20px; border-radius:4px;"><strong>Note:</strong> This matter is nuanced or sensitive. Please consult a qualified local scholar for a definitive personal fatwa.</div>', unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# UI Layout
# --------------------------------------------------------------------------- #
st.markdown(
    '<div class="hero"><div class="bismillah">بِسْمِ اللَّهِ الرَّحْمٰنِ الرَّحِيمِ</div>'
    '<div class="title">Muslim AI</div>'
    '<div class="subtitle">Authentic Islamic Knowledge grounded in Quran, Sahih Hadith, and Classical Scholarship</div></div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown('<div style="text-align:center; padding:20px 0;"><h2 style="color:#D4AF37; font-family:\'Playfair Display\',serif; margin-bottom:5px;">Muslim AI</h2><div style="color:#888; font-size:14px; letter-spacing:1px; text-transform:uppercase;">Knowledge & Reflection</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.messages = []
        st.rerun()
        
    st.markdown('<div class="creator-footer">Created by Aadil Rather</div>', unsafe_allow_html=True)


tab1, tab2, tab3, tab4, tab5 = st.tabs(["AI Assistant", "Quran Reader", "Dua Collection", "Deep Stories (AI)", "The Prophets (AI)"])

with tab1:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                try: render_response(json.loads(msg["content"]))
                except Exception: st.markdown(msg["content"])
            else:
                st.markdown(f'<div style="font-size:16px; line-height:1.5;">{msg["content"]}</div>', unsafe_allow_html=True)

    user_input = st.chat_input("Ask your Islamic question (English, Urdu, or Arabic)...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(f'<div style="font-size:16px; line-height:1.5;">{user_input}</div>', unsafe_allow_html=True)
        with st.chat_message("assistant"):
            with st.spinner("Consulting Quran and Hadith..."):
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
                    st.error("There was an issue processing your request. Please check your API key or connection.")

with tab2:
    st.markdown('<div class="section-title" style="margin-top:0;">The Holy Quran — Reader</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        surah_options = [f"{i + 1}. {name}" for i, name in enumerate(SURAH_NAMES)]
        selected_surah = st.selectbox("Select Surah", surah_options)
        surah_number = int(selected_surah.split(".")[0]) if selected_surah else None
        if st.button("Read Surah", type="primary", use_container_width=True):
            st.session_state.loaded_surah_number = surah_number
    with col2:
        if st.session_state.loaded_surah_number:
            surah_data = fetch_quran_surah(st.session_state.loaded_surah_number)
            if surah_data and len(surah_data) >= 2:
                arabic_edition, english_edition = surah_data[0], surah_data[1]
                english_ayahs = english_edition.get("ayahs", [])
                st.markdown(
                    f'<div style="font-family:\'Scheherazade New\',serif; font-size:40px; text-align:center; color:#D4AF37; direction:rtl; margin:20px 0 40px 0; text-shadow: 0 2px 10px rgba(212, 175, 55, 0.1);">'
                    f'{safe_html(arabic_edition.get("name", ""))}</div>',
                    unsafe_allow_html=True,
                )
                for i, ayah in enumerate(arabic_edition.get("ayahs", [])):
                    english = english_ayahs[i].get("text", "") if i < len(english_ayahs) else ""
                    st.markdown(
                        f'<div class="premium-card"><div class="muted" style="margin-bottom:12px; font-weight:600; color:#D4AF37 !important;">AYAH {ayah.get("numberInSurah", i + 1)}</div>'
                        f'<div class="arabic">{safe_html(ayah.get("text", ""))}</div>'
                        f'<div style="font-size:16px; line-height:1.7; color:#cccccc;">{safe_html(english)}</div></div>',
                        unsafe_allow_html=True,
                    )
        else:
            st.info("Select a Surah from the dropdown to begin reading.")

with tab3:
    st.markdown('<div class="section-title" style="margin-top:0;">Fortress of the Muslim (Dua)</div>', unsafe_allow_html=True)
    selected_category = st.selectbox("Select Collection", list(DUA_CATEGORIES.keys()))
    for dua in DUA_CATEGORIES.get(selected_category, []):
        st.markdown(
            f'<div class="premium-card"><h3 style="margin-top:0; color:#D4AF37; font-family:\'Playfair Display\',serif;">{safe_html(dua["title"])}</h3>'
            f'<div class="arabic" style="margin: 20px 0;">{safe_html(dua["arabic"])}</div>'
            f'<strong class="accent" style="font-size:14px; text-transform:uppercase;">Transliteration</strong><br><span style="color:#bbbbbb; line-height:1.6; display:inline-block; margin-bottom:16px;">{safe_html(dua["transliteration"])}</span><br>'
            f'<strong class="accent" style="font-size:14px; text-transform:uppercase;">Meaning</strong><br><span style="font-size:16px; line-height:1.6; color:#eeeeee;">{safe_html(dua["meaning"])}</span>'
            f'<div style="margin-top:20px; border-top:1px solid #2a2a2a; padding-top:12px;"><span class="muted">Reference: {source_link(dua["reference"], dua.get("source_url", ""))}</span></div></div>',
            unsafe_allow_html=True,
        )

with tab4:
    st.markdown('<div class="section-title" style="margin-top:0;">Dynamic Tafseer Stories</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Select a story. The AI will generate a comprehensive, authentic narrative based on classical Tafseer.</div>', unsafe_allow_html=True)
    
    selected_story = st.selectbox("Select an Event", DYNAMIC_STORIES)
    if st.button("Generate Full Authentic Story", key="gen_story"):
        with st.spinner(f"Extracting authentic Tafseer for {selected_story}..."):
            prompt = f"Provide a complete, multi-paragraph, highly detailed story of '{selected_story}'. Base it strictly on Quran and authentic Tafseer. Clearly detail the motives and the moral lessons."
            raw = call_api(prompt, [])
            result = parse_response(raw)
            render_response(result)

with tab5:
    st.markdown('<div class="section-title" style="margin-top:0;">Lives of the Prophets</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Select a Prophet. The AI will generate their full life profile based on Quranic texts and authentic Sunnah.</div>', unsafe_allow_html=True)
    
    selected_prophet = st.selectbox("Select a Prophet", DYNAMIC_PROPHETS)
    if st.button("Generate Comprehensive Life Profile", key="gen_prophet"):
        with st.spinner(f"Compiling authentic biography for {selected_prophet}..."):
            prompt = f"Provide a comprehensive, highly detailed life story of {selected_prophet}. Base it strictly on the Quran and authentic Ahadith/Tafseer. Outline their prophetic mission, their major trials, and their moral legacy."
            raw = call_api(prompt, [])
            result = parse_response(raw)
            render_response(result)
