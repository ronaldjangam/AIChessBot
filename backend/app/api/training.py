"""
Training API endpoints
"""
from fastapi import APIRouter, HTTPException, Request
from typing import List

from app.models.schemas import (
    PuzzleRequest, Puzzle, OpeningInfo, TrainingSession
)
from app.training.training_service import (
    OpeningTrainer, PuzzleGenerator, SRSAlgorithm, MistakeAnalyzer
)

router = APIRouter()


@router.get("/openings", response_model=List[OpeningInfo])
async def list_openings(limit: int = 20):
    """List popular chess openings."""
    openings_data = OpeningTrainer.get_all_openings()
    
    formatted_openings = []
    for opening in openings_data[:limit]:
        formatted_openings.append(OpeningInfo(
            name=opening["name"],
            eco_code=opening["eco"],
            moves=opening["moves"],
            description=f"Key ideas: {', '.join(opening['ideas'][:2])}",
            popularity=opening["popularity"]
        ))
    
    return formatted_openings


@router.get("/openings/popular")
async def get_popular_openings(limit: int = 5):
    """Get most popular openings."""
    openings = OpeningTrainer.get_popular_openings(limit=limit)
    return openings


@router.get("/openings/{opening_name}")
async def get_opening_details(opening_name: str):
    """Get detailed information about an opening."""
    opening = OpeningTrainer.get_opening_by_name(opening_name)
    if not opening:
        raise HTTPException(status_code=404, detail="Opening not found")
    return {"name": opening_name, **opening}


@router.get("/openings/{opening_name}/quiz")
async def get_opening_quiz(opening_name: str):
    """Get a quiz question for an opening."""
    quiz = OpeningTrainer.generate_opening_quiz(opening_name)
    if not quiz:
        raise HTTPException(status_code=404, detail="Opening not found")
    return quiz


@router.post("/puzzles")
async def get_puzzles(request: PuzzleRequest):
    """Get chess puzzles based on criteria."""
    difficulty = request.difficulty or 1500
    theme = request.theme
    count = min(request.count, 10)  # Max 10 at a time
    
    puzzles = PuzzleGenerator.get_puzzles_by_rating(
        target_rating=difficulty,
        count=count,
        theme=theme
    )
    
    return puzzles


@router.post("/puzzles/from-mistakes")
async def generate_puzzles_from_mistakes(mistakes: List[dict], count: int = 5):
    """Generate custom puzzles based on user mistakes."""
    puzzles = PuzzleGenerator.generate_from_mistakes(mistakes, count=count)
    return puzzles


@router.post("/analyze-game")
async def analyze_game(moves: List[dict], evaluations: List[dict]):
    """Analyze a game and provide mistake breakdown."""
    analysis = MistakeAnalyzer.analyze_game_mistakes(moves, evaluations)
    return analysis


@router.post("/opening-guide")
async def generate_opening_guide(
    opening_name: str,
    persona: str = "friendly_teacher",
    req: Request = None
):
    """Generate AI guide for an opening."""
    opening = OpeningTrainer.get_opening_by_name(opening_name)
    if not opening:
        raise HTTPException(status_code=404, detail="Opening not found")
    
    ollama_service = req.app.state.ollama_service
    
    if not ollama_service.is_connected():
        # Return non-AI guide if Ollama unavailable
        return {
            "opening": opening_name,
            "moves": opening["moves"],
            "ideas": opening["ideas"],
            "mistakes": opening["mistakes"],
            "guide": f"{opening_name}: " + ". ".join(opening["ideas"])
        }
    
    # Generate AI guide
    guide = await ollama_service.generate_opening_guide(
        opening_name,
        opening["moves"],
        persona=persona
    )
    
    return {
        "opening": opening_name,
        "moves": opening["moves"],
        "ideas": opening["ideas"],
        "ai_guide": guide,
        "persona": persona
    }


@router.post("/srs/calculate-interval")
async def calculate_srs_interval(
    ease_factor: float = 2.5,
    interval_days: int = 1,
    repetitions: int = 0,
    quality: int = 3
):
    """Calculate next SRS interval for an item."""
    new_ease, new_interval, new_reps = SRSAlgorithm.calculate_next_interval(
        ease_factor, interval_days, repetitions, quality
    )
    
    next_review = SRSAlgorithm.get_next_review_date(new_interval)
    
    return {
        "ease_factor": new_ease,
        "interval_days": new_interval,
        "repetitions": new_reps,
        "next_review": next_review.isoformat(),
        "quality_rating": quality
    }
