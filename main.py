from fastapi import FastAPI
from memedict import search

app = FastAPI()

@app.get("/memes/{slug}")
def get_entry(slug: str):
    try:
        summary = search(slug)
        
        if not isinstance(summary, str):
            return {
                "error": "Entry format is invalid",
                "actual_type": str(type(summary)),
                "entry_preview": str(summary)[:100]
            }

        return {
            "slug": slug,
            "summary": summary[:1000]
        }
    except Exception as e:
        return {"error": str(e)}









