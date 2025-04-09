# backend/app/routers/chat.py
from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.services.llm_service import generate_response
from app.services.memory_service import save_to_memory, retrieve_from_memory
from app.services.health_service import get_health_information
from app.services.location_service import find_nearby_facilities

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
async def process_chat(request: ChatRequest):
    try:
        # Get user ID
        user_id = request.user_id
        
        # Retrieve context from memory
        context = retrieve_from_memory(user_id, request.message)
        
        # Get real-time health information if needed
        health_info = get_health_information(request.message)
        
        # Check if location request is present
        location_info = None
        location_keywords = ["nearby", "closest", "hospital", "clinic", "pharmacy", "doctor", "emergency"]
        if any(keyword in request.message.lower() for keyword in location_keywords):
            # Use provided coordinates or default to NYC
            lat = request.latitude if request.latitude is not None else 40.7128
            lng = request.longitude if request.longitude is not None else -74.0060
            
            # Determine facility type
            facility_type = "healthcare"  # default
            if "pharmacy" in request.message.lower():
                facility_type = "pharmacy"
            elif "hospital" in request.message.lower():
                facility_type = "hospital"
                
            location_info = find_nearby_facilities(lat, lng, facility_type)
        
        # Generate response using LLM
        response = generate_response(
            user_message=request.message,
            context=context,
            health_info=health_info,
            location_info=location_info
        )
        
        # Save important information to memory
        save_to_memory(user_id, request.message, response)
        
        return ChatResponse(response=response)
    
    except Exception as e:
        print(f"Error processing chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))