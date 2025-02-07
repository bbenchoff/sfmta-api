import xml.etree.ElementTree as ET
import folium

# Load and parse the XML file
xml_file = "stops.xml"
tree = ET.parse(xml_file)
root = tree.getroot()

# Namespace for parsing XML
ns = {'siri': 'http://www.siri.org.uk/siri', 'netex': 'http://www.netex.org.uk/netex'}

# Extract stop locations with stop numbers
stops = []
for stop in root.findall(".//netex:ScheduledStopPoint", ns):
    stop_id = stop.get("id")  # Stop number (assumed to be a five-digit number)
    if stop_id and len(stop_id) == 5:  # Ensure it's a five-digit ID
        name = stop.find("netex:Name", ns).text if stop.find("netex:Name", ns) is not None else "Unknown"
        location = stop.find("netex:Location", ns)
        if location is not None:
            lat = location.find("netex:Latitude", ns).text
            lon = location.find("netex:Longitude", ns).text
            popup_text = f"{name} (Stop #{stop_id})"
            stops.append((popup_text, float(lat), float(lon)))

# Create a map centered at the first stop
if stops:
    first_stop = stops[0]
    transit_map = folium.Map(location=[first_stop[1], first_stop[2]], zoom_start=12)

    # Add markers for each stop
    for popup_text, lat, lon in stops:
        folium.Marker([lat, lon], popup=popup_text).add_to(transit_map)

    # Save the map to an HTML file
    transit_map.save("transit_stops_map.html")
    print("Map has been saved as 'transit_stops_map.html'. You can download and view it.")
else:
    print("No valid stops found in the XML file.")
