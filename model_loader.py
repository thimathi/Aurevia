from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Tuple

import torch
import torch.nn as nn
from transformers import AutoModelForSequenceClassification, AutoTokenizer, PreTrainedModel, PreTrainedTokenizerBase

LOGGER = logging.getLogger(__name__)


class VoiceEmotionCNN(nn.Module):
    """2D CNN model for 8-class speech emotion recognition on log-mel inputs."""

    def __init__(self, num_classes: int = 8) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((4, 4)),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 4 * 4, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.3),
            nn.Linear(256, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        return self.classifier(x)


EMOTION_LABELS = ["neutral", "calm", "happy", "sad", "angry", "fear", "disgust", "surprise"]


class ModelRegistry:
    """Holds models and metadata loaded once on application startup."""

    def __init__(
        self,
        text_model: PreTrainedModel,
        text_tokenizer: PreTrainedTokenizerBase,
        voice_model: nn.Module,
        device: torch.device,
        emotion_to_idx: Dict[str, int],
    ) -> None:
        self.text_model = text_model
        self.text_tokenizer = text_tokenizer
        self.voice_model = voice_model
        self.device = device
        self.emotion_to_idx = emotion_to_idx


def _load_text_model_and_tokenizer(text_model_dir: Path, device: torch.device) -> Tuple[PreTrainedModel, PreTrainedTokenizerBase]:
    if not text_model_dir.exists():
        raise FileNotFoundError(f"Text model directory not found: {text_model_dir}")

    LOGGER.info("Loading text tokenizer from %s", text_model_dir)
    tokenizer = AutoTokenizer.from_pretrained(str(text_model_dir))

    LOGGER.info("Loading text model from %s", text_model_dir)
    text_model = AutoModelForSequenceClassification.from_pretrained(
        str(text_model_dir),
        num_labels=2,
    )
    text_model.to(device)
    text_model.eval()
    return text_model, tokenizer


def _load_voice_model(voice_weights_path: Path, device: torch.device) -> nn.Module:
    if not voice_weights_path.exists():
        raise FileNotFoundError(f"Voice model weights file not found: {voice_weights_path}")

    LOGGER.info("Loading voice model weights from %s", voice_weights_path)
    model = VoiceEmotionCNN(num_classes=8)
    checkpoint = torch.load(str(voice_weights_path), map_location=device)

    if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
        state_dict = checkpoint["state_dict"]
    else:
        state_dict = checkpoint

    if not isinstance(state_dict, dict):
        raise ValueError("Voice model checkpoint is not a valid state_dict")

    cleaned_state_dict = {
        key.replace("module.", "", 1) if key.startswith("module.") else key: value
        for key, value in state_dict.items()
    }
    model.load_state_dict(cleaned_state_dict, strict=True)
    model.to(device)
    model.eval()
    return model


def load_models(
    text_model_dir: str = "text_model",
    voice_weights_path: str = "voice_model.pth",
) -> ModelRegistry:
    """Load all model artifacts and return a ready-to-use registry."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    LOGGER.info("Using inference device: %s", device)

    text_model, tokenizer = _load_text_model_and_tokenizer(Path(text_model_dir), device)
    voice_model = _load_voice_model(Path(voice_weights_path), device)

    emotion_to_idx = {emotion: idx for idx, emotion in enumerate(EMOTION_LABELS)}

    return ModelRegistry(
        text_model=text_model,
        text_tokenizer=tokenizer,
        voice_model=voice_model,
        device=device,
        emotion_to_idx=emotion_to_idx,
    )
