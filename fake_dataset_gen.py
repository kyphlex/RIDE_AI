import random
import pandas as pd


# Function to generate random coordinates within a specified range
def random_lat_lon():
    lat = round(random.uniform(6.0, 7.0), 4)  # Latitude between 6.0 and 7.0
    lon = round(random.uniform(3.0, 4.0), 4)  # Longitude between 3.0 and 4.0
    return lat, lon


# Function to generate a random rider profile
def generate_rider():
    ride_types = ['solo', 'shared']
    states = ['intrastate', 'interstate']
    features = ['drop', 'logistic', 'errand']
    classes = ['business', 'economy']
    exclusive_locations = [True, False]

    rider = {
        'ride_type': random.choice(ride_types),
        'state': random.choice(states),
        'premium_ride': random.choice([True, False]),
        'scheduled': random.choice([True, False]),
        'feature': random.choice(features),
        'pickup_lat': random_lat_lon()[0],
        'pickup_lon': random_lat_lon()[1],
        'destination_lat': random_lat_lon()[0],
        'destination_lon': random_lat_lon()[1],
        'exclusive_location': random.choice(exclusive_locations),
        'class': random.choice(classes)
    }

    return rider


# Function to generate a random driver profile
def generate_driver():
    ride_types = ['solo', 'shared']
    states = ['intrastate', 'interstate']
    features = ['drop', 'logistic', 'errand']
    classes = ['business', 'economy']

    driver = {
        'location_lat': random_lat_lon()[0],
        'location_lon': random_lat_lon()[1],
        'ride_type': random.choice(ride_types),
        'state': random.choice(states),
        'rating': round(random.uniform(3.0, 5.0), 1),  # Random driver rating between 3.0 and 5.0
        'class': random.choice(classes),
        'feature': random.choice(features)  # Driver can offer 1 or more features
    }

    return driver


# Generate synthetic data for riders and drivers
num_riders = 100  # Number of rider requests
num_drivers = 50  # Number of available drivers

riders_data = [generate_rider() for _ in range(num_riders)]
drivers_data = [generate_driver() for _ in range(num_drivers)]

# Convert to DataFrame for better visualization
riders_df = pd.DataFrame(riders_data)
drivers_df = pd.DataFrame(drivers_data)

# Display the generated data (optional)
print("Riders Data:")
print(riders_df.head(), "\n")

print("Drivers Data:")
print(drivers_df.head(), "\n")

# Optionally, save to CSV for future use
riders_df.to_csv("riders.csv", index=False)
drivers_df.to_csv("drivers.csv", index=False)
