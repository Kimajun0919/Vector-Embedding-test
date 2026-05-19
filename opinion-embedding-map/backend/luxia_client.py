import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

LUXIA_EMBEDDING_URL = os.getenv("LUXIA_EMBEDDING_URL", "https://unifier.lucasai.io/chains/synapses")
LUXIA_MODEL = os.getenv("LUXIA_EMBEDDING_MODEL", "luxia-embedding-small")
LUXIA_APP_NAME = os.getenv("LUXIA_APP_NAME", "opinion-embedding-map")
LUXIA_APP_ID = os.getenv("LUXIA_APP_ID", "opinion-embedding-map-local")


class LuxiaEmbeddingError(RuntimeError):
    pass


async def get_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    api_key = os.getenv("LUXIA_API_KEY")
    if not api_key:
        raise LuxiaEmbeddingError("LUXIA_API_KEY is missing. Set it in backend/.env.")

    payload: dict[str, Any] = {
        "name": LUXIA_APP_NAME,
        "app_id": LUXIA_APP_ID,
        "init_param": {
            "model": LUXIA_MODEL,
            "inputs": texts,
        },
    }

    headers = {
        "api_key": api_key,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(LUXIA_EMBEDDING_URL, headers=headers, json=payload)
            response.raise_for_status()
            body = response.json()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:1000]
        raise LuxiaEmbeddingError(f"LUXIA embedding API returned HTTP {exc.response.status_code}: {detail}") from exc
    except httpx.HTTPError as exc:
        raise LuxiaEmbeddingError(f"LUXIA embedding API request failed: {exc}") from exc
    except ValueError as exc:
        raise LuxiaEmbeddingError("LUXIA embedding API returned invalid JSON.") from exc

    data = body.get("data")
    if not isinstance(data, list):
        raise LuxiaEmbeddingError("LUXIA embedding API response does not include a valid data list.")

    try:
        ordered = sorted(data, key=lambda item: item["index"])
        embeddings = [item["embedding"] for item in ordered]
    except (KeyError, TypeError) as exc:
        raise LuxiaEmbeddingError("LUXIA embedding API response has an unexpected embedding object format.") from exc

    if len(embeddings) != len(texts):
        raise LuxiaEmbeddingError(f"LUXIA returned {len(embeddings)} embeddings for {len(texts)} input texts.")

    if not all(isinstance(vector, list) and vector for vector in embeddings):
        raise LuxiaEmbeddingError("LUXIA returned an empty or invalid embedding vector.")

    return embeddings
