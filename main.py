from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from inference import BurnoutScores, multimodal_burnout_inference, predict_text_burnout_probability
from model_loader import ModelRegistry, load_models
from utils.audio_processing import extract_log_mel_spectrogram

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
LOGGER = logging.getLogger("aurevia.backend")


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, description="User text input for burnout classification")


class BurnoutResponse(BaseModel):
    text_score: float
    voice_score: float
    final_score: float
    burnout_prediction: int


class TextOnlyResponse(BaseModel):
    text_score: float


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        LOGGER.info("Loading model artifacts at startup")
        app.state.registry = load_models(text_model_dir="text_model", voice_weights_path="voice_model.pth")
        LOGGER.info("Model artifacts loaded successfully")
    except Exception as exc:  # pragma: no cover - fatal startup path
        LOGGER.exception("Failed to load model artifacts: %s", exc)
        raise

    yield


app = FastAPI(title="Aurevia Burnout Detection API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _registry() -> ModelRegistry:
    registry: ModelRegistry | None = getattr(app.state, "registry", None)
    if registry is None:
        raise RuntimeError("Model registry is not initialized")
    return registry


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict/text", response_model=TextOnlyResponse, tags=["inference"])
def predict_text_only(payload: TextRequest) -> TextOnlyResponse:
    try:
        text_score = predict_text_burnout_probability(text=payload.text, registry=_registry())
        return TextOnlyResponse(text_score=text_score)
    except ValueError as exc:
        LOGGER.warning("Invalid text payload: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        LOGGER.exception("Unexpected text inference error: %s", exc)
        raise HTTPException(status_code=500, detail="Text inference failed") from exc


@app.post("/predict", response_model=BurnoutResponse, tags=["inference"])
async def predict_multimodal(
    text: str = Form(..., min_length=1),
    audio_file: UploadFile = File(...),
) -> BurnoutResponse:
    if not audio_file.filename.lower().endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only .wav files are supported")

    try:
        audio_bytes = await audio_file.read()
        mel_spectrogram = extract_log_mel_spectrogram(audio_bytes)
        scores: BurnoutScores = multimodal_burnout_inference(
            text=text,
            mel_spectrogram=mel_spectrogram,
            registry=_registry(),
        )
        return BurnoutResponse(**scores.__dict__)
    except ValueError as exc:
        LOGGER.warning("Invalid multimodal payload: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        LOGGER.exception("Unexpected multimodal inference error: %s", exc)
        raise HTTPException(status_code=500, detail="Multimodal inference failed") from exc


@app.exception_handler(RuntimeError)
async def runtime_error_handler(_: Request, exc: RuntimeError) -> JSONResponse:
    LOGGER.exception("Runtime error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Application runtime error"})
