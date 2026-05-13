"""
Fashion Helper AI Proxy Server
Holds the OpenAI API key server-side so it's never exposed in the app.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

app = FastAPI(title="Fashion Helper AI Proxy")

# CORS — allow requests from anywhere (the app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_IMAGES_URL = "https://api.openai.com/v1/images/generations"
DEFAULT_MODEL = "gpt-4o"


class SuggestionRequest(BaseModel):
    prompt: str
    model: str = DEFAULT_MODEL
    max_tokens: int = 500


class SuggestionResponse(BaseModel):
    suggestion: str
    model: str


class ImageRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"
    model: str = "dall-e-2"


class ImageResponse(BaseModel):
    image_url: str = ""
    image_base64: str = ""


@app.get("/health")
async def health():
    return {"status": "ok", "has_key": bool(OPENAI_API_KEY)}


@app.post("/suggest", response_model=SuggestionResponse)
async def suggest(req: SuggestionRequest):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured on server")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "model": req.model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a fashion stylist assistant for the Fashion Helper app. "
                    "Provide concise, practical outfit suggestions based on the user's wardrobe. "
                    "Keep responses under 200 words. Format as a numbered list of items with brief styling notes."
                ),
            },
            {"role": "user", "content": req.prompt},
        ],
        "max_tokens": req.max_tokens,
        "temperature": 0.7,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(OPENAI_URL, headers=headers, json=body)

    if resp.status_code != 200:
        detail = resp.text[:200]
        raise HTTPException(status_code=resp.status_code, detail=detail)

    data = resp.json()
    content = data["choices"][0]["message"]["content"].strip()
    return SuggestionResponse(suggestion=content, model=req.model)


@app.post("/generate-image", response_model=ImageResponse)
async def generate_image(req: ImageRequest):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured on server")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "model": req.model,
        "prompt": req.prompt,
        "size": req.size,
        "n": 1,
        "response_format": "url",
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(OPENAI_IMAGES_URL, headers=headers, json=body)

    if resp.status_code != 200:
        detail = resp.text[:300]
        raise HTTPException(status_code=resp.status_code, detail=detail)

    data = resp.json()
    image_url = data.get("data", [{}])[0].get("url", "")
    return ImageResponse(image_url=image_url)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
