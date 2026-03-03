from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from inference import fuse_scores, infer_text_score, infer_voice_score
from model_loader import ModelBundle, load_models

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
LOGGER = logging.getLogger("aurevia.api")

app_state: dict[str, Any] = {}


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, description="User-provided text for burnout analysis")

    @field_validator("text")
    @classmethod
    def validate_text_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("text cannot be blank")
        return stripped


class BurnoutResponse(BaseModel):
    text_score: float
    voice_score: float
    final_score: float
    burnout_prediction: int


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        app_state["models"] = load_models(text_model_dir="text_model", voice_model_path="voice_model.pth")
        LOGGER.info("Aurevia backend startup complete.")
        yield
    except Exception:
        LOGGER.exception("Failed to load models during startup.")
        raise
    finally:
        LOGGER.info("Shutting down Aurevia backend.")


app = FastAPI(
    title="Aurevia Burnout Detection API",
    version="1.0.0",
    description="Production-ready multimodal burnout detection backend.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", response_model=BurnoutResponse)
async def predict_burnout(payload: TextRequest, audio: UploadFile = File(...)) -> BurnoutResponse:
    if audio.content_type not in {"audio/wav", "audio/x-wav", "audio/wave"}:
        raise HTTPException(status_code=400, detail="Only WAV audio files are supported.")

    models: ModelBundle | None = app_state.get("models")
    if models is None:
        raise HTTPException(status_code=503, detail="Models are not loaded.")

    try:
        audio_bytes = await audio.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Uploaded audio file is empty.")

        text_score = infer_text_score(payload.text, models.tokenizer, models.text_model, models.device)
        voice_score = infer_voice_score(audio_bytes, models.voice_model, models.device)
        final_score = fuse_scores(text_score, voice_score)
        prediction = int(final_score >= 0.5)

        response = BurnoutResponse(
            text_score=round(text_score, 6),
            voice_score=round(voice_score, 6),
            final_score=round(final_score, 6),
            burnout_prediction=prediction,
        )
        LOGGER.info(
            "Inference complete | text_score=%.4f voice_score=%.4f final_score=%.4f prediction=%d",
            response.text_score,
            response.voice_score,
            response.final_score,
            response.burnout_prediction,
        )
        return response
    except HTTPException:
        raise
    except ValueError as exc:
        LOGGER.warning("Invalid inference input: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        LOGGER.exception("Unexpected inference failure.")
        raise HTTPException(status_code=500, detail="Internal server error during inference.") from exc
