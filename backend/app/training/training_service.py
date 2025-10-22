"""
Training service - SRS, puzzles, opening trainer
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SRSAlgorithm:
    """Spaced Repetition System (Anki-like algorithm)"""
    
    @staticmethod
    def calculate_next_interval(
        ease_factor: float,
        interval_days: int,
        repetitions: int,
        quality: int  # 0-5: 0=wrong, 5=perfect
    ) -> tuple[float, int, int]:
        """
        Calculate next review interval using SM-2 algorithm.
        
        Returns:
            (new_ease_factor, new_interval_days, new_repetitions)
        """
        # Update ease factor
        new_ease = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ease = max(1.3, new_ease)  # Minimum ease factor
        
        # Update interval
        if quality < 3:
            # Failed - reset
            new_interval = 1
            new_reps = 0
        else:
            # Passed - increase interval
            if repetitions == 0:
                new_interval = 1
            elif repetitions == 1:
                new_interval = 6
            else:
                new_interval = int(interval_days * new_ease)
            new_reps = repetitions + 1
        
        return new_ease, new_interval, new_reps
    
    @staticmethod
    def get_next_review_date(interval_days: int) -> datetime:
        """Get next review date based on interval"""
        return datetime.utcnow() + timedelta(days=interval_days)


class OpeningTrainer:
    """Opening repertoire training"""
    
    # Common openings database (subset)
    OPENINGS = {
        "Italian Game": {
            "eco": "C50",
            "moves": ["e4", "e5", "Nf3", "Nc6", "Bc4"],
            "ideas": [
                "Control center with e4",
                "Develop bishop to active square",
                "Prepare castling kingside"
            ],
            "mistakes": [
                "Moving same piece twice early",
                "Neglecting center control"
            ],
            "popularity": 0.85
        },
        "Sicilian Defense": {
            "eco": "B20",
            "moves": ["e4", "c5"],
            "ideas": [
                "Fight for initiative as Black",
                "Asymmetric pawn structure",
                "Counter-attack on queenside"
            ],
            "mistakes": [
                "Allowing Nc3-d5",
                "Ignoring piece development"
            ],
            "popularity": 0.95
        },
        "French Defense": {
            "eco": "C00",
            "moves": ["e4", "e6"],
            "ideas": [
                "Solid pawn chain",
                "Control d5 square",
                "Prepare ...d5 break"
            ],
            "mistakes": [
                "Blocking in light-squared bishop",
                "Passive piece placement"
            ],
            "popularity": 0.70
        },
        "Caro-Kann Defense": {
            "eco": "B10",
            "moves": ["e4", "c6"],
            "ideas": [
                "Solid defense like French but keeps bishop active",
                "Prepare ...d5",
                "Less space but fewer weaknesses"
            ],
            "mistakes": [
                "Too passive development",
                "Allowing e5 pawn wedge"
            ],
            "popularity": 0.75
        },
        "Queen's Gambit": {
            "eco": "D06",
            "moves": ["d4", "d5", "c4"],
            "ideas": [
                "Offer pawn for central control",
                "Develop queenside quickly",
                "Create imbalances"
            ],
            "mistakes": [
                "Taking c4 pawn and holding it",
                "Neglecting piece development"
            ],
            "popularity": 0.90
        },
        "King's Indian Defense": {
            "eco": "E60",
            "moves": ["d4", "Nf6", "c4", "g6"],
            "ideas": [
                "Hypermodern - control center from distance",
                "Fianchetto kingside bishop",
                "Prepare pawn breaks"
            ],
            "mistakes": [
                "Allowing center to get locked",
                "Premature attacks"
            ],
            "popularity": 0.80
        },
        "Ruy Lopez": {
            "eco": "C60",
            "moves": ["e4", "e5", "Nf3", "Nc6", "Bb5"],
            "ideas": [
                "Pressure on e5 pawn",
                "Develop with tempo",
                "Long-term strategic advantage"
            ],
            "mistakes": [
                "Exchanging bishop too early",
                "Allowing ...d5 easily"
            ],
            "popularity": 0.88
        }
    }
    
    @classmethod
    def get_opening_by_name(cls, name: str) -> Optional[Dict[str, Any]]:
        """Get opening details by name"""
        return cls.OPENINGS.get(name)
    
    @classmethod
    def get_all_openings(cls) -> List[Dict[str, Any]]:
        """Get all openings with names"""
        return [
            {"name": name, **details}
            for name, details in cls.OPENINGS.items()
        ]
    
    @classmethod
    def get_popular_openings(cls, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most popular openings"""
        openings = cls.get_all_openings()
        sorted_openings = sorted(openings, key=lambda x: x["popularity"], reverse=True)
        return sorted_openings[:limit]
    
    @classmethod
    def generate_opening_quiz(cls, opening_name: str) -> Dict[str, Any]:
        """Generate a quiz question for an opening"""
        opening = cls.get_opening_by_name(opening_name)
        if not opening:
            return {}
        
        quiz_types = [
            {
                "type": "identify_move",
                "question": f"What is the next move in {opening_name} after {' '.join(opening['moves'][:-1])}?",
                "answer": opening["moves"][-1],
                "options": cls._generate_move_options(opening["moves"][-1])
            },
            {
                "type": "key_idea",
                "question": f"What is a key idea in {opening_name}?",
                "answer": random.choice(opening["ideas"]),
                "options": cls._generate_idea_options(opening["ideas"])
            },
            {
                "type": "common_mistake",
                "question": f"What is a common mistake in {opening_name}?",
                "answer": random.choice(opening["mistakes"]),
                "options": cls._generate_mistake_options(opening["mistakes"])
            }
        ]
        
        return random.choice(quiz_types)
    
    @staticmethod
    def _generate_move_options(correct_move: str) -> List[str]:
        """Generate plausible wrong move options"""
        # Simplified - in production, use legal moves from position
        common_moves = ["d4", "Nf3", "Nc3", "e5", "c5", "Bf4", "Be3"]
        options = [correct_move]
        while len(options) < 4:
            move = random.choice(common_moves)
            if move not in options:
                options.append(move)
        random.shuffle(options)
        return options
    
    @staticmethod
    def _generate_idea_options(ideas: List[str]) -> List[str]:
        """Generate plausible wrong idea options"""
        wrong_ideas = [
            "Sacrifice queen for activity",
            "Trade all pieces quickly",
            "Ignore pawn structure",
            "Always castle queenside"
        ]
        correct = random.choice(ideas)
        options = [correct]
        for idea in wrong_ideas:
            if len(options) >= 4:
                break
            if idea not in options:
                options.append(idea)
        random.shuffle(options)
        return options
    
    @staticmethod
    def _generate_mistake_options(mistakes: List[str]) -> List[str]:
        """Generate plausible correct action options (opposite of mistakes)"""
        correct = random.choice(mistakes)
        wrong_options = [
            "Developing all pieces harmoniously",
            "Controlling the center effectively",
            "Castling at the right time"
        ]
        options = [correct] + wrong_options[:3]
        random.shuffle(options)
        return options


class PuzzleGenerator:
    """Generate and select chess puzzles"""
    
    @staticmethod
    def get_puzzles_by_rating(
        target_rating: int,
        count: int = 10,
        theme: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get puzzles near target rating.
        
        In production, this would query Lichess API or local puzzle database.
        """
        # Placeholder implementation
        puzzles = []
        for i in range(count):
            puzzle = {
                "id": f"puzzle_{i}_{target_rating}",
                "rating": target_rating + random.randint(-50, 50),
                "fen": "rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 2 4",
                "moves": ["Nxe5", "Nxe5", "Qf3"],
                "themes": [theme] if theme else ["fork", "pin"],
            }
            puzzles.append(puzzle)
        return puzzles
    
    @staticmethod
    def generate_from_mistakes(
        mistakes: List[Dict[str, Any]],
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate puzzles based on user's mistakes.
        
        Analyzes common mistake patterns and creates similar positions.
        """
        # Placeholder - in production, use position patterns from mistakes
        if not mistakes:
            return []
        
        # Group mistakes by type
        mistake_themes = {}
        for mistake in mistakes:
            theme = mistake.get("classification", "tactical")
            if theme not in mistake_themes:
                mistake_themes[theme] = []
            mistake_themes[theme].append(mistake)
        
        # Generate puzzles for each theme
        puzzles = []
        for theme, theme_mistakes in mistake_themes.items():
            if len(puzzles) >= count:
                break
            
            # Sample a mistake
            sample = random.choice(theme_mistakes)
            puzzle = {
                "id": f"custom_{theme}_{len(puzzles)}",
                "rating": 1500,  # Adjust based on user level
                "fen": sample.get("fen", "starting_position"),
                "moves": ["best_move_here"],
                "themes": [theme],
                "source": "generated_from_mistakes"
            }
            puzzles.append(puzzle)
        
        return puzzles


class MistakeAnalyzer:
    """Analyze game mistakes and suggest training"""
    
    @staticmethod
    def analyze_game_mistakes(
        moves: List[Dict[str, Any]],
        evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze a game's mistakes and categorize them.
        
        Returns:
            Dict with mistakes, blunders, inaccuracies, and suggestions
        """
        mistakes = []
        blunders = []
        inaccuracies = []
        
        for i, (move, eval_data) in enumerate(zip(moves, evaluations)):
            classification = eval_data.get("classification")
            score_diff = eval_data.get("score_difference", 0)
            
            error_data = {
                "move_number": i + 1,
                "move": move,
                "classification": classification,
                "score_loss": abs(score_diff),
                "fen": eval_data.get("fen")
            }
            
            if classification == "blunder":
                blunders.append(error_data)
            elif classification == "mistake":
                mistakes.append(error_data)
            elif classification == "inaccuracy":
                inaccuracies.append(error_data)
        
        # Calculate average centipawn loss
        total_loss = sum(
            m["score_loss"] for m in mistakes + blunders + inaccuracies
        )
        avg_loss = total_loss / len(moves) if moves else 0
        
        # Identify patterns
        patterns = MistakeAnalyzer._identify_patterns(mistakes + blunders)
        
        return {
            "blunders": blunders,
            "mistakes": mistakes,
            "inaccuracies": inaccuracies,
            "total_errors": len(mistakes) + len(blunders) + len(inaccuracies),
            "average_centipawn_loss": avg_loss,
            "patterns": patterns,
            "suggestions": MistakeAnalyzer._generate_suggestions(patterns)
        }
    
    @staticmethod
    def _identify_patterns(errors: List[Dict[str, Any]]) -> List[str]:
        """Identify common mistake patterns"""
        patterns = []
        
        # Simple pattern detection (can be expanded)
        if len(errors) > 5:
            patterns.append("multiple_tactical_errors")
        
        # Check for errors in opening (first 10 moves)
        opening_errors = [e for e in errors if e["move_number"] <= 10]
        if len(opening_errors) > 2:
            patterns.append("weak_opening")
        
        # Check for errors in endgame (after move 40)
        endgame_errors = [e for e in errors if e["move_number"] > 40]
        if len(endgame_errors) > 2:
            patterns.append("weak_endgame")
        
        return patterns
    
    @staticmethod
    def _generate_suggestions(patterns: List[str]) -> List[str]:
        """Generate training suggestions based on patterns"""
        suggestions = []
        
        if "weak_opening" in patterns:
            suggestions.append("Practice opening theory and principles")
            suggestions.append("Use the opening trainer daily")
        
        if "weak_endgame" in patterns:
            suggestions.append("Study basic endgame positions")
            suggestions.append("Practice rook endgames")
        
        if "multiple_tactical_errors" in patterns:
            suggestions.append("Solve tactics puzzles (20-30 min/day)")
            suggestions.append("Calculate variations before moving")
        
        if not suggestions:
            suggestions.append("Keep playing and analyzing your games")
            suggestions.append("Focus on reducing blunders")
        
        return suggestions
