import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1/agri"

def test_create_soil_reading_invalid_user():
    payload = {
        "field_id": "c83b9e4d-f1c0-442c-9ac9-3c5c8ee59d81",
        "location_geojson": {
            "additionalProp1": {}
        },
        "sample_depth_cm": 1,
        "sample_depth_range": "string",
        "moisture_pct": 100,
        "temperature_c": 10,
        "ph": 14,
        "nitrogen_ppm": 10,
        "phosphorus_ppm": 10,
        "potassium_ppm": 10,
        "organic_matter_pct": 100,
        "source": "MANUAL_TEST",
        "lab_name": "string",
        "lab_report_url": "string",
        "recorded_by": "string",
        "recorded_at": "2026-02-14T19:04:20.544Z",
        "weather_conditions": "string",
        "days_since_rain": 10
    }
    
    response = requests.post(f"{BASE_URL}/soil-readings", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    test_create_soil_reading_invalid_user()
