import streamlit as st
import requests

st.set_page_config(page_title="Muslim AI", layout="wide")

st.title("🕌 Muslim AI")
st.write("Simple AI Test Version")

# ================= AI =================
API_KEY = st.secrets.get("NVIDIA_API_KEY")

def get_ai_response(question):
    if not API_KEY:
        return "❌ API key missing"

    url = "https://integrate.api.nvidia.com/v1/chat/completions"

    payload = {
        "model": "meta/llama-4-maverick-17b-128e-instruct",
        "messages": [
            {"role": "system", "content": "You are an Islamic assistant."},
            {"role": "user", "content": question}
        ],
        "max_tokens": 300
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=30)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ ERROR: {str(e)}"

# ================= UI =================
question = st.text_input("Ask something")

if st.button("Ask") and question:
    with st.spinner("Thinking..."):
        answer = get_ai_response(question)
    st.write(answer)
