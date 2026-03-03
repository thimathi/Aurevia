const API_BASE_URL = 'http://localhost:8000';

export async function predictBurnout({ text, audioFile }) {
  if (!text?.trim()) {
    throw new Error('Please provide a text sample before submitting.');
  }

  if (!audioFile) {
    throw new Error('Please upload a .wav audio file before submitting.');
  }

  const audioFormData = new FormData();
  audioFormData.append('audio', audioFile);

  const [textResponse, audioResponse] = await Promise.all([
    fetch(`${API_BASE_URL}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    }),
    fetch(`${API_BASE_URL}/predict`, {
      method: 'POST',
      body: audioFormData,
    }),
  ]);

  if (!textResponse.ok || !audioResponse.ok) {
    const textError = !textResponse.ok ? await safeReadError(textResponse) : null;
    const audioError = !audioResponse.ok ? await safeReadError(audioResponse) : null;

    throw new Error(textError || audioError || 'Prediction request failed. Please try again.');
  }

  const [textPayload, audioPayload] = await Promise.all([
    textResponse.json(),
    audioResponse.json(),
  ]);

  const textScore = getScore(textPayload, ['text_burnout_score', 'burnout_score', 'score']);
  const voiceScore = getScore(audioPayload, ['voice_burnout_score', 'burnout_score', 'score']);
  const finalScore =
    getScore(textPayload, ['final_burnout_score']) ??
    getScore(audioPayload, ['final_burnout_score']) ??
    Number(((textScore + voiceScore) / 2).toFixed(4));

  const prediction =
    textPayload?.burnout_prediction ??
    audioPayload?.burnout_prediction ??
    (finalScore >= 0.5 ? 'High' : 'Low');

  return {
    textBurnoutScore: textScore,
    voiceBurnoutScore: voiceScore,
    finalBurnoutScore: finalScore,
    burnoutPrediction: normalizePrediction(prediction),
  };
}

function getScore(payload, keys) {
  for (const key of keys) {
    const value = payload?.[key];
    if (typeof value === 'number') return value;
    if (typeof value === 'string' && !Number.isNaN(Number(value))) {
      return Number(value);
    }
  }
  return 0;
}

function normalizePrediction(value) {
  const normalized = String(value || '').toLowerCase();
  return normalized.includes('high') ? 'High' : 'Low';
}

async function safeReadError(response) {
  try {
    const data = await response.json();
    return data?.detail || data?.message;
  } catch {
    return null;
  }
}
