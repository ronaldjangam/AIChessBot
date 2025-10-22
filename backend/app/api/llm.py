"""
LLM/Chat API endpoints
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
import json

from app.models.schemas import (
    ChatRequest, ChatResponse, ExplainMoveRequest
)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, req: Request):
    """Send a chat message to the AI."""
    ollama_service = req.app.state.ollama_service
    
    if not ollama_service.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Ollama service is not available. Please ensure Ollama is running."
        )
    
    try:
        if request.stream:
            # Return streaming response
            async def generate():
                async for chunk in await ollama_service.chat(
                    request.message,
                    context=request.context,
                    persona=request.persona,
                    stream=True
                ):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                yield "data: [DONE]\n\n"
            
            return StreamingResponse(generate(), media_type="text/event-stream")
        else:
            # Return complete response
            response = await ollama_service.chat(
                request.message,
                context=request.context,
                persona=request.persona,
                stream=False
            )
            
            return ChatResponse(
                message=response,
                persona=request.persona
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.post("/explain-move")
async def explain_move(request: ExplainMoveRequest, req: Request):
    """Get a natural language explanation for a chess move."""
    ollama_service = req.app.state.ollama_service
    
    if not ollama_service.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Ollama service is not available."
        )
    
    try:
        explanation = await ollama_service.explain_move(
            request.move,
            request.fen,
            evaluation=request.evaluation,
            persona=request.persona
        )
        
        return {
            "move": request.move,
            "explanation": explanation,
            "persona": request.persona
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")


@router.get("/personas")
async def list_personas():
    """List available AI personas."""
    from app.services.ollama_service import PersonaConfig
    
    return {
        "personas": [
            {
                "id": key,
                "name": config["name"],
                "style": config["style"]
            }
            for key, config in PersonaConfig.PERSONAS.items()
        ]
    }


@router.get("/status")
async def llm_status(req: Request):
    """Check LLM service status."""
    ollama_service = req.app.state.ollama_service
    
    return {
        "connected": ollama_service.is_connected(),
        "base_url": ollama_service.base_url,
        "model": ollama_service.model,
        "status": "operational" if ollama_service.is_connected() else "offline"
    }
