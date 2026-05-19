from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from luxia_client import LuxiaEmbeddingError, get_embeddings
from projection import project_embeddings_umap
from sample_data import SAMPLE_OPINIONS
from similarity import find_top_k_similar


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
    opinions = [item.model_dump() for item in request.opinions] if request and request.opinions else SAMPLE_OPINIONS

    if not opinions:
        raise HTTPException(status_code=400, detail="No opinions were provided.")

    missing_fields = [opinion.get("id", "<unknown>") for opinion in opinions if not opinion.get("text")]
    if missing_fields:
        raise HTTPException(status_code=400, detail=f"Opinions must include text: {missing_fields}")

    texts = [opinion["text"] for opinion in opinions]

    try:
        embeddings = await get_embeddings(texts)
        similar_by_id = find_top_k_similar(opinions, embeddings, k=5)
        coordinates = project_embeddings_umap(embeddings)
    except LuxiaEmbeddingError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc

    analyzed = []
    for opinion, point in zip(opinions, coordinates):
        analyzed.append({
            **opinion,
            "x": point["x"],
            "y": point["y"],
            "similarOpinions": similar_by_id[opinion["id"]],
        })

    return {"opinions": analyzed}
