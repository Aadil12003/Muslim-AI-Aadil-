import json
import re
import time
import requests
import streamlit as st

st.set_page_config(page_title="Muslim AI Pro+", layout="wide")

# ================= CONFIG =================
API_KEY = st.secrets["NVIDIA_API_KEY"]
API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "meta/llama-4-maverick-17b-128e-instruct"

# ================= MODES =================
deep_mode = st.sidebar.toggle("🧠 Scholar Mode (Detailed)", value=True)

SYSTEM_PROMPT = f"""
You are an expert Islamic scholar AI.

RULES:
- Use Quran, Sahih Hadith, classical scholars only
- Quote FULL hadith text
- Provide multiple evidences
- Explain reasoning deeply
- Mention ikhtilaf if exists

DEPTH MODE: {"DETAILED" if deep_mode else "NORMAL"}

RETURN JSON:
{{
 "direct_answer":"",
 "detailed_explanation":"",
 "quran_evidence":[],
 "hadith_evidence":[],
 "scholarly_opinions":[],
 "ikhtilaf":"",
 "conclusion":""
}}
"""

# ================= SAFETY =================
def validate_response(data):
    if not isinstance(data, dict):
        return False
    if "direct_answer" not in data:
        return False
    return True

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
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    for i in range(3):
        try:
            res = requests.post(API_URL, headers=headers, json=payload, timeout=45)
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"]
        except:
            time.sleep(2 ** i)

    return '{"direct_answer":"Service busy. Try again.","detailed_explanation":""}'

# ================= PARSE =================
def parse(raw):
    try:
        cleaned = re.sub(r'```json|```', '', raw)
        start = cleaned.find('{')
        end = cleaned.rfind('}') + 1
        data = json.loads(cleaned[start:end])

        if validate_response(data):
            return data
    except:
        pass

    return {"direct_answer": raw}

# ================= UI =================
st.title("🕌 Aadil's Muslim AI Pro+")
st.caption("Advanced Islamic AI with deep scholarly reasoning")

# ================= STATE =================
if "history" not in st.session_state:
    st.session_state.history = []

# ================= DISPLAY =================
def display(data):
    tabs = st.tabs(["Answer", "Explanation", "Quran", "Hadith", "Scholars"])

    with tabs[0]:
        st.write(data.get("direct_answer", ""))
        st.code(data.get("direct_answer", ""), language="text")

    with tabs[1]:
        st.write(data.get("detailed_explanation", ""))

    with tabs[2]:
        for q in data.get("quran_evidence", []):
            with st.expander(q.get("reference", "Quran")):
                st.write(q.get("arabic", ""))
                st.write(q.get("translation", ""))

    with tabs[3]:
        for h in data.get("hadith_evidence", []):
            with st.expander(h.get("source", "Hadith")):
                st.write(h.get("arabic", ""))
                st.write(h.get("text", ""))

    with tabs[4]:
        for s in data.get("scholarly_opinions", []):
            st.write(f"**{s.get('madhab','')}**: {s.get('opinion','')}")

# ================= CHAT =================
for h in st.session_state.history:
    with st.chat_message("user"):
        st.write(h["user"])
    with st.chat_message("assistant"):
        try:
            display(json.loads(h["assistant"]))
        except:
            st.write(h["assistant"])

# ================= INPUT =================
user_input = st.chat_input("Ask anything about Islam...")

# ================= RATE LIMIT =================
if "last_call" not in st.session_state:
    st.session_state.last_call = 0

if user_input:
    if time.time() - st.session_state.last_call < 2:
        st.warning("Slow down. Wait 2 seconds.")
        st.stop()

    st.session_state.last_call = time.time()

    st.session_state.history.append({"user": user_input, "assistant": ""})

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing deeply..."):
            raw = call_api(user_input, st.session_state.history)
            data = parse(raw)
            display(data)

    st.session_state.history[-1]["assistant"] = json.dumps(data)
