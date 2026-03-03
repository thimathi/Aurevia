from __future__ import annotations

import logging
from typing import Final

import numpy as np
import torch
from transformers import PreTrainedModel, PreTrainedTokenizerBase

from model_loader import VoiceEmotionCNN
from utils.audio_processing import extract_log_mel_spectrogram

LOGGER = logging.getLogger(__name__)

EMOTION_LABELS: Final[list[str]] = [
    "neutral",
    "calm",
    "happy",
    "sad",
    "angry",
    "fear",
    "disgust",
    "surprise",
]
BURNOUT_EMOTIONS: Final[set[str]] = {"sad", "angry", "fear", "disgust"}


def infer_text_score(
    text: str,
    tokenizer: PreTrainedTokenizerBase,
    text_model: PreTrainedModel,
    device: torch.device,
) -> float:
    """Return burnout probability from text classifier."""
    encoded = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=256,
        padding="max_length",
    )
    encoded = {k: v.to(device) for k, v in encoded.items()}

    with torch.no_grad():
        logits = text_model(**encoded).logits
        probs = torch.softmax(logits, dim=-1)

    burnout_prob = probs.squeeze(0)[1].item()
    return float(burnout_prob)


def infer_voice_score(audio_bytes: bytes, voice_model: VoiceEmotionCNN, device: torch.device) -> float:
    """Return burnout-related emotion probability score from voice model."""
    mel = extract_log_mel_spectrogram(audio_bytes)
    tensor = torch.from_numpy(mel).unsqueeze(0).to(device)  # [B, 1, 128, 128]

    with torch.no_grad():
        logits = voice_model(tensor)
        probs = torch.softmax(logits, dim=-1).squeeze(0).cpu().numpy()

    emotion_prob_map = dict(zip(EMOTION_LABELS, probs.tolist(), strict=True))
    burnout_prob = float(sum(prob for emo, prob in emotion_prob_map.items() if emo in BURNOUT_EMOTIONS))
    LOGGER.debug("Voice emotion probabilities: %s", emotion_prob_map)
    return float(np.clip(burnout_prob, 0.0, 1.0))


def fuse_scores(text_score: float, voice_score: float) -> float:
    """Multimodal weighted fusion."""
    return float((0.6 * text_score) + (0.4 * voice_score))
