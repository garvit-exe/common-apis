# app/routers/dev_utils.py
from fastapi import APIRouter, Request, Query, HTTPException
from pydantic import BaseModel, Field
from user_agents import parse as ua_parse
import requests
from datetime import datetime, timezone  # For timestamp

router = APIRouter()


# --- Models (Existing and New) ---
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


class TimestampRequest(BaseModel):
    value: int | str = Field(..., example=1678886400,
                             description="Unix timestamp (integer) or datetime string (YYYY-MM-DD HH:MM:SS)")
    direction: str = Field("from_unix", example="from_unix",
                           description="Conversion direction: 'to_unix' or 'from_unix'")
    timezone_str: str = Field("UTC", example="UTC",
                              description="Timezone for human-readable string (e.g., 'America/New_York', 'UTC')")  # Added timezone awareness


# --- Endpoints (Existing) ---
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
    client_ip = request.headers.get("x-vercel-forwarded-for") or \
                request.headers.get("x-forwarded-for", "").split(',')[0].strip() or \
                request.client.host

    basic_info = {"ip_address": client_ip}
    # External IP lookup can be added here if desired, mindful of rate limits
    # Example:
    # try:
    #     response = requests.get(f"http://ip-api.com/json/{client_ip}?fields=61439", timeout=3) # query,status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as
    #     response.raise_for_status()
    #     geo_data = response.json()
    #     if geo_data.get("status") == "success":
    #         basic_info.update(geo_data)
    # except requests.RequestException:
    #     basic_info["geolocation_error"] = "Could not fetch detailed IP geolocation."
    return basic_info


HTTP_STATUS_CODES = {
    100: "Continue", 101: "Switching Protocols", 102: "Processing",
    200: "OK", 201: "Created", 202: "Accepted", 203: "Non-Authoritative Information", 204: "No Content",
    205: "Reset Content", 206: "Partial Content", 207: "Multi-Status",
    300: "Multiple Choices", 301: "Moved Permanently", 302: "Found", 303: "See Other", 304: "Not Modified",
    305: "Use Proxy", 307: "Temporary Redirect", 308: "Permanent Redirect",
    400: "Bad Request", 401: "Unauthorized", 402: "Payment Required", 403: "Forbidden", 404: "Not Found",
    405: "Method Not Allowed", 406: "Not Acceptable", 407: "Proxy Authentication Required", 408: "Request Timeout",
    409: "Conflict", 410: "Gone", 411: "Length Required", 412: "Precondition Failed", 413: "Payload Too Large",
    414: "URI Too Long", 415: "Unsupported Media Type", 416: "Range Not Satisfiable", 417: "Expectation Failed",
    421: "Misdirected Request", 422: "Unprocessable Entity", 423: "Locked", 424: "Failed Dependency",
    426: "Upgrade Required", 428: "Precondition Required", 429: "Too Many Requests",
    431: "Request Header Fields Too Large", 451: "Unavailable For Legal Reasons",
    500: "Internal Server Error", 501: "Not Implemented", 502: "Bad Gateway", 503: "Service Unavailable",
    504: "Gateway Timeout", 505: "HTTP Version Not Supported", 506: "Variant Also Negotiates",
    507: "Insufficient Storage", 508: "Loop Detected", 510: "Not Extended", 511: "Network Authentication Required"
}


@router.get("/http-status")
async def get_http_status_explainer(code: int = Query(..., example=200, description="HTTP Status Code")):
    explanation = HTTP_STATUS_CODES.get(code)
    if not explanation:
        raise HTTPException(status_code=404, detail=f"Explanation for HTTP status code {code} not found in our list.")

    image_cat_url = f"https://http.cat/{code}.jpg"
    # image_dog_url = f"https://http.dog/{code}.jpg" # Seems less complete

    return {
        "code": code,
        "explanation": explanation,
        "image_url_cat": image_cat_url
    }


# --- New Endpoints ---
@router.post("/timestamp-converter")  # Changed to POST to accept a body easily
async def timestamp_converter(req_data: TimestampRequest):
    value = req_data.value
    direction = req_data.direction.lower()
    # For timezone, we can use pytz if installed and more complex tz are needed.
    # For now, sticking to UTC for from_unix or assuming input string has tz info or is naive UTC.
    # A proper timezone implementation would use `pytz`

    dt_format = "%Y-%m-%d %H:%M:%S"
    human_readable = None
    unix_timestamp = None

    try:
        if direction == "from_unix":
            if not isinstance(value, int):
                raise HTTPException(status_code=400,
                                    detail="For 'from_unix', value must be an integer (Unix timestamp).")
            # Naive datetime object representing UTC
            dt_object_utc = datetime.fromtimestamp(value, tz=timezone.utc)
            human_readable = dt_object_utc.strftime(dt_format) + " UTC"  # Indicate it's UTC
            unix_timestamp = value
        elif direction == "to_unix":
            if not isinstance(value, str):
                raise HTTPException(status_code=400,
                                    detail="For 'to_unix', value must be a datetime string (YYYY-MM-DD HH:MM:SS).")
            # Assuming the input string is naive and represents UTC, or has tzinfo parseable by fromisoformat
            try:
                # Attempt to parse with common format, assuming UTC if naive
                dt_object_naive = datetime.strptime(value, dt_format)
                dt_object_aware = dt_object_naive.replace(tzinfo=timezone.utc)  # Assume UTC
            except ValueError:
                try:
                    # Try ISO format which can include timezone
                    dt_object_aware = datetime.fromisoformat(value)
                    if dt_object_aware.tzinfo is None:  # If still naive after fromisoformat
                        dt_object_aware = dt_object_aware.replace(tzinfo=timezone.utc)  # Assume UTC
                except ValueError:
                    raise HTTPException(status_code=400,
                                        detail=f"Invalid datetime string format. Use '{dt_format}' or ISO 8601 format.")

            unix_timestamp = int(dt_object_aware.timestamp())
            human_readable = dt_object_aware.strftime(dt_format + " %Z%z")  # Show timezone
        else:
            raise HTTPException(status_code=400, detail="Invalid direction. Supported: 'to_unix', 'from_unix'.")
    except OverflowError:
        raise HTTPException(status_code=400, detail="Timestamp value out of range for conversion.")
    except Exception as e:  # Catch any other unexpected errors
        raise HTTPException(status_code=500, detail=f"An error occurred during conversion: {str(e)}")

    return {
        "input_value": value,
        "direction": direction,
        "unix_timestamp": unix_timestamp,
        "human_readable_utc": human_readable.replace("UTC+0000", "UTC").replace("UTC+00:00",
                                                                                "UTC") if human_readable else None,
        "note": "Human readable time is in UTC unless input string specified timezone."
    }


@router.get("/view-headers")
async def view_http_headers(request: Request):
    # Convert headers to a simple dict; Header items can be list-like.
    headers_dict = {k: v for k, v in request.headers.items()}
    return {"headers": headers_dict}