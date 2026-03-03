from __future__ import annotations

import io
from typing import Final

import librosa
import numpy as np

TARGET_SR: Final[int] = 16_000
N_MELS: Final[int] = 128
TARGET_FRAMES: Final[int] = 128

# Training-time normalization constants (adapt if your training config differs).
MEL_MEAN: Final[float] = -27.0
MEL_STD: Final[float] = 18.0


def _pad_or_trim(mel_spec: np.ndarray, target_frames: int = TARGET_FRAMES) -> np.ndarray:
    current = mel_spec.shape[1]
    if current == target_frames:
        return mel_spec
    if current > target_frames:
        return mel_spec[:, :target_frames]
    pad_width = target_frames - current
    return np.pad(mel_spec, ((0, 0), (0, pad_width)), mode="constant")


def extract_log_mel_spectrogram(audio_bytes: bytes) -> np.ndarray:
    """Convert wav audio bytes to normalized [1, 128, 128] log-mel tensor-ready array."""
    stream = io.BytesIO(audio_bytes)
    signal, _ = librosa.load(stream, sr=TARGET_SR, mono=True)
    if signal.size == 0:
        raise ValueError("Uploaded audio is empty.")

    mel_spec = librosa.feature.melspectrogram(
        y=signal,
        sr=TARGET_SR,
        n_mels=N_MELS,
        n_fft=1024,
        hop_length=256,
        fmin=20,
        fmax=TARGET_SR // 2,
        power=2.0,
    )
    log_mel = librosa.power_to_db(mel_spec, ref=np.max)
    log_mel = _pad_or_trim(log_mel, target_frames=TARGET_FRAMES)

    normalized = (log_mel - MEL_MEAN) / MEL_STD
    normalized = normalized.astype(np.float32)
    return normalized[None, :, :]
