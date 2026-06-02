from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from analysis_pipeline import analyze_opinion_embeddings
from luxia_client import LuxiaEmbeddingError, get_embeddings
from sample_data import SAMPLE_OPINIONS


class Opinion(BaseModel):
    id: str
    text: str
    responseType: str
    category: str


class AnalyzeRequest(BaseModel):
    opinions: Optional[list[Opinion]] = Field(default=None)


app = FastAPI(title="Civic Opinion Embedding Map")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/sample-opinions")
async def get_sample_opinions():
    return {"opinions": SAMPLE_OPINIONS}


@app.post("/api/analyze-opinions")
async def analyze_opinions(request: Optional[AnalyzeRequest] = None):
    if request is not None and request.opinions is not None:
        opinions = [item.model_dump() for item in request.opinions]
    else:
        opinions = SAMPLE_OPINIONS

    if not opinions:
        return analyze_opinion_embeddings([], [])

    missing_fields = [opinion.get("id", "<unknown>") for opinion in opinions if not opinion.get("text")]
    if missing_fields:
        raise HTTPException(status_code=400, detail=f"Opinions must include text: {missing_fields}")

    texts = [opinion["text"] for opinion in opinions]

    try:
        embeddings = await get_embeddings(texts)
        return analyze_opinion_embeddings(opinions, embeddings)
    except LuxiaEmbeddingError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc
