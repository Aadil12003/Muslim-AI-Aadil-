import streamlit as st
import requests
import json
import re

st.set_page_config(page_title="Muslim AI", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Scheherazade+New:wght@400;700&display=swap');

body {background: linear-gradient(135deg, #0d1b2a 0%, #1a3a4a 100%);}
.main-header {
    font-size: 42px; font-weight: 700; color: #c9a84c;
    text-align: center; padding: 20px 0;
    text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
    font-family: 'Amiri', serif;
    border-bottom: 2px solid #c9a84c;
    margin-bottom: 10px;
}
.bismillah {
    font-family: 'Scheherazade New', serif;
    font-size: 36px; color: #c9a84c;
    text-align: center; direction: rtl;
    margin: 10px 0; line-height: 2;
}
.sub-header {font-size: 16px; color: #a0b0c0; text-align: center; margin-bottom: 20px;}
.answer-card {
    background: linear-gradient(135deg, #1a2a3a, #1e3448);
    border-left: 4px solid #c9a84c;
    padding: 20px; border-radius: 12px; margin: 15px 0;
    line-height: 1.8; color: #e0e0e0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
.quran-card {
    background: linear-gradient(135deg, #0d2a1a, #1a3a2a);
    border: 1px solid #27ae60;
    border-left: 4px solid #27ae60;
    padding: 20px; border-radius: 12px; margin: 10px 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
.hadith-card {
    background: linear-gradient(135deg, #0d1a2a, #1a2a3a);
    border: 1px solid #2980b9;
    border-left: 4px solid #2980b9;
    padding: 15px; border-radius: 12px; margin: 10px 0;
    color: #e0e0e0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
.scholar-card {
    background: linear-gradient(135deg, #2a1a0d, #3a2a1a);
    border-left: 4px solid #c9a84c;
    padding: 15px; border-radius: 12px; margin: 10px 0;
    color: #e0e0e0;
}
.warning-card {
    background: linear-gradient(135deg, #2a0d0d, #3a1a1a);
    border-left: 4px solid #e74c3c;
    padding: 15px; border-radius: 12px; margin: 10px 0;
    color: #e0e0e0;
}
.dua-card {
    background: linear-gradient(135deg, #1a0d2a, #2a1a3a);
    border: 2px solid #8e44ad;
    padding: 25px; border-radius: 12px;
    margin: 10px 0; text-align: center;
    color: #e0e0e0;
    box-shadow: 0 4px 20px rgba(142,68,173,0.3);
}
.arabic-text {
    font-family: 'Scheherazade New', 'Amiri', serif;
    font-size: 28px; font-weight: 700;
    color: #c9a84c; direction: rtl;
    text-align: right; margin: 10px 0;
    line-height: 2.5;
}
.arabic-translation {color: #a0c0a0; font-style: italic; margin: 8px 0;}
.quran-ref {color: #27ae60; font-weight: 700; font-size: 14px;}
.badge-sahih {background: #27ae60; color: white; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 700;}
.badge-hasan {background: #f39c12; color: white; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 700;}
.badge-weak {background: #e74c3c; color: white; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 700;}
.section-title {font-size: 20px; font-weight: 700; color: #c9a84c; margin: 20px 0 10px 0; border-bottom: 1px solid #c9a84c; padding-bottom: 5px;}
.quran-ayah {
    background: linear-gradient(135deg, #0d2a1a, #1a3a2a);
    border: 1px solid #27ae60;
    padding: 20px; border-radius: 12px;
    margin: 8px 0; color: #e0e0e0;
}
.dua-category-card {
    background: linear-gradient(135deg, #1a0d2a, #2a1a3a);
    border: 1px solid #8e44ad;
    padding: 20px; border-radius: 12px;
    margin: 8px 0; color: #e0e0e0;
    text-align: center;
}
.sidebar-topic {
    background: #1a2a3a; color: #c9a84c;
    border: 1px solid #c9a84c;
    padding: 8px; border-radius: 8px;
    margin: 4px 0; cursor: pointer;
}
.info-box {
    background: linear-gradient(135deg, #0d1a2a, #1a2a3a);
    border: 1px solid #c9a84c;
    padding: 15px; border-radius: 12px;
    color: #e0e0e0; margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

NVIDIA_API_KEY = st.secrets["NVIDIA_API_KEY"]
API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "meta/llama-4-maverick-17b-128e-instruct"

SYSTEM_PROMPT = """You are an advanced Islamic AI Assistant. You provide accurate, source-based, and respectful answers strictly grounded in authentic Islamic knowledge.

CORE RULES:
- Base answers ONLY on Quran, authentic Hadith, and recognized scholarly fatwas
- Never fabricate Quran verses or Hadith
- Never give rulings without evidence
- If unsure say: No strong authentic evidence found

SOURCES TO USE:
- Quran with Surah and Ayah numbers
- Sahih Bukhari, Sahih Muslim, Abu Dawood, Tirmidhi
- Scholarly fatwas from IslamQA and Dar al-Ifta

RESPONSE FORMAT - Always return valid JSON:
{
  "direct_answer": "clear concise answer",
  "quran_evidence": [
    {
      "arabic": "Arabic verse text",
      "translation": "English translation",
      "reference": "Surah Name Ayah number",
      "explanation": "brief explanation"
    }
  ],
  "hadith_evidence": [
    {
      "text": "hadith text in English",
      "arabic": "Arabic hadith if available",
      "source": "Book name and number",
      "authenticity": "Sahih or Hasan or Weak",
      "note": "any important note"
    }
  ],
  "scholarly_opinions": [
    {
      "madhab": "Hanafi or Shafii or Maliki or Hanbali or General",
      "opinion": "opinion text",
      "source": "fatwa source"
    }
  ],
  "dua": {
    "arabic": "Arabic dua text if applicable",
    "transliteration": "transliteration",
    "meaning": "English meaning",
    "reference": "source"
  },
  "ikhtilaf": "Yes or No - is there difference of opinion",
  "conclusion": "neutral summary",
  "consult_scholar": "Yes or No",
  "language_detected": "English or Urdu or Arabic or Hindi"
}

If question is in Urdu respond with Urdu in the answer fields but keep JSON keys in English.
If question is about dua fill the dua field completely.
Return ONLY valid JSON nothing else."""

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

DUA_CATEGORIES = {
    "Morning Adhkar": [
        {
            "title": "Morning Remembrance",
            "arabic": "أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ، لاَ إِلَهَ إِلاَّ اللهُ وَحْدَهُ لاَ شَرِيكَ لَهُ",
            "transliteration": "Asbahna wa asbahal mulku lillah, walhamdu lillah, la ilaha illallah wahdahu la sharika lah",
            "meaning": "We have entered the morning and the whole kingdom belongs to Allah. All praise is for Allah. None has the right to be worshipped except Allah, alone, without partner.",
            "reference": "Abu Dawood 4/317"
        },
        {
            "title": "Sayyidul Istighfar - Morning",
            "arabic": "اللَّهُمَّ أَنْتَ رَبِّي لاَ إِلَهَ إِلاَّ أَنْتَ، خَلَقْتَنِي وَأَنَا عَبْدُكَ",
            "transliteration": "Allahumma anta rabbi la ilaha illa anta, khalaqtani wa ana abduk",
            "meaning": "O Allah, You are my Lord. None has the right to be worshipped except You. You created me and I am Your servant.",
            "reference": "Bukhari 7/150"
        }
    ],
    "Evening Adhkar": [
        {
            "title": "Evening Remembrance",
            "arabic": "أَمْسَيْنَا وَأَمْسَى الْمُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ، لاَ إِلَهَ إِلاَّ اللهُ وَحْدَهُ لاَ شَرِيكَ لَهُ",
            "transliteration": "Amsayna wa amsal mulku lillah, walhamdu lillah, la ilaha illallah wahdahu la sharika lah",
            "meaning": "We have entered the evening and the whole kingdom belongs to Allah. All praise is for Allah. None has the right to be worshipped except Allah, alone, without partner.",
            "reference": "Abu Dawood 4/317"
        }
    ],
    "Before Sleep": [
        {
            "title": "Dua Before Sleeping",
            "arabic": "بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا",
            "transliteration": "Bismika Allahumma amootu wa ahya",
            "meaning": "In Your name O Allah, I die and I live.",
            "reference": "Bukhari 11/113"
        },
        {
            "title": "Ayatul Kursi Before Sleep",
            "arabic": "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ",
            "transliteration": "Allahu la ilaha illa huwal hayyul qayyum",
            "meaning": "Allah - there is no deity except Him, the Ever-Living, the Sustainer of existence.",
            "reference": "Quran 2:255 - Bukhari 6/325"
        }
    ],
    "Entering Home": [
        {
            "title": "Dua for Entering Home",
            "arabic": "اللَّهُمَّ إِنِّي أَسْأَلُكَ خَيْرَ الْمَوْلَجِ وَخَيْرَ الْمَخْرَجِ",
            "transliteration": "Allahumma inni as'aluka khayral mawlaji wa khayral makhraji",
            "meaning": "O Allah, I ask You for the good of the entrance and the good of the exit.",
            "reference": "Abu Dawood 4/325"
        }
    ],
    "Eating and Drinking": [
        {
            "title": "Before Eating",
            "arabic": "بِسْمِ اللَّهِ",
            "transliteration": "Bismillah",
            "meaning": "In the name of Allah.",
            "reference": "Abu Dawood, Tirmidhi"
        },
        {
            "title": "After Eating",
            "arabic": "الْحَمْدُ لِلَّهِ الَّذِي أَطْعَمَنَا وَسَقَانَا وَجَعَلَنَا مُسْلِمِينَ",
            "transliteration": "Alhamdu lillahil ladhi at'amana wa saqana wa ja'alana muslimin",
            "meaning": "All praise is for Allah who fed us and gave us drink and made us Muslims.",
            "reference": "Abu Dawood 3/345"
        }
    ],
    "Anxiety and Distress": [
        {
            "title": "Dua for Anxiety",
            "arabic": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ",
            "transliteration": "Allahumma inni a'udhu bika minal hammi wal hazan",
            "meaning": "O Allah, I seek refuge in You from worry and grief.",
            "reference": "Bukhari 7/158"
        }
    ],
    "Travel": [
        {
            "title": "Dua for Travel",
            "arabic": "سُبْحَانَ الَّذِي سَخَّرَ لَنَا هَذَا وَمَا كُنَّا لَهُ مُقْرِنِينَ",
            "transliteration": "Subhanal ladhi sakhkhara lana hadha wa ma kunna lahu muqrinin",
            "meaning": "Glory be to Him Who has subjected this to us, and we could never have it by our efforts.",
            "reference": "Quran 43:13 - Abu Dawood 3/34"
        }
    ],
    "For Forgiveness": [
        {
            "title": "Seeking Forgiveness",
            "arabic": "رَبِّ اغْفِرْ لِي وَتُبْ عَلَيَّ إِنَّكَ أَنْتَ التَّوَّابُ الرَّحِيمُ",
            "transliteration": "Rabbighfir li wa tub alayya innaka antat tawwabur rahim",
            "meaning": "My Lord, forgive me and accept my repentance. Verily You are the Oft-Returning, the Most Merciful.",
            "reference": "Abu Dawood, Ibn Majah"
        }
    ]
}

HADITH_COLLECTIONS = {
    "Sahih Bukhari - Faith": [
        {
            "number": "Bukhari 1",
            "arabic": "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ",
            "text": "Actions are judged by intentions, and every person will get the reward according to what he has intended.",
            "narrator": "Umar ibn al-Khattab (RA)",
            "authenticity": "Sahih"
        },
        {
            "number": "Bukhari 8",
            "arabic": "بُنِيَ الإِسْلاَمُ عَلَى خَمْسٍ",
            "text": "Islam has been built upon five things: the testimony that there is no god but Allah and that Muhammad is the Messenger of Allah, establishing the prayer, giving the Zakat, making the pilgrimage to the House, and fasting in Ramadan.",
            "narrator": "Ibn Umar (RA)",
            "authenticity": "Sahih"
        }
    ],
    "Sahih Muslim - Mercy": [
        {
            "number": "Muslim 2318",
            "arabic": "الرَّاحِمُونَ يَرْحَمُهُمُ الرَّحْمَنُ",
            "text": "The merciful will be shown mercy by the Most Merciful. Be merciful to those on the earth and the One above the heavens will have mercy upon you.",
            "narrator": "Abdullah ibn Amr (RA)",
            "authenticity": "Sahih"
        }
    ],
    "40 Hadith Nawawi": [
        {
            "number": "Nawawi 1",
            "arabic": "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ",
            "text": "Verily actions are by intentions, and for every person is what he intended.",
            "narrator": "Umar ibn al-Khattab (RA)",
            "authenticity": "Sahih"
        },
        {
            "number": "Nawawi 2",
            "arabic": "الإِسْلاَمُ أَنْ تَشْهَدَ أَنْ لاَ إِلَهَ إِلاَّ اللهُ",
            "text": "Islam is to testify that there is no god but Allah and Muhammad is the Messenger of Allah, to establish the prayers, to pay the Zakat, to fast in Ramadan, and to make the pilgrimage to the House if you are able to do so.",
            "narrator": "Umar ibn al-Khattab (RA)",
            "authenticity": "Sahih"
        }
    ]
}

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "quick_question" not in st.session_state:
    st.session_state.quick_question = ""

def call_api(user_message, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history[-6:]:
        messages.append({"role": "user", "content": h["user"]})
        messages.append({"role": "assistant", "content": h["assistant"]})
    messages.append({"role": "user", "content": user_message})
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 2000,
        "temperature": 0.1,
        "stream": False
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    data = response.json()
    if "choices" not in data:
        raise Exception(f"API error: {json.dumps(data)}")
    content = data["choices"][0]["message"]["content"]
    if not content:
        raise Exception("Empty response from API")
    return content

def parse_response(raw):
    cleaned = re.sub(r'```json|```', '', raw).strip()
    start = cleaned.find('{')
    end = cleaned.rfind('}') + 1
    if start != -1 and end > start:
        cleaned = cleaned[start:end]
    return json.loads(cleaned)

def fetch_quran_surah(surah_number):
    try:
        response = requests.get(f"https://api.alquran.cloud/v1/surah/{surah_number}/editions/quran-uthmani,en.asad", timeout=10)
        data = response.json()
        if data.get("status") == "OK":
            return data["data"]
        return None
    except Exception:
        return None

def render_response(result):
    st.markdown(f'<div class="answer-card"><strong style="color:#c9a84c;">Answer:</strong><br><br>{result.get("direct_answer", "")}</div>', unsafe_allow_html=True)

    quran = result.get("quran_evidence", [])
    if quran:
        st.markdown('<div class="section-title">Quran Evidence</div>', unsafe_allow_html=True)
        for verse in quran:
            st.markdown(f'<div class="quran-card"><div class="arabic-text">{verse.get("arabic", "")}</div><div class="arabic-translation">{verse.get("translation", "")}</div><span class="quran-ref">{verse.get("reference", "")}</span><br><br><em style="color:#a0b0c0;">{verse.get("explanation", "")}</em></div>', unsafe_allow_html=True)

    hadith = result.get("hadith_evidence", [])
    if hadith:
        st.markdown('<div class="section-title">Hadith Evidence</div>', unsafe_allow_html=True)
        for h in hadith:
            auth = h.get("authenticity", "")
            badge_class = "badge-sahih" if auth == "Sahih" else "badge-hasan" if auth == "Hasan" else "badge-weak"
            arabic_text = f'<div class="arabic-text">{h.get("arabic", "")}</div>' if h.get("arabic") else ""
            st.markdown(f'<div class="hadith-card">{arabic_text}<strong style="color:#e0e0e0;">{h.get("text", "")}</strong><br><br><strong>Source:</strong> {h.get("source", "")} <span class="{badge_class}">{auth}</span><br><small style="color:#a0b0c0;">{h.get("note", "")}</small></div>', unsafe_allow_html=True)

    scholarly = result.get("scholarly_opinions", [])
    if scholarly and result.get("ikhtilaf") == "Yes":
        st.markdown('<div class="section-title">Scholarly Opinions</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">There is a difference of opinion among scholars on this matter.</div>', unsafe_allow_html=True)
        for opinion in scholarly:
            st.markdown(f'<div class="scholar-card"><strong style="color:#c9a84c;">{opinion.get("madhab", "")}:</strong> {opinion.get("opinion", "")}<br><small style="color:#a0b0c0;">Source: {opinion.get("source", "")}</small></div>', unsafe_allow_html=True)

    dua = result.get("dua", {})
    if dua and dua.get("arabic"):
        st.markdown('<div class="section-title">Dua</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="dua-card"><div class="arabic-text">{dua.get("arabic", "")}</div><br><strong style="color:#c9a84c;">Transliteration:</strong><br>{dua.get("transliteration", "")}<br><br><strong style="color:#c9a84c;">Meaning:</strong><br>{dua.get("meaning", "")}<br><br><small style="color:#8e44ad;">Reference: {dua.get("reference", "")}</small></div>', unsafe_allow_html=True)

    conclusion = result.get("conclusion", "")
    if conclusion:
        st.markdown('<div class="section-title">Conclusion</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="answer-card">{conclusion}</div>', unsafe_allow_html=True)

    if result.get("consult_scholar") == "Yes":
        st.markdown('<div class="warning-card">This matter involves complexity. Please consult a qualified Islamic scholar for a personal ruling.</div>', unsafe_allow_html=True)

st.markdown('<div class="bismillah">بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</div>', unsafe_allow_html=True)
st.markdown('<div class="main-header">Muslim AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Your Islamic companion — answers based on Quran, Hadith, and scholarly opinion</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div style="color:#c9a84c; font-size:20px; font-weight:700; text-align:center; margin-bottom:15px;">Navigation</div>', unsafe_allow_html=True)

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
    st.markdown('<div style="color:#c9a84c; font-weight:700; margin-bottom:8px;">Quick Topics</div>', unsafe_allow_html=True)
    for topic in topics:
        if st.button(topic, use_container_width=True, key=f"topic_{topic}"):
            st.session_state.quick_question = topic

    st.markdown("---")
    st.markdown('<div style="color:#a0b0c0; font-size:12px; text-align:center;">You can ask in English, Urdu, or Arabic</div>', unsafe_allow_html=True)
    st.markdown("---")
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.messages = []
        st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(["AI Assistant", "Quran Reader", "Dua Collection", "Hadith Library"])

with tab1:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                try:
                    result = json.loads(msg["content"])
                    render_response(result)
                except Exception:
                    st.markdown(msg["content"])
            else:
                st.markdown(msg["content"])

    quick_q = st.session_state.get("quick_question", "")
    if quick_q:
        st.session_state.quick_question = ""
        user_input = quick_q
    else:
        user_input = st.chat_input("Ask your Islamic question in English, Urdu, or Arabic...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner("Searching Quran and Hadith..."):
                try:
                    raw = call_api(user_input, st.session_state.chat_history)
                    result = parse_response(raw)
                    render_response(result)
                    st.session_state.messages.append({"role": "assistant", "content": json.dumps(result)})
                    st.session_state.chat_history.append({"user": user_input, "assistant": raw})
                except Exception as e:
                    error_msg = f"Error: {str(e)}. Please try again."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

with tab2:
    st.markdown('<div class="section-title">Quran Reader — All 114 Surahs</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Select any Surah to read with Arabic text and English translation.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        surah_options = [f"{num}. {name} ({verses} verses)" for num, name, verses in QURAN_SURAHS]
        selected_surah = st.selectbox("Select Surah", surah_options)
        surah_number = int(selected_surah.split(".")[0])
        surah_info = QURAN_SURAHS[surah_number - 1]

        st.markdown(f'<div class="info-box"><strong style="color:#c9a84c;">Surah {surah_info[0]}: {surah_info[1]}</strong><br>Total Ayahs: {surah_info[2]}</div>', unsafe_allow_html=True)
        load_button = st.button("Load Surah", type="primary", use_container_width=True)

    with col2:
        if load_button:
            with st.spinner(f"Loading Surah {surah_info[1]}..."):
                surah_data = fetch_quran_surah(surah_number)
                if surah_data:
                    arabic_edition = surah_data[0]
                    english_edition = surah_data[1]
                    st.markdown(f'<div class="bismillah">{arabic_edition.get("name", "")}</div>', unsafe_allow_html=True)
                    for i, ayah in enumerate(arabic_edition.get("ayahs", [])):
                        arabic = ayah.get("text", "")
                        english = english_edition.get("ayahs", [])[i].get("text", "") if i < len(english_edition.get("ayahs", [])) else ""
                        ayah_number = ayah.get("numberInSurah", i+1)
                        st.markdown(f'<div class="quran-ayah"><span style="color:#c9a84c; font-size:12px;">Ayah {ayah_number}</span><div class="arabic-text">{arabic} ﴿{ayah_number}﴾</div><div class="arabic-translation">{english}</div></div>', unsafe_allow_html=True)
                else:
                    st.error("Could not load Surah. Please check your internet connection and try again.")

with tab3:
    st.markdown('<div class="section-title">Dua Collection</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Authentic duas from Quran and Sunnah for every occasion.</div>', unsafe_allow_html=True)

    selected_category = st.selectbox("Select Category", list(DUA_CATEGORIES.keys()))
    duas = DUA_CATEGORIES.get(selected_category, [])

    for dua in duas:
        st.markdown(f'<div class="dua-card"><strong style="color:#c9a84c; font-size:16px;">{dua["title"]}</strong><br><div class="arabic-text">{dua["arabic"]}</div><br><strong style="color:#8e44ad;">Transliteration:</strong><br><em>{dua["transliteration"]}</em><br><br><strong style="color:#c9a84c;">Meaning:</strong><br>{dua["meaning"]}<br><br><small style="color:#8e44ad;">Reference: {dua["reference"]}</small></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section-title">Hadith Library</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Authentic Hadith from major collections with Arabic text and authenticity grades.</div>', unsafe_allow_html=True)

    selected_collection = st.selectbox("Select Collection", list(HADITH_COLLECTIONS.keys()))
    hadiths = HADITH_COLLECTIONS.get(selected_collection, [])

    for hadith in hadiths:
        auth = hadith.get("authenticity", "Sahih")
        badge_class = "badge-sahih" if auth == "Sahih" else "badge-hasan" if auth == "Hasan" else "badge-weak"
        st.markdown(f'<div class="hadith-card"><span style="color:#c9a84c; font-size:13px; font-weight:700;">{hadith.get("number", "")}</span> <span class="{badge_class}">{auth}</span><div class="arabic-text">{hadith.get("arabic", "")}</div><br><strong style="color:#e0e0e0;">{hadith.get("text", "")}</strong><br><br><small style="color:#a0b0c0;">Narrator: {hadith.get("narrator", "")}</small></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="info-box">Ask the AI Assistant for more Hadith on any topic.</div>', unsafe_allow_html=True)
