import streamlit as st
import requests
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

st.set_page_config(page_title="Muslim AI FAISS", layout="wide")

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
</style>
""", unsafe_allow_html=True)

st.title("🕌 Muslim AI (FAISS Semantic Engine)")

API_KEY = st.secrets.get("NVIDIA_API_KEY")

# ================= LOAD HADITH =================
@st.cache_data
def load_hadith():
    with open("hadith.json", "r", encoding="utf-8") as f:
        return json.load(f)

hadith_data = load_hadith()

# ================= LOAD MODEL =================
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

# ================= BUILD FAISS =================
@st.cache_resource
def build_faiss():
    texts = [h["text"] for h in hadith_data]
    embeddings = model.encode(texts)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))

    return index, texts

index, texts = build_faiss()

# ================= SEARCH =================
def faiss_search(query):
    q_emb = model.encode([query])
    D, I = index.search(np.array(q_emb), 5)

    results = []
    for i in I[0]:
        results.append(hadith_data[i])

    return results

# ================= QURAN =================
def search_quran(query):
    try:
        res = requests.get(f"https://api.alquran.cloud/v1/search/{query}/all/en")
        return res.json()["data"]["matches"][:3]
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
Answer ONLY using provided sources.

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
    except:
        return "❌ AI Error"

# ================= UI =================
question = st.text_input("💬 Ask your question")

if st.button("Ask") and question:

    # VECTOR SEARCH
    hadith_results = faiss_search(question)
    quran_results = search_quran(question)

    # AI ANSWER
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
