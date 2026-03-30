from fastapi import FastAPI
from pydantic import BaseModel
from ai import generate_answer
from db import save_chat, get_history

app = FastAPI()

class Query(BaseModel):
    question: str

@app.post("/ask")
def ask(q: Query):
    answer = generate_answer(q.question)
    save_chat(q.question, answer)
    return {"response": answer}

@app.get("/history")
def history():
    return get_history()
