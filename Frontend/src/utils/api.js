
/**
 * Simulates a call to the backend Trigram model.
 * @param {string} prompt - The starting Urdu text.
 * @returns {Promise<string>} - The generated continuation text.
 */
export const generateText = async (prompt) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // Mock response: A continuation of the prompt in Urdu
      // In a real scenario, this would be the response from the Flask/FastAPI backend
      const mockResponse = " ایک دفعہ کا ذکر ہے کہ ایک جنگل میں ایک شیر رہتا تھا۔ وہ بہت بہادر تھا۔ سب جانور اس سے ڈرتے تھے۔";
      resolve(mockResponse);
    }, 1500); // Simulate network delay
  });
};
