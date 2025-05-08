from fastapi import FastAPI
from pydantic import BaseModel
import requests


app = FastAPI()

GOOGLE_MAPS_API_KEY = "AIzaSyA0ERXgkeSWSQfzrGETFUEHhv7HRGlAlBM"

class Location(BaseModel):
    lat: float
    lon: float

class FareRequest(BaseModel):
    origin: Location
    destination: Location
    ride_type: str
    passengers: int

def is_drivable(lat, lon):
    url = f'https://roads.googleapis.com/v1/snapToRoads?path={lat},{lon}&key={GOOGLE_MAPS_API_KEY}'

    try:
        response = requests.get(url)
        data = response.json()

        if 'snappedPoints' in data and len(data['snappedPoints']) > 0:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking drivable location: {e}")
        return False


def get_distance_duration(origin_lat, origin_lon, dest_lat, dest_lon):
    origin = f"{origin_lat},{origin_lon}"
    destination = f"{dest_lat},{dest_lon}"

    url = f"https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origin,
        "destinations": destination,
        "mode": "driving",
        "departure_time": "now",
        "key": GOOGLE_MAPS_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data['status'] != 'OK':
        raise Exception(f"Error from Google API: {data['status']}")

    try:
        result = data['rows'][0]['elements'][0]
        distance_km = result['distance']['value'] / 1000
        duration_min = result['duration']['value'] / 60
        duration_in_traffic = result.get('duration_in_traffic', result['duration'])['value'] / 60

        traffic = (duration_in_traffic - duration_min) > 5

        return round(distance_km, 2), round(duration_in_traffic, 2), traffic
    except:
        raise Exception("Invalid response from Google API")


