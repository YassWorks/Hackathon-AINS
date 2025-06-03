from fastapi import FastAPI

app = FastAPI(title="ANTI-SCAM APP")

@app.get("/")
def read_root():
    return {"status": "works fine <3"}
