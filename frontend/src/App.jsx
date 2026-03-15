import { useState, useEffect, useRef } from 'react'
import './App.css'
import Register from './components/register.jsx'
import Kmap from './components/Kmap.jsx';
import AnswerCard from './components/AnswerCard.jsx';
import TimeAttackCard from './components/TimeAttackCard.jsx';
import About from './components/About.jsx';
import TutorialPanel from './components/TutorialPanel.jsx';

function App() {
  const [globalName, setGlobalName] = useState('');
  const [gameState, setGameState] = useState(null);
  const [globalState, setGlobalState] = useState('hide');
  const [mapKey, setMapKey] = useState(0);
  const [slideDir, setSlideDir] = useState('in');
  const [isLastAnswerCorrect, setIsLastAnswerCorrect] = useState(true);
  const [showAbout, setShowAbout] = useState(false);
  const [isMapLoading, setIsMapLoading] = useState(false);
  const prevGameState = useRef(null);

  useEffect(() => {
    if (!gameState) return;
    if (!prevGameState.current) {
      prevGameState.current = gameState;
      setSlideDir('in');
      return;
    }
    if (
      prevGameState.current.q_terms !== gameState.q_terms ||
      prevGameState.current.q_num_var !== gameState.q_num_var
    ) {
      setSlideDir('out');
      const t1 = setTimeout(() => {
        setMapKey(k => k + 1);
        setSlideDir('in');
        prevGameState.current = gameState;
      }, 350);
      return () => clearTimeout(t1);
    }
    prevGameState.current = gameState;
  }, [gameState]);

  return (
    <>
      <style>{`
        @keyframes slideInLeft {
          from { opacity: 0; transform: translateX(-40px) scale(0.97); }
          to   { opacity: 1; transform: translateX(0) scale(1); }
        }
        @keyframes slideOutLeft {
          from { opacity: 1; transform: translateX(0) scale(1); }
          to   { opacity: 0; transform: translateX(-40px) scale(0.97); }
        }
        @keyframes fadeInCard {
          from { opacity: 0; transform: translateY(16px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        .kmap-slide-in  { animation: slideInLeft  0.4s cubic-bezier(0.22,1,0.36,1) both; }
        .kmap-slide-out { animation: slideOutLeft 0.35s cubic-bezier(0.4,0,1,1) both; }
        .card-fade-in   { animation: fadeInCard   0.45s cubic-bezier(0.22,1,0.36,1) both; }
      `}</style>

      
      {showAbout && globalName === '' ? (
        <About onBack={() => setShowAbout(false)} />
      ) : (
      <div className="min-h-screen w-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center relative justify-center p-6">

        {globalName === '' && (
          <button
            type="button"
            onClick={() => setShowAbout(true)}
            className="absolute top-4 right-6 px-4 py-2 rounded-lg border border-cyan-500/40 text-cyan-200 hover:bg-cyan-900/20 transition z-10"
          >
            About
          </button>
        )}

        {globalName === '' && isMapLoading && (
          <div className="absolute inset-0 z-20 flex items-center justify-center bg-slate-900/70 backdrop-blur-sm">
            <div className="flex items-center gap-3 text-cyan-200">
              <div className="h-6 w-6 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin" />
              <span className="text-base sm:text-lg font-semibold">Generating K‑Map…</span>
            </div>
          </div>
        )}

        {globalName === '' ? (
          <Register
            globalName={globalName}
            setGlobalName={setGlobalName}
            setGameState={setGameState}
            setIsMapLoading={setIsMapLoading}
            isMapLoading={isMapLoading}
          />
        ) : (
          
          <div className="absolute flex flex-col lg:flex-row items-center z-3 justify-center gap-8 w-full">

            
            <div
              key={mapKey}
              className={`flex-none relative ${gameState?.is_tutorial ? '' : (slideDir === 'in' ? 'kmap-slide-in' : 'kmap-slide-out')}`}
            >
              <Kmap
                dont_cares={gameState.q_dont_cares}
                form={gameState.q_form}
                num_var={gameState.q_num_var}
                terms={gameState.q_terms}
                groupings={gameState.q_groupings}
                globalState={globalState}
                showGroupings={gameState?.difficulty !== 4 || globalState !== 'show' || isLastAnswerCorrect}
                forceGroupings={gameState?.is_tutorial || false}
                cellValues={gameState?.is_tutorial ? gameState.tutorial_cells : undefined}
                disableCells={gameState?.is_tutorial ? gameState.tutorial_busy : false}
                onToggleCell={gameState?.is_tutorial ? (index => {
                  if (gameState.tutorial_busy) {
                    return;
                  }
                  const nextCells = [...gameState.tutorial_cells];
                  const current = nextCells[index];
                  const nextVal = current === 0 ? 1 : current === 1 ? "x" : 0;
                  nextCells[index] = nextVal;

                  setGameState({
                    ...gameState,
                    tutorial_cells: nextCells,
                  });
                }) : undefined}
              />
              {isMapLoading && !gameState?.is_tutorial && (
                <div className="absolute inset-0 flex items-center justify-center rounded-2xl bg-slate-900/70 backdrop-blur-sm">
                  <div className="flex items-center gap-3 text-cyan-200">
                    <div className="h-5 w-5 rounded-full border-2 border-cyan-400 border-t-transparent animate-spin" />
                    <span className="text-sm sm:text-base">Generating K‑Map…</span>
                  </div>
                </div>
              )}
            </div>

            
            <div className="hidden lg:block w-px self-stretch bg-cyan-500/20" />

        
            <div className="flex-none w-full max-w-md card-fade-in mb-10">
              {gameState?.is_tutorial ? (
                <TutorialPanel
                  gameState={gameState}
                  setGameState={setGameState}
                />
              ) : gameState?.is_time_attack ? (
                <TimeAttackCard
                  gameState={gameState}
                  setGlobalState={setGlobalState}
                  globalState={globalState}
                  setGameState={setGameState}
                  setIsMapLoading={setIsMapLoading}
                  isMapLoading={isMapLoading}
                />
              ) : (
                <AnswerCard
                  gameState={gameState}
                  setGlobalState={setGlobalState}
                  globalState={globalState}
                  setGameState={setGameState}
                  setIsLastAnswerCorrect={setIsLastAnswerCorrect}
                  setIsMapLoading={setIsMapLoading}
                  isMapLoading={isMapLoading}
                />
              )}
            </div>
          </div>
        )}

        <img
          src="logo.png"
          alt="Logo"
          className="fixed bottom-0 right-0 w-[30vw] max-w-xs opacity-10 z-0 pointer-events-none select-none grayscale invert"
        />

       
        <div className="absolute fixed bottom-4 left-6 text-slate-400 opacity-20 z-0 select-none leading-tight">
          <div className="text-lg md:text-5xl font-bold">Kmap GamEEE</div>
          <div className="text-xs md:text-2xl">
            by Francois Abedejos | Updated by Shaira Rodriguez & Isaac Sy
          </div>
        </div>
      </div>
      )}
    </>
  );
}

export default App
