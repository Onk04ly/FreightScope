import asyncio
import base64
from pathlib import Path
from typing import Any

import httpx

from app.config import settings

HF_API_BASE = "https://api-inference.huggingface.co/models"
_MAX_RETRIES = 5
_RETRY_SLEEP = 20  # seconds — HF returns 503 while model loads


async def infer(model_id: str, payload: dict[str, Any]) -> Any:
    """Call the HF Inference API. Retries on 503 (model loading)."""
    url = f"{HF_API_BASE}/{model_id}"
    headers = {"Authorization": f"Bearer {settings.hf_api_key}"}

    async with httpx.AsyncClient(timeout=60) as client:
        for attempt in range(_MAX_RETRIES):
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code == 503:
                # Model is loading — wait and retry
                await asyncio.sleep(_RETRY_SLEEP * (attempt + 1))
                continue
            response.raise_for_status()
            return response.json()

    raise RuntimeError(f"HF model {model_id} unavailable after {_MAX_RETRIES} retries")


async def infer_image(model_id: str, image_path: str) -> Any:
    """Send a binary image file to the HF Inference API."""
    url = f"{HF_API_BASE}/{model_id}"
    headers = {
        "Authorization": f"Bearer {settings.hf_api_key}",
        "Content-Type": "application/octet-stream",
    }
    image_bytes = Path(image_path).read_bytes()

    async with httpx.AsyncClient(timeout=60) as client:
        for attempt in range(_MAX_RETRIES):
            response = await client.post(url, headers=headers, content=image_bytes)
            if response.status_code == 503:
                await asyncio.sleep(_RETRY_SLEEP * (attempt + 1))
                continue
            response.raise_for_status()
            return response.json()

    raise RuntimeError(f"HF model {model_id} unavailable after {_MAX_RETRIES} retries")
