"""
Social media posting tool.
Real API calls when credentials are set; logs to DB in dry-run mode.
"""
import httpx
import json
from config.settings import settings
from datetime import datetime

class LinkedInPoster:
    BASE_URL = "https://api.linkedin.com/v2"

    def post(self, text: str, image_url: str = None) -> Dict:
        if not settings.LINKEDIN_ACCESS_TOKEN:
            return {"status": "dry_run", "message": "LinkedIn token not set — post queued for manual publishing", "content": text[:100]}

        headers = {
            "Authorization": f"Bearer {settings.LINKEDIN_ACCESS_TOKEN}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

        # Use org page if available, else personal
        author = settings.LINKEDIN_ORGANIZATION_URN or settings.LINKEDIN_PERSON_URN
        if not author:
            return {"status": "error", "message": "No LinkedIn URN configured"}

        payload = {
            "author": author,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

        try:
            with httpx.Client(timeout=15) as client:
                response = client.post(f"{self.BASE_URL}/ugcPosts", headers=headers, json=payload)
                if response.status_code in (200, 201):
                    return {"status": "posted", "post_id": response.headers.get("x-restli-id", ""), "platform": "linkedin"}
                return {"status": "error", "code": response.status_code, "detail": response.text[:200]}
        except Exception as e:
            return {"status": "error", "message": str(e)}


class FacebookPoster:
    BASE_URL = "https://graph.facebook.com/v21.0"

    def post(self, text: str, image_url: str = None) -> dict:
        if not settings.FACEBOOK_PAGE_ACCESS_TOKEN or not settings.FACEBOOK_PAGE_ID:
            return {"status": "dry_run", "message": "Facebook credentials not set", "content": text[:100]}

        try:
            endpoint = f"{self.BASE_URL}/{settings.FACEBOOK_PAGE_ID}/feed"
            payload = {"message": text, "access_token": settings.FACEBOOK_PAGE_ACCESS_TOKEN}

            with httpx.Client(timeout=15) as client:
                response = client.post(endpoint, data=payload)
                data = response.json()
                if "id" in data:
                    return {"status": "posted", "post_id": data["id"], "platform": "facebook"}
                return {"status": "error", "detail": str(data)[:200]}
        except Exception as e:
            return {"status": "error", "message": str(e)}


class InstagramPoster:
    BASE_URL = "https://graph.facebook.com/v21.0"

    def post(self, caption: str, image_url: str = None) -> dict:
        if not settings.INSTAGRAM_ACCESS_TOKEN or not settings.INSTAGRAM_BUSINESS_ACCOUNT_ID:
            return {"status": "dry_run", "message": "Instagram credentials not set", "content": caption[:100]}

        if not image_url:
            return {"status": "skipped", "message": "Instagram requires an image URL"}

        try:
            acct_id = settings.INSTAGRAM_BUSINESS_ACCOUNT_ID
            token = settings.INSTAGRAM_ACCESS_TOKEN

            with httpx.Client(timeout=15) as client:
                # Step 1: Create media container
                r1 = client.post(
                    f"{self.BASE_URL}/{acct_id}/media",
                    data={"image_url": image_url, "caption": caption, "access_token": token}
                )
                creation_id = r1.json().get("id")
                if not creation_id:
                    return {"status": "error", "detail": r1.text[:200]}

                # Step 2: Publish
                r2 = client.post(
                    f"{self.BASE_URL}/{acct_id}/media_publish",
                    data={"creation_id": creation_id, "access_token": token}
                )
                data = r2.json()
                if "id" in data:
                    return {"status": "posted", "post_id": data["id"], "platform": "instagram"}
                return {"status": "error", "detail": str(data)[:200]}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Type fix
from typing import Dict
