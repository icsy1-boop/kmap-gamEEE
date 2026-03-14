import React, { useEffect } from 'react'
import { apiUrl } from '../config/api'

const TutorialPanel = ({ gameState, setGameState }) => {
  const solve = async (nextState) => {
    try {
      const response = await fetch(apiUrl('/tutorial-solve'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          num_var: nextState.q_num_var,
          form_terms: nextState.q_form,
          terms: nextState.q_terms,
          dont_cares: nextState.q_dont_cares,
        }),
      })
      const data = await response.json()
      if (!response.ok) {
        throw new Error(data.error || 'Failed to solve tutorial')
      }
      setGameState({
        ...nextState,
        q_groupings: data.groupings || [],
        tutorial_expression: data.expression || '',
      })
    } catch (error) {
      setGameState({
        ...nextState,
        q_groupings: [],
        tutorial_expression: '',
      })
    } finally {
    }
  }

  const deriveTermsFromCells = (cells, form, numVar) => {
    const twos = ["0", "1"]
    const fours = ["00", "01", "11", "10"]
    const outerRows = numVar === 4 ? fours : twos
    const outerCols = numVar === 2 ? twos : fours
    const rowCount = outerRows.length
    const colCount = outerCols.length
    const terms = []
    const dontCares = []
    for (let i = 0; i < cells.length; i += 1) {
      const row = Math.floor(i / colCount)
      const col = i % colCount
      const mapped = parseInt(`${outerRows[row]}${outerCols[col]}`, 2)
      if (cells[i] === 'x') {
        dontCares.push(mapped)
      } else if (form === 'min' && cells[i] === 1) {
        terms.push(mapped)
      } else if (form === 'max' && cells[i] === 0) {
        terms.push(mapped)
      }
    }
    return { terms, dontCares }
  }

  useEffect(() => {
    const { terms, dontCares } = deriveTermsFromCells(
      gameState.tutorial_cells,
      gameState.q_form,
      gameState.q_num_var,
    )
    solve({
      ...gameState,
      q_terms: terms,
      q_dont_cares: dontCares,
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [gameState.tutorial_cells, gameState.q_form, gameState.q_num_var])

  const toggleForm = () => {
    const nextForm = gameState.q_form === 'min' ? 'max' : 'min'
    const { terms, dontCares } = deriveTermsFromCells(
      gameState.tutorial_cells,
      nextForm,
      gameState.q_num_var,
    )
    const nextState = {
      ...gameState,
      q_form: nextForm,
      q_terms: terms,
      q_dont_cares: dontCares,
    }
    solve(nextState)
  }

  const resetMap = () => {
    const nextCells = Array(2 ** gameState.q_num_var).fill(0)
    const nextState = {
      ...gameState,
      tutorial_cells: nextCells,
      q_form: 'min',
      q_terms: [],
      q_dont_cares: [],
    }
    solve(nextState)
  }

  const setVariables = (numVar) => {
    const nextCells = Array(2 ** numVar).fill(0)
    const nextState = {
      ...gameState,
      q_num_var: numVar,
      q_form: 'min',
      tutorial_cells: nextCells,
      q_terms: [],
      q_dont_cares: [],
      q_groupings: [],
      tutorial_expression: '',
    }
    solve(nextState)
  }

  return (
    <div className="w-full max-w-md card-fade-in mb-10">
      <div className="w-full p-5 sm:p-8 md:p-10 from-slate-800 via-slate-900 to-slate-800 backdrop-blur-lg rounded-2xl shadow-2xl border-2 border-cyan-500/95">
        <div className="mb-4 flex items-center justify-between gap-3">
          <div>
            <div className="text-sm text-slate-400">Tutorial Mode</div>
            <div className="text-lg font-bold text-cyan-300">{gameState.q_num_var}-Variable K-Map</div>
          </div>
          <button
            type="button"
            onClick={toggleForm}
            className="px-4 py-2 rounded-lg border border-cyan-500/40 text-cyan-200 hover:bg-cyan-900/20 transition"
          >
            {gameState.q_form === 'min' ? 'SOP' : 'POS'}
          </button>
        </div>

        <div className="mb-4 flex items-center gap-2">
          {[2, 3, 4].map((numVar) => (
            <button
              key={numVar}
              type="button"
              onClick={() => setVariables(numVar)}
              className={`px-3 py-1.5 rounded-lg border text-sm transition ${
                gameState.q_num_var === numVar
                  ? 'border-cyan-400 text-cyan-200 bg-cyan-900/30'
                  : 'border-slate-600 text-slate-300 hover:bg-slate-800/60'
              }`}
            >
              {numVar} Vars
            </button>
          ))}
        </div>

        <div className="mb-4 rounded-xl border border-slate-700/60 bg-slate-900/50 p-4">
          <div className="text-xs uppercase tracking-wide text-slate-400">Simplified Expression</div>
          <div className="mt-2 text-cyan-200 text-sm sm:text-base break-words">
            {gameState.tutorial_expression || '—'}
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="text-xs text-slate-400">Click cells to toggle 0 ? 1 ? X</div>
          <button
            type="button"
            onClick={resetMap}
            className="px-3 py-1.5 rounded-lg border border-slate-600 text-slate-200 hover:bg-slate-800/60 transition"
          >
            Reset
          </button>
        </div>
      </div>
    </div>
  )
}

export default TutorialPanel
