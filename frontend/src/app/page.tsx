'use client'

import { useState } from 'react'
import ChessBoard from '@/components/ChessBoard'
import ChatPanel from '@/components/ChatPanel'
import AnalysisPanel from '@/components/AnalysisPanel'
import GameControls from '@/components/GameControls'
import { useGameStore } from '@/store/gameStore'

export default function Home() {
  const [showChat, setShowChat] = useState(true)
  const [showAnalysis, setShowAnalysis] = useState(true)
  const { gameId } = useGameStore()

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <header className="mb-6">
          <h1 className="text-4xl font-bold text-white mb-2">
            🤖♟️ AI Chess Learning Platform
          </h1>
          <p className="text-slate-300">
            Learn chess with personalized AI coaching powered by Ollama
          </p>
        </header>

        {/* Main Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Chess Board */}
          <div className="lg:col-span-2">
            <div className="bg-slate-800 rounded-lg shadow-2xl p-6">
              <GameControls />
              <div className="mt-6">
                <ChessBoard />
              </div>
            </div>
          </div>

          {/* Right Column - Panels */}
          <div className="space-y-6">
            {/* Chat Panel */}
            <div className={`transition-all duration-300 ${showChat ? 'block' : 'hidden'}`}>
              <ChatPanel onClose={() => setShowChat(false)} />
            </div>

            {/* Analysis Panel */}
            <div className={`transition-all duration-300 ${showAnalysis ? 'block' : 'hidden'}`}>
              <AnalysisPanel onClose={() => setShowAnalysis(false)} />
            </div>

            {/* Toggle Buttons */}
            <div className="flex gap-2">
              {!showChat && (
                <button
                  onClick={() => setShowChat(true)}
                  className="flex-1 bg-purple-600 hover:bg-purple-700 text-white py-2 px-4 rounded-lg transition"
                >
                  Show Chat
                </button>
              )}
              {!showAnalysis && (
                <button
                  onClick={() => setShowAnalysis(true)}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition"
                >
                  Show Analysis
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-8 text-center text-slate-400 text-sm">
          <p>
            Powered by{' '}
            <span className="text-purple-400 font-semibold">Ollama</span>,{' '}
            <span className="text-blue-400 font-semibold">Stockfish</span>, and{' '}
            <span className="text-green-400 font-semibold">Open Source</span>
          </p>
        </footer>
      </div>
    </main>
  )
}
