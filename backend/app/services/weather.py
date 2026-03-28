"""OpenWeatherMap REST client — current weather at a port city."""
from typing import Any

import httpx

from app.config import settings

_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


async def get_weather(city: str) -> dict[str, Any]:
    """Return current weather dict for a city name, or empty dict on error."""
    if not settings.openweather_api_key:
        return {}
    params = {"q": city, "appid": settings.openweather_api_key, "units": "metric"}
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            return {
                "city": city,
                "description": data["weather"][0]["description"],
                "temp_c": data["main"]["temp"],
                "wind_mps": data["wind"]["speed"],
            }
        except Exception:
            return {}
