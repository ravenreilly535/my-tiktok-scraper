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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.tiktok.com/",
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return JSONResponse(status_code=404, content={"error": "User not found or blocked"})

        soup = BeautifulSoup(response.text, "html.parser")

        # TikTok ka data ab "window['SIGI_STATE']" JS variable me hota hai.
        scripts = soup.find_all("script")
        sigi_state = None
        for script in scripts:
            if script.string and "window['SIGI_STATE']" in script.string:
                # JS code hota hai: window['SIGI_STATE']={...json...};
                raw = script.string
                start = raw.find("window['SIGI_STATE']=") + len("window['SIGI_STATE']=")
                end = raw.rfind(";")
                json_str = raw[start:end].strip()
                sigi_state = json.loads(json_str)
                break

        if not sigi_state:
            return JSONResponse(status_code=404, content={"error": "Profile data script not found"})

        user_info = sigi_state.get("UserModule", {}).get("users", {})
        stats_info = sigi_state.get("UserModule", {}).get("stats", {})

        user = user_info.get(username)
        stats = stats_info.get(username)

        if not user or not stats:
            return JSONResponse(status_code=404, content={"error": "User or stats data not found"})

        profile = {
            "username": username,
            "displayName": user.get("nickname"),
            "avatar": user.get("avatarLarger"),
            "bio": user.get("signature"),
            "followers": stats.get("followerCount"),
            "following": stats.get("followingCount"),
            "likes": stats.get("heart"),
        }

        return JSONResponse(content=profile)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
