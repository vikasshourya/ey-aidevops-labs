from datetime import datetime, timezone
from random import uniform

from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/health")
def health():
    return "ok"


@app.get("/quote")
def quote(symbol: str):
    if not symbol:
        raise HTTPException(status_code=400, detail="symbol is required")
    return {"symbol": symbol, "price": round(uniform(100, 500), 2), "ts": datetime.now(timezone.utc).isoformat()}