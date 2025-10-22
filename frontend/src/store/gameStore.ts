import { create } from 'zustand'
import { Chess } from 'chess.js'

interface GameStore {
  game: Chess | null
  gameId: string | null
  moves: string[]
  persona: string
  setGame: (game: Chess) => void
  setGameId: (id: string | null) => void
  addMove: (move: string) => void
  resetMoves: () => void
  setPersona: (persona: string) => void
}

export const useGameStore = create<GameStore>((set) => ({
  game: null,
  gameId: null,
  moves: [],
  persona: 'friendly_teacher',
  setGame: (game) => set({ game }),
  setGameId: (id) => set({ gameId: id }),
  addMove: (move) => set((state) => ({ moves: [...state.moves, move] })),
  resetMoves: () => set({ moves: [] }),
  setPersona: (persona) => set({ persona }),
}))
