# 🤖♟️ AI Chess Learning Platform

A fully open-source, privacy-first chess learning platform powered by local LLMs (via Ollama), Stockfish, and Maia. Learn chess through personalized AI coaching, interactive chat, adaptive training, and comprehensive game analysis—all running locally on your machine.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![Node](https://img.shields.io/badge/node-18+-green.svg)

## ✨ Features

### 🎮 Dynamic AI Opponent Chat
- **Persona-based opponents**: Play against "The Grandmaster," "Friendly Teacher," or "Aggressive Rival"
- **Live move explanations**: Ask "Why?" or "What if I...?" and get instant, natural-language feedback
- **Powered by Ollama**: Run Llama 3, Mistral, Phi, or other models locally—zero API costs

### 📚 Comprehensive Training Suite
- **Opening Explorer**: Learn major openings (Spanish, Sicilian, etc.) with interactive theory guides
- **MoveTrainer (SRS)**: Spaced-repetition drills for openings, tactics, and endgames
- **Mistake-based Puzzles**: Auto-generated puzzles targeting your weak points
- **Post-game Analysis**: Full blunder detection with natural-language improvement tips

### 📈 ELO Progression & Personalization
- **Adaptive Difficulty**: Bot calibrates to your rating, scaling engine depth and chat complexity
- **Performance Dashboard**: Track per-opening stats, tactics solved, ELO trends, and learning streaks
- **Automated Curriculum**: AI detects weak spots and schedules targeted review sessions

### 🎨 Modern, Accessible UI
- **Responsive Design**: Beautiful animated chessboard with drag-and-drop, mobile support
- **Collapsible Panels**: Moves list, opening explorer, mistake map, chat window
- **Accessibility**: Keyboard navigation, font scaling, colorblind-friendly themes

### 🔐 Privacy & Offline First
- **100% Local LLM**: All AI runs on your device via Ollama
- **No Subscriptions**: Open-source engines (Stockfish, Maia) and models
- **Optional Cloud Sync**: Lichess/Chess.com integration for game import/export

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js/React)                  │
│  • Chessboard UI  • Chat Interface  • Analytics Dashboard   │
└───────────────────────┬─────────────────────────────────────┘
                        │ WebSocket + REST API
┌───────────────────────▼─────────────────────────────────────┐
│              Backend (FastAPI + Python)                      │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Stockfish  │  │ Ollama LLM   │  │  Maia Chess  │       │
│  │  Engine     │  │ Integration  │  │  Engine      │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Training   │  │   Lichess/   │  │  Analytics   │       │
│  │  Module     │  │  Chess.com   │  │  Engine      │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Ollama** ([Install](https://ollama.ai))
- **Stockfish** ([Install](https://stockfishchess.org/download/))

### 1. Install Ollama and Download a Model

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Download Llama 3 (or your preferred model)
ollama pull llama3
# Alternatives: ollama pull mistral, ollama pull phi3
```

### 2. Clone and Setup Backend

```bash
# Clone repository
git clone https://github.com/ronaldjangam/AIChessBot.git
cd AIChessBot/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download Stockfish (if not installed system-wide)
# The app will guide you on first run

# Start backend
uvicorn app.main:app --reload
```

### 3. Setup Frontend

```bash
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Open in Browser

Navigate to `http://localhost:3000` and start learning chess!

## 📖 Documentation

- [Architecture Overview](./docs/ARCHITECTURE.md)
- [API Documentation](./docs/API.md)
- [LLM Integration Guide](./docs/OLLAMA_SETUP.md)
- [Training Modules](./docs/TRAINING.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance async Python web framework
- **python-chess**: Chess game logic and move validation
- **Stockfish**: World's strongest chess engine (analysis & play)
- **Maia**: Human-like chess engine for realistic mistakes
- **Ollama**: Local LLM inference (Llama 3, Mistral, etc.)
- **Berserk**: Lichess API client

### Frontend
- **Next.js 14**: React framework with App Router
- **Tailwind CSS**: Utility-first styling
- **react-chessboard**: Interactive chessboard component
- **Zustand**: State management
- **Socket.io**: Real-time communication

### AI Models
- **Llama 3 / Mistral / Phi**: Via Ollama (local inference)
- **Stockfish 16+**: Move analysis and adaptive play
- **Maia**: Human-like move prediction

## 🎯 Roadmap

- [x] Core architecture and project setup
- [ ] Chess engine integration (Stockfish + Maia)
- [ ] Ollama LLM service layer
- [ ] Basic game play interface
- [ ] Opening explorer and trainer
- [ ] Spaced-repetition (SRS) system
- [ ] Post-game analysis with LLM summaries
- [ ] Lichess/Chess.com API integration
- [ ] Analytics dashboard
- [ ] Mobile-responsive UI
- [ ] Accessibility features
- [ ] Export functionality (PGN, CSV, Anki)
- [ ] Automated daily/weekly reports
- [ ] Multi-language support

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](./CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🙏 Acknowledgments

- **Stockfish Team**: For the incredible open-source chess engine
- **Maia Chess**: For human-like AI research
- **Ollama**: For making local LLM inference accessible
- **Lichess**: For their generous open API
- **Chess.com**: For their platform and API

## 📧 Contact

- **Author**: Ronald Jangam
- **GitHub**: [@ronaldjangam](https://github.com/ronaldjangam)
- **Repository**: [AIChessBot](https://github.com/ronaldjangam/AIChessBot)

---

**Built with ❤️ for the chess community. Learn, improve, and master chess—privately and freely.**