from fastapi import FastAPI
from memedict import search_meme

app = FastAPI()

@app.get("/memes/{slug}")
def get_entry(slug: str):
    try:
        entry = search_meme(slug)

        # Handle tuple return (e.g., (title, summary))
        if isinstance(entry, tuple):
            title, summary = entry
            if not title and not summary:
                return {"error": f"No entry found for slug '{slug}'"}
            return {
                "title": title or "Untitled",
                "summary": summary or "",
                "origin": "",
                "analysis": ""
            }

        # Handle dict return
        if isinstance(entry, dict):
            return {
                "title": entry.get("title", "Untitled"),
                "summary": entry.get("summary", "")[:1000],
                "origin": entry.get("origin", "")[:1000],
                "analysis": entry.get("analysis", "")[:1000]
            }

        return {
            "error": "Entry is not a recognized format.",
            "actual_type": str(type(entry)),
            "entry_preview": str(entry)
        }

    except Exception as e:
        return {"error": str(e)}








