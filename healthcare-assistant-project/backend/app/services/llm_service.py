from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the LLM with the required 'model' parameter
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",  # Add the model parameter
    api_key=os.getenv("GEMINI_API_KEY")
)

def generate_response(user_message, context=None, health_info=None, location_info=None):
    # Rest of your function remains the same
    # ...
    """
    Generate a response using the LLM.
    
    Args:
        user_message (str): The user's message
        context (dict): The context from previous conversations
        health_info (dict): Real-time health information
        location_info (dict): Location-based healthcare facility information
        
    Returns:
        str: The generated response
    """
    # Prepare prompt
    system_message = """
    You are a helpful healthcare assistant chatbot. Your goal is to help users understand common 
    medical symptoms, find healthcare facilities, and access reliable health resources. 
    
    You can:
    - Explain possible causes for symptoms
    - Suggest when to seek professional care
    - Provide links to purchase over-the-counter medicines
    - Recommend hospitals or clinics based on location
    
    IMPORTANT: Always emphasize that you are not a substitute for professional medical advice.
    """
    
    context_message = ""
    if context:
        context_message = f"Here is relevant information from our previous conversations: {context['content']}"
    
    health_info_message = ""
    if health_info:
        health_info_message = f"Here is current medical information related to your query: {health_info}"
    
    location_info_message = ""
    if location_info:
        location_info_message = f"Here are healthcare facilities near you: {location_info}"
    
    # Combine all parts
    full_prompt = f"{system_message}\n\n{context_message}\n\n{health_info_message}\n\n{location_info_message}\n\nUser: {user_message}\n\nHealth Assistant:"
    
    # Generate response
    response = llm.invoke(full_prompt)
    
    return response.content