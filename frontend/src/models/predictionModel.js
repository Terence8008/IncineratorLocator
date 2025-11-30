// models/predictionModel.js
import { API_URL } from "../config";

export async function fetchPrediction(lat, lon) {
  const response = await fetch(`${API_URL}/api/predict?lat=${lat}&lon=${lon}`);

  if (!response.ok) {
    throw new Error("Failed to get prediction");
  }

  return await response.json();
}
