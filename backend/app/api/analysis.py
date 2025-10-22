"""
Analysis API endpoints
"""
from fastapi import APIRouter, HTTPException, Request
from typing import List
import chess

from app.models.schemas import (
    AnalysisRequest, AnalysisResult,
    MoveEvaluationRequest, MoveEvaluation
)

router = APIRouter()


@router.post("/position", response_model=List[AnalysisResult])
async def analyze_position(request: AnalysisRequest, req: Request):
    """Analyze a chess position."""
    try:
        board = chess.Board(request.fen)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid FEN notation")
    
    engine_manager = req.app.state.engine_manager
    
    try:
        results = await engine_manager.analyze_position(
            board,
            depth=request.depth,
            multipv=request.multipv,
            use_maia=request.use_maia
        )
        
        return [AnalysisResult(**r) for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/evaluate-move", response_model=MoveEvaluation)
async def evaluate_move(request: MoveEvaluationRequest, req: Request):
    """Evaluate the quality of a specific move."""
    try:
        board = chess.Board(request.fen)
        move = chess.Move.from_uci(request.move)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    
    if move not in board.legal_moves:
        raise HTTPException(status_code=400, detail="Illegal move")
    
    engine_manager = req.app.state.engine_manager
    
    try:
        evaluation = await engine_manager.evaluate_move_quality(
            board, move, depth=request.depth
        )
        return MoveEvaluation(**evaluation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.get("/best-move/{fen}")
async def get_best_move(fen: str, elo: int = None, req: Request = None):
    """Get the best move for a position."""
    try:
        board = chess.Board(fen)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid FEN notation")
    
    engine_manager = req.app.state.engine_manager
    
    try:
        best_move = await engine_manager.get_best_move(board, elo=elo)
        return {
            "best_move": best_move.uci(),
            "fen": fen,
            "elo_calibrated": elo is not None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get best move: {str(e)}")
