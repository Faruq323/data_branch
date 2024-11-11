import requests
import csv
import time
from decimal import Decimal, InvalidOperation

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
        print(f"Fetching data from: {url}")  # Debugging: show URL being requested
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Error fetching data. Status code: {response.status_code}")
            break

        data = response.json()
        print(f"API Response: {data}")  # Debugging: print raw API response

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
    print(f"Fetched {len(alerts)} alerts, filtering by event type...")

    # Filter alerts by event type (optional for debugging)
    filtered_alerts = []
    for feature in alerts:
        properties = feature.get("properties", {})
        event = properties.get("event", "")

        # Log all event types found in the data (for debugging)
        if event not in event_types:
            print(f"Found event not in list: {event}")
        
        # If event type is in the allowed list, keep the alert
        if event in event_types:
            filtered_alerts.append(feature)

    print(f"Total alerts after filtering by event type: {len(filtered_alerts)}")

    # If no alerts remain after filtering, print a message
    if not filtered_alerts:
        print("No alerts after filtering by event type.")
    else:
        print(f"Writing {len(filtered_alerts)} alerts to CSV...")

        # Open a CSV file for writing
        with open("weather_a10.csv", "w", newline="") as csvfile:
            # Create a CSV writer object
            writer = csv.writer(csvfile)

            # Write header row
            writer.writerow([
                "Area Desc", "polygon-coordinates", "affected_zone_url", "affected_zone-coordinates", "effective", 
                "onset", "expires", "ends", "Status", "message type", "Category", "Severity", "Certainty", "Urgency", "event"
            ])

            # Extract and write filtered alert data
            for feature in filtered_alerts:
                properties = feature.get("properties", {})
                geometry = feature.get("geometry", {})

                # Debugging: Log the properties for troubleshooting
                print(f"Properties for alert {properties.get('id', 'Unknown ID')}: {properties}")

                # Extract coordinates from geometry if available (main alert area)
                polygon_coordinates = None
                if geometry and geometry.get("type") == "Polygon":
                    polygon_coordinates = geometry.get("coordinates", [])[0]
                elif geometry and geometry.get("type") == "MultiPolygon":
                    # If it's a MultiPolygon, get all the coordinates
                    polygon_coordinates = [coords for polygon in geometry.get("coordinates", []) for coords in polygon]
                else:
                    print(f"Warning: No valid Polygon or MultiPolygon geometry found for alert {properties.get('id')}.")
                
                # Handle coordinates as string with full precision
                if polygon_coordinates:
                    polygon_coordinates = [f"{Decimal(coord):.15f}" for coord in polygon_coordinates if isinstance(coord, (int, float))]
                else:
                    print(f"Missing polygon coordinates for alert {properties.get('id')}.")

                # Extract the Area Description with additional handling
                area_desc = properties.get("areaDesc", "N/A")
                if isinstance(area_desc, (int, float)):
                    print(f"Warning: areaDesc is not a string for alert {properties.get('id')}: {area_desc}. Setting it to N/A.")
                    area_desc = "N/A"  # Set it to "N/A" if it's a number or other invalid type

                # Extract coordinates for affected zones (if available)
                affected_zones = properties.get("affectedZones", [])
                affected_zone_coordinates = "N/A"
                if affected_zones:
                    for zone_url in affected_zones:
                        # Fetch data for each affected zone URL
                        zone_response = requests.get(zone_url)
                        if zone_response.status_code == 200:
                            zone_data = zone_response.json()
                            zone_geometry = zone_data.get("geometry", {})
                            
                            # Handle both Polygon and MultiPolygon
                            if zone_geometry.get("type") == "Polygon":
                                affected_zone_coordinates = zone_geometry.get("coordinates", [])[0]
                            elif zone_geometry.get("type") == "MultiPolygon":
                                # For MultiPolygon, get all coordinates as a list of polygons
                                affected_zone_coordinates = [coords for polygon in zone_geometry.get("coordinates", []) for coords in polygon]
                            else:
                                print(f"Warning: Zone {zone_url} does not contain a valid Polygon or MultiPolygon geometry.")
                        
                        else:
                            print(f"Failed to fetch affected zone data from {zone_url}, status code {zone_response.status_code}")
                        time.sleep(0.1)  # Add a small delay between requests to avoid hitting rate limits

                # Helper function to safely convert to Decimal
                def safe_decimal_conversion(value):
                    try:
                        return str(Decimal(value)) if value not in ["N/A", None] else "N/A"
                    except InvalidOperation:
                        return "N/A"

                # Write to CSV
                writer.writerow([
                    area_desc,  # Write the corrected areaDesc
                    polygon_coordinates if polygon_coordinates else "N/A",  # Write N/A if no polygon coordinates
                    zone_url,  # The URL of the affected zone
                    affected_zone_coordinates if affected_zone_coordinates != "N/A" else "N/A",  # Coordinates for affected zone
                    safe_decimal_conversion(properties.get("effective", "N/A")),
                    safe_decimal_conversion(properties.get("onset", "N/A")),
                    safe_decimal_conversion(properties.get("expires", "N/A")),
                    safe_decimal_conversion(properties.get("ends", "N/A")),
                    properties.get("status", "N/A"),
                    properties.get("messageType", "N/A"),
                    properties.get("category", "N/A"),
                    properties.get("severity", "N/A"),
                    properties.get("certainty", "N/A"),
                    properties.get("urgency", "N/A"),
                    properties.get("event", "N/A")
                ])

        print("Generated CSV file successfully.")
