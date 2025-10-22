"""
Configuration management for AI Chess Learning Platform
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    
    # Chess Engine Paths
    STOCKFISH_PATH: str = ""
    MAIA_PATH: str = ""
    
    # Lichess API
    LICHESS_API_TOKEN: str = ""
    LICHESS_USERNAME: str = ""
    
    # Chess.com API
    CHESSCOM_USERNAME: str = ""
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./chess_learning.db"
    
    # Training Configuration
    DEFAULT_PLAYER_ELO: int = 1200
    SRS_REVIEW_INTERVALS: str = "1,3,7,14,30"
    PUZZLE_DIFFICULTY_RANGE: int = 200
    
    # LLM Persona Configuration
    DEFAULT_PERSONA: str = "friendly_teacher"
    
    # Analytics
    TRACK_DETAILED_ANALYTICS: bool = True
    AUTO_GENERATE_REPORTS: bool = True
    WEEKLY_REPORT_DAY: str = "sunday"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def srs_intervals(self) -> List[int]:
        """Parse SRS review intervals from string to list of integers."""
        return [int(x.strip()) for x in self.SRS_REVIEW_INTERVALS.split(",")]


# Global settings instance
settings = Settings()
