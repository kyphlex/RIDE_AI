from datetime import datetime, timedelta
from calculations import dist_calc


def is_driver_available_for_scheduled(driver, pickup, scheduled_time):
    """Check if driver can reach pickup location by scheduled time."""
    driver_lat, driver_lon = driver['current_location']['lat'], driver['current_location']['lon']
    _, eta_minutes = dist_calc.get_distance_duration(driver_lat, driver_lon, pickup['lat'], pickup['lon'])

    # Calculate arrival time considering current ride (if any)
    current_ride_end = driver.get("current_ride_end_time", datetime.now())
    arrival_time = current_ride_end + timedelta(minutes=eta_minutes)

    return arrival_time <= scheduled_time


def filter_eligible_drivers(rider, drivers):
    """Filter drivers who meet all rider constraints."""
    eligible = []
    for driver in drivers:
        driver_prefs = driver['open_to']
        if (rider['ride_type'] in driver_prefs['ride_types'] and
                rider['state'] in driver_prefs['states'] and
                rider['feature'] in driver_prefs['features'] and
                rider['class'] in driver_prefs['classes']):
            eligible.append(driver)
    return eligible


def get_best_driver(rider, drivers):
    """Rule-based driver matching with priority: scheduled > idle > all eligible."""
    pickup = rider['pickup']
    now = datetime.now()

    # --- SCHEDULED RIDES ---
    if rider.get("scheduled") and rider.get("scheduled_time"):
        scheduled_time = rider["scheduled_time"]

        # 1. Drivers who can arrive by scheduled time
        suitable_drivers = [
            d for d in drivers
            if is_driver_available_for_scheduled(d, pickup, scheduled_time)
        ]

        if suitable_drivers:
            # Priority: Earliest available + closest
            best_driver = min(
                suitable_drivers,
                key=lambda d: (
                    (d.get("current_ride_end_time") or now),
                    dist_calc.get_distance_duration(
                        pickup['lat'], pickup['lon'],
                        d['current_location']['lat'], d['current_location']['lon']
                    )[1]
                )
            )
            return best_driver['id']

        # 2. Fallback: Idle drivers if within 10 mins of scheduled time
        if scheduled_time - now <= timedelta(minutes=10):
            idle_drivers = [d for d in drivers if not d.get("current_ride_end_time")]
            if idle_drivers:
                closest_idle = min(
                    idle_drivers,
                    key=lambda d: dist_calc.get_distance_duration(
                        pickup['lat'], pickup['lon'],
                        d['current_location']['lat'], d['current_location']['lon']
                    )[1]
                )
                return closest_idle['id']

        return None

    # --- REAL-TIME RIDES ---
    eligible_drivers = filter_eligible_drivers(rider, drivers)

    # Priority: Idle drivers first
    idle_drivers = [d for d in eligible_drivers if not d.get("current_ride_end_time")]
    if idle_drivers:
        return min(
            idle_drivers,
            key=lambda d: dist_calc.get_distance_duration(
                pickup['lat'], pickup['lon'],
                d['current_location']['lat'], d['current_location']['lon']
            )[1]
        )['id']

    # Fallback: All eligible drivers (even busy ones)
    if eligible_drivers:
        return min(
            eligible_drivers,
            key=lambda d: dist_calc.get_distance_duration(
                pickup['lat'], pickup['lon'],
                d['current_location']['lat'], d['current_location']['lon']
            )[1]
        )['id']

    return None  # No matches