from __future__ import annotations

import io
from typing import Final

import librosa
import numpy as np

TARGET_SAMPLE_RATE: Final[int] = 16_000
N_MELS: Final[int] = 128
N_FFT: Final[int] = 1024
HOP_LENGTH: Final[int] = 256
SPEC_SHAPE: Final[tuple[int, int]] = (128, 128)
EPS: Final[float] = 1e-8


def extract_log_mel_spectrogram(audio_bytes: bytes) -> np.ndarray:
    """Return normalized log-mel spectrogram in shape [1, 128, 128]."""
    if not audio_bytes:
        raise ValueError("Uploaded audio payload is empty")

    audio_stream = io.BytesIO(audio_bytes)
    signal, _ = librosa.load(audio_stream, sr=TARGET_SAMPLE_RATE, mono=True)

    if signal.size == 0:
        raise ValueError("Audio decoding produced an empty signal")

    mel_spec = librosa.feature.melspectrogram(
        y=signal,
        sr=TARGET_SAMPLE_RATE,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
        n_mels=N_MELS,
        power=2.0,
    )
    log_mel = librosa.power_to_db(mel_spec, ref=np.max)
    fixed_size = librosa.util.fix_length(log_mel, size=SPEC_SHAPE[1], axis=1)

    normalized = (fixed_size - np.mean(fixed_size)) / (np.std(fixed_size) + EPS)
    normalized = normalized.astype(np.float32)

    return np.expand_dims(normalized, axis=0)
