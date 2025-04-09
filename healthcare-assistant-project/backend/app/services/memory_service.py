from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv
import google.generativeai as genai

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
    print(f"Creating new index: {pinecone_index_name}")
    pc.create_index(
        name=pinecone_index_name,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-west-2"
        )
    )
else:
    print(f"Using existing index: {pinecone_index_name}")

# Get the index
index = pc.Index(pinecone_index_name)

# Initialize embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    task_type="retrieval_document"
)

# Initialize Vector Store
vectorstore = PineconeVectorStore(index=index, embedding=embeddings)

# ✅ Save memory (e.g., user chat or document)
# ✅ Save memory (e.g., user chat or document)
def save_to_memory(text: str, metadata: dict = None):
    try:
        metadata = metadata or {}
        doc_id = str(hash(text))  # Unique ID based on content
        vectorstore.add_texts(
            texts=[text],
            ids=[doc_id],
            metadatas=[metadata]
        )
        print(f"✅ Saved to memory: {text[:50]}...")  # Log a snippet
    except Exception as e:
        print(f"❌ Error saving to memory: {e}")
        raise e

# ✅ Retrieve similar past memory
def retrieve_from_memory(query: str, metadata_filter: dict = None, k: int = 3):
    try:
        metadata_filter = metadata_filter or {}
        results = vectorstore.similarity_search(
            query=query,
            k=k,
            filter=metadata_filter  # e.g., {"user_id": "abc123"}
        )
        return [r.page_content for r in results]
    except Exception as e:
        print(f"❌ Error retrieving from memory: {e}")
        return []
