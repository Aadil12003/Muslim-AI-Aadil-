import streamlit as st
import requests

st.set_page_config(page_title="Muslim AI Pro", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
.section {
    padding: 15px;
    border-radius: 10px;
    background: #161b22;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("🕌 Muslim AI Pro")
st.caption("Quran • Hadith • Dua • Scholarly Knowledge")

# ================= SETTINGS =================
deep_mode = st.toggle("🧠 Deep Scholarly Mode", value=True)

API_KEY = st.secrets.get("NVIDIA_API_KEY")

# ================= AI =================
def get_ai_response(question):
    if not API_KEY:
        return "❌ API key missing"

    prompt = f"""
You are an expert Islamic scholar AI.

Rules:
- Do NOT guess
- Use authentic Islamic knowledge
- Provide structured answer

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

# ================= UI =================
question = st.text_input("Ask your question...")

if st.button("Ask") and question:
    with st.spinner("Thinking deeply..."):
        answer = get_ai_response(question)

    st.markdown("## 📌 Answer")
    st.markdown(f"<div class='section'>{answer}</div>", unsafe_allow_html=True)

# ================= QURAN =================
st.markdown("## 📖 Quran")

col1, col2 = st.columns(2)

with col1:
    surah = st.number_input("Surah (1-114)", 1, 114, 1)

    if st.button("Load Surah"):
        data = load_surah(surah)
        if data:
            for ayah in data["data"]["ayahs"]:
                st.write(f"{ayah['numberInSurah']}. {ayah['text']}")

with col2:
    keyword = st.text_input("Search Quran keyword")

    if st.button("Search"):
        st.write("⚠️ Basic search (AI-based):")
        result = get_ai_response(f"Give Quran verses about {keyword}")
        st.write(result)

# ================= DUAS =================
st.markdown("## 🤲 Duas")

st.write("**Before Sleep:**")
st.write("بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا")

st.write("**For Anxiety:**")
st.write("اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ")

# ================= HADITH =================
st.markdown("## 📜 Hadith")

st.write("Actions are judged by intentions (Sahih Bukhari 1)")
