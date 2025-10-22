"""
AI Chess Learning Platform - Main FastAPI Application
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.api import game, analysis, training, llm, user
from app.config import settings
from app.services.engine_manager import EngineManager
from app.services.ollama_service import OllamaService
from app.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting AI Chess Learning Platform...")
    
    # Initialize database
    try:
        await init_db()
        logger.info("✓ Database initialized")
    except Exception as e:
        logger.warning(f"⚠️  Database initialization skipped: {e}")
    
    # Initialize chess engines
    engine_manager = EngineManager()
    await engine_manager.initialize()
    app.state.engine_manager = engine_manager
    
    # Initialize Ollama service
    ollama_service = OllamaService()
    await ollama_service.initialize()
    app.state.ollama_service = ollama_service
    
    logger.info("✓ All services initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down services...")
    await engine_manager.shutdown()
    logger.info("✓ Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="AI Chess Learning Platform API",
    description="Open-source chess learning platform with Ollama LLM integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(game.router, prefix="/api/game", tags=["Game"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(training.router, prefix="/api/training", tags=["Training"])
app.include_router(llm.router, prefix="/api/llm", tags=["LLM"])
app.include_router(user.router, prefix="/api/user", tags=["User"])


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "AI Chess Learning Platform API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "ollama_connected": app.state.ollama_service.is_connected(),
        "engines_ready": app.state.engine_manager.is_ready()
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    engine_manager = app.state.engine_manager
    ollama_service = app.state.ollama_service
    
    return {
        "status": "healthy",
        "services": {
            "stockfish": engine_manager.stockfish_available(),
            "maia": engine_manager.maia_available(),
            "ollama": ollama_service.is_connected(),
            "database": True  # TODO: Add database health check
        },
        "ollama_model": settings.OLLAMA_MODEL,
        "version": "1.0.0"
    }


@app.websocket("/ws/game/{game_id}")
async def game_websocket(websocket: WebSocket, game_id: str):
    """WebSocket endpoint for real-time game updates and chat."""
    await websocket.accept()
    logger.info(f"WebSocket connection established for game {game_id}")
    
    try:
        while True:
            data = await websocket.receive_json()
            # Handle different message types
            message_type = data.get("type")
            
            if message_type == "move":
                # Process move and send response
                response = await process_move(game_id, data, app.state)
                await websocket.send_json(response)
                
            elif message_type == "chat":
                # Process chat message with LLM
                response = await process_chat(game_id, data, app.state)
                await websocket.send_json(response)
                
            elif message_type == "hint":
                # Request hint from engine
                response = await process_hint_request(game_id, data, app.state)
                await websocket.send_json(response)
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for game {game_id}")
    except Exception as e:
        logger.error(f"WebSocket error for game {game_id}: {e}")
        await websocket.close(code=1011, reason=str(e))


async def process_move(game_id: str, data: dict, state):
    """Process a chess move and generate AI response."""
    # TODO: Implement move processing
    return {"type": "move_response", "success": True}


async def process_chat(game_id: str, data: dict, state):
    """Process chat message with Ollama LLM."""
    # TODO: Implement chat processing
    return {"type": "chat_response", "message": "Hello!"}


async def process_hint_request(game_id: str, data: dict, state):
    """Process hint request using chess engine."""
    # TODO: Implement hint generation
    return {"type": "hint_response", "hint": "Consider controlling the center"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
