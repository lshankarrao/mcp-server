"""
Ultra-minimal FastAPI test for Railway
"""
from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World", "Port": os.getenv("PORT", "Not Set")}

@app.get("/health")
def health():
    return {"status": "ok"}

# For Railway's uvicorn command
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
