import streamlit as st
import requests
import json

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
st.title("🕌 Muslim AI (Authentic System)")
st.caption("AI Explanation + Quran + Hadith Dataset + Duas")

API_KEY = st.secrets.get("NVIDIA_API_KEY")

# ================= LOAD HADITH =================
@st.cache_data
def load_hadith():
    with open("hadith.json", "r", encoding="utf-8") as f:
        return json.load(f)

hadith_data = load_hadith()

# ================= AI =================
def get_ai_answer(question):
    prompt = f"""
You are an Islamic assistant.

Rules:
- Do NOT generate fake Quran or Hadith
- Only explain

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
        ar = requests.get(f"https://api.alquran.cloud/v1/surah/{surah}/ar.alafasy").json()
        en = requests.get(f"https://api.alquran.cloud/v1/surah/{surah}/en.asad").json()
        ur = requests.get(f"https://api.alquran.cloud/v1/surah/{surah}/ur.jalandhry").json()
        return ar, en, ur
    except:
        return None, None, None

# ================= HADITH SEARCH =================
def search_hadith(query, book):
    results = []
    for h in hadith_data:
        if query.lower() in h["text"].lower():
            if book == "All" or h["book"] == book:
                results.append(h)
    return results[:20]

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

# ================= LAYOUT =================
col1, col2 = st.columns([2,1])

# ================= AI =================
with col1:
    st.markdown("## 🧠 AI Explanation")

    question = st.text_input("Ask your question")

    if st.button("Ask") and question:
        ai = get_ai_answer(question)
        st.markdown(f"<div class='card'>{ai}</div>", unsafe_allow_html=True)

# ================= RIGHT PANEL =================
with col2:

    # -------- QURAN --------
    st.markdown("## 📖 Quran")

    surah = st.number_input("Surah (1-114)", 1, 114, 1)

    if st.button("Load Quran"):
        ar, en, ur = get_quran(surah)

        if ar:
            for i in range(len(ar["data"]["ayahs"])):
                st.markdown(
                    f"<div class='card'>"
                    f"<b>{i+1}</b><br>"
                    f"{ar['data']['ayahs'][i]['text']}<br><br>"
                    f"{en['data']['ayahs'][i]['text']}<br>"
                    f"<i>{ur['data']['ayahs'][i]['text']}</i>"
                    f"</div>",
                    unsafe_allow_html=True
                )

    # -------- HADITH --------
    st.markdown("## 📜 Hadith Search")

    search_query = st.text_input("Search Hadith")

    book_filter = st.selectbox(
        "Book",
        ["All", "Bukhari", "Muslim", "Tirmidhi"]
    )

    if st.button("Search Hadith"):
        results = search_hadith(search_query, book_filter)

        if results:
            for h in results:
                st.markdown(
                    f"<div class='card'>"
                    f"{h['text']}<br><br>"
                    f"<b>{h['book']} {h['number']}</b> | {h['grade']}"
                    f"</div>",
                    unsafe_allow_html=True
                )
        else:
            st.warning("No results found")

    # -------- DUAS --------
    st.markdown("## 🤲 Duas")

    for d in DUAS:
        st.markdown(
            f"<div class='card'><b>{d['title']}</b><br>{d['arabic']}<br><i>{d['meaning']}</i></div>",
            unsafe_allow_html=True
        )
