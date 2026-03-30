import streamlit as st
import requests

st.set_page_config(page_title="Muslim AI Pro", layout="wide")

# ================= PREMIUM CSS =================
st.markdown("""
<style>
/* Background */
.stApp {
    background-color: #0f172a;
}

/* Container spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Card */
.card {
    background: #1e293b;
    padding: 20px;
    border-radius: 14px;
    margin-bottom: 15px;
    border: 1px solid #334155;
    color: #f1f5f9;
    line-height: 1.6;
    font-size: 16px;
}

/* Title */
h1 {
    color: #38bdf8;
}

/* Headings */
h2, h3 {
    color: #e2e8f0;
}

/* Input */
.stTextInput > div > div > input {
    background-color: #1e293b;
    color: white;
    border-radius: 10px;
    border: 1px solid #334155;
}

/* Buttons */
.stButton button {
    background-color: #2563eb;
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    border: none;
}

.stButton button:hover {
    background-color: #1d4ed8;
}

/* Divider */
hr {
    border: 1px solid #334155;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.title("🕌 Muslim AI Pro")
st.caption("Quran • Hadith • Dua • Scholarly Knowledge")

# ================= SETTINGS =================
deep_mode = st.toggle("🧠 Deep Scholarly Mode", value=True)

API_KEY = st.secrets.get("NVIDIA_API_KEY")

# ================= AI FUNCTION =================
def get_ai_response(question):
    if not API_KEY:
        return "❌ API key missing"

    prompt = f"""
You are an expert Islamic scholar AI.

Rules:
- Do NOT guess
- Provide accurate Islamic knowledge
- Use Quran and Hadith if relevant

Format:
1. Direct Answer
2. Explanation
3. Quran Evidence
4. Hadith
5. Dua

Question: {question}
"""

    payload = {
        "model": "meta/llama-4-maverick-17b-128e-instruct",
        "messages": [
            {"role": "system", "content": "You are an Islamic expert."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1200 if deep_mode else 600
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
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ ERROR: {str(e)}"

# ================= QURAN =================
def load_surah(num):
    try:
        res = requests.get(f"https://api.alquran.cloud/v1/surah/{num}/en.asad")
        return res.json()
    except:
        return None

# ================= CHAT UI =================
question = st.text_input("💬 Ask your question...")

if st.button("Ask") and question:
    with st.spinner("Thinking deeply..."):
        answer = get_ai_response(question)

    st.markdown("### 📌 Answer")
    st.markdown(f"<div class='card'>{answer}</div>", unsafe_allow_html=True)

st.markdown("---")

# ================= QURAN =================
st.markdown("## 📖 Quran")

col1, col2 = st.columns(2)

with col1:
    surah = st.number_input("Surah (1-114)", 1, 114, 1)

    if st.button("Load Surah"):
        data = load_surah(surah)
        if data:
            for ayah in data["data"]["ayahs"]:
                st.markdown(f"<div class='card'>{ayah['numberInSurah']}. {ayah['text']}</div>", unsafe_allow_html=True)

with col2:
    keyword = st.text_input("🔍 Search Quran topic")

    if st.button("Search Quran"):
        result = get_ai_response(f"Give Quran verses about {keyword}")
        st.markdown(f"<div class='card'>{result}</div>", unsafe_allow_html=True)

st.markdown("---")

# ================= DUAS =================
st.markdown("## 🤲 Duas")

st.markdown("<div class='card'><b>Before Sleep:</b><br>بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا</div>", unsafe_allow_html=True)

st.markdown("<div class='card'><b>For Anxiety:</b><br>اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ</div>", unsafe_allow_html=True)

st.markdown("---")

# ================= HADITH =================
st.markdown("## 📜 Hadith")

st.markdown("<div class='card'>Actions are judged by intentions (Sahih Bukhari 1)</div>", unsafe_allow_html=True)
