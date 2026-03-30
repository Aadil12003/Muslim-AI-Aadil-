import json
import re
import time
import requests
import streamlit as st

st.set_page_config(page_title="Muslim AI Pro", layout="wide")

# ================= CONFIG =================
API_KEY = st.secrets["NVIDIA_API_KEY"]
API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "meta/llama-4-maverick-17b-128e-instruct"

deep_mode = st.sidebar.toggle("🧠 Scholar Mode", value=True)

# ================= PROMPT =================
SYSTEM_PROMPT = f"""
You are an expert Islamic scholar AI.

RULES:
- Use Quran, Sahih Hadith, classical scholars only
- Quote FULL hadith text
- Provide multiple evidences
- Explain reasoning deeply
- Mention ikhtilaf

DEPTH: {"DETAILED" if deep_mode else "NORMAL"}

RETURN JSON:
{{
 "direct_answer":"",
 "detailed_explanation":"",
 "quran_evidence":[],
 "hadith_evidence":[],
 "scholarly_opinions":[],
 "dua": {{}},
 "conclusion":""
}}
"""

# ================= API =================
def call_api(prompt, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for h in history[-2:]:
        messages.append({"role": "user", "content": h["user"]})
        messages.append({"role": "assistant", "content": h["assistant"]})

    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 3000 if deep_mode else 1500,
        "temperature": 0.2
    }

    headers = {
        "Authorization": f"Bearer {API_KEY},
        "Content-Type": "application/json"
    }

    for i in range(3):
        try:
            res = requests.post(API_URL, headers=headers, json=payload, timeout=45)
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"]
        except:
            time.sleep(2 ** i)

    return '{"direct_answer":"Service busy"}'

# ================= PARSE =================
def parse(raw):
    try:
        cleaned = re.sub(r'```json|```', '', raw)
        start = cleaned.find('{')
        end = cleaned.rfind('}') + 1
        return json.loads(cleaned[start:end])
    except:
        return {"direct_answer": raw}

# ================= UI =================
st.title("🕌 Muslim AI Pro")
st.caption("Quran • Hadith • Dua • Scholarly Knowledge")

# ================= STATE =================
if "history" not in st.session_state:
    st.session_state.history = []

# ================= RENDER =================
def render(data):
    st.markdown("## 📌 Answer")
    st.write(data.get("direct_answer", ""))

    st.markdown("## 📖 Detailed Explanation")
    st.write(data.get("detailed_explanation", ""))

    if data.get("quran_evidence"):
        st.markdown("## 📖 Quran Evidence")
        for q in data["quran_evidence"]:
            st.markdown(f"**{q.get('reference','')}**")
            st.write(q.get("arabic",""))
            st.write(q.get("translation",""))

    if data.get("hadith_evidence"):
        st.markdown("## 📜 Hadith Evidence")
        for h in data["hadith_evidence"]:
            st.markdown(f"**{h.get('source','')}**")
            st.write(h.get("arabic",""))
            st.write(h.get("text",""))

    if data.get("scholarly_opinions"):
        st.markdown("## 🧠 Scholarly Opinions")
        for s in data["scholarly_opinions"]:
            st.write(f"**{s.get('madhab','')}**: {s.get('opinion','')}")

    if data.get("dua") and data["dua"].get("arabic"):
        st.markdown("## 🤲 Dua")
        st.write(data["dua"]["arabic"])
        st.write(data["dua"].get("transliteration",""))
        st.write(data["dua"].get("meaning",""))

    if data.get("conclusion"):
        st.markdown("## 📌 Conclusion")
        st.write(data["conclusion"])

# ================= NAVIGATION =================
tab1, tab2, tab3, tab4 = st.tabs(["AI Assistant", "Quran", "Dua", "Hadith"])

# ================= AI TAB =================
with tab1:
    for h in st.session_state.history:
        with st.chat_message("user"):
            st.write(h["user"])
        with st.chat_message("assistant"):
            try:
                render(json.loads(h["assistant"]))
            except:
                st.write(h["assistant"])

    user_input = st.chat_input("Ask your question...")

    if user_input:
        st.session_state.history.append({"user": user_input, "assistant": ""})

        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking deeply..."):
                raw = call_api(user_input, st.session_state.history)
                data = parse(raw)
                render(data)

        st.session_state.history[-1]["assistant"] = json.dumps(data)

# ================= QURAN TAB =================
with tab2:
    st.subheader("📖 Quran Reader")
    surah = st.number_input("Surah (1-114)", 1, 114, 1)

    if st.button("Load Quran"):
        res = requests.get(f"https://api.alquran.cloud/v1/surah/{surah}/en.asad")
        data = res.json()

        for ayah in data["data"]["ayahs"]:
            st.write(f"{ayah['numberInSurah']}. {ayah['text']}")

# ================= DUA TAB =================
with tab3:
    st.subheader("🤲 Dua Collection")

    st.write("Before Sleep:")
    st.write("بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا")

    st.write("For Anxiety:")
    st.write("اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ")

# ================= HADITH TAB =================
with tab4:
    st.subheader("📜 Hadith Library")

    st.write("Bukhari 1:")
    st.write("Actions are judged by intentions.")
