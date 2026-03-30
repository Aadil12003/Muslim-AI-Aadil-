import streamlit as st
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Muslim AI API System", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
.stApp { background-color: #0f172a; }
.card {
    background: #1e293b;
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 10px;
    border: 1px solid #334155;
    color: #f1f5f9;
}
h1 { color: #38bdf8; }
</style>
""", unsafe_allow_html=True)

st.title("🕌 Muslim AI (No Dataset Mode)")

API_KEY = st.secrets.get("NVIDIA_API_KEY")

# ================= HADITH API =================
def fetch_hadith_api(query):
    try:
        url = f"https://api.hadith.gading.dev/search?q={query}"
        res = requests.get(url)
        data = res.json()

        results = []
        for item in data["data"][:10]:
            results.append({
                "text": item["arab"] + " - " + item["id"],
                "book": item["kitab"],
                "number": item["hadits"]
            })

        return results

    except:
        return []

# ================= AI RERANK =================
def rerank_with_ai(question, candidates):

    if not candidates:
        return []

    text_block = "\n".join([
        f"{i}. {h['text']} ({h['book']} {h['number']})"
        for i, h in enumerate(candidates)
    ])

    prompt = f"""
Select the 3 most relevant Hadith.

Return ONLY numbers.

Question:
{question}

Hadith:
{text_block}
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
                "max_tokens": 50
            },
            timeout=20
        )

        nums = res.json()["choices"][0]["message"]["content"]

        selected = []
        for n in nums.split():
            if n.isdigit():
                idx = int(n)
                if idx < len(candidates):
                    selected.append(candidates[idx])

        return selected[:3]

    except:
        return candidates[:3]

# ================= QURAN =================
def search_quran(query):
    try:
        res = requests.get(f"https://api.alquran.cloud/v1/search/{query}/all/en")
        return res.json()["data"]["matches"][:3]
    except:
        return []

# ================= AI ANSWER =================
def get_ai_answer(question, hadith_results, quran_results):

    if not hadith_results and not quran_results:
        mode = "general"
    else:
        mode = "strict"

    hadith_text = "\n".join([
        f"{h['text']} ({h['book']} {h['number']})"
        for h in hadith_results
    ])

    quran_text = "\n".join([
        f"{v['text']} (Surah {v['surah']['name']} {v['numberInSurah']})"
        for v in quran_results
    ])

    if mode == "strict":
        prompt = f"""
Answer ONLY using provided sources.

Question:
{question}

Quran:
{quran_text}

Hadith:
{hadith_text}
"""
    else:
        prompt = f"""
Answer using general Islamic knowledge.

Do NOT fabricate references.

Question:
{question}
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
                "max_tokens": 800
            },
            timeout=30
        )

        return res.json()["choices"][0]["message"]["content"], mode

    except:
        return "❌ AI Error", mode

# ================= UI =================
question = st.text_input("💬 Ask your question")

if st.button("Ask") and question:

    # HADITH API
    candidates = fetch_hadith_api(question)
    hadith_results = rerank_with_ai(question, candidates)

    # QURAN
    quran_results = search_quran(question)

    # ANSWER
    answer, mode = get_ai_answer(question, hadith_results, quran_results)

    st.markdown("## 🧠 AI Answer")

    if mode == "general":
        st.warning("⚠️ No direct Quran/Hadith found. Showing general explanation.")

    st.markdown(f"<div class='card'>{answer}</div>", unsafe_allow_html=True)

    # HADITH
    st.markdown("## 📜 Hadith Sources")
    if hadith_results:
        for h in hadith_results:
            st.markdown(
                f"<div class='card'>{h['text']}<br><b>{h['book']} {h['number']}</b></div>",
                unsafe_allow_html=True
            )
    else:
        st.info("No Hadith found")

    # QURAN
    st.markdown("## 📖 Quran Sources")
    if quran_results:
        for v in quran_results:
            st.markdown(
                f"<div class='card'>{v['text']}<br><b>{v['surah']['name']} {v['numberInSurah']}</b></div>",
                unsafe_allow_html=True
            )
    else:
        st.info("No Quran match found")

# ================= DUA =================
st.markdown("## 🤲 Duas")

st.markdown("<div class='card'>بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا</div>", unsafe_allow_html=True)
st.markdown("<div class='card'>اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ</div>", unsafe_allow_html=True)
