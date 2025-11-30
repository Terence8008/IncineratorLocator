> Install Packages
pip install -r requirements.txt

> Start fastapi server
uvicorn main:app --reload

> Sample Command for curl
curl -X GET "http://127.0.0.1:8000/api/predict?lat=3.07&lon=101.6"
