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
