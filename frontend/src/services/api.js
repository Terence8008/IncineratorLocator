import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000/api";

/**
 * Service to handle all backend communication
 */
export const SiteService = {
  // Fetch site suitability and insights
  predict: async (lat, lng) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/predict`, {
        params: { latitude: lat, longitude: lng },
      });
      return response.data;
    } catch (err) {
      console.error("Prediction API Error:", err.response?.data || err.message);
      throw err;
    }
  },

  // Get the URL for the heatmap layers
  getLayerUrl: (layerName) => {
    return `${API_BASE_URL}/layers/${layerName}`;
  }
};