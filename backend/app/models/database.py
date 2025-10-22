"""
Database models for the chess learning platform
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User profile and stats"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True)
    current_elo = Column(Integer, default=1200)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Preferences
    preferred_persona = Column(String, default="friendly_teacher")
    preferred_color = Column(String, default="white")
    
    # Relationships
    games = relationship("Game", back_populates="user")
    training_sessions = relationship("TrainingSession", back_populates="user")
    puzzle_attempts = relationship("PuzzleAttempt", back_populates="user")


class Game(Base):
    """Chess game record"""
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Game details
    pgn = Column(Text)
    fen_final = Column(String)
    moves = Column(JSON)  # List of moves in SAN notation
    result = Column(String)  # "1-0", "0-1", "1/2-1/2"
    
    # Configuration
    player_color = Column(String)
    player_elo = Column(Integer)
    ai_persona = Column(String)
    
    # Analysis
    mistakes = Column(JSON)  # List of mistake objects
    blunders = Column(JSON)
    inaccuracies = Column(JSON)
    average_centipawn_loss = Column(Float)
    
    # Metadata
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime)
    duration_seconds = Column(Integer)
    
    # Relationships
    user = relationship("User", back_populates="games")


class Opening(Base):
    """Chess opening database"""
    __tablename__ = "openings"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    eco_code = Column(String, index=True)  # ECO classification (e.g., "C50")
    
    # Opening details
    moves = Column(JSON)  # List of moves in SAN notation
    fen = Column(String)  # Position after opening moves
    description = Column(Text)
    popularity = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # Theory
    key_ideas = Column(JSON)  # List of strategic ideas
    common_mistakes = Column(JSON)
    variations = Column(JSON)  # Dict of variation names to move lists
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)


class Puzzle(Base):
    """Chess puzzle/tactic"""
    __tablename__ = "puzzles"
    
    id = Column(Integer, primary_key=True, index=True)
    lichess_id = Column(String, unique=True, index=True)
    
    # Puzzle data
    fen = Column(String, nullable=False)
    moves = Column(JSON)  # List of moves (solution)
    rating = Column(Integer, index=True)
    rating_deviation = Column(Integer)
    
    # Classification
    themes = Column(JSON)  # List of themes (e.g., ["fork", "pin"])
    game_url = Column(String)
    
    # Metadata
    popularity = Column(Integer, default=0)
    nb_plays = Column(Integer, default=0)
    
    # Relationships
    attempts = relationship("PuzzleAttempt", back_populates="puzzle")


class PuzzleAttempt(Base):
    """User's attempt at a puzzle"""
    __tablename__ = "puzzle_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    puzzle_id = Column(Integer, ForeignKey("puzzles.id"))
    
    # Attempt data
    solved = Column(Boolean, default=False)
    time_seconds = Column(Integer)
    moves_made = Column(JSON)  # List of moves user made
    hints_used = Column(Integer, default=0)
    
    # Timestamp
    attempted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="puzzle_attempts")
    puzzle = relationship("Puzzle", back_populates="attempts")


class TrainingSession(Base):
    """Spaced repetition training session"""
    __tablename__ = "training_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Session details
    session_type = Column(String)  # "opening", "tactic", "endgame"
    items_completed = Column(Integer, default=0)
    items_total = Column(Integer)
    accuracy = Column(Float)  # 0.0 to 1.0
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="training_sessions")
    items = relationship("TrainingItem", back_populates="session")


class TrainingItem(Base):
    """Individual item in a training session (SRS)"""
    __tablename__ = "training_items"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("training_sessions.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Item content
    item_type = Column(String)  # "opening_line", "tactic", "endgame_position"
    content = Column(JSON)  # Flexible content storage
    question = Column(Text)
    answer = Column(JSON)
    
    # SRS data
    ease_factor = Column(Float, default=2.5)  # Anki-like ease factor
    interval_days = Column(Integer, default=1)
    repetitions = Column(Integer, default=0)
    next_review = Column(DateTime)
    
    # Last attempt
    last_reviewed = Column(DateTime)
    last_result = Column(Boolean)  # True = correct, False = incorrect
    
    # Relationships
    session = relationship("TrainingSession", back_populates="items")


class UserStats(Base):
    """Aggregated user statistics"""
    __tablename__ = "user_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Game stats
    games_played = Column(Integer, default=0)
    games_won = Column(Integer, default=0)
    games_drawn = Column(Integer, default=0)
    games_lost = Column(Integer, default=0)
    
    # Performance
    puzzles_solved = Column(Integer, default=0)
    puzzles_attempted = Column(Integer, default=0)
    puzzle_accuracy = Column(Float, default=0.0)
    
    # ELO tracking
    elo_peak = Column(Integer)
    elo_lowest = Column(Integer)
    elo_history = Column(JSON)  # List of {date, elo} objects
    
    # Learning
    learning_streak_days = Column(Integer, default=0)
    last_active = Column(DateTime)
    total_study_time_minutes = Column(Integer, default=0)
    
    # Opening performance
    opening_stats = Column(JSON)  # Dict of opening_name -> {wins, losses, accuracy}
    weak_areas = Column(JSON)  # List of identified weak areas
    favorite_openings = Column(JSON)  # List of opening names
    
    # Metadata
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
