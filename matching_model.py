# Convert to dataframes
riders_encoded_df = pd.DataFrame(riders_encoded, columns=encoder.get_feature_names_out())
drivers_encoded_df = pd.DataFrame(drivers_encoded, columns=encoder.get_feature_names_out())

# Calculate distances between rider's pickup and driver's location
riders['driver_distance'] = [calculate_distance((riders.loc[i, 'pickup_lat'], riders.loc[i, 'pickup_lon']), (drivers.loc[i, 'current_lat'], drivers.loc[i, 'current_lon'])) for i in range(len(riders))]

# Calculate distances between rider's destination and driver's location
riders['destination_distance'] = [calculate_distance((riders.loc[i, 'destination_lat'], riders.loc[i, 'destination_lon']), (drivers.loc[i, 'current_lat'], drivers.loc[i, 'current_lon'])) for i in range(len(riders))]

# Add one-hot encoded features back into the riders dataframe
riders = pd.concat([riders, riders_encoded_df], axis=1)
drivers = pd.concat([drivers, drivers_encoded_df], axis=1)

# Now the data is ready for the model training!

print(riders.head())
print(drivers.head())


