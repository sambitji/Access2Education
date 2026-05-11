from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Edu-Platform API"}

@app.get("/")
async def root():
    return {"message": "API is working!"}