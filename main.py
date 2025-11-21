from fastapi import FastAPI
from memedict import search_meme

app = FastAPI()

@app.get("/memes/{slug}")
def get_entry(slug: str):
    try:
        entry = search_meme(slug)

        if not isinstance(entry, tuple) or len(entry) != 2:
            return {"error": "Entry format is invalid", "entry_preview": str(entry)}

        data, _ = entry  # Unpack the tuple

        if not isinstance(data, dict):
            return {
                "error": "Entry is not a dictionary.",
                "actual_type": str(type(data)),
                "entry_preview": str(data)
            }

        return {
            "title": data.get("title"),
            "summary": data.get("about", "")[:1000],
            "origin": data.get("origin", "")[:1000],
            "analysis": data.get("spread", "")[:1000]
        }

    except Exception as e:
        return {"error": str(e)}








