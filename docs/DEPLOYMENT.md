# Deployment & Setup Guide

Complete guide to getting the AI Chess Learning Platform running on your machine.

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Python 3.10 or higher** - [Download](https://www.python.org/downloads/)
- [ ] **Node.js 18 or higher** - [Download](https://nodejs.org/)
- [ ] **Git** - [Download](https://git-scm.com/)
- [ ] **Ollama** - [Install Guide](./OLLAMA_SETUP.md)
- [ ] **Stockfish** (chess engine)

## Quick Start (5 Minutes)

### 1. Install Ollama and Download a Model

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download Llama 3
ollama pull llama3

# Keep Ollama running in background
ollama serve
```

### 2. Install Stockfish

**macOS:**
```bash
brew install stockfish
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install stockfish
```

**Windows:**
1. Download from [stockfishchess.org](https://stockfishchess.org/download/)
2. Extract to `C:\Program Files\Stockfish\`
3. Add to PATH or note the full path

### 3. Clone and Setup Project

```bash
# Clone repository
git clone https://github.com/ronaldjangam/AIChessBot.git
cd AIChessBot
```

### 4. Setup Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env if needed (optional - defaults work for most setups)
# nano .env
```

**Start the backend:**
```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Starting AI Chess Learning Platform...
INFO:     ✓ Stockfish initialized
INFO:     ✓ Ollama connected - Model: llama3
INFO:     ✓ All services initialized successfully
```

### 5. Setup Frontend (New Terminal)

```bash
# Open new terminal, navigate to project
cd AIChessBot/frontend

# Install dependencies
npm install

# Create env file
cp .env.local.example .env.local

# Start development server
npm run dev
```

You should see:
```
ready - started server on 0.0.0.0:3000
```

### 6. Open in Browser

Navigate to: **http://localhost:3000**

🎉 **You're ready to play!**

---

## Detailed Setup

### Backend Configuration

The `.env` file in `/backend` controls all backend settings:

```env
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Ollama (LLM)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# Chess Engines
STOCKFISH_PATH=/usr/local/bin/stockfish  # Auto-detected if empty
MAIA_PATH=  # Optional - leave empty if not using Maia

# Database
DATABASE_URL=sqlite+aiosqlite:///./chess_learning.db

# Training
DEFAULT_PLAYER_ELO=1200
SRS_REVIEW_INTERVALS=1,3,7,14,30
```

**Key Settings:**

- **OLLAMA_MODEL**: Change to `mistral`, `phi3`, or `qwen2` for different models
- **STOCKFISH_PATH**: Set manually if auto-detection fails
- **DEFAULT_PLAYER_ELO**: Starting ELO for new players (400-3000)

### Frontend Configuration

The `.env.local` file in `/frontend`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

Change these if running backend on different host/port.

### Testing Your Setup

#### 1. Check Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:
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

#### 2. Test Ollama Integration

```bash
curl -X POST http://localhost:8000/api/llm/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain why 1.e4 is a popular opening move",
    "persona": "friendly_teacher"
  }'
```

#### 3. Test Chess Engine

```bash
curl "http://localhost:8000/api/analysis/best-move/rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR%20w%20KQkq%20-%200%201?elo=1500"
```

### Running in Production

#### Option 1: Docker Compose (Recommended)

**Coming Soon** - Docker configuration will be added in future releases.

#### Option 2: systemd (Linux)

**Backend Service:**

Create `/etc/systemd/system/chess-backend.service`:
```ini
[Unit]
Description=AI Chess Learning Platform Backend
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/AIChessBot/backend
Environment="PATH=/path/to/AIChessBot/backend/venv/bin"
ExecStart=/path/to/AIChessBot/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable chess-backend
sudo systemctl start chess-backend
sudo systemctl status chess-backend
```

**Frontend (Static Export):**

```bash
cd frontend
npm run build
npm run export  # Future feature - static HTML export
```

Serve with nginx or any static file server.

#### Option 3: PM2 (Node.js Process Manager)

```bash
# Install PM2
npm install -g pm2

# Start backend
cd backend
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name chess-backend

# Start frontend
cd frontend
pm2 start "npm run start" --name chess-frontend

# Save configuration
pm2 save
pm2 startup
```

### Reverse Proxy with Nginx

Example nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
```

## Troubleshooting

### Backend Won't Start

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Stockfish Not Found

**Problem**: `⚠️  Stockfish not available`

**Solution**:
```bash
# Find Stockfish path
which stockfish  # macOS/Linux
where stockfish  # Windows

# Add to .env
echo "STOCKFISH_PATH=/path/to/stockfish" >> .env
```

### Ollama Connection Failed

**Problem**: `⚠️  Could not connect to Ollama`

**Solution**:
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama
ollama serve

# In another terminal, verify model is downloaded
ollama list

# Pull model if missing
ollama pull llama3
```

### Frontend Build Errors

**Problem**: `Cannot find module 'next'`

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Port Already in Use

**Problem**: `Error: Address already in use`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or change port in .env
PORT=8001
```

### Database Errors

**Problem**: `Could not open database file`

**Solution**:
```bash
cd backend
# Database file is auto-created, ensure write permissions
chmod 755 .
touch chess_learning.db
chmod 644 chess_learning.db
```

## Performance Optimization

### For Low-Resource Systems

If you have limited RAM/CPU:

1. **Use lighter LLM model:**
   ```env
   OLLAMA_MODEL=phi3  # Instead of llama3
   ```

2. **Reduce analysis depth:**
   - Default depth: 20
   - Lower to 15 or 12 for faster responses

3. **Disable Maia:**
   - Leave `MAIA_PATH` empty (uses only Stockfish)

### For High-Performance Systems

If you have powerful hardware:

1. **Use larger models:**
   ```bash
   ollama pull llama3:70b  # Requires 32GB+ RAM
   ```

2. **Increase analysis depth:**
   - Set depth to 25-30 for tournament-level analysis

3. **Enable GPU acceleration:**
   - Ollama automatically uses CUDA/Metal if available
   - Verify with `nvidia-smi` (NVIDIA) or Activity Monitor (Mac)

## Security Considerations

### For Local Use (Default)
- No authentication needed
- Only accessible from localhost
- All data stored locally

### For Remote Access (Advanced)
If exposing to network:

1. **Add authentication** (future feature)
2. **Use HTTPS** (Let's Encrypt + nginx)
3. **Firewall rules**:
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

4. **Limit origins in backend .env**:
   ```env
   CORS_ORIGINS=https://your-domain.com
   ```

## Backup and Data

### Backup User Data

```bash
# Backup database
cp backend/chess_learning.db backup/chess_learning_$(date +%Y%m%d).db

# Backup configuration
tar -czf backup/config_$(date +%Y%m%d).tar.gz backend/.env frontend/.env.local
```

### Export Games

```bash
# Export all games to PGN (future feature)
curl http://localhost:8000/api/user/{user_id}/export?format=pgn > my_games.pgn
```

## Next Steps

After successful setup:

1. ✅ Read the [Architecture Documentation](./ARCHITECTURE.md)
2. ✅ Explore the [API Documentation](./API.md)
3. ✅ Review [Training Modules](./TRAINING.md)
4. ✅ Try different AI personas
5. ✅ Import your Lichess games
6. ✅ Start your learning journey!

## Getting Help

- **Documentation**: Check the `/docs` folder
- **API Docs**: http://localhost:8000/docs
- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions in GitHub Discussions

---

**Happy Learning! ♟️🤖**
