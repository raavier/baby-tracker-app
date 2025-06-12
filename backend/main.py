from fastapi import FastAPI

app = FastAPI(title="Baby Tracker API", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Hello World from Baby Tracker API! 🍼"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "baby-tracker-api"}