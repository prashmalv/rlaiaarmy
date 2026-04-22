"""
Image generation tool.
Uses DALL-E if OPENAI_API_KEY is set, otherwise searches Pexels (if PEXELS_API_KEY set),
or falls back to returning None so posts go out text-only.
"""
from typing import Optional
import httpx
from config.settings import settings


def generate_image(prompt: str, platform: str = "linkedin") -> Optional[str]:
    """Returns a public image URL or None if no image service configured."""

    sizes = {"instagram": "1080x1080", "linkedin": "1200x627", "facebook": "1200x630"}
    size = sizes.get(platform, "1200x630")

    # Try DALL-E first
    if getattr(settings, "OPENAI_API_KEY", ""):
        url = _dalle(prompt, size)
        if url:
            return url

    # Try Pexels
    if getattr(settings, "PEXELS_API_KEY", ""):
        url = _pexels(prompt)
        if url:
            return url

    return None


def _dalle(prompt: str, size: str) -> Optional[str]:
    try:
        import openai
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        w, h = size.split("x")
        # DALL-E 3 supports 1024x1024, 1792x1024, 1024x1792
        dall_size = "1792x1024" if int(w) > int(h) else "1024x1024"
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"Professional business image for RightLeftAI social media post. {prompt}. Clean, modern, corporate style.",
            size=dall_size,
            quality="standard",
            n=1,
        )
        return response.data[0].url
    except Exception:
        return None


def _pexels(query: str) -> Optional[str]:
    try:
        # Use first 5 words as search query
        search = " ".join(query.split()[:5])
        with httpx.Client(timeout=10) as client:
            r = client.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": settings.PEXELS_API_KEY},
                params={"query": search, "per_page": 1, "orientation": "landscape"},
            )
            data = r.json()
            photos = data.get("photos", [])
            if photos:
                return photos[0]["src"]["large2x"]
    except Exception:
        pass
    return None
