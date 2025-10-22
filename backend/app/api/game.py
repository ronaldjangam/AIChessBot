"""
Game API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import uuid
import chess
from datetime import datetime

from app.models.schemas import (
    GameStartRequest, GameState, MoveRequest, MoveResponse
)
from app.services.engine_manager import EngineManager
from app.services.ollama_service import OllamaService

router = APIRouter()

# In-memory game storage (replace with database in production)
active_games: Dict[str, Dict[str, Any]] = {}


@router.post("/start", response_model=GameState)
async def start_game(request: GameStartRequest):
    """Start a new chess game."""
    game_id = str(uuid.uuid4())
    board = chess.Board()
    
    game_data = {
        "game_id": game_id,
        "board": board,
        "fen": board.fen(),
        "moves": [],
        "player_color": request.player_color,
        "player_elo": request.player_elo,
        "ai_persona": request.ai_persona,
        "use_maia": request.use_maia,
        "is_game_over": False,
        "result": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    active_games[game_id] = game_data
    
    return GameState(
        game_id=game_id,
        fen=board.fen(),
        moves=[],
        player_color=request.player_color,
        ai_persona=request.ai_persona,
        is_game_over=False,
        result=None,
        created_at=game_data["created_at"],
        updated_at=game_data["updated_at"]
    )


@router.post("/move", response_model=MoveResponse)
async def make_move(request: MoveRequest):
    """Make a move in an active game."""
    if request.game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = active_games[request.game_id]
    board: chess.Board = game["board"]
    
    try:
        # Parse and validate move
        move = chess.Move.from_uci(request.move)
        if move not in board.legal_moves:
            raise HTTPException(status_code=400, detail="Illegal move")
        
        # Make player's move
        board.push(move)
        game["moves"].append(request.move)
        game["updated_at"] = datetime.utcnow()
        
        # Check if game is over
        if board.is_game_over():
            game["is_game_over"] = True
            game["result"] = board.result()
            return MoveResponse(
                success=True,
                move=request.move,
                fen=board.fen(),
                is_game_over=True,
                result=board.result()
            )
        
        # Generate AI response move (placeholder - will integrate engine manager)
        # TODO: Integrate engine manager to get AI move
        ai_move = None
        
        return MoveResponse(
            success=True,
            move=request.move,
            fen=board.fen(),
            is_game_over=False,
            ai_move=ai_move,
            ai_fen=board.fen() if ai_move else None
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid move format: {str(e)}")


@router.get("/{game_id}", response_model=GameState)
async def get_game(game_id: str):
    """Get current game state."""
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = active_games[game_id]
    board: chess.Board = game["board"]
    
    return GameState(
        game_id=game_id,
        fen=board.fen(),
        moves=game["moves"],
        player_color=game["player_color"],
        ai_persona=game["ai_persona"],
        is_game_over=game["is_game_over"],
        result=game.get("result"),
        created_at=game["created_at"],
        updated_at=game["updated_at"]
    )


@router.delete("/{game_id}")
async def delete_game(game_id: str):
    """Delete a game."""
    if game_id not in active_games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    del active_games[game_id]
    return {"message": "Game deleted successfully"}
