from fastapi import APIRouter
import httpx
import os

router = APIRouter()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

@router.post("/chatbot/summarize")
async def summarize_lecture(payload: dict):
    lecture_text = payload.get("lecture_text")
    student_style = payload.get("learning_style", "general")

    prompt = f"""
    You are an educational assistant. A student who is a '{student_style}' 
    needs help understanding this lecture content.
    
    Summarize this in a way that suits their learning style.
    Use diagrams descriptions if visual, examples if practice-based, 
    step-by-step breakdown if sequential.
    
    Lecture content:
    {lecture_text}
    """

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000
            }
        )
    
    result = response.json()
    return {"summary": result["choices"][0]["message"]["content"]}

@router.post("/chatbot/ask")
async def ask_question(payload: dict):
    question = payload.get("question")
    context = payload.get("lecture_context", "")
    
    prompt = f"Context: {context}\n\nStudent question: {question}\n\nAnswer clearly and simply:"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
    
    return {"answer": response.json()["choices"][0]["message"]["content"]}