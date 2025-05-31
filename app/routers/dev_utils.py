# app/routers/dev_utils.py
from fastapi import APIRouter, Request, Query, HTTPException
from pydantic import BaseModel
from user_agents import parse as ua_parse
import requests  # For external IP info

router = APIRouter()


class UserAgentResponse(BaseModel):
    user_agent_string: str
    browser_family: str
    browser_version: str
    os_family: str
    os_version: str
    device_family: str
    device_brand: str
    device_model: str
    is_mobile: bool
    is_tablet: bool
    is_pc: bool
    is_bot: bool


@router.get("/user-agent", response_model=UserAgentResponse)
async def parse_user_agent(request: Request):
    ua_string = request.headers.get("user-agent", "Unknown")
    user_agent = ua_parse(ua_string)
    return UserAgentResponse(
        user_agent_string=ua_string,
        browser_family=user_agent.browser.family,
        browser_version=user_agent.browser.version_string,
        os_family=user_agent.os.family,
        os_version=user_agent.os.version_string,
        device_family=user_agent.device.family,
        device_brand=user_agent.device.brand,
        device_model=user_agent.device.model,
        is_mobile=user_agent.is_mobile,
        is_tablet=user_agent.is_tablet,
        is_pc=user_agent.is_pc,
        is_bot=user_agent.is_bot
    )


@router.get("/ip-info")
async def get_ip_info(request: Request):
    # Vercel sets specific headers for client IP.
    # 'x-forwarded-for' can contain a list of IPs, client is usually the first.
    # 'x-real-ip' is often set by reverse proxies like Nginx.
    # On Vercel, 'x-vercel-forwarded-for' is reliable for the original client IP.
    client_ip = request.headers.get("x-vercel-forwarded-for") or \
                request.headers.get("x-forwarded-for", "").split(',')[0].strip() or \
                request.client.host

    # Basic info: just the IP
    basic_info = {"ip_address": client_ip}

    # For more detailed info (e.g., geolocation), use a free external API
    # Be mindful of rate limits on free external APIs
    try:
        # Example using ip-api.com (check their terms of use)
        # response = requests.get(f"http://ip-api.com/json/{client_ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query")
        # response.raise_for_status() # Raise an exception for HTTP errors
        # geo_data = response.json()
        # if geo_data.get("status") == "success":
        #     basic_info.update(geo_data)
        # else:
        #     basic_info["geolocation_error"] = geo_data.get("message", "Failed to fetch geolocation data")
        pass  # Keep it simple for now, just returning IP
    except requests.RequestException as e:
        basic_info["geolocation_error"] = f"Error fetching geolocation: {str(e)}"

    return basic_info


HTTP_STATUS_CODES = {
    # ... (Populate with common codes and descriptions)
    200: "OK - The request has succeeded.",
    201: "Created - The request has been fulfilled and resulted in a new resource being created.",
    204: "No Content - The server successfully processed the request and is not returning any content.",
    400: "Bad Request - The server cannot or will not process the request due to something that is perceived to be a client error.",
    401: "Unauthorized - The client must authenticate itself to get the requested response.",
    403: "Forbidden - The client does not have access rights to the content.",
    404: "Not Found - The server can not find the requested resource.",
    500: "Internal Server Error - The server has encountered a situation it doesn't know how to handle."
}


@router.get("/http-status")
async def get_http_status_explainer(code: int = Query(..., example=200, description="HTTP Status Code")):
    explanation = HTTP_STATUS_CODES.get(code)
    if not explanation:
        raise HTTPException(status_code=404, detail=f"Explanation for HTTP status code {code} not found.")

    # Fun addition: link to HTTP Cats/Dogs
    image_cat_url = f"https://http.cat/{code}.jpg"
    # image_dog_url = f"https://http.dog/{code}.jpg" # http.dog seems less reliable or complete

    return {
        "code": code,
        "explanation": explanation,
        "image_url": image_cat_url
    }

# URL Shortener: This is complex for a purely serverless free setup without an external DB.
# A true URL shortener needs persistent storage.
# Vercel KV, Upstash Redis, or Firebase Firestore (free tiers) could be used.
# For a *very* basic, non-persistent demo (resets on deploy):
# temp_short_urls = {}
# @router.post("/url-shortener/create")
# async def create_short_url(long_url: str = Body(..., embed=True)):
#     if not long_url.startswith("http://") and not long_url.startswith("https://"):
#         raise HTTPException(status_code=400, detail="URL must start with http:// or https://")
#     short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
#     temp_short_urls[short_code] = long_url
#     # This short URL will only work if accessed by the same server instance.
#     # On Vercel, each request might hit a different instance.
#     # So this is NOT a reliable shortener.
#     return {"long_url": long_url, "short_code": short_code, "note": "This is a temporary, non-persistent shortener."}

# @router.get("/url-shortener/go/{short_code}")
# async def redirect_short_url(short_code: str):
#     long_url = temp_short_urls.get(short_code)
#     if not long_url:
#         raise HTTPException(status_code=404, detail="Short URL not found or expired.")
#     return RedirectResponse(url=long_url)
# For now, let's comment out the URL shortener or simplify it greatly
# as persistent storage is out of scope for this basic Vercel setup without extra services.