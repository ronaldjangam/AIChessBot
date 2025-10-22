"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MoveClassification(str, Enum):
    """Classification of move quality."""
    BRILLIANT = "brilliant"
    GOOD = "good"
    OK = "ok"
    INACCURACY = "inaccuracy"
    MISTAKE = "mistake"
    BLUNDER = "blunder"


class Persona(str, Enum):
    """Available AI personas."""
    GRANDMASTER = "grandmaster"
    FRIENDLY_TEACHER = "friendly_teacher"
    AGGRESSIVE_RIVAL = "aggressive_rival"


class MoveRequest(BaseModel):
    """Request to make a move in a game."""
    game_id: str
    move: str = Field(..., description="Move in UCI format (e.g., 'e2e4')")
    fen: Optional[str] = Field(None, description="Current position in FEN notation")


class MoveResponse(BaseModel):
    """Response after making a move."""
    success: bool
    move: str
    fen: str
    is_game_over: bool
    result: Optional[str] = None
    ai_move: Optional[str] = None
    ai_fen: Optional[str] = None


class AnalysisRequest(BaseModel):
    """Request for position analysis."""
    fen: str = Field(..., description="Position in FEN notation")
    depth: int = Field(20, ge=1, le=30, description="Analysis depth")
    multipv: int = Field(3, ge=1, le=5, description="Number of variations")
    use_maia: bool = Field(False, description="Use Maia for human-like analysis")


class AnalysisResult(BaseModel):
    """Analysis result for a position."""
    move: Optional[str]
    score: Dict[str, Any]
    depth: int
    pv: List[str] = Field(default_factory=list, description="Principal variation")


class MoveEvaluationRequest(BaseModel):
    """Request to evaluate a specific move."""
    fen: str
    move: str
    depth: int = Field(18, ge=10, le=25)


class MoveEvaluation(BaseModel):
    """Evaluation of a specific move."""
    move: str
    classification: MoveClassification
    score_difference: float
    before_score: float
    after_score: float
    best_move: Optional[str]


class ChatRequest(BaseModel):
    """Chat message request."""
    message: str
    game_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    persona: Persona = Persona.FRIENDLY_TEACHER
    stream: bool = False


class ChatResponse(BaseModel):
    """Chat message response."""
    message: str
    persona: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ExplainMoveRequest(BaseModel):
    """Request for move explanation."""
    move: str
    fen: str
    evaluation: Optional[Dict[str, Any]] = None
    persona: Persona = Persona.FRIENDLY_TEACHER


class GameStartRequest(BaseModel):
    """Request to start a new game."""
    player_color: str = Field("white", pattern="^(white|black)$")
    player_elo: int = Field(1200, ge=400, le=3000)
    ai_persona: Persona = Persona.FRIENDLY_TEACHER
    use_maia: bool = False


class GameState(BaseModel):
    """Current state of a chess game."""
    game_id: str
    fen: str
    moves: List[str]
    player_color: str
    ai_persona: str
    is_game_over: bool
    result: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class OpeningInfo(BaseModel):
    """Information about a chess opening."""
    name: str
    eco_code: str
    moves: List[str]
    description: str
    popularity: float = Field(ge=0, le=1)


class PuzzleRequest(BaseModel):
    """Request for a chess puzzle."""
    difficulty: Optional[int] = Field(None, ge=400, le=3000, description="Target ELO")
    theme: Optional[str] = Field(None, description="Puzzle theme (e.g., 'fork', 'pin')")
    count: int = Field(1, ge=1, le=10)


class Puzzle(BaseModel):
    """Chess puzzle."""
    puzzle_id: str
    fen: str
    moves: List[str]
    rating: int
    themes: List[str]
    solution_moves: List[str]


class UserStats(BaseModel):
    """User statistics and progress."""
    current_elo: int
    games_played: int
    puzzles_solved: int
    accuracy: float = Field(ge=0, le=100)
    favorite_openings: List[str]
    weak_areas: List[str]
    learning_streak: int
    last_active: datetime


class TrainingSession(BaseModel):
    """Spaced-repetition training session."""
    session_id: str
    items: List[Dict[str, Any]]
    total_items: int
    completed: int
    next_review: Optional[datetime] = None
