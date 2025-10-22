# API Documentation

Base URL: `http://localhost:8000/api`

## Authentication

Currently, the platform runs in single-user mode with no authentication required. Future versions will include user authentication.

## Endpoints

### Game Management

#### Start New Game
```http
POST /game/start
```

**Request Body:**
```json
{
  "player_color": "white",
  "player_elo": 1200,
  "ai_persona": "friendly_teacher",
  "use_maia": false
}
```

**Response:**
```json
{
  "game_id": "uuid-string",
  "fen": "starting-position-fen",
  "moves": [],
  "player_color": "white",
  "ai_persona": "friendly_teacher",
  "is_game_over": false,
  "result": null,
  "created_at": "2025-10-22T10:00:00Z",
  "updated_at": "2025-10-22T10:00:00Z"
}
```

#### Make Move
```http
POST /game/move
```

**Request Body:**
```json
{
  "game_id": "uuid-string",
  "move": "e2e4"
}
```

**Response:**
```json
{
  "success": true,
  "move": "e2e4",
  "fen": "position-after-move",
  "is_game_over": false,
  "result": null,
  "ai_move": "e7e5",
  "ai_fen": "position-after-ai-move"
}
```

#### Get Game State
```http
GET /game/{game_id}
```

**Response:**
```json
{
  "game_id": "uuid-string",
  "fen": "current-position",
  "moves": ["e2e4", "e7e5", "g1f3"],
  "player_color": "white",
  "ai_persona": "friendly_teacher",
  "is_game_over": false,
  "result": null,
  "created_at": "2025-10-22T10:00:00Z",
  "updated_at": "2025-10-22T10:05:00Z"
}
```

### Analysis

#### Analyze Position
```http
POST /analysis/position
```

**Request Body:**
```json
{
  "fen": "position-fen",
  "depth": 20,
  "multipv": 3,
  "use_maia": false
}
```

**Response:**
```json
[
  {
    "move": "e2e4",
    "score": {
      "type": "cp",
      "value": 25,
      "display": "0.25"
    },
    "depth": 20,
    "pv": ["e2e4", "e7e5", "g1f3", "b8c6"]
  },
  {
    "move": "d2d4",
    "score": {
      "type": "cp",
      "value": 20,
      "display": "0.20"
    },
    "depth": 20,
    "pv": ["d2d4", "d7d5", "c2c4"]
  }
]
```

#### Evaluate Move Quality
```http
POST /analysis/evaluate-move
```

**Request Body:**
```json
{
  "fen": "position-before-move",
  "move": "e2e4",
  "depth": 18
}
```

**Response:**
```json
{
  "move": "e2e4",
  "classification": "good",
  "score_difference": 15,
  "before_score": 10,
  "after_score": 25,
  "best_move": "d2d4"
}
```

### LLM / Chat

#### Send Chat Message
```http
POST /llm/chat
```

**Request Body:**
```json
{
  "message": "Why is controlling the center important?",
  "game_id": "optional-game-id",
  "context": {
    "position": "current-fen",
    "move": "last-move"
  },
  "persona": "friendly_teacher",
  "stream": false
}
```

**Response:**
```json
{
  "message": "Controlling the center is crucial because...",
  "persona": "friendly_teacher",
  "timestamp": "2025-10-22T10:00:00Z"
}
```

#### Explain Move
```http
POST /llm/explain-move
```

**Request Body:**
```json
{
  "move": "e2e4",
  "fen": "starting-position",
  "evaluation": {
    "classification": "good",
    "score_difference": 20
  },
  "persona": "grandmaster"
}
```

**Response:**
```json
{
  "move": "e2e4",
  "explanation": "The move 1.e4 is excellent because...",
  "persona": "grandmaster"
}
```

#### List Personas
```http
GET /llm/personas
```

**Response:**
```json
{
  "personas": [
    {
      "id": "grandmaster",
      "name": "The Grandmaster",
      "style": "analytical"
    },
    {
      "id": "friendly_teacher",
      "name": "Friendly Teacher",
      "style": "encouraging"
    },
    {
      "id": "aggressive_rival",
      "name": "Aggressive Rival",
      "style": "competitive"
    }
  ]
}
```

### Training

#### List Openings
```http
GET /training/openings?limit=20
```

**Response:**
```json
[
  {
    "name": "Italian Game",
    "eco_code": "C50",
    "moves": ["e4", "e5", "Nf3", "Nc6", "Bc4"],
    "description": "Classical opening focusing on central control",
    "popularity": 0.85
  }
]
```

### Health Check

#### API Status
```http
GET /
```

**Response:**
```json
{
  "message": "AI Chess Learning Platform API",
  "version": "1.0.0",
  "status": "operational",
  "docs": "/docs",
  "ollama_connected": true,
  "engines_ready": true
}
```

#### Detailed Health
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "stockfish": true,
    "maia": false,
    "ollama": true,
    "database": true
  },
  "ollama_model": "llama3",
  "version": "1.0.0"
}
```

## WebSocket

### Game WebSocket
```
ws://localhost:8000/ws/game/{game_id}
```

**Message Types:**

**Client → Server:**
```json
{
  "type": "move",
  "move": "e2e4"
}
```

```json
{
  "type": "chat",
  "message": "Why is this good?"
}
```

```json
{
  "type": "hint",
  "difficulty": "easy"
}
```

**Server → Client:**
```json
{
  "type": "move_response",
  "success": true,
  "ai_move": "e7e5",
  "fen": "new-position"
}
```

```json
{
  "type": "chat_response",
  "message": "That move is excellent because...",
  "persona": "friendly_teacher"
}
```

## Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad request (invalid input)
- `404`: Resource not found
- `500`: Internal server error
- `503`: Service unavailable (e.g., Ollama not running)

## Rate Limiting

Currently, no rate limiting is implemented for local single-user deployment. Future multi-user versions will include rate limiting.

## Interactive Documentation

FastAPI automatically generates interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
