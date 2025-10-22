"""
Chess Engine Manager - Handles Stockfish and Maia engines
"""
import chess
import chess.engine
import asyncio
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
import shutil

from app.config import settings

logger = logging.getLogger(__name__)


class EngineManager:
    """Manages chess engines (Stockfish and Maia) for game play and analysis."""
    
    def __init__(self):
        self.stockfish_engine: Optional[chess.engine.SimpleEngine] = None
        self.maia_engine: Optional[chess.engine.SimpleEngine] = None
        self._stockfish_path: Optional[Path] = None
        self._maia_path: Optional[Path] = None
    
    async def initialize(self):
        """Initialize chess engines."""
        logger.info("Initializing chess engines...")
        
        # Find and initialize Stockfish
        await self._init_stockfish()
        
        # Find and initialize Maia (optional)
        await self._init_maia()
        
        if not self.stockfish_engine:
            logger.warning("⚠️  Stockfish not available - some features will be limited")
        else:
            logger.info("✓ Stockfish initialized")
        
        if not self.maia_engine:
            logger.warning("⚠️  Maia not available - using Stockfish for all analysis")
        else:
            logger.info("✓ Maia initialized")
    
    async def _init_stockfish(self):
        """Initialize Stockfish engine."""
        try:
            # Try configured path first
            if settings.STOCKFISH_PATH:
                self._stockfish_path = Path(settings.STOCKFISH_PATH)
            else:
                # Auto-detect Stockfish
                self._stockfish_path = self._find_stockfish()
            
            if self._stockfish_path and self._stockfish_path.exists():
                transport, engine = await chess.engine.popen_uci(str(self._stockfish_path))
                self.stockfish_engine = engine
                logger.info(f"Stockfish loaded from: {self._stockfish_path}")
            else:
                logger.warning("Stockfish not found. Please install or configure path.")
        except Exception as e:
            logger.error(f"Failed to initialize Stockfish: {e}")
    
    async def _init_maia(self):
        """Initialize Maia engine."""
        try:
            if settings.MAIA_PATH:
                self._maia_path = Path(settings.MAIA_PATH)
                if self._maia_path.exists():
                    transport, engine = await chess.engine.popen_uci(str(self._maia_path))
                    self.maia_engine = engine
                    logger.info(f"Maia loaded from: {self._maia_path}")
        except Exception as e:
            logger.error(f"Failed to initialize Maia: {e}")
    
    def _find_stockfish(self) -> Optional[Path]:
        """Auto-detect Stockfish installation."""
        # Common paths for Stockfish
        common_paths = [
            "stockfish",  # System PATH
            "/usr/local/bin/stockfish",
            "/usr/bin/stockfish",
            "/opt/homebrew/bin/stockfish",
            "C:\\Program Files\\Stockfish\\stockfish.exe",
        ]
        
        for path_str in common_paths:
            path = shutil.which(path_str) or path_str
            path_obj = Path(path)
            if path_obj.exists():
                return path_obj
        
        return None
    
    async def shutdown(self):
        """Shutdown all chess engines."""
        if self.stockfish_engine:
            await self.stockfish_engine.quit()
            logger.info("Stockfish engine shutdown")
        
        if self.maia_engine:
            await self.maia_engine.quit()
            logger.info("Maia engine shutdown")
    
    def is_ready(self) -> bool:
        """Check if at least one engine is available."""
        return self.stockfish_engine is not None
    
    def stockfish_available(self) -> bool:
        """Check if Stockfish is available."""
        return self.stockfish_engine is not None
    
    def maia_available(self) -> bool:
        """Check if Maia is available."""
        return self.maia_engine is not None
    
    async def analyze_position(
        self,
        board: chess.Board,
        depth: int = 20,
        multipv: int = 3,
        use_maia: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Analyze a chess position.
        
        Args:
            board: Chess board to analyze
            depth: Analysis depth (higher = stronger, slower)
            multipv: Number of best moves to return
            use_maia: Use Maia for human-like analysis
        
        Returns:
            List of analysis results with moves and evaluations
        """
        engine = self.maia_engine if use_maia and self.maia_engine else self.stockfish_engine
        
        if not engine:
            raise RuntimeError("No chess engine available for analysis")
        
        try:
            info = await engine.analyse(
                board,
                chess.engine.Limit(depth=depth),
                multipv=multipv
            )
            
            results = []
            for item in info if isinstance(info, list) else [info]:
                score = item.get("score")
                pv = item.get("pv", [])
                
                result = {
                    "move": pv[0].uci() if pv else None,
                    "score": self._format_score(score),
                    "depth": item.get("depth"),
                    "pv": [move.uci() for move in pv[:5]],  # First 5 moves of principal variation
                }
                results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise
    
    async def get_best_move(
        self,
        board: chess.Board,
        elo: Optional[int] = None,
        time_limit: float = 1.0,
        use_maia: bool = False
    ) -> chess.Move:
        """
        Get the best move for the current position.
        
        Args:
            board: Chess board
            elo: Target ELO rating (for calibrated play)
            time_limit: Time limit in seconds
            use_maia: Use Maia for human-like moves
        
        Returns:
            Best chess move
        """
        engine = self.maia_engine if use_maia and self.maia_engine else self.stockfish_engine
        
        if not engine:
            raise RuntimeError("No chess engine available")
        
        # Adjust engine strength based on ELO
        if elo and self.stockfish_engine == engine:
            await self._set_elo_limit(engine, elo)
        
        try:
            result = await engine.play(
                board,
                chess.engine.Limit(time=time_limit),
                info=chess.engine.INFO_ALL
            )
            return result.move
        except Exception as e:
            logger.error(f"Failed to get best move: {e}")
            raise
    
    async def _set_elo_limit(self, engine: chess.engine.SimpleEngine, elo: int):
        """Configure Stockfish to play at a specific ELO level."""
        await engine.configure({"UCI_LimitStrength": True, "UCI_Elo": elo})
    
    def _format_score(self, score: Optional[chess.engine.Score]) -> Dict[str, Any]:
        """Format engine score for API response."""
        if not score:
            return {"type": "unknown", "value": 0}
        
        if score.is_mate():
            return {
                "type": "mate",
                "value": score.relative.mate(),
                "display": f"M{score.relative.mate()}"
            }
        else:
            cp = score.relative.score()
            return {
                "type": "cp",
                "value": cp,
                "display": f"{cp/100:.2f}" if cp is not None else "0.00"
            }
    
    async def evaluate_move_quality(
        self,
        board: chess.Board,
        move: chess.Move,
        depth: int = 18
    ) -> Dict[str, Any]:
        """
        Evaluate the quality of a move (brilliant, good, inaccuracy, mistake, blunder).
        
        Args:
            board: Chess board before the move
            move: The move to evaluate
            depth: Analysis depth
        
        Returns:
            Move evaluation with classification and score difference
        """
        if not self.stockfish_engine:
            raise RuntimeError("Stockfish required for move evaluation")
        
        # Analyze position before move
        before_analysis = await self.analyze_position(board, depth=depth, multipv=1)
        before_score = before_analysis[0]["score"]["value"] if before_analysis else 0
        
        # Make the move
        board.push(move)
        
        # Analyze position after move
        after_analysis = await self.analyze_position(board, depth=depth, multipv=1)
        after_score = after_analysis[0]["score"]["value"] if after_analysis else 0
        
        # Undo the move
        board.pop()
        
        # Calculate score difference (from player's perspective)
        score_diff = before_score - after_score if board.turn == chess.WHITE else after_score - before_score
        
        # Classify move quality
        classification = self._classify_move(score_diff)
        
        return {
            "move": move.uci(),
            "classification": classification,
            "score_difference": score_diff,
            "before_score": before_score,
            "after_score": after_score,
            "best_move": before_analysis[0]["move"] if before_analysis else None
        }
    
    def _classify_move(self, score_diff: float) -> str:
        """Classify move quality based on score difference (in centipawns)."""
        if score_diff <= -300:
            return "blunder"
        elif score_diff <= -100:
            return "mistake"
        elif score_diff <= -50:
            return "inaccuracy"
        elif score_diff >= 100:
            return "brilliant"
        elif score_diff >= 0:
            return "good"
        else:
            return "ok"
