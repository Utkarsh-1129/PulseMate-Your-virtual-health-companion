# backend/app/services/location_service.py
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def find_nearby_facilities(latitude, longitude, facility_type="healthcare", radius=5000):
    """
    Find nearby healthcare facilities using OpenStreetMap.
    
    Args:
        latitude (float): User's latitude
        longitude (float): User's longitude
        facility_type (str): Type of facility to search for
        radius (int): Search radius in meters
        
    Returns:
        str: Formatted string with nearby facilities
    """
    try:
        # Use Overpass API to query OpenStreetMap
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Build query for healthcare facilities
        query_map = {
            "healthcare": "amenity=hospital or amenity=clinic or amenity=doctors or healthcare=*",
            "pharmacy": "amenity=pharmacy",
            "hospital": "amenity=hospital"
        }
        
        # Use the appropriate query based on facility type
        query_filter = query_map.get(facility_type.lower(), query_map["healthcare"])
        
        # Create the Overpass query
        query = f"""
        [out:json];
        (
          node[{query_filter}](around:{radius},{latitude},{longitude});
          way[{query_filter}](around:{radius},{latitude},{longitude});
          relation[{query_filter}](around:{radius},{latitude},{longitude});
        );
        out center;
        """
        
        # Make the request
        response = requests.post(overpass_url, data={"data": query})
        
        if response.status_code == 200:
            data = response.json()
            
            # Process the results
            if "elements" in data and data["elements"]:
                facilities = []
                
                for element in data["elements"][:5]:  # Limit to 5 results
                    name = element.get("tags", {}).get("name", "Unnamed facility")
                    facility_type = element.get("tags", {}).get("amenity", "healthcare")
                    
                    # Get coordinates - different for nodes vs ways/relations
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
                            "type": facility_type,
                            "latitude": lat,
                            "longitude": lon
                        })
                
                if facilities:
                    # Format the facilities into a readable string
                    result = "I found these healthcare facilities near you:\n\n"
                    
                    for i, facility in enumerate(facilities):
                        result += f"{i+1}. {facility['name']} ({facility['type']})\n"
                        # Google Maps URL
                        result += f"   Location: https://www.google.com/maps?q={facility['latitude']},{facility['longitude']}\n\n"
                    
                    return result
            
            return "I couldn't find any healthcare facilities in that area."
        
        return "Sorry, I'm having trouble searching for healthcare facilities right now."
    
    except Exception as e:
        print(f"Error finding nearby facilities: {e}")
        return "I encountered an error while searching for healthcare facilities."