import streamlit as st
import requests

st.set_page_config(page_title="Muslim AI Pro", layout="wide")

# ================== API ==================
API_KEY = st.secrets["NVIDIA_API_KEY"]

def get_ai_response(question):
    url = "https://integrate.api.nvidia.com/v1/chat/completions"

    payload = {
        "model": "meta/llama-4-maverick-17b-128e-instruct",
        "messages": [
            {"role": "system", "content": "You are an expert Islamic assistant. Give detailed answers with dua if relevant."},
            {"role": "user", "content": question}
        ],
        "max_tokens": 700
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=30)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ ERROR: {str(e)}"

# ================== UI ==================
st.title("🕌 Muslim AI Pro")
st.caption("Quran • Hadith • Dua • Scholarly Knowledge")

st.markdown("---")

question = st.text_input("Ask your question...")

if st.button("Ask") and question:
    with st.spinner("Thinking..."):
        answer = get_ai_response(question)

    st.markdown("## 📌 Answer")
    st.write(answer)

st.markdown("---")

# ================== EXTRA SECTIONS ==================

st.markdown("## 📖 Quran (Quick Access)")
if st.button("Load Surah Al-Fatiha"):
    res = requests.get("https://api.alquran.cloud/v1/surah/1/en.asad")
    data = res.json()

    for ayah in data["data"]["ayahs"]:
        st.write(f"{ayah['numberInSurah']}. {ayah['text']}")

st.markdown("---")

st.markdown("## 🤲 Common Duas")
st.write("Before Sleep:")
st.write("بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا")

st.write("For Anxiety:")
st.write("اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ")

st.markdown("---")

st.markdown("## 📜 Hadith")
st.write("Actions are judged by intentions (Sahih Bukhari 1)")
