import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from geopy.distance import geodesic

# Create a function to calculate distance between two lat/lon points
def calculate_distance(loc1, loc2):
    return geodesic(loc1, loc2).km


riders = pd.read_csv('riders.csv')
drivers = pd.read_csv('drivers.csv')


# One-hot encode categorical features
encoder = OneHotEncoder(sparse_output=False)

riders_encoded = encoder.fit_transform(riders[['ride_type', 'state', 'feature', 'class']])
drivers_encoded = encoder.transform(drivers[['ride_type', 'state', 'feature', 'class']])

#print(riders_encoded)
print(drivers_encoded)