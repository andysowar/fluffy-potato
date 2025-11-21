from fastapi import FastAPI
from memedict import search_meme

app = FastAPI()

@app.get("/memes/{slug}")
def get_entry(slug: str):
    try:
        title, content = search_meme(slug)

        if not title and not content:
            return {"error": f"No entry found for slug '{slug}'"}

        if not isinstance(content, dict):
            return {
                "error": "Content format is invalid",
                "actual_type": str(type(content)),
                "content_preview": str(content)[:500]
            }

        return {
            "title": title or slug.replace("-", " ").title(),
            "about": content.get("about", "")[:1000],
            "origin": content.get("origin", "")[:1000],
            "spread": content.get("spread", "")[:1000],
            "notable_examples": content.get("notable_examples", "")[:1000],
        }
    except Exception as e:
        return {"error": str(e)}







