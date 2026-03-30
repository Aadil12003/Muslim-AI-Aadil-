import streamlit as st
import requests
import json

st.set_page_config(page_title="Muslim AI Semantic", layout="wide")

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
st.title("🕌 Muslim AI (Semantic System)")
st.caption("AI + Quran + Hadith (Semantic Retrieval Mode)")

API_KEY = st.secrets.get("NVIDIA_API_KEY")

# ================= LOAD HADITH =================
@st.cache_data
def load_hadith():
    with open("hadith.json", "r", encoding="utf-8") as f:
        return json.load(f)

hadith_data = load_hadith()

# ================= SEMANTIC HADITH SEARCH =================
def semantic_hadith_search(question):
    sample = hadith_data[:200]  # limit for performance

    hadith_text = "\n".join([
        f"{i}. {h['text']} ({h['book']} {h['number']})"
        for i, h in enumerate(sample)
    ])

    prompt = f"""
You are an Islamic assistant.

From the following Hadith list, select the 3 most relevant to the question.

Return ONLY numbers.

Question:
{question}

Hadith List:
{hadith_text}
"""

    payload = {
        "model": "meta/llama-4-maverick-17b-128e-instruct",
        "messages": [
            {"role": "system", "content": "Islamic assistant"},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 100
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

        nums = res.json()["choices"][0]["message"]["content"]

        selected = []
        for n in nums.split():
            if n.isdigit():
                idx = int(n)
                if idx < len(sample):
                    selected.append(sample[idx])

        return selected[:3]

    except:
        return []

# ================= QURAN SEARCH =================
def search_quran(query):
    try:
        res = requests.get(f"https://api.alquran.cloud/v1/search/{query}/all/en")
        return res.json()["data"]["matches"][:3]
    except:
        return []

# ================= AI ANSWER =================
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
Answer the question using ONLY the given sources.

Question:
{question}

Quran:
{quran_text}

Hadith:
{hadith_text}

Give:
1. Answer
2. Explanation
3. References
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

    # SEMANTIC SEARCH
    hadith_results = semantic_hadith_search(question)
    quran_results = search_quran(question)

    # AI ANSWER
    st.markdown("## 🧠 AI Answer")
    answer = get_ai_answer(question, hadith_results, quran_results)
    st.markdown(f"<div class='card'>{answer}</div>", unsafe_allow_html=True)

    # QURAN
    st.markdown("## 📖 Quran Sources")
    for v in quran_results:
        st.markdown(
            f"<div class='card'>{v['text']}<br><b>{v['surah']['name']} {v['numberInSurah']}</b></div>",
            unsafe_allow_html=True
        )

    # HADITH
    st.markdown("## 📜 Hadith Sources")
    for h in hadith_results:
        st.markdown(
            f"<div class='card'>{h['text']}<br><b>{h['book']} {h['number']}</b></div>",
            unsafe_allow_html=True
        )
