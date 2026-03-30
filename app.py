import streamlit as st
import requests

st.set_page_config(page_title="Muslim AI Fixed", layout="wide")

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

st.title("🕌 Muslim AI (Fixed Version)")

API_KEY = st.secrets.get("NVIDIA_API_KEY")

# ================= HADITH API =================
def fetch_hadith(query):
    try:
        url = f"https://api.hadith.gading.dev/search?q={query}"
        res = requests.get(url)
        data = res.json()

        results = []
        if "data" in data:
            for item in data["data"][:5]:
                results.append({
                    "arabic": item.get("arab", ""),
                    "text": item.get("id", ""),
                    "book": item.get("kitab", ""),
                    "number": item.get("hadits", "")
                })

        return results

    except:
        return []

# ================= QURAN =================
def search_quran(query):
    try:
        res = requests.get(f"https://api.alquran.cloud/v1/search/{query}/all/en")
        matches = res.json()["data"]["matches"][:3]

        results = []
        for m in matches:
            surah = m["surah"]["number"]
            ayah = m["numberInSurah"]

            # get arabic ayah
            ar = requests.get(f"https://api.alquran.cloud/v1/ayah/{surah}:{ayah}/ar").json()

            results.append({
                "arabic": ar["data"]["text"],
                "english": m["text"],
                "surah": m["surah"]["name"],
                "ayah": ayah
            })

        return results

    except:
        return []

# ================= AI =================
def get_ai_answer(question, has_sources):

    if has_sources:
        prompt = f"""
Explain briefly using Islamic understanding.

Do NOT add references.
Question: {question}
"""
    else:
        prompt = f"""
Explain the answer using general Islamic knowledge.

Do NOT mention fake references.

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

# ================= UI =================
question = st.text_input("💬 Ask your question")

if st.button("Ask") and question:

    # Fetch data
    hadith_results = fetch_hadith(question)
    quran_results = search_quran(question)

    has_sources = bool(hadith_results or quran_results)

    # ================= AI =================
    st.markdown("## 🧠 AI Answer")

    if not has_sources:
        st.warning("⚠️ No direct Quran/Hadith found. Showing general explanation.")

    answer = get_ai_answer(question, has_sources)
    st.markdown(f"<div class='card'>{answer}</div>", unsafe_allow_html=True)

    # ================= HADITH =================
    st.markdown("## 📜 Hadith")

    if hadith_results:
        for h in hadith_results:
            st.markdown(
                f"<div class='card'>"
                f"{h['arabic']}<br><br>"
                f"{h['text']}<br>"
                f"<b>{h['book']} {h['number']}</b>"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        st.info("No Hadith found")

    # ================= QURAN =================
    st.markdown("## 📖 Quran")

    if quran_results:
        for q in quran_results:
            st.markdown(
                f"<div class='card'>"
                f"{q['arabic']}<br><br>"
                f"{q['english']}<br>"
                f"<b>{q['surah']} {q['ayah']}</b>"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        st.info("No Quran match found")

# ================= DUA =================
st.markdown("## 🤲 Duas")

st.markdown("<div class='card'>بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا</div>", unsafe_allow_html=True)
st.markdown("<div class='card'>اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ</div>", unsafe_allow_html=True)
