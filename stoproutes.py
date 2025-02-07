import os
import folium
import xml.etree.ElementTree as ET
import json
import csv
from collections import defaultdict

# Directory containing route files (XML or JSON)
ROUTES_DIR = "Routes"
MAP_OUTPUT = "stops_routes_map.html"
CSV_OUTPUT = "stops_routes_data.csv"
STOPS_XML = "stops.xml"

# Namespace for XML parsing
NS = {'netex': 'http://www.netex.org.uk/netex'}

# Function to parse stop locations from stops.xml
def parse_stops():
    stops = {}  # stop_id -> (lat, lon, name)
    tree = ET.parse(STOPS_XML)
    root = tree.getroot()
    
    for stop in root.findall(".//netex:ScheduledStopPoint", NS):
        stop_id = stop.get("id")
        name_elem = stop.find("netex:Name", NS)
        location_elem = stop.find("netex:Location", NS)
        
        if stop_id and name_elem is not None and location_elem is not None:
            name = name_elem.text.strip()
            lat = float(location_elem.find("netex:Latitude", NS).text)
            lon = float(location_elem.find("netex:Longitude", NS).text)
            stops[stop_id] = (lat, lon, name)
    
    print(f"Total stops parsed from stops.xml: {len(stops)}")
    return stops

# Function to parse route files (handling both XML and JSON formats)
def parse_routes():
    stops_data = defaultdict(set)  # stop_id -> set of (line_name, destination)
    route_paths = defaultdict(list)  # line_name -> list of (lat, lon)
    parsed_stop_ids = set()
    
    for filename in os.listdir(ROUTES_DIR):
        filepath = os.path.join(ROUTES_DIR, filename)
        
        try:
            with open(filepath, "rb") as file:
                raw_content = file.read().strip()
                
                # Check for and remove BOM
                if raw_content.startswith(b'\xef\xbb\xbf'):
                    raw_content = raw_content[3:]
                
                # Convert to string
                content = raw_content.decode("utf-8", errors="replace")
                
                # Check if file is JSON format
                if content.startswith("{"):
                    try:
                        data = json.loads(content)
                        print(f"Parsing JSON file: {filename}")
                        for journey_pattern in data.get("journeyPatterns", []):
                            line_ref = journey_pattern.get("LineRef")
                            destination_display = journey_pattern.get("DestinationDisplayView", {}).get("FontText", "")
                            
                            if not line_ref or not destination_display:
                                continue
                            
                            for stop in journey_pattern.get("PointsInSequence", {}).get("StopPointInJourneyPattern", []):
                                stop_ref = stop.get("ScheduledStopPointRef")
                                if stop_ref:
                                    parsed_stop_ids.add(stop_ref)
                                    stops_data[stop_ref].add((line_ref, destination_display))
                    except json.JSONDecodeError as e:
                        print(f"Skipping {filename}: Invalid JSON format ({e})")
                    continue  # Skip XML parsing if JSON parsing succeeds
        except UnicodeDecodeError as e:
            print(f"Skipping {filename}: Encoding issue ({e})")
            continue
        
    print(f"Total stops referenced in route data: {len(stops_data)}")
    print("Sample of stop IDs from routes:", list(parsed_stop_ids)[:10])  # Print first 10 stop IDs for debugging
    return stops_data, route_paths

# Generate map and CSV
def create_map_and_csv(stops, stops_data, route_paths):
    map_center = (37.7749, -122.4194)  # Default center on San Francisco
    m = folium.Map(location=map_center, zoom_start=12)
    
    # Prepare data for CSV
    csv_data = []
    
    # Add all stops from stops.xml, even if they don't appear in routes
    for stop_id, (lat, lon, name) in stops.items():
        route_list = [line for line, _ in stops_data.get(stop_id, [])]
        lines_info = "<br>".join([f"{line} to {dest}" for line, dest in stops_data.get(stop_id, [])])
        if not lines_info:
            lines_info = "No route data available"
        popup_text = f"<div style='width: 250px;'><b>Stop ID: {stop_id}</b><br><b>{name}</b><br><br>{lines_info}</div>"
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)
        
        csv_data.append([stop_id, len(route_list), name] + route_list)
    
    # Draw routes as polylines
    for line_id, path in route_paths.items():
        if path:
            folium.PolyLine(path, color="red", weight=3, opacity=0.7, tooltip=f"Route {line_id}").add_to(m)
    
    # Save the map
    m.save(MAP_OUTPUT)
    print(f"Map saved as {MAP_OUTPUT}")
    
    # Write to CSV file
    with open(CSV_OUTPUT, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Stop Number", "Total Routes", "Description"] + [f"Route {i+1}" for i in range(max(len(row)-3 for row in csv_data))])
        writer.writerows(csv_data)
    print(f"CSV saved as {CSV_OUTPUT}")

# Main Execution
stops = parse_stops()
stops_data, route_paths = parse_routes()
create_map_and_csv(stops, stops_data, route_paths)
