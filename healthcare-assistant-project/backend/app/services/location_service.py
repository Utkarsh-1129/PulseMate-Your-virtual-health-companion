# backend/app/services/location_service.py
# location_service----

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def find_nearby_facilities(latitude, longitude, facility_type="healthcare", radius=5000):
    """
    Find nearby healthcare facilities using OpenStreetMap via the Overpass API.
    
    Args:
        latitude (float): User's latitude
        longitude (float): User's longitude
        facility_type (str): Type of facility to search for
        radius (int): Search radius in meters
        
    Returns:
        str: Formatted string with nearby facilities
    """
    try:
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Define Overpass query templates
        query_map = {
            "healthcare": """
                node["amenity"="hospital"](around:{radius},{lat},{lon});
                node["amenity"="clinic"](around:{radius},{lat},{lon});
                node["amenity"="doctors"](around:{radius},{lat},{lon});
                node["healthcare"](around:{radius},{lat},{lon});
                way["amenity"="hospital"](around:{radius},{lat},{lon});
                way["amenity"="clinic"](around:{radius},{lat},{lon});
                way["amenity"="doctors"](around:{radius},{lat},{lon});
                way["healthcare"](around:{radius},{lat},{lon});
                relation["amenity"="hospital"](around:{radius},{lat},{lon});
                relation["amenity"="clinic"](around:{radius},{lat},{lon});
                relation["amenity"="doctors"](around:{radius},{lat},{lon});
                relation["healthcare"](around:{radius},{lat},{lon});
            """,
            "pharmacy": """
                node["amenity"="pharmacy"](around:{radius},{lat},{lon});
                way["amenity"="pharmacy"](around:{radius},{lat},{lon});
                relation["amenity"="pharmacy"](around:{radius},{lat},{lon});
            """,
            "hospital": """
                node["amenity"="hospital"](around:{radius},{lat},{lon});
                way["amenity"="hospital"](around:{radius},{lat},{lon});
                relation["amenity"="hospital"](around:{radius},{lat},{lon});
            """
        }
        
        # Use the appropriate query or fallback to "healthcare"
        query_filter = query_map.get(facility_type.lower(), query_map["healthcare"])
        
        # Build the full Overpass query
        query = f"""
        [out:json];
        (
            {query_filter.format(radius=radius, lat=latitude, lon=longitude)}
        );
        out center;
        """
        
        # Make the request
        response = requests.post(overpass_url, data={"data": query})
        
        if response.status_code == 200:
            data = response.json()
            
            if "elements" in data and data["elements"]:
                facilities = []
                
                for element in data["elements"][:5]:  # Limit to top 5 results
                    tags = element.get("tags", {})
                    name = tags.get("name", "Unnamed facility")
                    facility_kind = tags.get("amenity") or tags.get("healthcare", "unknown")
                    
                    # Coordinates differ by element type
                    if element["type"] == "node":
                        lat = element.get("lat")
                        lon = element.get("lon")
                    else:
                        center = element.get("center", {})
                        lat = center.get("lat")
                        lon = center.get("lon")
                    
                    if name and lat and lon:
                        facilities.append({
                            "name": name,
                            "type": facility_kind,
                            "latitude": lat,
                            "longitude": lon
                        })
                
                if facilities:
                    result = "I found these healthcare facilities near you:\n\n"
                    for i, facility in enumerate(facilities):
                        result += f"{i+1}. {facility['name']} ({facility['type']})\n"
                        result += f"   📍 Location: https://www.google.com/maps?q={facility['latitude']},{facility['longitude']}\n\n"
                    return result
            
            return "I couldn't find any healthcare facilities in that area."
        
        return "Sorry, I'm having trouble searching for healthcare facilities right now."
    
    except Exception as e:
        print(f"Error finding nearby facilities: {e}")
        return "I encountered an error while searching for healthcare facilities."