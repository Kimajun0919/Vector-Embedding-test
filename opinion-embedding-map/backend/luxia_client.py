import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

LUXIA_EMBEDDING_URL = os.getenv("LUXIA_EMBEDDING_URL", "https://bridge.luxiacloud.com/luxia/v1/embedding")


class LuxiaEmbeddingError(RuntimeError):
    pass


async def get_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    api_key = os.getenv("LUXIA_API_KEY")
    if not api_key:
        raise LuxiaEmbeddingError("LUXIA_API_KEY is missing. Set it in backend/.env.")

    payload: dict[str, Any] = {"inputs": texts}

    headers = {
        "apikey": api_key,
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

    embeddings = _extract_embeddings(body)

    if len(embeddings) != len(texts):
        raise LuxiaEmbeddingError(f"LUXIA returned {len(embeddings)} embeddings for {len(texts)} input texts.")

    if not all(isinstance(vector, list) and vector for vector in embeddings):
        raise LuxiaEmbeddingError("LUXIA returned an empty or invalid embedding vector.")

    return embeddings


def _extract_embeddings(body: dict[str, Any]) -> list[list[float]]:
    if isinstance(body.get("embeddings"), list):
        return body["embeddings"]

    if isinstance(body.get("data"), list):
        data = body["data"]
        if data and isinstance(data[0], dict) and "embedding" in data[0]:
            return [item["embedding"] for item in sorted(data, key=lambda item: item.get("index", 0))]
        if data and isinstance(data[0], list):
            return data

    if isinstance(body.get("result"), list):
        return body["result"]

    raise LuxiaEmbeddingError("LUXIA embedding API response does not include recognizable embeddings.")
