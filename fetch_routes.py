import os
import time
import requests
import xml.etree.ElementTree as ET

# API Configuration
API_KEY = "da03f504-fc16-43e7-a736-319af37570be"
BASE_URL = "https://api.511.org/transit/patterns"
OPERATOR_ID = "SF"
SAVE_DIR = "routes"

# Ensure the routes directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

# Read and parse lines.xml to get line numbers
def read_xml_file(filepath: str) -> str:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='iso-8859-1') as f:
            return f.read()

xml_content = read_xml_file("lines.xml")

try:
    tree = ET.ElementTree(ET.fromstring(xml_content))
    root = tree.getroot()
except ET.ParseError as e:
    print(f"Failed to parse XML: {e}")
    print("First 100 characters of content:", xml_content[:100])
    raise

namespace = {"netex": "http://www.netex.org.uk/netex"}
line_numbers = [line.get("id") for line in root.findall('.//*{http://www.netex.org.uk/netex}Line') if line.get("id")]

# Print all lines to be queried
print("Lines to be queried:")
print(" ".join(line_numbers))

# Iterate over each line number and query the API
for index, line_number in enumerate(line_numbers):
    url = f"{BASE_URL}?api_key={API_KEY}&operator_id={OPERATOR_ID}&line_id={line_number}"
    print(f"Fetching data for line {line_number} ({index + 1}/{len(line_numbers)})")
    print(f"API Endpoint: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        
        # Save XML response
        file_path = os.path.join(SAVE_DIR, f"{line_number}.xml")
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"Saved: {file_path}")
        
    except requests.RequestException as e:
        print(f"Failed to fetch line {line_number}: {e}")
    
    # Wait for 60 seconds before next request to comply with API rate limit
    if index < len(line_numbers) - 1:
        print("Waiting 60 seconds before next request...")
        time.sleep(60)

print("All routes have been fetched.")
