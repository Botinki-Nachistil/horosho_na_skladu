from fastapi import FastAPI

app = FastAPI(title="sklad fastapi_part")


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}

