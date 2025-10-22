# AI Chess Learning Platform - Architecture

## System Overview

The AI Chess Learning Platform is designed as a modular, scalable system with clear separation between frontend, backend, and AI services. All AI processing runs locally via Ollama, ensuring privacy and eliminating API costs.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer (Browser)                    │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Chess Board │  │ Chat Panel   │  │  Analytics   │       │
│  │ Component   │  │              │  │  Dashboard   │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
│         │                  │                 │              │
│         └──────────────────┴─────────────────┘              │
│                          │                                  │
└──────────────────────────┼──────────────────────────────────┘
                           │
              WebSocket + REST API (HTTPS)
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   API Gateway (FastAPI)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Endpoints: /game, /analysis, /training, /llm, /user │  │
│  └──────────────────────────────────────────────────────┘  │
└───────┬────────────┬────────────┬────────────┬─────────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ Engine   │  │  Ollama  │  │ Training │  │ External │
│ Manager  │  │  Service │  │  Module  │  │   APIs   │
│          │  │          │  │          │  │          │
│Stockfish │  │  Llama3  │  │   SRS    │  │ Lichess  │
│  Maia    │  │ Mistral  │  │ Puzzles  │  │Chess.com │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
      │             │             │             │
      └─────────────┴─────────────┴─────────────┘
                      │
               ┌──────▼──────┐
               │  Database   │
               │  (SQLite/   │
               │ PostgreSQL) │
               └─────────────┘
```

## Component Breakdown

### 1. Frontend (Next.js/React)

**Location**: `/frontend`

**Key Components**:
- **ChessBoard**: Interactive chess board with drag-and-drop
- **ChatPanel**: Real-time AI chat interface with persona switching
- **AnalysisPanel**: Move analysis and engine evaluations
- **TrainingDashboard**: Opening explorer, puzzles, SRS drills
- **GameHistory**: Past games with annotations and insights
- **SettingsPanel**: User preferences, persona config, engine settings

**State Management**:
- Zustand stores for game state, user preferences, training data
- WebSocket manager for real-time updates
- API client wrapper (axios) for REST endpoints

**Styling**:
- Tailwind CSS for responsive, utility-first design
- Framer Motion for animations and transitions
- Custom chess theme with accessibility features

### 2. Backend (FastAPI/Python)

**Location**: `/backend`

**Core Modules**:

#### a. API Layer (`/app/api`)
- **game.py**: Game creation, move handling, state management
- **analysis.py**: Position analysis, move evaluation
- **llm.py**: Chat, explanations, persona management
- **training.py**: Openings, puzzles, SRS sessions
- **user.py**: User stats, game history, external API integration

#### b. Service Layer (`/app/services`)
- **engine_manager.py**: Chess engine orchestration (Stockfish/Maia)
- **ollama_service.py**: LLM integration and prompt engineering
- **training_service.py**: SRS algorithm, puzzle generation
- **analytics_service.py**: Stats tracking, report generation
- **lichess_service.py**: Lichess API integration (via Berserk)

#### c. Models (`/app/models`)
- **schemas.py**: Pydantic models for API validation
- **database.py**: SQLAlchemy ORM models
- **enums.py**: Shared enumerations

### 3. Chess Engines

#### Stockfish
- **Purpose**: Strongest analysis, calibrated play (1400-3000 ELO)
- **Features**: 
  - Multi-PV analysis (multiple best moves)
  - Depth-limited search
  - UCI protocol communication
  - ELO-calibrated strength limiting

#### Maia
- **Purpose**: Human-like move prediction, mistake modeling
- **Features**:
  - Realistic blunders at various skill levels
  - Training data based on real human games
  - Multiple Maia models for different ELO ranges

### 4. Ollama LLM Service

**Models Supported**:
- Llama 3 (default, best all-around)
- Mistral (fast, efficient)
- Phi-3 (lightweight, quick responses)
- Qwen2 (multilingual support)

**Persona System**:
Three distinct AI personalities with custom prompts:

1. **The Grandmaster**
   - Analytical, technical, demanding
   - Uses chess notation and theory
   - Best for advanced players

2. **Friendly Teacher**
   - Encouraging, patient, explanatory
   - Uses analogies and simple language
   - Best for beginners/intermediate

3. **Aggressive Rival**
   - Competitive, playful trash talk
   - Energetic and motivating
   - Best for casual, fun learning

**Capabilities**:
- Real-time chat during games
- Move-by-move explanations
- Opening theory guides
- Post-game analysis summaries
- Personalized lesson generation

### 5. Training System

#### Opening Explorer
- Database of 100+ major openings
- Interactive move tree visualization
- Line-by-line theory with LLM explanations
- Performance tracking per opening

#### MoveTrainer (SRS)
- Spaced Repetition System (Anki-like)
- Dynamic intervals: 1, 3, 7, 14, 30 days
- Categories: Openings, Tactics, Endgames
- Adaptive difficulty based on accuracy

#### Puzzle Engine
- Lichess puzzle database integration
- Auto-generated puzzles from user mistakes
- Theme-based filtering (pins, forks, mates)
- ELO-calibrated difficulty

### 6. Analytics Engine

**Tracked Metrics**:
- ELO progression over time
- Accuracy by opening
- Mistake patterns (tactical, positional)
- Time management
- Learning streaks

**Reports**:
- Daily summary (auto-generated at end of session)
- Weekly report (comprehensive analysis, AI-generated)
- Strength/weakness heatmap

## Data Flow Examples

### Game Move Sequence

```
1. User drags piece on board (Frontend)
   ↓
2. WebSocket sends move to /ws/game/{id} (Backend)
   ↓
3. Game service validates move with python-chess
   ↓
4. Engine manager calculates AI response (Stockfish/Maia)
   ↓
5. Ollama generates chat response based on move quality
   ↓
6. WebSocket broadcasts: AI move + chat message
   ↓
7. Frontend updates board + chat panel
```

### Analysis Request

```
1. User clicks "Analyze Position" (Frontend)
   ↓
2. POST /api/analysis/position (REST API)
   ↓
3. Engine manager runs Stockfish multi-PV analysis
   ↓
4. Returns top 3 moves with evaluations
   ↓
5. User clicks "Explain" on a move
   ↓
6. POST /api/llm/explain-move
   ↓
7. Ollama generates natural language explanation
   ↓
8. Frontend displays formatted explanation
```

## Scalability Considerations

### Current (v1.0)
- Single-user, local deployment
- In-memory game storage
- SQLite database
- Direct engine subprocesses

### Future (v2.0+)
- Multi-user support with authentication
- PostgreSQL with connection pooling
- Redis for session/cache management
- Kubernetes for engine orchestration
- Horizontal scaling of API servers

## Security

- **Local-first**: No user data leaves the machine
- **Optional cloud sync**: Encrypted game export to Lichess/Chess.com
- **No API keys**: Zero dependency on paid services
- **CORS**: Strict origin checking for API access
- **Input validation**: Pydantic schemas for all endpoints

## Deployment Options

### Development
```bash
# Backend
uvicorn app.main:app --reload

# Frontend  
npm run dev

# Ollama
ollama serve
```

### Production
- **Docker Compose**: Single-command deployment
- **Nginx**: Reverse proxy for API + static files
- **Systemd**: Service management on Linux
- **PM2**: Process manager for Node.js frontend (if needed)

## Technology Decisions Rationale

| Technology | Why Chosen |
|------------|------------|
| **FastAPI** | Async support, automatic API docs, excellent performance |
| **Next.js** | SSR/SSG flexibility, excellent DX, production-ready |
| **Ollama** | Local LLM inference, model flexibility, no cloud dependency |
| **Stockfish** | Industry-standard, strongest open-source engine |
| **python-chess** | Comprehensive chess logic, well-maintained |
| **Tailwind** | Rapid UI development, consistent design system |
| **WebSockets** | Real-time bidirectional communication for games |

## Performance Targets

- **Move analysis**: < 2s for depth 20
- **LLM response**: < 3s for chat messages
- **Frontend load**: < 1s initial page load
- **WebSocket latency**: < 50ms for move updates
- **Database queries**: < 100ms for user stats
