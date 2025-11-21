from fastapi import FastAPI
from memedict import search_meme

app = FastAPI()

@app.get("/entries/{slug}")
def get_entry(slug: str):
    try:
        entry = search_meme(slug)
        return {
            "title": entry.get("title"),
            "summary": entry.get("summary"),
            "origin": entry.get("origin"),
            "spread": entry.get("spread"),
            "notableExamples": entry.get("examples"),
            "analysis": entry.get("analysis"),
        }
    except Exception as e:
        return {"error": str(e)}


