
const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

async function request(endpoint, options = {}) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });
  } catch {
    throw new Error(
      "Cannot connect to the backend. Make sure FastAPI is running at http://127.0.0.1:8000."
    );
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message =
      data.message ||
      data.detail ||
      data.error ||
      `Request failed with status ${response.status}.`;

    throw new Error(
      typeof message === "string" ? message : JSON.stringify(message)
    );
  }

  return data;
}

export function createSession() {
  return request("/sessions", {
    method: "POST",
  });
}

export function analyzeCode({ language, code, sessionId }) {
  return request("/analyze-code", {
    method: "POST",
    body: JSON.stringify({
      language: language.toLowerCase(),
      code,
      ...(sessionId ? { session_id: sessionId } : {}),
    }),
  });
}

export function generateExercises({
  language,
  code,
  analysis,
  sessionId,
  count = 3,
}) {
  return request("/generate-exercises", {
    method: "POST",
    body: JSON.stringify({
      language: language.toLowerCase(),
      code,
      analysis,
      count,
      ...(sessionId ? { session_id: sessionId } : {}),
    }),
  });
}

export function evaluateExercise({
  language,
  exercise,
  answer,
  sessionId,
}) {
  return request("/evaluate-exercise", {
    method: "POST",
    body: JSON.stringify({
      language: language.toLowerCase(),
      exercise,
      answer,
      ...(sessionId ? { session_id: sessionId } : {}),
    }),
  });
}

export function getSessionReport(sessionId) {
  return request(`/sessions/${encodeURIComponent(sessionId)}/report`);
}
