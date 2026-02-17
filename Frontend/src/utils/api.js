/**
 * API utilities — Urdu Story Generator
 *
 * Fixes addressed:
 *   5A-01: API URL from VITE_API_URL env var
 *   5A-04: SSE streaming via generateTextStream()
 */

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Non-streaming generation (fallback).
 * @param {string} prompt  Urdu prefix text
 * @param {number} maxLength  max tokens to generate
 * @returns {Promise<{story: string, seed_words: string[]}>}
 */
export const generateText = async (prompt, maxLength = 150) => {
  const res = await fetch(`${API_BASE_URL}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prefix: prompt, max_length: maxLength }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to generate story");
  }

  return res.json();
};

/**
 * Streaming generation via SSE.
 *
 * @param {string} prompt      Urdu prefix text
 * @param {(token: string) => void} onToken  called for every decoded chunk
 * @param {number} maxLength   max tokens
 * @returns {Promise<void>}    resolves when stream finishes
 */
export const generateTextStream = async (
  prompt,
  onToken,
  maxLength = 150
) => {
  const res = await fetch(`${API_BASE_URL}/generate/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prefix: prompt, max_length: maxLength }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to generate story");
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // Process complete SSE lines
    const lines = buffer.split("\n");
    buffer = lines.pop(); // keep incomplete line in buffer

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || !trimmed.startsWith("data: ")) continue;

      const payload = trimmed.slice(6); // strip "data: "
      if (payload === "[DONE]") return;

      try {
        const parsed = JSON.parse(payload);
        if (parsed.error) throw new Error(parsed.error);
        if (parsed.token) onToken(parsed.token);
      } catch (e) {
        if (e.message && !e.message.startsWith("Unexpected"))
          throw e;
        // ignore malformed JSON fragments
      }
    }
  }
};
