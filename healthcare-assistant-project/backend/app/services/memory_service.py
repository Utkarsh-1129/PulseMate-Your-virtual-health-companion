from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
import re

# Load environment variables
load_dotenv()

# Get environment variables
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Print debug information
print(f"Pinecone API Key present: {'Yes' if pinecone_api_key else 'No'}")
print(f"Pinecone Index Name: {pinecone_index_name}")
print(f"Gemini API Key present: {'Yes' if gemini_api_key else 'No'}")

# Check required env vars
if not pinecone_api_key:
    raise ValueError("PINECONE_API_KEY environment variable is not set")
if not pinecone_index_name:
    raise ValueError("PINECONE_INDEX_NAME environment variable is not set")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

# Configure Gemini
genai.configure(api_key=gemini_api_key)
os.environ["GOOGLE_API_KEY"] = gemini_api_key

# Initialize Pinecone
pc = Pinecone(api_key=pinecone_api_key)

# Ensure index exists
indexes = pc.list_indexes()
index_names = [idx.name for idx in indexes.indexes]

if pinecone_index_name not in index_names:
    print(f"Creating index: {pinecone_index_name}")
    pc.create_index(
        name=pinecone_index_name,
        dimension=768,  # Gemini embedding size
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",  # or "gcp"
            region="us-central1"
        )
    )
else:
    print(f"Using existing index: {pinecone_index_name}")

# Initialize Embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=gemini_api_key)

# Connect to VectorStore
vectorstore = PineconeVectorStore.from_existing_index(
    index_name=pinecone_index_name,
    embedding=embeddings
)

print("✅ Pinecone + Gemini setup is complete.")

def extract_health_info(text):
    """
    Extract important health information from text.
    This is a simple implementation - in a real system, you would use 
    more sophisticated NLP techniques.
    """
    health_info = {
        "symptoms": [],
        "conditions": [],
        "medications": [],
        "age_info": None
    }
    
    # Simple pattern matching for common symptoms
    symptom_patterns = [
        r"(headache|migraine|pain|ache|fever|cough|cold|flu|nausea|vomiting|diarrhea|constipation|fatigue|tired|exhaustion)",
        r"(shortness of breath|difficulty breathing|chest pain|heart|palpitations|dizziness|fainting)",
        r"(rash|itching|swelling|inflammation)"
    ]
    
    for pattern in symptom_patterns:
        matches = re.findall(pattern, text.lower())
        health_info["symptoms"].extend(matches)
    
    # Pattern matching for common conditions
    condition_patterns = [
        r"(diabetes|hypertension|high blood pressure|asthma|arthritis|depression|anxiety)",
        r"(allergy|allergies|migraine|heart disease|cancer)"
    ]
    
    for pattern in condition_patterns:
        matches = re.findall(pattern, text.lower())
        health_info["conditions"].extend(matches)
    
    # Pattern matching for medications
    medication_patterns = [
        r"(aspirin|ibuprofen|tylenol|advil|aleve|acetaminophen|paracetamol)",
        r"(antibiotic|probiotic|vitamin|supplement)"
    ]
    
    for pattern in medication_patterns:
        matches = re.findall(pattern, text.lower())
        health_info["medications"].extend(matches)
    
    # Pattern matching for age
    age_pattern = r"(\d+)[\s-]*years?[\s-]*old"
    age_match = re.search(age_pattern, text.lower())
    if age_match:
        health_info["age_info"] = age_match.group(1)
    
    # Remove duplicates
    health_info["symptoms"] = list(set(health_info["symptoms"]))
    health_info["conditions"] = list(set(health_info["conditions"]))
    health_info["medications"] = list(set(health_info["medications"]))
    
    return health_info

def save_to_memory(user_id, query, response):
    """
    Save important information from the conversation to memory.
    """
    # Extract health information
    user_health_info = extract_health_info(query)
    response_health_info = extract_health_info(response)
    
    # Combine the extracted information
    combined_health_info = {
        "symptoms": list(set(user_health_info["symptoms"] + response_health_info["symptoms"])),
        "conditions": list(set(user_health_info["conditions"] + response_health_info["conditions"])),
        "medications": list(set(user_health_info["medications"] + response_health_info["medications"])),
        "age_info": user_health_info["age_info"] or response_health_info["age_info"]
    }
    
    # If we found any health information, save it
    if any(combined_health_info.values()):
        # Create document for vector storage
        document_text = f"User ID: {user_id}\nQuery: {query}\nResponse: {response}\nHealth Info: {json.dumps(combined_health_info)}"
        
        # Add document to vector store
        vectorstore.add_texts(
            texts=[document_text],
            metadatas=[{
                "user_id": user_id,
                "health_info": json.dumps(combined_health_info)
            }]
        )

def retrieve_from_memory(user_id, query):
    """
    Retrieve relevant information from memory based on user ID and query.
    """
    # Search for similar content
    search_results = vectorstore.similarity_search(
        query=query,
        k=5,  # Return top 5 results
        filter={"user_id": user_id}
    )
    
    if not search_results:
        return None
    
    # Extract and combine health information
    health_info = {
        "symptoms": [],
        "conditions": [],
        "medications": [],
        "age_info": None
    }
    
    context_text = []
    
    for doc in search_results:
        context_text.append(doc.page_content)
        
        # Extract metadata
        if hasattr(doc, 'metadata') and 'health_info' in doc.metadata:
            try:
                doc_health_info = json.loads(doc.metadata['health_info'])
                
                # Combine with existing health info
                health_info["symptoms"].extend(doc_health_info.get("symptoms", []))
                health_info["conditions"].extend(doc_health_info.get("conditions", []))
                health_info["medications"].extend(doc_health_info.get("medications", []))
                
                # Use the first age info we find
                if not health_info["age_info"] and doc_health_info.get("age_info"):
                    health_info["age_info"] = doc_health_info["age_info"]
            except:
                pass
    
    # Remove duplicates
    health_info["symptoms"] = list(set(health_info["symptoms"]))
    health_info["conditions"] = list(set(health_info["conditions"]))
    health_info["medications"] = list(set(health_info["medications"]))
    
    # Format the context
    formatted_context = f"""
    Previous health information:
    Symptoms: {', '.join(health_info['symptoms']) if health_info['symptoms'] else 'None mentioned'}
    Conditions: {', '.join(health_info['conditions']) if health_info['conditions'] else 'None mentioned'}
    Medications: {', '.join(health_info['medications']) if health_info['medications'] else 'None mentioned'}
    Age: {health_info['age_info'] if health_info['age_info'] else 'Not mentioned'}
    """
    
    return {
        "content": formatted_context,
        "raw_text": "\n".join(context_text),
        "health_info": health_info
    }