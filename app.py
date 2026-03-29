import streamlit as st
import requests
import json
import re

st.set_page_config(page_title="Muslim AI", layout="wide")

st.markdown("""
<style>
.main-header {font-size: 32px; font-weight: 700; color: #1a5276; text-align: center; padding: 20px 0;}
.sub-header {font-size: 16px; color: #666; text-align: center; margin-bottom: 30px;}
.answer-card {background: #f8f9fa; border-left: 4px solid #1a5276; padding: 20px; border-radius: 8px; margin: 15px 0; line-height: 1.8;}
.quran-card {background: #eafaf1; border-left: 4px solid #27ae60; padding: 15px; border-radius: 8px; margin: 10px 0;}
.hadith-card {background: #eaf4fb; border-left: 4px solid #2980b9; padding: 15px; border-radius: 8px; margin: 10px 0;}
.scholar-card {background: #fef9e7; border-left: 4px solid #f39c12; padding: 15px; border-radius: 8px; margin: 10px 0;}
.warning-card {background: #fdedec; border-left: 4px solid #e74c3c; padding: 15px; border-radius: 8px; margin: 10px 0;}
.dua-card {background: #f5eef8; border-left: 4px solid #8e44ad; padding: 20px; border-radius: 8px; margin: 10px 0; text-align: center;}
.arabic-text {font-size: 24px; font-weight: 700; color: #1a5276; direction: rtl; text-align: right; margin: 10px 0; line-height: 2;}
.badge-sahih {background: #27ae60; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;}
.badge-hasan {background: #f39c12; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;}
.badge-weak {background: #e74c3c; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;}
</style>
""", unsafe_allow_html=True)

NVIDIA_API_KEY = "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"
API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "meta/llama-3.1-70b-instruct"

SYSTEM_PROMPT = """You are an advanced Islamic AI Assistant. You provide accurate, source-based, and respectful answers strictly grounded in authentic Islamic knowledge.

CORE RULES:
- Base answers ONLY on Quran, authentic Hadith, and recognized scholarly fatwas
- Never fabricate Quran verses or Hadith
- Never give rulings without evidence
- If unsure say: No strong authentic evidence found

SOURCES TO USE:
- Quran with Surah and Ayah numbers
- Sahih Bukhari, Sahih Muslim, Abu Dawood, Tirmidhi
- Scholarly fatwas from IslamQA and Dar al-Ifta

RESPONSE FORMAT - Always return valid JSON:
{
  "direct_answer": "clear concise answer",
  "quran_evidence": [
    {
      "arabic": "Arabic verse text",
      "translation": "English translation",
      "reference": "Surah Name Ayah number",
      "explanation": "brief explanation"
    }
  ],
  "hadith_evidence": [
    {
      "text": "hadith text in English",
      "arabic": "Arabic hadith if available",
      "source": "Book name and number",
      "authenticity": "Sahih or Hasan or Weak",
      "note": "any important note"
    }
  ],
  "scholarly_opinions": [
    {
      "madhab": "Hanafi or Shafii or Maliki or Hanbali or General",
      "opinion": "opinion text",
      "source": "fatwa source"
    }
  ],
  "dua": {
    "arabic": "Arabic dua text if applicable",
    "transliteration": "transliteration",
    "meaning": "English meaning",
    "reference": "source"
  },
  "ikhtilaf": "Yes or No - is there difference of opinion",
  "conclusion": "neutral summary",
  "consult_scholar": "Yes or No",
  "language_detected": "English or Urdu or Arabic or Hindi"
}

If question is in Urdu respond with Urdu in the answer fields but keep JSON keys in English.
If question is about dua fill the dua field completely.
Return ONLY valid JSON nothing else."""

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def call_api(user_message, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history[-6:]:
        messages.append({"role": "user", "content": h["user"]})
        messages.append({"role": "assistant", "content": h["assistant"]})
    messages.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 2000,
        "temperature": 0.1,
        "stream": False
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    data = response.json()
    if "choices" not in data:
        raise Exception(f"API error: {json.dumps(data)}")
    content = data["choices"][0]["message"]["content"]
    if not content:
        raise Exception("Empty response from API")
    return content

def parse_response(raw):
    cleaned = re.sub(r'```json|```', '', raw).strip()
    start = cleaned.find('{')
    end = cleaned.rfind('}') + 1
    if start != -1 and end > start:
        cleaned = cleaned[start:end]
    return json.loads(cleaned)

def render_response(result):
    st.markdown(f'<div class="answer-card"><strong>Answer:</strong><br><br>{result.get("direct_answer", "")}</div>', unsafe_allow_html=True)

    quran = result.get("quran_evidence", [])
    if quran:
        st.markdown("### Quran Evidence")
        for verse in quran:
            st.markdown(f'<div class="quran-card"><div class="arabic-text">{verse.get("arabic", "")}</div><br><strong>Translation:</strong> {verse.get("translation", "")}<br><strong>Reference:</strong> {verse.get("reference", "")}<br><em>{verse.get("explanation", "")}</em></div>', unsafe_allow_html=True)

    hadith = result.get("hadith_evidence", [])
    if hadith:
        st.markdown("### Hadith Evidence")
        for h in hadith:
            auth = h.get("authenticity", "")
            badge_class = "badge-sahih" if auth == "Sahih" else "badge-hasan" if auth == "Hasan" else "badge-weak"
            auth_symbol = "Sahih" if auth == "Sahih" else "Hasan" if auth == "Hasan" else "Weak"
            arabic_text = f'<div class="arabic-text">{h.get("arabic", "")}</div>' if h.get("arabic") else ""
            st.markdown(f'<div class="hadith-card">{arabic_text}<strong>Hadith:</strong> {h.get("text", "")}<br><strong>Source:</strong> {h.get("source", "")} <span class="{badge_class}">{auth_symbol}</span><br>{h.get("note", "")}</div>', unsafe_allow_html=True)

    scholarly = result.get("scholarly_opinions", [])
    if scholarly and result.get("ikhtilaf") == "Yes":
        st.markdown("### Scholarly Opinions")
        st.info("There is a difference of opinion among scholars on this matter.")
        for opinion in scholarly:
            st.markdown(f'<div class="scholar-card"><strong>{opinion.get("madhab", "")}:</strong> {opinion.get("opinion", "")}<br><small>Source: {opinion.get("source", "")}</small></div>', unsafe_allow_html=True)

    dua = result.get("dua", {})
    if dua and dua.get("arabic"):
        st.markdown("### Dua")
        st.markdown(f'<div class="dua-card"><div class="arabic-text">{dua.get("arabic", "")}</div><br><strong>Transliteration:</strong> {dua.get("transliteration", "")}<br><br><strong>Meaning:</strong> {dua.get("meaning", "")}<br><br><small>Reference: {dua.get("reference", "")}</small></div>', unsafe_allow_html=True)

    conclusion = result.get("conclusion", "")
    if conclusion:
        st.markdown("### Conclusion")
        st.markdown(f'<div class="answer-card">{conclusion}</div>', unsafe_allow_html=True)

    if result.get("consult_scholar") == "Yes":
        st.markdown('<div class="warning-card">This matter involves complexity. Please consult a qualified Islamic scholar for a personal ruling.</div>', unsafe_allow_html=True)

st.markdown('<div class="main-header">Muslim AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Ask any Islamic question — answers based on Quran, Hadith, and scholarly opinion</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Quick Topics")
    topics = [
        "What is the ruling on missing Fajr prayer?",
        "Give me morning adhkar",
        "What breaks the fast in Ramadan?",
        "Is music halal or haram?",
        "Dua for anxiety and stress",
        "What is the ruling on zakah?",
        "Dua before sleeping",
        "What is tawakkul in Islam?",
        "Is insurance halal?",
        "Dua for entering home"
    ]
    for topic in topics:
        if st.button(topic, use_container_width=True):
            st.session_state.quick_question = topic

    st.markdown("---")
    st.markdown("### Language")
    st.markdown("You can ask in English, Urdu, or Arabic")
    st.markdown("---")
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.messages = []
        st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            try:
                result = json.loads(msg["content"])
                render_response(result)
            except Exception:
                st.markdown(msg["content"])
        else:
            st.markdown(msg["content"])

quick_q = st.session_state.get("quick_question", "")
if quick_q:
    st.session_state.quick_question = ""
    user_input = quick_q
else:
    user_input = st.chat_input("Ask your Islamic question in English, Urdu, or Arabic...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Searching Quran and Hadith..."):
            try:
                raw = call_api(user_input, st.session_state.chat_history)
                result = parse_response(raw)
                render_response(result)
                st.session_state.messages.append({"role": "assistant", "content": json.dumps(result)})
                st.session_state.chat_history.append({
                    "user": user_input,
                    "assistant": raw
                })
            except Exception as e:
                error_msg = f"Error: {str(e)}. Please try again."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
