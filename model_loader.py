from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import torch
from torch import nn
from transformers import AutoModelForSequenceClassification, AutoTokenizer, PreTrainedModel, PreTrainedTokenizerBase

LOGGER = logging.getLogger(__name__)


class VoiceEmotionCNN(nn.Module):
    """CNN architecture for 8-class RAVDESS voice emotion classification."""

    def __init__(self, num_classes: int = 8) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
            nn.Dropout(0.2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
            nn.Dropout(0.25),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
            nn.Dropout(0.3),
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((4, 4)),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 4 * 4, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.4),
            nn.Linear(256, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        return self.classifier(x)


@dataclass(frozen=True)
class ModelBundle:
    tokenizer: PreTrainedTokenizerBase
    text_model: PreTrainedModel
    voice_model: VoiceEmotionCNN
    device: torch.device


def _resolve_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def load_models(
    text_model_dir: str | Path = "text_model",
    voice_model_path: str | Path = "voice_model.pth",
) -> ModelBundle:
    """Load and return all models needed for multimodal inference."""
    text_model_dir = Path(text_model_dir)
    voice_model_path = Path(voice_model_path)

    if not text_model_dir.exists():
        raise FileNotFoundError(f"Text model directory not found: {text_model_dir}")
    if not voice_model_path.exists():
        raise FileNotFoundError(f"Voice model weights not found: {voice_model_path}")

    device = _resolve_device()
    LOGGER.info("Using compute device: %s", device)

    tokenizer = AutoTokenizer.from_pretrained(text_model_dir)
    text_model = AutoModelForSequenceClassification.from_pretrained(text_model_dir, num_labels=2)
    text_model.to(device)
    text_model.eval()

    voice_model = VoiceEmotionCNN(num_classes=8)
    state = torch.load(voice_model_path, map_location=device)
    if isinstance(state, dict) and "state_dict" in state:
        state = state["state_dict"]
    voice_model.load_state_dict(state)
    voice_model.to(device)
    voice_model.eval()

    LOGGER.info("Models loaded successfully from %s and %s", text_model_dir, voice_model_path)
    return ModelBundle(tokenizer=tokenizer, text_model=text_model, voice_model=voice_model, device=device)
