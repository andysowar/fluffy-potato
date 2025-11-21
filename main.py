from fastapi import FastAPI, HTTPException

from services import fetch_meme_entry

app = FastAPI()

@app.get("/memes/{slug}")
def get_entry(slug: str, trace: bool = False):
    try:
        entry = fetch_meme_entry(slug)
    except Exception as exc:  # noqa: BLE001 - surfaced as HTTP error
        raise HTTPException(status_code=502, detail=f"Lookup failed: {exc}") from exc

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    return {
        "title": entry.get("title"),
        "origin": entry.get("origin", "")[:1000],
        "spread": entry.get("spread", "")[:1000],
        "analysis": entry.get("analysis", "")[:1000],
    }












