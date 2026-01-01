import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000/api";

/**
 * Service to handle all backend communication
 */
export const SiteService = {
  /**
   * Fetch site suitability and insights
   * @param {number} lat - Latitude of selected point
   * @param {number} lng - Longitude of selected point
   * @param {object} weights - Weights from ScenarioSliders (e.g., {w_pop: 0.25, ...})
   */
  predict: async (lat, lng, weights = {}) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/predict`, {
        params: { 
          latitude: lat, 
          longitude: lng,
          ...weights // This spreads w_pop, w_river, w_road, w_land into the request
        },
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