from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
import json

app = FastAPI()

@app.get("/api/tiktok")
async def get_tiktok_profile(request: Request):
    username = request.query_params.get("username")
    if not username:
        return JSONResponse(status_code=400, content={"error": "Username is required"})

    url = f"https://www.tiktok.com/@{username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.tiktok.com/",
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return JSONResponse(status_code=404, content={"error": "User not found or blocked"})

        soup = BeautifulSoup(response.text, "html.parser")
        script_tag = soup.find("script", id="__NEXT_DATA__")
        if not script_tag:
            return JSONResponse(status_code=404, content={"error": "Profile data script not found"})

        data = json.loads(script_tag.string)
        user_data = data["props"]["pageProps"]["userInfo"]["user"]
        stats = data["props"]["pageProps"]["userInfo"]["stats"]

        profile = {
            "username": user_data.get("uniqueId"),
            "displayName": user_data.get("nickname"),
            "avatar": user_data.get("avatarLarger"),
            "bio": user_data.get("signature"),
            "followers": stats.get("followerCount"),
            "following": stats.get("followingCount"),
            "likes": stats.get("heartCount"),
        }
        return JSONResponse(content=profile)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
