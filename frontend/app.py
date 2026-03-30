import streamlit as st
import requests
import json

st.set_page_config(page_title="Muslim AI SaaS", layout="wide")

# ===== UI DESIGN =====
st.markdown("""
<style>
.big-card {
    background: #0f1f2e;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 10px;
}
.answer {
    border-left: 4px solid gold;
    padding-left: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("🕌 Muslim AI SaaS")
st.caption("AI + Quran + Hadith + Database")

# ===== INPUT =====
question = st.text_input("Ask your question")

if st.button("Ask"):
    res = requests.post("http://localhost:8000/ask", json={"question": question})
    data = res.json()

    try:
        parsed = json.loads(data["response"])
    except:
        parsed = {"direct_answer": data["response"]}

    st.markdown("### 📌 Answer")
    st.markdown(f'<div class="big-card answer">{parsed.get("direct_answer","")}</div>', unsafe_allow_html=True)

    if parsed.get("quran_evidence"):
        st.markdown("### 📖 Quran")
        for q in parsed["quran_evidence"]:
            st.markdown(f'<div class="big-card">{q.get("translation","")}</div>', unsafe_allow_html=True)

    if parsed.get("hadith_evidence"):
        st.markdown("### 📜 Hadith")
        for h in parsed["hadith_evidence"]:
            st.markdown(f'<div class="big-card">{h.get("text","")}</div>', unsafe_allow_html=True)

# ===== HISTORY =====
st.markdown("## 🕘 Recent Questions")

history = requests.get("http://localhost:8000/history").json()

for h in history:
    st.markdown(f"""
    <div class="big-card">
    <b>Q:</b> {h[1]}<br>
    <b>A:</b> {h[2][:200]}...
    </div>
    """, unsafe_allow_html=True)
