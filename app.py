import streamlit as st
import requests

st.set_page_config(page_title="Muslim AI Clean", layout="wide")

# ================= UI FIX =================
st.markdown("""
<style>
.stApp { background-color: #0f172a; }

.block-container {
    padding-top: 2rem;
}

.card {
    background: #1e293b;
    padding: 18px;
    border-radius: 14px;
    margin-bottom: 15px;
    border: 1px solid #334155;
    color: #e2e8f0;
    line-height: 1.6;
    font-size: 15px;
}

h1 { color: #38bdf8; }
h2, h3 { color: #e2e8f0; }

input {
    background-color: #1e293b !important;
    color: white !important;
}

button {
    background-color: #2563eb !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🕌 Muslim AI (Clean Fixed Version)")

API_KEY = st.secrets.get("NVIDIA_API_KEY")

# ================= HADITH =================
def fetch_hadith(query):
    try:
        res = requests.get(f"https://api.hadith.gading.dev/search?q={query}")
        data = res.json()

        results = []
        if "data" in data:
            for item in data["data"][:3]:
                results.append({
                    "arabic": item.get("arab", ""),
                    "text": item.get("id", ""),
                    "book": item.get("kitab", ""),
                    "number": item.get("hadits", "")
                })
        return results
    except:
        return []

# ================= QURAN (FORCED + ARABIC) =================
def get_quran_fixed():
    try:
        # Always load Surah Ikhlas (reliable)
        ar = requests.get("https://api.alquran.cloud/v1/surah/112/ar").json()
        en = requests.get("https://api.alquran.cloud/v1/surah/112/en.asad").json()

        results = []
        for i in range(len(ar["data"]["ayahs"])):
            results.append({
                "arabic": ar["data"]["ayahs"][i]["text"],
                "english": en["data"]["ayahs"][i]["text"],
                "ayah": i+1
            })

        return results
    except:
        return []

# ================= AI =================
def get_ai_answer(question):
    prompt = f"""
Explain clearly in simple Islamic understanding.

Do NOT add fake references.

Question: {question}
"""
    try:
        res = requests.post(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta/llama-4-maverick-17b-128e-instruct",
                "messages": [
                    {"role": "system", "content": "Islamic assistant"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500
            }
        )
        return res.json()["choices"][0]["message"]["content"]
    except:
        return "❌ AI Error"

# ================= INPUT =================
question = st.text_input("💬 Ask your question")

if st.button("Ask") and question:

    # ===== AI =====
    st.markdown("## 🧠 AI Answer")
    answer = get_ai_answer(question)
    st.markdown(f"<div class='card'>{answer}</div>", unsafe_allow_html=True)

    # ===== HADITH =====
    st.markdown("## 📜 Hadith")

    hadith = fetch_hadith(question)

    if hadith:
        for h in hadith:
            st.markdown(
                f"<div class='card'>"
                f"{h['arabic']}<br><br>"
                f"{h['text']}<br>"
                f"<b>{h['book']} {h['number']}</b>"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        st.info("No Hadith found (API limitation)")

    # ===== QURAN =====
    st.markdown("## 📖 Quran (Arabic + English)")

    quran = get_quran_fixed()

    for q in quran:
        st.markdown(
            f"<div class='card'>"
            f"{q['arabic']}<br><br>"
            f"{q['english']}<br>"
            f"<b>Surah Ikhlas - Ayah {q['ayah']}</b>"
            f"</div>",
            unsafe_allow_html=True
        )

# ===== DUA =====
st.markdown("## 🤲 Duas")

st.markdown("<div class='card'><b>Before Sleep:</b><br>بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا</div>", unsafe_allow_html=True)
st.markdown("<div class='card'><b>For Anxiety:</b><br>اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ</div>", unsafe_allow_html=True)
