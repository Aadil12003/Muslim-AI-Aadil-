import streamlit as st
import requests
import json

st.set_page_config(page_title="Muslim AI Intelligent", layout="wide")

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
st.title("🕌 Muslim AI (Intelligent System)")
st.caption("AI + Quran + Hadith (No Hallucination Mode)")

API_KEY = st.secrets.get("NVIDIA_API_KEY")

# ================= LOAD HADITH =================
@st.cache_data
def load_hadith():
    with open("hadith.json", "r", encoding="utf-8") as f:
        return json.load(f)

hadith_data = load_hadith()

# ================= SEARCH HADITH =================
def search_hadith(query):
    results = []
    for h in hadith_data:
        if query.lower() in h["text"].lower():
            results.append(h)
    return results[:5]

# ================= SEARCH QURAN =================
def search_quran(query):
    try:
        res = requests.get(f"https://api.alquran.cloud/v1/search/{query}/all/en")
        return res.json()["data"]["matches"][:5]
    except:
        return []

# ================= AI =================
def get_ai_answer(question, hadith_results, quran_results):

    hadith_text = "\n".join([
        f"{h['text']} ({h['book']} {h['number']})"
        for h in hadith_results
    ])

    quran_text = "\n".join([
        f"{v['text']} (Surah {v['surah']['name']} {v['numberInSurah']})"
        for v in quran_results
    ])

    prompt = f"""
You are an Islamic assistant.

STRICT RULES:
- Use ONLY the provided Quran and Hadith
- Do NOT add anything from your own knowledge
- If no data is provided, say "No direct source found"

Question:
{question}

Quran:
{quran_text}

Hadith:
{hadith_text}

Give:
1. Direct Answer
2. Explanation
3. References (only from above)
"""

    payload = {
        "model": "meta/llama-4-maverick-17b-128e-instruct",
        "messages": [
            {"role": "system", "content": "Islamic expert"},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 800
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

# ================= UI =================
question = st.text_input("💬 Ask your question")

if st.button("Ask") and question:

    # STEP 1: SEARCH DATA
    hadith_results = search_hadith(question)
    quran_results = search_quran(question)

    # STEP 2: AI ANSWER
    st.markdown("## 🧠 AI Answer")
    answer = get_ai_answer(question, hadith_results, quran_results)
    st.markdown(f"<div class='card'>{answer}</div>", unsafe_allow_html=True)

    # STEP 3: SHOW SOURCES

    st.markdown("## 📖 Quran Sources")
    if quran_results:
        for v in quran_results:
            st.markdown(
                f"<div class='card'>{v['text']}<br><b>{v['surah']['name']} {v['numberInSurah']}</b></div>",
                unsafe_allow_html=True
            )
    else:
        st.warning("No Quran match found")

    st.markdown("## 📜 Hadith Sources")
    if hadith_results:
        for h in hadith_results:
            st.markdown(
                f"<div class='card'>{h['text']}<br><b>{h['book']} {h['number']}</b></div>",
                unsafe_allow_html=True
            )
    else:
        st.warning("No Hadith match found")

# ================= DUA =================
st.markdown("## 🤲 Duas")

st.markdown("<div class='card'>بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا</div>", unsafe_allow_html=True)
st.markdown("<div class='card'>اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ</div>", unsafe_allow_html=True)
