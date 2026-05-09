from fastapi import APIRouter
import httpx
import os
import sys

# Add Backend and Root to path for direct execution
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "Backend")
if ROOT_DIR not in sys.path: sys.path.append(ROOT_DIR)
if BACKEND_DIR not in sys.path: sys.path.append(BACKEND_DIR)

router = APIRouter()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

@router.post("/summarize")
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

    # Mock fallback agar key missing ho
    if not DEEPSEEK_API_KEY or "YAHAN_APNI" in DEEPSEEK_API_KEY:
        return {"summary": f"SUMMARY (Demo Mode): Yeh lecture '{student_style}' style mein summarize kiya gaya hai. DeepSeek API key missing hai isliye ye mock response hai.\n\nKey Points:\n1. Basic concepts\n2. Practical examples\n3. Next steps"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000
                },
                timeout=15.0
            )
            response.raise_for_status()
            result = response.json()
            return {"summary": result["choices"][0]["message"]["content"]}
    except Exception as e:
        print(f"Chatbot Error: {e}")
        return {"summary": "Abhi summary generate nahi ho pa rahi. DeepSeek API check karein."}

@router.post("/ask")
async def ask_question(payload: dict):
    question = payload.get("question")
    context = payload.get("lecture_context", "")
    
    prompt = f"Context: {context}\n\nStudent question: {question}\n\nAnswer clearly and simply:"
    
    # Mock fallback
    if not DEEPSEEK_API_KEY or "YAHAN_APNI" in DEEPSEEK_API_KEY:
        return {"answer": f"CHATBOT (Demo): Aapka sawaal '{question}' achha hai! DeepSeek key missing hone ki wajah se main detail mein nahi bata sakta, par aap lecture notes check kar sakte hain."}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=15.0
            )
            response.raise_for_status()
            return {"answer": response.json()["choices"][0]["message"]["content"]}
    except Exception as e:
        print(f"Chatbot Error: {e}")
        return {"answer": "Maaf kijiye, abhi main jawab nahi de pa raha hoon."}