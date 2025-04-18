import requests

zoom_level = int(input('Please select ZOOM level (0: Entire world, 5: Country, 10: City, 12–14: Town/Neighborhood, 15–16: Streets and Landmarks): '))
def get_static_map_image_with_marker(api_key, lat, lon, zoom=zoom_level, size="800x600"):

    base_url = "https://maps.googleapis.com/maps/api/staticmap?"

    params = {
        'center': f"{lat},{lon}",
        'zoom': zoom,
        'size': size,
        'markers': f"{lat},{lon}",
        'key': api_key
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        with open("map_with_marker.png", "wb") as f:
            f.write(response.content)
        print("Map image with marker saved as map_with_marker.png")
    else:
        print("Failed to retrieve map image:", response.status_code)


app_key = "AIzaSyA0ERXgkeSWSQfzrGETFUEHhv7HRGlAlBM"
try:
    latitude = float(input('Latitude: '))
    longitude = float(input('Longitude: '))
    if not (-90 <= latitude <= 90):
        print('Invalid Latitude. Latitude must be between -90 and 90.')
    elif not (-180 <= longitude <= 180):
        print('Invalid Longitude. Longitude must be between -180 and 180.')
    else:
        get_static_map_image_with_marker(app_key, latitude, longitude)

except ValueError:
    print('Latitude/Longitude written in an invalid format.')
