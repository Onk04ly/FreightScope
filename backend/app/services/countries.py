"""REST Countries API client — country metadata for route enrichment."""
from typing import Any

import httpx

_BASE_URL = "https://restcountries.com/v3.1/name"


async def get_country_info(country_name: str) -> dict[str, Any]:
    """Return tariff zone, trade blocks, and region for a country name."""
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(
                f"{_BASE_URL}/{country_name}", params={"fields": "name,region,subregion,tld,cca2"}
            )
            response.raise_for_status()
            data = response.json()
            if data:
                entry = data[0]
                return {
                    "name": entry.get("name", {}).get("common", country_name),
                    "region": entry.get("region", ""),
                    "subregion": entry.get("subregion", ""),
                    "cca2": entry.get("cca2", ""),
                }
        except Exception:
            pass
    return {"name": country_name}
