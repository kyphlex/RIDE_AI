import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import pandas as pd
from calculations import preprocessing, dist_calc

fake = Faker()

LAGOS_BOUNDS = {
    'min_lat': 6.3930,
    'max_lat': 6.7000,
    'min_lon': 2.6500,
    'max_lon': 3.6000
}

def generate_coords():
    while True:
        lat = np.random.uniform(LAGOS_BOUNDS['min_lat'], LAGOS_BOUNDS['max_lat'])
        lon = np.random.uniform(LAGOS_BOUNDS['min_lon'], LAGOS_BOUNDS['max_lon'])

        if dist_calc.is_drivable(lat, lon):
            return lat, lon

def generate_ride_requests(n=50):
    data = []
    for _ in range(n):
        is_scheduled = np.random.choice([True, False], p=[0.2, 0.8])
        scheduled_time = (datetime.now() + timedelta(minutes=np.random.randint(10, 120))) if is_scheduled else None
        pickup_lat, pickup_lon = generate_coords()

        data.append({
            "request_id": f"RQ_{fake.unique.random_number(digits=6)}",
            "ride_type": np.random.choice(["solo", "shared"], p=[0.7, 0.3]),
            "state": np.random.choice(["intrastate", "interstate"], p=[0.8, 0.2]),
            "is_scheduled": is_scheduled,
            "scheduled_time": scheduled_time,
            "is_premium": np.random.choice([True, False], p=[0.3, 0.7]),
            "feature": np.random.choice(["drop", "logistic", "errand"], p=[0.6, 0.3, 0.1]),
            "pickup_lat": pickup_lat,
            "pickup_lon": pickup_lon,
            "is_exclusive": np.random.choice([True, False], p=[0.1, 0.9]),
            "ride_class": np.random.choice(["economy", "business"], p=[0.6, 0.4]),
            "timestamp": fake.date_time_this_month()
        })
    return pd.DataFrame(data)


def generate_drivers(n=10):
    data = []
    for _ in range(n):
        is_idle = np.random.choice([True, False], p=[0.6, 0.4])
        current_ride_end = (datetime.now() + timedelta(minutes=np.random.randint(1, 30))) if not is_idle else None
        current_lat, current_lon = generate_coords()

        data.append({
            "driver_id": f"DR_{fake.unique.random_number(digits=6)}",
            "current_lat": current_lat,
            "current_lon": current_lon,
            "accepts_solo": np.random.choice([True, False], p=[0.8, 0.2]),
            "accepts_shared": np.random.choice([True, False], p=[0.5, 0.5]),
            "allows_interstate": np.random.choice([True, False], p=[0.3, 0.7]),
            "vehicle_type": np.random.choice(["sedan", "truck", "bike"], p=[0.6, 0.3, 0.1]),
            "vehicle_class": np.random.choice(["economy", "business"], p=[0.7, 0.3]),
            "rating": round(np.random.uniform(3.5, 5.0), 1),
            "is_idle": is_idle,
            "current_ride_end": current_ride_end
        })
    return pd.DataFrame(data)


requests_df = generate_ride_requests()
drivers_df = generate_drivers()

requests_df.to_csv("ride_requests.csv", index=False)
drivers_df.to_csv("drivers.csv", index=False)

requests = pd.read_csv("ride_requests.csv").to_dict('records')
drivers = pd.read_csv("drivers.csv").to_dict('records')


matched_data = []

for rider in requests:
    matched_driver_id = preprocessing.get_best_driver(rider, drivers)
    matched_driver = next((d for d in drivers if d['driver_id'] == matched_driver_id), None)
    if not matched_driver:
        continue
    class_match = int(rider['ride_class'] == matched_driver['vehicle_class'])
    distance = dist_calc.get_distance_duration(rider['pickup_lat'], rider['pickup_lon'], matched_driver['current_lat'], matched_driver['current_lon'])

    match_record = {
    'request_id': rider['request_id'],
    'driver_id': matched_driver_id,
    'timestamp': datetime.now().isoformat(),

    'ride_type': rider['ride_type'],
    'ride_class': rider['ride_class'],
    'is_premium': int(rider['is_premium']),
    'is_scheduled': int(rider['is_scheduled']),
    'is_exclusive': int(rider['is_exclusive']),
    'rider_rating': rider.get('feature', 3.0),

    'driver_rating': matched_driver['rating'],
    'vehicle_type': matched_driver['vehicle_type'],
    'vehicle_class': matched_driver['vehicle_class'],
    'allows_interstate': int(matched_driver['allows_interstate']),

    'pickup_lat': rider['pickup_lat'],
    'pickup_lon': rider['pickup_lon'],
    'driver_lat': matched_driver['current_lat'],
    'driver_lon': matched_driver['current_lon'],

    'distance': distance,
    'class_match': class_match
    }

    matched_data.append(match_record)

matches = pd.DataFrame(matched_data)
matches.to_csv("matches.csv", index=False)
