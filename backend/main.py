from fastapi import FastAPI

app = FastAPI(title="ANTI-SCAM BACKEND")

@app.get("/")
def read_root():
    return {"status": "works fine <3"}