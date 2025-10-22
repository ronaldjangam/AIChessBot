'use client'

import { useEffect, useState } from 'react'
import { Chessboard } from 'react-chessboard'
import { Chess } from 'chess.js'
import { useGameStore } from '@/store/gameStore'
import { apiClient } from '@/lib/api'

export default function ChessBoard() {
  const { game, setGame, gameId, moves, addMove } = useGameStore()
  const [boardOrientation, setBoardOrientation] = useState<'white' | 'black'>('white')
  const [moveFrom, setMoveFrom] = useState('')
  const [rightClickedSquares, setRightClickedSquares] = useState<Record<string, any>>({})
  const [optionSquares, setOptionSquares] = useState<Record<string, any>>({})

  useEffect(() => {
    // Initialize chess game
    const chess = new Chess()
    setGame(chess)
  }, [setGame])

  function getMoveOptions(square: string) {
    if (!game) return

    const moves = game.moves({
      square,
      verbose: true,
    })

    if (moves.length === 0) {
      setOptionSquares({})
      return false
    }

    const newSquares: Record<string, any> = {}
    moves.forEach((move) => {
      newSquares[move.to] = {
        background:
          game.get(move.to) && game.get(move.to).color !== game.get(square).color
            ? 'radial-gradient(circle, rgba(0,0,0,.1) 85%, transparent 85%)'
            : 'radial-gradient(circle, rgba(0,0,0,.1) 25%, transparent 25%)',
        borderRadius: '50%',
      }
    })
    newSquares[square] = {
      background: 'rgba(255, 255, 0, 0.4)',
    }
    setOptionSquares(newSquares)
    return true
  }

  function onSquareClick(square: string) {
    if (!game) return

    // If no piece selected, try to select this square
    if (!moveFrom) {
      const hasMoveOptions = getMoveOptions(square)
      if (hasMoveOptions) setMoveFrom(square)
      return
    }

    // Attempt to make move
    try {
      const move = game.move({
        from: moveFrom,
        to: square,
        promotion: 'q', // Always promote to queen for simplicity
      })

      if (move) {
        // Move successful
        setGame(new Chess(game.fen()))
        addMove(move.san)
        
        // Send move to backend and get AI response
        handleMove(move.san)
        
        setMoveFrom('')
        setOptionSquares({})
        return
      }
    } catch (error) {
      // Invalid move, reset
    }

    // Invalid move or same square clicked, clear selection
    setMoveFrom('')
    setOptionSquares({})
    getMoveOptions(square)
    setMoveFrom(square)
  }

  async function handleMove(move: string) {
    if (!gameId || !game) return

    try {
      const response = await apiClient.post('/game/move', {
        game_id: gameId,
        move: move,
        fen: game.fen()
      })

      if (response.data.ai_move) {
        // Make AI move
        setTimeout(() => {
          if (game) {
            game.move(response.data.ai_move)
            setGame(new Chess(game.fen()))
            addMove(response.data.ai_move)
          }
        }, 500)
      }
    } catch (error) {
      console.error('Failed to make move:', error)
    }
  }

  function onSquareRightClick(square: string) {
    const color = 'rgba(255, 0, 0, 0.5)'
    setRightClickedSquares({
      ...rightClickedSquares,
      [square]: rightClickedSquares[square]
        ? undefined
        : { backgroundColor: color },
    })
  }

  if (!game) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
      </div>
    )
  }

  return (
    <div className="chess-board">
      <Chessboard
        id="PlayVsAI"
        position={game.fen()}
        onSquareClick={onSquareClick}
        onSquareRightClick={onSquareRightClick}
        boardOrientation={boardOrientation}
        customSquareStyles={{
          ...optionSquares,
          ...rightClickedSquares,
        }}
        customBoardStyle={{
          borderRadius: '8px',
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.5)',
        }}
        customDarkSquareStyle={{ backgroundColor: '#b58863' }}
        customLightSquareStyle={{ backgroundColor: '#f0d9b5' }}
      />

      {/* Move History */}
      <div className="mt-4 p-4 bg-slate-700 rounded-lg">
        <h3 className="text-white font-semibold mb-2">Move History</h3>
        <div className="flex flex-wrap gap-2">
          {moves.map((move, index) => (
            <span
              key={index}
              className="px-2 py-1 bg-slate-600 text-white rounded text-sm"
            >
              {Math.floor(index / 2) + 1}. {move}
            </span>
          ))}
        </div>
      </div>

      {/* Flip Board Button */}
      <button
        onClick={() => setBoardOrientation(boardOrientation === 'white' ? 'black' : 'white')}
        className="mt-4 w-full bg-slate-600 hover:bg-slate-500 text-white py-2 px-4 rounded-lg transition"
      >
        Flip Board
      </button>
    </div>
  )
}
