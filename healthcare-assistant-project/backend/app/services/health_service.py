import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_health_information(query):
    """
    Get health information from the web based on the query.
    
    Args:
        query (str): The user's health-related query
        
    Returns:
        str: Health information in a formatted string
    """
    # Check if the query is health-related
    health_keywords = [
        "symptom", "disease", "condition", "treatment", "medicine", "medication",
        "prescription", "doctor", "hospital", "clinic", "health", "medical",
        "pain", "ache", "fever", "cough", "cold", "flu", "nausea", "vomiting"
    ]
    
    is_health_related = any(keyword in query.lower() for keyword in health_keywords)
    
    if not is_health_related:
        return None
    
    try:
        # Use Serper API (you need to sign up for an API key)
        serper_api_key = os.getenv("SERPER_API_KEY")
        if not serper_api_key:
            return "Health information service not configured."
        
        # Format query for health search
        search_query = f"medical information about {query}"
        
        # Make API request
        response = requests.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY": serper_api_key,
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "q": search_query,
                "gl": "us",
                "hl": "en",
                "autocorrect": True
            })
        )
        
        if response.status_code == 200:
            search_results = response.json()
            
            # Extract and format the top organic results
            if "organic" in search_results and search_results["organic"]:
                top_results = search_results["organic"][:3]
                
                formatted_info = "Here's some relevant health information:\n\n"
                
                for i, result in enumerate(top_results):
                    formatted_info += f"{i+1}. {result.get('title', 'No title')}\n"
                    formatted_info += f"   {result.get('snippet', 'No description')}\n\n"
                
                return formatted_info
            
        return "I couldn't find specific health information about that. Please consult a healthcare professional."
        
    except Exception as e:
        print(f"Error fetching health information: {e}")
        return None