'use client'

import { useState, useEffect } from 'react'
import { useGameStore } from '@/store/gameStore'
import { apiClient } from '@/lib/api'

interface AnalysisPanelProps {
  onClose: () => void
}

interface AnalysisResult {
  move: string
  score: {
    type: string
    value: number
    display: string
  }
  depth: number
  pv: string[]
}

export default function AnalysisPanel({ onClose }: AnalysisPanelProps) {
  const [analysis, setAnalysis] = useState<AnalysisResult[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [depth, setDepth] = useState(20)
  const { game } = useGameStore()

  async function analyzePosition() {
    if (!game) return

    setIsAnalyzing(true)
    try {
      const response = await apiClient.post('/analysis/position', {
        fen: game.fen(),
        depth: depth,
        multipv: 3,
        use_maia: false,
      })
      setAnalysis(response.data)
    } catch (error) {
      console.error('Analysis error:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  function getScoreColor(score: number): string {
    if (score > 200) return 'text-green-400'
    if (score > 50) return 'text-green-300'
    if (score > -50) return 'text-yellow-300'
    if (score > -200) return 'text-orange-400'
    return 'text-red-400'
  }

  return (
    <div className="bg-slate-800 rounded-lg shadow-2xl overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-cyan-600 p-4 flex justify-between items-center">
        <h2 className="text-white font-bold text-lg">📊 Position Analysis</h2>
        <button
          onClick={onClose}
          className="text-white hover:text-slate-200 transition"
        >
          ✕
        </button>
      </div>

      {/* Controls */}
      <div className="p-4 bg-slate-700 border-b border-slate-600">
        <div className="flex items-center gap-4 mb-3">
          <label className="text-white text-sm font-semibold">
            Depth: {depth}
          </label>
          <input
            type="range"
            min="10"
            max="30"
            value={depth}
            onChange={(e) => setDepth(parseInt(e.target.value))}
            className="flex-1"
          />
        </div>
        <button
          onClick={analyzePosition}
          disabled={isAnalyzing || !game}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white py-2 px-4 rounded-lg transition font-semibold"
        >
          {isAnalyzing ? 'Analyzing...' : 'Analyze Position'}
        </button>
      </div>

      {/* Analysis Results */}
      <div className="p-4 space-y-3 max-h-96 overflow-y-auto">
        {isAnalyzing ? (
          <div className="flex flex-col items-center justify-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4"></div>
            <p className="text-slate-300">Analyzing with Stockfish...</p>
          </div>
        ) : analysis.length > 0 ? (
          analysis.map((result, index) => (
            <div
              key={index}
              className="bg-slate-700 rounded-lg p-4 border-l-4 border-blue-500"
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <span className="text-slate-400 text-xs">#{index + 1}</span>
                  <h3 className="text-white font-bold text-lg">{result.move}</h3>
                </div>
                <div className="text-right">
                  <div className={`font-bold text-xl ${getScoreColor(result.score.value)}`}>
                    {result.score.display}
                  </div>
                  <div className="text-slate-400 text-xs">
                    Depth {result.depth}
                  </div>
                </div>
              </div>
              <div className="text-slate-300 text-sm">
                <span className="text-slate-500">Line:</span>{' '}
                {result.pv.join(' → ')}
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-8 text-slate-400">
            <p>Click "Analyze Position" to see the best moves</p>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="p-4 bg-slate-900 border-t border-slate-700">
        <div className="text-xs text-slate-400 space-y-1">
          <p><span className="text-green-400">●</span> Winning advantage</p>
          <p><span className="text-yellow-300">●</span> Equal position</p>
          <p><span className="text-red-400">●</span> Losing position</p>
        </div>
      </div>
    </div>
  )
}
