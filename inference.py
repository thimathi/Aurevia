from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

import numpy as np
import torch

from model_loader import ModelRegistry

BURNOUT_RELATED_EMOTIONS = ("sad", "angry", "fear", "disgust")


@dataclass(frozen=True)
class BurnoutScores:
    text_score: float
    voice_score: float
    final_score: float
    burnout_prediction: int


def predict_text_burnout_probability(text: str, registry: ModelRegistry, max_length: int = 256) -> float:
    if not text.strip():
        raise ValueError("Text input cannot be empty")

    encoded = registry.text_tokenizer(
        text,
        truncation=True,
        max_length=max_length,
        padding="max_length",
        return_tensors="pt",
    )
    encoded = {k: v.to(registry.device) for k, v in encoded.items()}

    with torch.no_grad():
        outputs = registry.text_model(**encoded)
        probs = torch.softmax(outputs.logits, dim=-1)

    return float(probs[0, 1].item())


def predict_voice_emotion_probabilities(mel_spectrogram: np.ndarray, registry: ModelRegistry) -> np.ndarray:
    if mel_spectrogram.shape != (1, 128, 128):
        raise ValueError(f"Expected mel spectrogram shape (1, 128, 128), got {mel_spectrogram.shape}")

    tensor = torch.from_numpy(mel_spectrogram).unsqueeze(0).to(registry.device)

    with torch.no_grad():
        logits = registry.voice_model(tensor)
        probs = torch.softmax(logits, dim=-1)

    return probs.squeeze(0).detach().cpu().numpy()


def burnout_score_from_emotions(
    emotion_probabilities: np.ndarray,
    emotion_to_idx: Dict[str, int],
    burnout_emotions: Iterable[str] = BURNOUT_RELATED_EMOTIONS,
) -> float:
    score = 0.0
    for emotion in burnout_emotions:
        idx = emotion_to_idx.get(emotion)
        if idx is None:
            raise KeyError(f"Emotion '{emotion}' is missing in emotion_to_idx mapping")
        score += float(emotion_probabilities[idx])

    return max(0.0, min(1.0, score))


def fuse_scores(text_score: float, voice_score: float, text_weight: float = 0.6, voice_weight: float = 0.4) -> float:
    total = (text_weight * text_score) + (voice_weight * voice_score)
    return max(0.0, min(1.0, float(total)))


def multimodal_burnout_inference(text: str, mel_spectrogram: np.ndarray, registry: ModelRegistry) -> BurnoutScores:
    text_score = predict_text_burnout_probability(text=text, registry=registry)
    emotion_probs = predict_voice_emotion_probabilities(mel_spectrogram=mel_spectrogram, registry=registry)
    voice_score = burnout_score_from_emotions(emotion_probabilities=emotion_probs, emotion_to_idx=registry.emotion_to_idx)
    final_score = fuse_scores(text_score=text_score, voice_score=voice_score)
    prediction = int(final_score >= 0.5)

    return BurnoutScores(
        text_score=text_score,
        voice_score=voice_score,
        final_score=final_score,
        burnout_prediction=prediction,
    )
