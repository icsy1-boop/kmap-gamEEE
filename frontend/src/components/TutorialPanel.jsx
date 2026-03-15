import React, { useEffect } from 'react'
import { apiUrl } from '../config/api'

const COLORS = [
  "59,130,246",
  "239,68,68",
  "245,158,11",
  "45,212,191",
  "168,85,247",
  "16,185,129",
  "249,115,22",
  "14,165,233",
  "236,72,153",
  "251,191,36",
  "34,197,94",
  "132,204,22",
]

const TutorialPanel = ({ gameState, setGameState }) => {
  const solve = async (nextState) => {
    try {
      setGameState((prev) => ({
        ...prev,
        ...nextState,
        tutorial_busy: true,
      }))

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
        tutorial_expression_terms: data.terms || [],
        tutorial_busy: false,
      })
    } catch (error) {
      setGameState({
        ...nextState,
        q_groupings: [],
        tutorial_expression: '',
        tutorial_expression_terms: [],
        tutorial_busy: false,
      })
    } finally {
    }
  }

  const deriveTermsFromCells = (cells, form, numVar) => {
    const twos = ["0", "1"]
    const fours = ["00", "01", "11", "10"]
    const outerRows = numVar >= 4 ? fours : twos
    const outerCols = numVar === 2 ? twos : fours
    const colCount = outerCols.length

    const terms = []
    const dontCares = []

    for (let i = 0; i < cells.length; i += 1) {
      let mapped = 0
      if (numVar <= 4) {
        const row = Math.floor(i / colCount)
        const col = i % colCount
        mapped = parseInt(`${outerRows[row]}${outerCols[col]}`, 2)
      } else {
        const layer = Math.floor(i / 16)
        const local = i % 16
        const row = Math.floor(local / 4)
        const col = local % 4
        const within = parseInt(`${outerRows[row]}${outerCols[col]}`, 2)
        mapped = layer * 16 + within
      }

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
      tutorial_expression_terms: [],
      tutorial_busy: false,
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

          <div className="flex flex-col items-end gap-1">
            <div className="text-[10px] uppercase tracking-wide text-slate-400">Toggle SOP/POS</div>
            <button
            type="button"
            onClick={toggleForm}
            className={`relative h-8 w-16 rounded-full border transition ${
              gameState.q_form === 'min'
                ? 'border-cyan-400 bg-cyan-900/30'
                : 'border-rose-400 bg-rose-900/30'
            }`}
            aria-pressed={gameState.q_form === 'min'}
          >
            <span
              className={`absolute top-0.5 h-7 w-7 rounded-full bg-white shadow transition ${
                gameState.q_form === 'min' ? 'left-0.5' : 'left-8'
              }`}
            />
            <span className="sr-only">Toggle SOP/POS</span>
            </button>
          </div>
        </div>

        <div className="mb-4 flex items-center gap-2 flex-wrap">
          {[2, 3, 4, 5, 6].map((numVar) => (
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
          <div className="mt-2 text-sm sm:text-base break-words">
            {gameState.tutorial_expression_terms && gameState.tutorial_expression_terms.length > 0 ? (
              <div className="flex flex-wrap items-center gap-2">
                {gameState.tutorial_expression_terms.map((term, idx) => (
                  <React.Fragment key={`${term}-${idx}`}>
                    {idx > 0 && gameState.q_form === 'min' && (
                      <span className="text-slate-400 font-semibold">+</span>
                    )}
                    <span
                      className="px-2 py-1 rounded-md border text-cyan-100"
                      style={{
                        borderColor: `rgb(${COLORS[idx % COLORS.length]})`,
                        backgroundColor: `rgba(${COLORS[idx % COLORS.length]}, 0.15)`,
                      }}
                    >
                      {term}
                    </span>
                  </React.Fragment>
                ))}
              </div>
            ) : (
              <span className="text-cyan-200">{gameState.tutorial_expression || '-'} </span>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="text-xs text-slate-400">Click cells to toggle 0 - 1 - X</div>
          <button
            type="button"
            onClick={resetMap}
            className="px-3 py-1.5 rounded-lg border border-slate-600 text-slate-200 hover:bg-slate-800/60 transition"
          >
            Reset
          </button>
        </div>

        <div className="mt-5 rounded-xl border border-slate-700/60 bg-slate-900/50 p-4">
          <div className="text-xs uppercase tracking-wide text-slate-400">Di ka nakinig sa lecture noh?</div>
          <div className="mt-2 text-sm text-slate-300 leading-relaxed">
            Make groups as large as possible to simplify the expression. Remember, groups must be rectangular and contain 1s (or 0s for POS) and can include Xs if needed. Try to cover all the 1s (or 0s) with as few groups as possible! The edge columns and rows are logically adjacent with each other, so don't forget to wrap around when making groups. To determine the expression, look at the group and see which variable did not change within the group. The rules are essentially flipped when switching from SOP to POS! Try it out!
          </div>
        </div>
      </div>
    </div>
  )
}

export default TutorialPanel
