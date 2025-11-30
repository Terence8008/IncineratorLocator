// controllers/predictionController.js
import { fetchPrediction } from "../models/predictionModel";

export async function getPredictionController(lat, lon, setLoading, setResult, setError) {
  try {
    setLoading(true);
    setError(null);

    const result = await fetchPrediction(lat, lon);

    setResult({
      score: result.prediction,
      features: result.features
    });
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
}
