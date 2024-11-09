import requests
import csv
import time

# Define the API endpoint
url = "https://api.weather.gov/alerts/active"

# Define the desired event types (for filtering later)
event_types = [
    "Fire Warning", "Fire Weather Watch", "Flash Flood Warning", "Flash Flood Watch", "Flood Warning",
    "Flood Watch", "Hazardous Materials Warning", "Heat Advisory", "Hurricane Warning", "Hurricane Watch",
    "Severe Thunderstorm Warning", "Severe Thunderstorm Watch", "Tornado Warning", "Tornado Watch",
    "Winter Storm Warning", "Winter Storm Watch", "Winter Weather Advisory"
]

# Function to fetch weather data with pagination
def fetch_alerts(url):
    alerts = []
    while url:
        print(f"Fetching data from: {url}")
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Error fetching data. Status code: {response.status_code}")
            break

        data = response.json()
        alerts.extend(data.get("features", []))

        # Check if there is a next page
        url = data.get("links", {}).get("next", None)  # Get the next page URL if it exists
        
        if not url:
            print("No more pages to fetch.")
    
    print(f"Total alerts fetched: {len(alerts)}")
    return alerts

# Fetch all alerts with pagination
alerts = fetch_alerts(url)

# Check if any alerts were found
if not alerts:
    print("No alerts found.")
else:
    print("Alerts fetched, filtering by event type...")
    
    # Filter alerts by event type
    filtered_alerts = []
    for feature in alerts:
        properties = feature.get("properties", {})
        event = properties.get("event", "")
        
        # Log the event types found in the data
        if event not in event_types:
            print(f"Found event not in list: {event}")

        if event in event_types:
            filtered_alerts.append(feature)
    
    print(f"Total alerts after filtering by event type: {len(filtered_alerts)}")
    
    # Open a CSV file for writing
    with open("weather_a5.csv", "w", newline="") as csvfile:
        # Create a CSV writer object
        writer = csv.writer(csvfile)

        # Write header row
        writer.writerow([
            "type", "Area Desc", "polygon-coordinates", "affected_zones", "affected_zone-coordinates", "effective", 
            "onset", "expires", "ends", "Status", "message type", "Category", "Severity", "Certainty", "Urgency", "event"
        ])

        # Extract and write filtered alert data
        for feature in filtered_alerts:
            properties = feature.get("properties", {})
            geometry = feature.get("geometry", {})

            # Extract coordinates from geometry if available (main alert area)
            polygon_coordinates = None
            if geometry and geometry.get("type") == "Polygon":
                polygon_coordinates = geometry.get("coordinates", [])[0]  # Get the first polygon (coordinates)

            # Extract coordinates for affected zones (if available)
            affected_zone_coordinates = []
            affected_zones = properties.get("affectedZones", [])
            if affected_zones:
                for zone_url in affected_zones:
                    zone_response = requests.get(zone_url)
                    if zone_response.status_code == 200:
                        zone_data = zone_response.json()
                        zone_geometry = zone_data.get("geometry", {})
                        if zone_geometry.get("type") == "Polygon":
                            affected_zone_coordinates.append(zone_geometry.get("coordinates", [])[0])
                        else:
                            print(f"Warning: Zone {zone_url} does not contain a valid Polygon geometry.")
                    else:
                        print(f"Failed to fetch affected zone data from {zone_url}, status code {zone_response.status_code}")
                    time.sleep(0.1)  # Add a small delay between requests to avoid hitting rate limits

            # Log if we have any missing data
            missing_fields = []
            if not polygon_coordinates:
                missing_fields.append("polygon-coordinates")
            if not affected_zone_coordinates:
                missing_fields.append("affected_zone-coordinates")
            if not affected_zones:
                missing_fields.append("affected_zones")

            if missing_fields:
                print(f"Warning: Missing fields for alert ID {properties.get('id')}: {', '.join(missing_fields)}")

            # Write data to CSV with error handling for missing fields
            try:
                writer.writerow([
                    properties.get("type", "N/A"),
                    properties.get("areaDesc", "N/A"),
                    polygon_coordinates,  # Coordinates of the alert (main area)
                    affected_zones,  # List of affected zone URLs
                    affected_zone_coordinates,  # Coordinates for affected zones
                    properties.get("effective", "N/A"),
                    properties.get("onset", "N/A"),
                    properties.get("expires", "N/A"),
                    properties.get("ends", "N/A"),
                    properties.get("status", "N/A"),
                    properties.get("messageType", "N/A"),
                    properties.get("category", "N/A"),
                    properties.get("severity", "N/A"),
                    properties.get("certainty", "N/A"),
                    properties.get("urgency", "N/A"),
                    properties.get("event", "N/A")
                ])
            except KeyError as e:
                print(f"Missing field: {e}")
                # Write default values if a field is missing
                writer.writerow([
                    "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
                ])

    print("Weather alerts successfully written to weather_alerts.csv")
