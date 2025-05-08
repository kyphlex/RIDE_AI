from datetime import datetime, timedelta
import time
from calculations import dist_calc


def safe_distance_calc(origin_lat, origin_lon, dest_lat, dest_lon, max_retries=2):
    for attempt in range(max_retries):
        try:
            result = dist_calc.get_distance_duration(origin_lat, origin_lon, dest_lat, dest_lon)
            if isinstance(result, (list, tuple)) and len(result) >= 2:
                return float(result[1])  # Return ETA in minutes
            return float('inf')
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"API failed for ({origin_lat},{origin_lon})→({dest_lat},{dest_lon}): {str(e)}")
                return float('inf')
            time.sleep(1)  # Wait before retry


def get_best_driver(rider, drivers):
    now = datetime.now()
    best_driver = None
    min_eta = float('inf')
    fallback_drivers = []

    for driver in drivers:
        try:
            if not driver['is_idle']:
                if driver['current_ride_end']:
                    ride_end = (datetime.fromisoformat(driver['current_ride_end'])
                                if isinstance(driver['current_ride_end'], str)
                                else driver['current_ride_end'])
                    if ride_end > now + timedelta(minutes=5):
                        continue

            if not ((rider['ride_type'] == 'solo' and driver['accepts_solo']) or
                    (rider['ride_type'] == 'shared' and driver['accepts_shared'])):
                continue

            if rider['state'] == 'interstate' and not driver['allows_interstate']:
                continue

            if rider['ride_class'] != driver['vehicle_class']:
                continue

            if rider['feature'] != driver['vehicle_type']:
                continue

            # 4. ETA
            eta = safe_distance_calc(
                driver['current_lat'], driver['current_lon'],
                rider['pickup_lat'], rider['pickup_lon']
            )

            # 5. Scheduled ride check
            if rider['is_scheduled'] and rider.get('scheduled_time'):
                scheduled_time = (datetime.fromisoformat(rider['scheduled_time'])
                                  if isinstance(rider['scheduled_time'], str)
                                  else rider['scheduled_time'])
                arrival_time = (ride_end if 'ride_end' in locals() else now) + timedelta(minutes=eta)
                if arrival_time > scheduled_time + timedelta(minutes=5):
                    continue

            if eta < min_eta:
                min_eta = eta
                best_driver = driver

        except Exception as e:
            print(f"Skipping driver {driver.get('driver_id')}: {str(e)}")
            continue

    # === Fallback Clause: Find Closest Driver if No Match ===
    if best_driver is None:
        for driver in drivers:
            try:
                if not driver['is_idle']:
                    continue

                eta = safe_distance_calc(
                    driver['current_lat'], driver['current_lon'],
                    rider['pickup_lat'], rider['pickup_lon']
                )

                # Determine if driver is "premium" (rating ≥ 4.2)
                driver_is_premium = driver.get('rating', 0) >= 4.2

                fallback_drivers.append({
                    "driver": driver,
                    "eta": eta,
                    "is_premium": driver_is_premium,
                    "ride_class_match": rider['ride_class'] == driver['vehicle_class']
                })
            except Exception as e:
                continue

        # Sort fallback options by:
        # 1. Premium drivers first
        # 2. Ride class match
        # 3. Shortest ETA
        if fallback_drivers:
            fallback_drivers.sort(
                key=lambda x: (
                    not x['is_premium'],         # prefer premium
                    not x['ride_class_match'],   # prefer matching class
                    x['eta']                     # then shortest ETA
                )
            )
            best_driver = fallback_drivers[0]['driver']

    return best_driver['driver_id'] if best_driver else None
