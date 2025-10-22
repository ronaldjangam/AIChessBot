'use client'

import { useState } from 'react'
import { useGameStore } from '@/store/gameStore'
import { apiClient } from '@/lib/api'
import { Chess } from 'chess.js'

export default function GameControls() {
  const [isStarting, setIsStarting] = useState(false)
  const [playerColor, setPlayerColor] = useState<'white' | 'black'>('white')
  const [playerElo, setPlayerElo] = useState(1200)
  const { gameId, setGameId, setGame, resetMoves, persona } = useGameStore()

  async function startNewGame() {
    setIsStarting(true)
    try {
      const response = await apiClient.post('/game/start', {
        player_color: playerColor,
        player_elo: playerElo,
        ai_persona: persona,
        use_maia: false,
      })

      setGameId(response.data.game_id)
      const chess = new Chess(response.data.fen)
      setGame(chess)
      resetMoves()
    } catch (error) {
      console.error('Failed to start game:', error)
      alert('Failed to start game. Make sure the backend is running!')
    } finally {
      setIsStarting(false)
    }
  }

  function resetGame() {
    const chess = new Chess()
    setGame(chess)
    resetMoves()
    setGameId(null)
  }

  return (
    <div className="space-y-4">
      {/* Game Status */}
      <div className="bg-slate-700 rounded-lg p-4">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-white font-semibold">Game Status</h3>
            <p className="text-slate-300 text-sm">
              {gameId ? `Game ID: ${gameId.substring(0, 8)}...` : 'No active game'}
            </p>
          </div>
          <div className={`px-3 py-1 rounded-full text-sm font-semibold ${
            gameId ? 'bg-green-600 text-white' : 'bg-slate-600 text-slate-300'
          }`}>
            {gameId ? '● Active' : '○ Inactive'}
          </div>
        </div>
      </div>

      {/* Game Settings */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-white text-sm font-semibold block mb-2">
            Play As
          </label>
          <select
            value={playerColor}
            onChange={(e) => setPlayerColor(e.target.value as 'white' | 'black')}
            className="w-full bg-slate-700 text-white rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="white">⚪ White</option>
            <option value="black">⚫ Black</option>
          </select>
        </div>

        <div>
          <label className="text-white text-sm font-semibold block mb-2">
            Your ELO: {playerElo}
          </label>
          <input
            type="range"
            min="400"
            max="3000"
            step="100"
            value={playerElo}
            onChange={(e) => setPlayerElo(parseInt(e.target.value))}
            className="w-full"
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-3">
        <button
          onClick={startNewGame}
          disabled={isStarting}
          className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:from-slate-600 disabled:to-slate-600 text-white py-3 px-4 rounded-lg transition font-semibold shadow-lg"
        >
          {isStarting ? 'Starting...' : '🎮 New Game'}
        </button>

        <button
          onClick={resetGame}
          className="bg-slate-600 hover:bg-slate-500 text-white py-3 px-4 rounded-lg transition font-semibold"
        >
          🔄 Reset
        </button>
      </div>

      {/* Quick Actions */}
      <div className="flex gap-2">
        <button
          disabled={!gameId}
          className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white py-2 px-3 rounded-lg transition text-sm"
        >
          💡 Hint
        </button>
        <button
          disabled={!gameId}
          className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-600 text-white py-2 px-3 rounded-lg transition text-sm"
        >
          ↩️ Undo
        </button>
        <button
          disabled={!gameId}
          className="flex-1 bg-orange-600 hover:bg-orange-700 disabled:bg-slate-600 text-white py-2 px-3 rounded-lg transition text-sm"
        >
          🎯 Analyze
        </button>
      </div>
    </div>
  )
}
