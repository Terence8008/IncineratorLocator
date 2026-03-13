# Incinerator Location Optimizer App for Malaysia

## Project Overview
This is a Final Year Project (FYP) web-based application that optimizes incinerator placement and waste transport routes in Malaysia. The app uses Geographic Information Systems (GIS) to analyze spatial data, Random Forest for site selection (predicting suitability based on distance to landfills, population density, and environmental risk), and Ant Colony Optimization (ACO) for efficient route planning. It targets regions like Selangor and Johor, helping urban planners, environmental agencies (e.g., DOE), and waste management companies make sustainable decisions.

The project aligns with **SDG 12: Responsible Consumption and Production** (Targets 12.4 and 12.5 for environmentally sound waste management and waste reduction) and the **Basel Convention** principles for hazardous waste (e.g., incinerator ash). It addresses Malaysia's MSW challenges (39,000 tons daily, 142 landfills with only 21 sanitary) by providing an interactive tool for data-driven site selection and routing, reducing environmental impact and operational costs.

## Features
- **Site Selection**: Random Forest model predicts suitability scores for potential incinerator locations.
- **Route Optimization**: ACO calculates optimal waste transport paths from incinerators to landfills.
- **Interactive Map**: Leaflet.js visualization with color-coded sites, heatmaps for population density, and route polylines.
- **User Controls**: Adjust criteria weights (distance, density, risk) and view feature importance from Random Forest.
- **Data Integration**: Open-source sources (OpenStreetMap for roads/landfills, WorldPop for density, IUCN/DOE for environmental risk).

## Technologies
- **Backend**: Flask (Python), Scikit-learn (Random Forest), DEAP (ACO), GeoPandas, NetworkX.
- **Frontend**: HTML/CSS/JavaScript with Leaflet.js for maps.
- **Data Processing**: GeoPandas, Pandas, NumPy.
- **Development Tools**: Python 3.12, Git.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/incinerator-optimizer.git
   cd incinerator-optimizer

> Install Packages
pip install -r requirements.txt

> Start fastapi server at backend(Use (.venv)cmd instead of powershell if not recognized )
uvicorn main:app --reload

> Check online routes
http://127.0.0.1:8000/docs

> Start React APP at frontend
npm start

> Sample Command for curl
curl -X GET "http://127.0.0.1:8000/api/predict?lat=3.07&lon=101.6"
curl "http://localhost:8000/api/check-route-to-landfill?latitude=3.0738&longitude=101.5183"

> Download data:
Selangor roads/landfills from OpenStreetMap (save as data/selangor_roads.geojson and data/selangor_landfills.geojson).
Population density from WorldPop (save as data/selangor_pop_density.tif).
Environmental risk from IUCN or DOE (save as data/selangor_protected_areas.geojson).
Pretrained Random Forest model (models/rf_model.pkl).

# Data Sources
OpenStreetMap: Roads and landfills.
WorldPop: Population density.
IUCN/DOE: Environmental risk.
Simulated labels for Random Forest training.

# Future Work
Expand to Johor or full Peninsular Malaysia.
Add real-time data integration (e.g., traffic via APIs).
Implement user authentication for stakeholders.
Hybrid RF + ACO validation.