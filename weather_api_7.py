import os
import csv
import requests
import time
from google.cloud import storage
from google.auth.exceptions import DefaultCredentialsError

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

        if event in event_types:
            filtered_alerts.append(feature)

    print(f"Total alerts after filtering by event type: {len(filtered_alerts)}")

    # Prepare the CSV data to upload to GCS
    csv_file_name = "weather_a9.csv"
    with open(csv_file_name, "w", newline="") as csvfile:
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

            # Extract coordinates from geometry if available (main alert area)
            polygon_coordinates = None
            if geometry and geometry.get("type") == "Polygon":
                polygon_coordinates = geometry.get("coordinates", [])[0]
            elif geometry and geometry.get("type") == "MultiPolygon":
                polygon_coordinates = [coords for polygon in geometry.get("coordinates", []) for coords in polygon]

            # Extract the Area Description with additional handling
            area_desc = properties.get("areaDesc", "N/A")
            if isinstance(area_desc, (int, float)):
                area_desc = "N/A"  # Set it to "N/A" if it's a number or other invalid type

            # Write each row of the CSV
            writer.writerow([
                area_desc,
                polygon_coordinates if polygon_coordinates else "N/A",  # Coordinates if available
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

    print(f"CSV file '{csv_file_name}' generated successfully.")

    # Upload the CSV file to GCS
    bucket_name = "bucket_name"  # Replace with your GCS bucket name
    destination_blob_name = "weather_a9.csv"  # Path inside the bucket where you want to save the file

    try:
        # Initialize a GCS client
        storage_client = storage.Client()

        # Get the GCS bucket
        bucket = storage_client.bucket(bucket_name)

        # Create a blob (file) in the GCS bucket
        blob = bucket.blob(destination_blob_name)

        # Upload the CSV file to GCS
        blob.upload_from_filename(csv_file_name)

        print(f"CSV file uploaded to GCS at gs://{bucket_name}/{destination_blob_name}")
    
    except DefaultCredentialsError:
        print("Error: Google Cloud credentials not found. Please ensure the GOOGLE_APPLICATION_CREDENTIALS environment variable is set.")
    
    except Exception as e:
        print(f"Error uploading CSV to GCS: {e}")
