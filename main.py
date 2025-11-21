from fastapi import FastAPI
from memedict import search_meme

app = FastAPI()

@app.get("/memes/{slug}")
def get_entry(slug: str):
    try:
        entry = search_meme(slug)

        if not isinstance(entry, dict):
            return {
                "error": "Entry is not a dictionary.",
                "actual_type": str(type(entry)),
                "entry_preview": str(entry)[:500]  # Only show first 500 chars to avoid large output
            }

        return {
            "title": entry.get("title", slug.replace("-", " ").title()),
            "about": entry.get("about", "")[:1000],
            "origin": entry.get("origin", "")[:1000],
            "spread": entry.get("spread", "")[:1000],
            "notable_examples": entry.get("notable_examples", "")[:1000],
        }
    except Exception as e:
        return {"error": str(e)}






