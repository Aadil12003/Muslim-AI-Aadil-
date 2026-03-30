import streamlit as st
import requests
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Muslim AI Hybrid", layout="wide")

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

st.title("🕌 Muslim AI (Hybrid Search System)")

API_KEY = st.secrets.get("NVIDIA_API_KEY")

# ================= LOAD HADITH =================
@st.cache_data
def load_hadith():
    with open("hadith.json", "r", encoding="utf-8") as f:
        return json.load(f)

hadith_data = load_hadith()

# ================= TF-IDF =================
@st.cache_resource
def build_vectorizer():
    texts = [h["text"] for h in hadith_data]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(texts)
    return vectorizer, matrix

vectorizer, matrix = build_vectorizer()

# ================= FAST SEARCH =================
def tfidf_search(query):
    query_vec = vectorizer.transform([query])
    similarity = cosine_similarity(query_vec, matrix).flatten()
    top_indices = similarity.argsort()[-10:][::-1]
    return [hadith_data[i] for i in top_indices]

# ================= AI RERANK =================
def rerank_with_ai(question, candidates):

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

    payload = {
        "model": "meta/llama-4-maverick-17b-128e-instruct",
        "messages": [
            {"role": "system", "content": "Islamic assistant"},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 50
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

    hadith_text = "\n".join([
        f"{h['text']} ({h['book']} {h['number']})"
        for h in hadith_results
    ])

    quran_text = "\n".join([
        f"{v['text']} (Surah {v['surah']['name']} {v['numberInSurah']})"
        for v in quran_results
    ])

    prompt = f"""
Answer ONLY using sources below.

Question:
{question}

Quran:
{quran_text}

Hadith:
{hadith_text}
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
    except Exception as e:
        return f"❌ ERROR: {str(e)}"

# ================= UI =================
question = st.text_input("💬 Ask your question")

if st.button("Ask") and question:

    # STEP 1: FAST SEARCH
    candidates = tfidf_search(question)

    # STEP 2: AI RERANK
    hadith_results = rerank_with_ai(question, candidates)

    # STEP 3: QURAN
    quran_results = search_quran(question)

    # STEP 4: ANSWER
    st.markdown("## 🧠 AI Answer")
    answer = get_ai_answer(question, hadith_results, quran_results)
    st.markdown(f"<div class='card'>{answer}</div>", unsafe_allow_html=True)

    # HADITH
    st.markdown("## 📜 Hadith Sources")
    for h in hadith_results:
        st.markdown(
            f"<div class='card'>{h['text']}<br><b>{h['book']} {h['number']}</b></div>",
            unsafe_allow_html=True
        )

    # QURAN
    st.markdown("## 📖 Quran Sources")
    for v in quran_results:
        st.markdown(
            f"<div class='card'>{v['text']}<br><b>{v['surah']['name']} {v['numberInSurah']}</b></div>",
            unsafe_allow_html=True
        )

# ================= DUA =================
st.markdown("## 🤲 Duas")

st.markdown("<div class='card'>بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا</div>", unsafe_allow_html=True)
st.markdown("<div class='card'>اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ</div>", unsafe_allow_html=True)
