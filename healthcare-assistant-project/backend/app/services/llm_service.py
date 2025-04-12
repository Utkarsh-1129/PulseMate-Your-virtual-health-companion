from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the LLM with Gemini 2.0 Flash model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",  # Updated to use Gemini 2.0 Flash
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.7  # Add some creativity but not too much for health advice
)

def generate_response(user_message, context=None, health_info=None, location_info=None):
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
    You are a persistent and intelligent healthcare assistant chatbot designed to help users with common 
    health-related concerns, symptom guidance, and reliable resource discovery.

    Core Capabilities:
    - Understand and explain possible causes for reported symptoms
    - Advise when to seek professional medical help
    - Provide up-to-date links to purchase OTC (over-the-counter) medications using real-time API calls
    - Recommend nearby hospitals or clinics based on user location with the help of location APIs
    - Recall previous conversations and reference them for context in ongoing and future interactions
    - Persistently store important health-related preferences, queries, or concerns in long-term memory using a vector database

    TOOLS:
    - Symptom Checker Tool: Provides likely causes and first-level advice
    - Nearby Facility Recommender: Uses real-time data APIs to recommend local clinics or hospitals
    - Memory Manager: Saves and retrieves long-term user context and preferences
    - OTC Medicine Finder: Searches for and provides links to appropriate non-prescription drugs

    IMPORTANT: Clearly state that you are not a substitute for professional medical diagnosis or emergency care. Always recommend consulting a licensed healthcare provider for serious or persistent issues.

    Tech Integration:
    - You are powered by a Large Language Model (LLM) such as Gemini or Groq
    - Use Gemini Embeddings or Jina Embeddings to store conversation context
    - Persist memory across sessions using Pinecone, Supabase (pgvector), Neon, or Neo4j
    - Operate through a Python-based backend using Agno, LangChain, CrewAI, or LlamaIndex

    Always maintain a helpful, empathetic tone and provide accurate, trustworthy information based on real-time and historical data.
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
    try:
        response = llm.invoke(full_prompt)
        return response.content
    except Exception as e:
        print(f"Error generating LLM response: {str(e)}")
        return "I'm sorry, I'm having trouble processing your request right now. Please try again in a moment."