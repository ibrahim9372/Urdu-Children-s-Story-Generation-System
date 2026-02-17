const API_BASE_URL = "http://localhost:8000";

/**
 * Calls the backend API to generate a story continuation.
 * @param {string} prompt - The starting Urdu text.
 * @returns {Promise<{story: string, seed_words: string[]}>} - The generated continuation.
 */
export const generateText = async (prompt) => {
  const response = await fetch(`${API_BASE_URL}/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ prefix: prompt }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to generate story");
  }

  return response.json();
};
