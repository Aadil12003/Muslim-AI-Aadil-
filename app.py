import streamlit as st
import requests

st.set_page_config(page_title="Muslim AI Authentic", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
.stApp { background-color: #0f172a; }

.card {
    background: #1e293b;
    padding: 18px;
    border-radius: 12px;
    margin-bottom: 12px;
    border: 1px solid #334155;
    color: #f1f5f9;
}

h1 { color: #38bdf8; }
h2, h3 { color: #e2e8f0; }

</style>
""", unsafe_allow_html=True)

# ================= TITLE =================
st.title("🕌 Muslim AI (Authentic Mode)")
st.caption("AI Explanation + Real Quran + Verified Hadith + Duas")

API_KEY = st.secrets.get("NVIDIA_API_KEY")

# ================= AI =================
def get_ai_answer(question):
    prompt = f"""
You are an Islamic assistant.

IMPORTANT:
- Do NOT invent Quran or Hadith
- Only give explanation
- Do NOT fabricate references

Question: {question}
"""

    payload = {
        "model": "meta/llama-4-maverick-17b-128e-instruct",
        "messages": [
            {"role": "system", "content": "Islamic assistant"},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        res = requests.post(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        return res.json()["choices"][0]["message"]["content"]
    except:
        return "❌ AI Error"

# ================= QURAN =================
def get_quran(surah):
    try:
        en = requests.get(f"https://api.alquran.cloud/v1/surah/{surah}/en.asad").json()
        ur = requests.get(f"https://api.alquran.cloud/v1/surah/{surah}/ur.jalandhry").json()
        return en, ur
    except:
        return None, None

# ================= HADITH (STATIC VERIFIED SAMPLE) =================
HADITH = [
    {
        "text": "Actions are judged by intentions...",
        "source": "Sahih Bukhari 1"
    },
    {
        "text": "The best among you are those who have the best manners...",
        "source": "Sahih Bukhari"
    }
]

# ================= DUAS =================
DUAS = [
    {
        "title": "Before Sleep",
        "arabic": "بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا",
        "meaning": "O Allah, in Your name I die and live."
    },
    {
        "title": "For Anxiety",
        "arabic": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ",
        "meaning": "O Allah, I seek refuge from anxiety and sorrow."
    }
]

# ================= INPUT =================
question = st.text_input("💬 Ask your question")

if st.button("Ask") and question:

    # -------- AI --------
    st.markdown("## 🧠 AI Explanation")
    ai = get_ai_answer(question)
    st.markdown(f"<div class='card'>{ai}</div>", unsafe_allow_html=True)

    # -------- QURAN --------
    st.markdown("## 📖 Quran")
    surah = 1  # default
    en, ur = get_quran(surah)

    if en:
        for i in range(len(en["data"]["ayahs"])):
            st.markdown(
                f"<div class='card'><b>{i+1}</b><br>{en['data']['ayahs'][i]['text']}<br><i>{ur['data']['ayahs'][i]['text']}</i></div>",
                unsafe_allow_html=True
            )

    # -------- HADITH --------
    st.markdown("## 📜 Hadith")
    for h in HADITH:
        st.markdown(
            f"<div class='card'>{h['text']}<br><b>{h['source']}</b></div>",
            unsafe_allow_html=True
        )

    # -------- DUA --------
    st.markdown("## 🤲 Duas")
    for d in DUAS:
        st.markdown(
            f"<div class='card'><b>{d['title']}</b><br>{d['arabic']}<br><i>{d['meaning']}</i></div>",
            unsafe_allow_html=True
        )
