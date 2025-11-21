from fastapi import FastAPI
from memedict import search_meme

app = FastAPI()

@app.get("/entries/{slug}")
def get_entry(slug: str):
    try:
        entry = search_meme(slug)

        # Only return trimmed fields to avoid large payloads
        return {
            "title": entry.get("title"),
            "summary": entry.get("summary")[:1000],  # cap to 1000 chars
            "origin": entry.get("origin")[:1000],
            "analysis": entry.get("analysis")[:1000]
        }
    except Exception as e:
        return {"error": str(e)}



