from fastapi import FastAPI, HTTPException

from services import fetch_meme_entry, fetch_meme_entry_with_trace

app = FastAPI()

@app.get("/memes/{slug}")
def get_entry(slug: str, trace: bool = False):
    try:
        entry, attempts = fetch_meme_entry_with_trace(slug) if trace else (fetch_meme_entry(slug), [])
    except Exception as exc:  # noqa: BLE001 - surfaced as HTTP error
        raise HTTPException(status_code=502, detail=f"Lookup failed: {exc}") from exc

    if not entry:
        detail = {"message": "Entry not found", "attempts": attempts} if trace else "Entry not found"
        raise HTTPException(status_code=404, detail=detail)

    response = {
        "title": entry.get("title"),
        "origin": entry.get("origin", "")[:1000],
        "spread": entry.get("spread", "")[:1000],
        "analysis": entry.get("analysis", "")[:1000],
    }

    if trace:
        response["trace"] = attempts

    return response












