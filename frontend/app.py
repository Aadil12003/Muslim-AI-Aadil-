import streamlit as st
import requests
import json

st.set_page_config(page_title="Muslim AI", layout="wide")

st.title("🕌 Muslim AI")
st.caption("AI + Quran + Hadith + Knowledge")

# ===== INPUT =====
question = st.text_input("Ask your question")

if st.button("Ask"):
    res = requests.post("http://127.0.0.1:8000/ask", json={"question": question})
    data = res.json()

    try:
        parsed = json.loads(data["response"])
    except:
        parsed = {"direct_answer": data["response"]}

    # ===== DISPLAY =====
    st.markdown("## 📌 Answer")
    st.write(parsed.get("direct_answer", ""))

    st.markdown("## 📖 Explanation")
    st.write(parsed.get("detailed_explanation", ""))

    if parsed.get("quran_evidence"):
        st.markdown("## 📖 Quran")
        for q in parsed["quran_evidence"]:
            st.write(q)

    if parsed.get("hadith_evidence"):
        st.markdown("## 📜 Hadith")
        for h in parsed["hadith_evidence"]:
            st.write(h)

    if parsed.get("scholarly_opinions"):
        st.markdown("## 🧠 Scholars")
        for s in parsed["scholarly_opinions"]:
            st.write(s)

    st.markdown("## 📌 Conclusion")
    st.write(parsed.get("conclusion", ""))

# ===== HISTORY =====
st.markdown("## 🕘 Recent Questions")

history = requests.get("http://127.0.0.1:8000/history").json()

for h in history:
    st.write(f"Q: {h[1]}")
    st.write(f"A: {h[2][:100]}...")
    st.markdown("---")
