import xml.etree.ElementTree as ET
from collections import defaultdict
import sys
from typing import Dict, List

def read_xml_file(filepath: str) -> str:
    """
    Read XML file with proper encoding handling.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='iso-8859-1') as f:
            return f.read()

def parse_transit_xml(xml_content: str) -> List[Dict]:
    """
    Parse the transit XML content and return a list of dictionaries containing line information.
    """
    try:
        tree = ET.ElementTree(ET.fromstring(xml_content))
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Failed to parse XML: {e}")
        print("First 100 characters of content:", xml_content[:100])
        raise

    lines = []
    for line in root.findall('.//*{http://www.netex.org.uk/netex}Line'):
        try:
            line_info = {
                'id': line.get('id'),
                'name': line.find('.//{http://www.netex.org.uk/netex}Name').text,
                'transport_mode': line.find('.//{http://www.netex.org.uk/netex}TransportMode').text,
                'public_code': line.find('.//{http://www.netex.org.uk/netex}PublicCode').text,
            }
            lines.append(line_info)
        except AttributeError as e:
            print(f"Warning: Skipping incomplete line entry: {e}")
            continue

    return lines

def categorize_lines(lines: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Categorize lines by transport mode and sort them by code.
    """
    categories = defaultdict(list)
    
    for line in lines:
        categories[line['transport_mode']].append(line)
    
    # Sort each category by public code
    for mode in categories:
        categories[mode].sort(key=lambda x: x['public_code'])
    
    return categories

def generate_report(categories: Dict[str, List[Dict]]) -> str:
    """
    Generate a formatted report showing all lines by category.
    """
    report = []
    report.append("SF MUNI Transit System - Complete Line Listing")
    report.append("=" * 50)

    total_lines = sum(len(lines) for lines in categories.values())
    report.append(f"\nTotal Lines: {total_lines}\n")

    for mode in sorted(categories.keys()):
        report.append(f"\n{mode.upper()} LINES")
        report.append("-" * 20)
        report.append(f"Total {mode} lines: {len(categories[mode])}\n")
        
        for line in categories[mode]:
            report.append(f"Line {line['public_code']}: {line['name']}")
    
    return "\n".join(report)

def main():
    """
    Main function to process command line arguments and generate analysis.
    """
    if len(sys.argv) != 2:
        print("Usage: python script.py <xml_file>")
        sys.exit(1)
        
    try:
        xml_content = read_xml_file(sys.argv[1])
        lines = parse_transit_xml(xml_content)
        categories = categorize_lines(lines)
        print(generate_report(categories))
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()