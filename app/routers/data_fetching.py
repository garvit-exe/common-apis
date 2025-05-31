# app/routers/data_fetching.py
import json
from pathlib import Path
from fastapi import APIRouter, Query, HTTPException
from datetime import datetime
import pytz  # For timezone conversion
import holidays  # For holiday calendar

router = APIRouter()

DATA_PATH = Path(__file__).parent.parent / "data"


def load_json_data(filename: str):
    try:
        with open(DATA_PATH / filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None  # Indicate that data is missing


countries_data_simplified = load_json_data("countries_simplified.json")


# Create `app/data/countries_simplified.json` with a few entries:
# [
#   {"name": "United States", "capital": "Washington D.C.", "currency": "USD", "iso2": "US"},
#   {"name": "Canada", "capital": "Ottawa", "currency": "CAD", "iso2": "CA"}
# ]

@router.get("/country-info")
async def get_country_info(
        country_name: str = Query(None, description="Full name of the country (e.g., United States)"),
        country_code_iso2: str = Query(None, description="ISO2 country code (e.g., US)")):
    if not countries_data_simplified:
        raise HTTPException(status_code=503, detail="Country data is currently unavailable.")
    if not country_name and not country_code_iso2:
        raise HTTPException(status_code=400, detail="Please provide either country_name or country_code_iso2.")

    found_country = None
    if country_name:
        for country in countries_data_simplified:
            if country["name"].lower() == country_name.lower():
                found_country = country
                break
    elif country_code_iso2:
        for country in countries_data_simplified:
            if country.get("iso2", "").lower() == country_code_iso2.lower():
                found_country = country
                break

    if not found_country:
        raise HTTPException(status_code=404, detail="Country not found in our simplified dataset.")
    return found_country


@router.get("/timezones")
async def list_timezones():
    return {"timezones": pytz.common_timezones}


@router.get("/time/convert")
async def convert_timezone(
        dt_str: str = Query(None,
                            description="Datetime string (YYYY-MM-DD HH:MM:SS). If None, current UTC time is used."),
        from_tz: str = Query("UTC", description="Source timezone (e.g., 'America/New_York')"),
        to_tz: str = Query("UTC", description="Target timezone (e.g., 'Europe/London')")
):
    try:
        source_tz = pytz.timezone(from_tz)
    except pytz.UnknownTimeZoneError:
        raise HTTPException(status_code=400, detail=f"Unknown source timezone: {from_tz}")
    try:
        target_tz = pytz.timezone(to_tz)
    except pytz.UnknownTimeZoneError:
        raise HTTPException(status_code=400, detail=f"Unknown target timezone: {to_tz}")

    if dt_str:
        try:
            naive_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid datetime format. Use YYYY-MM-DD HH:MM:SS")
        source_dt = source_tz.localize(naive_dt)
    else:
        source_dt = datetime.now(source_tz)  # If no dt_str, use current time in from_tz

    target_dt = source_dt.astimezone(target_tz)

    return {
        "source_datetime": source_dt.strftime("%Y-%m-%d %H:%M:%S %Z%z"),
        "source_timezone": from_tz,
        "target_datetime": target_dt.strftime("%Y-%m-%d %H:%M:%S %Z%z"),
        "target_timezone": to_tz,
    }


@router.get("/holidays")
async def get_public_holidays(
        country_code: str = Query(..., min_length=2, max_length=2, example="US",
                                  description="Two-letter ISO country code (e.g., US, CA, GB)."),
        year: int = Query(datetime.now().year, ge=1950, le=2050, description="Year for holidays.")
):
    try:
        # The 'holidays' library uses country codes directly.
        # Some countries might need subdivisions (e.g., US states, Canadian provinces)
        # For simplicity, we're not handling subdivisions here.
        country_holidays = holidays.CountryHoliday(country_code.upper(), years=year)
    except KeyError:  # holidays library raises KeyError for unknown country codes
        raise HTTPException(status_code=404,
                            detail=f"Holiday data not available for country code: {country_code}. Check supported codes.")

    if not country_holidays:
        return {"country_code": country_code, "year": year, "holidays": [],
                "message": "No holidays found or country not supported extensively."}

    holiday_list = [{"date": date.isoformat(), "name": name} for date, name in sorted(country_holidays.items())]
    return {"country_code": country_code, "year": year, "holidays": holiday_list}