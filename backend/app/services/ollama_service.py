"""
Ollama LLM Service - Handles all AI chat and explanation features
"""
import httpx
import logging
from typing import Optional, Dict, Any, List, AsyncGenerator
import json

from app.config import settings

logger = logging.getLogger(__name__)


class PersonaConfig:
    """Configuration for different AI personas."""
    
    PERSONAS = {
        "grandmaster": {
            "name": "The Grandmaster",
            "system_prompt": """You are a world-class chess grandmaster with decades of experience. 
            You are analytical, precise, and sometimes stern. You expect excellence and point out mistakes directly.
            You use technical chess terminology and provide deep strategic insights. Keep responses concise but authoritative.""",
            "temperature": 0.5,
            "style": "analytical"
        },
        "friendly_teacher": {
            "name": "Friendly Teacher",
            "system_prompt": """You are an encouraging and patient chess teacher who loves helping students improve.
            You explain concepts clearly, use analogies, and celebrate small victories. You're supportive but honest about mistakes.
            Your goal is to make chess fun and accessible while building genuine understanding. Be warm and conversational.""",
            "temperature": 0.7,
            "style": "encouraging"
        },
        "aggressive_rival": {
            "name": "Aggressive Rival",
            "system_prompt": """You are a competitive chess rival who loves the battle. You're confident, sometimes cocky,
            and enjoy trash talk (in a playful way). You respect good moves but won't hesitate to mock mistakes.
            You make the game exciting and intense. Be bold and spirited, but never mean-spirited.""",
            "temperature": 0.8,
            "style": "competitive"
        }
    }
    
    @classmethod
    def get_persona(cls, persona_name: str) -> Dict[str, Any]:
        """Get persona configuration by name."""
        return cls.PERSONAS.get(persona_name, cls.PERSONAS["friendly_teacher"])


class OllamaService:
    """Service for interacting with Ollama LLM for chess coaching and explanations."""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self._client: Optional[httpx.AsyncClient] = None
        self._available = False
    
    async def initialize(self):
        """Initialize Ollama service and check availability."""
        self._client = httpx.AsyncClient(timeout=30.0)
        
        try:
            # Check if Ollama is running
            response = await self._client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]
                
                if self.model in model_names or f"{self.model}:latest" in model_names:
                    self._available = True
                    logger.info(f"✓ Ollama connected - Model: {self.model}")
                else:
                    logger.warning(f"⚠️  Model '{self.model}' not found. Available: {model_names}")
                    logger.info(f"Run: ollama pull {self.model}")
            else:
                logger.warning("⚠️  Ollama service not responding")
        except Exception as e:
            logger.warning(f"⚠️  Could not connect to Ollama: {e}")
            logger.info("Install Ollama: https://ollama.ai")
    
    def is_connected(self) -> bool:
        """Check if Ollama is available."""
        return self._available
    
    async def chat(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        persona: str = "friendly_teacher",
        stream: bool = False
    ) -> str | AsyncGenerator[str, None]:
        """
        Send a chat message to the LLM.
        
        Args:
            message: User message
            context: Chess game context (position, moves, etc.)
            persona: AI persona to use
            stream: Whether to stream the response
        
        Returns:
            AI response or async generator for streaming
        """
        if not self._available:
            return "Ollama LLM is not available. Please install and start Ollama."
        
        persona_config = PersonaConfig.get_persona(persona)
        
        # Build context-aware system prompt
        system_prompt = self._build_system_prompt(persona_config, context)
        
        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        if stream:
            return self._stream_chat(messages, persona_config["temperature"])
        else:
            return await self._chat(messages, persona_config["temperature"])
    
    async def explain_move(
        self,
        move: str,
        position_fen: str,
        evaluation: Optional[Dict[str, Any]] = None,
        persona: str = "friendly_teacher"
    ) -> str:
        """
        Generate a natural language explanation for a chess move.
        
        Args:
            move: Move in UCI format (e.g., "e2e4")
            position_fen: Board position in FEN notation
            evaluation: Engine evaluation of the move
            persona: AI persona
        
        Returns:
            Natural language explanation
        """
        context = {
            "move": move,
            "position": position_fen,
            "evaluation": evaluation
        }
        
        prompt = f"""Explain this chess move: {move}
        
Position (FEN): {position_fen}
Move Quality: {evaluation.get('classification', 'unknown') if evaluation else 'unknown'}

Provide a clear, concise explanation of:
1. What the move accomplishes tactically/strategically
2. Why it's a {evaluation.get('classification', 'reasonable') if evaluation else 'reasonable'} move
3. Key ideas or threats created

Keep it to 2-3 sentences."""
        
        return await self.chat(prompt, context=context, persona=persona)
    
    async def generate_opening_guide(
        self,
        opening_name: str,
        moves: List[str],
        persona: str = "friendly_teacher"
    ) -> str:
        """
        Generate a natural language guide for a chess opening.
        
        Args:
            opening_name: Name of the opening
            moves: List of moves in the opening
            persona: AI persona
        
        Returns:
            Opening guide text
        """
        moves_str = " ".join(moves)
        
        prompt = f"""Create a beginner-friendly guide for the {opening_name} chess opening.

Opening moves: {moves_str}

Include:
1. Core ideas and principles (2-3 key points)
2. What each side is trying to accomplish
3. Common patterns or tactics to watch for
4. One practical tip for learning this opening

Keep it concise and encouraging - about 4-5 sentences total."""
        
        return await self.chat(prompt, persona=persona)
    
    async def analyze_game_summary(
        self,
        game_pgn: str,
        mistakes: List[Dict[str, Any]],
        player_color: str,
        persona: str = "friendly_teacher"
    ) -> str:
        """
        Generate a post-game analysis summary.
        
        Args:
            game_pgn: Full game in PGN format
            mistakes: List of mistakes/blunders made
            player_color: Player's color (white/black)
            persona: AI persona
        
        Returns:
            Game analysis summary
        """
        mistake_summary = "\n".join([
            f"Move {m['move_number']}: {m['move']} - {m['classification']}"
            for m in mistakes[:5]  # Top 5 mistakes
        ])
        
        prompt = f"""Analyze this chess game for a player who played as {player_color}.

Key mistakes made:
{mistake_summary}

Provide:
1. Brief overview of the game (what went well, what didn't)
2. Top 2-3 areas to improve
3. One specific action item for next game
4. Encouraging closing message

Keep it conversational and constructive - about 5-6 sentences."""
        
        context = {"game_pgn": game_pgn, "player_color": player_color}
        return await self.chat(prompt, context=context, persona=persona)
    
    def _build_system_prompt(
        self,
        persona_config: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build context-aware system prompt."""
        base_prompt = persona_config["system_prompt"]
        
        if context:
            context_info = "\n\nCurrent game context:\n"
            if "position" in context:
                context_info += f"Position: {context['position']}\n"
            if "move" in context:
                context_info += f"Last move: {context['move']}\n"
            if "evaluation" in context and context["evaluation"]:
                eval_data = context["evaluation"]
                context_info += f"Move quality: {eval_data.get('classification', 'unknown')}\n"
            
            return base_prompt + context_info
        
        return base_prompt
    
    async def _chat(self, messages: List[Dict[str, str]], temperature: float) -> str:
        """Send chat request to Ollama (non-streaming)."""
        try:
            response = await self._client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("content", "")
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return "Sorry, I couldn't generate a response."
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return "An error occurred while processing your message."
    
    async def _stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float
    ) -> AsyncGenerator[str, None]:
        """Stream chat response from Ollama."""
        try:
            async with self._client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "stream": True
                }
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "message" in data:
                                content = data["message"].get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield "An error occurred while streaming the response."
