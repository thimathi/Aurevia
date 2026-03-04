const API_BASE_URL = 'http://localhost:8000';

const formatErrorMessage = async (response) => {
  let detail = 'Request failed. Please try again.';

  try {
    const body = await response.json();
    if (typeof body.detail === 'string') {
      detail = body.detail;
    }
  } catch {
    // ignore non-json errors and keep fallback
  }

  return detail;
};

export const predictBurnout = async ({ text, audioFile }) => {
  const formData = new FormData();
  formData.append('text', text);
  formData.append('audio_file', audioFile);

  const response = await fetch(`${API_BASE_URL}/predict`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(await formatErrorMessage(response));
  }

  return response.json();
};

export const predictTextBurnout = async (text) => {
  const response = await fetch(`${API_BASE_URL}/predict/text`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    throw new Error(await formatErrorMessage(response));
  }

  return response.json();
};
