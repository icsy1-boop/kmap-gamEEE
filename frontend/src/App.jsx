import { useState, useEffect, useRef } from 'react'
import './App.css'
import Register from './components/register.jsx'
import Kmap from './components/Kmap.jsx';
import AnswerCard from './components/AnswerCard.jsx';
import TimeAttackCard from './components/TimeAttackCard.jsx';

function App() {
  const [globalName, setGlobalName] = useState('');
  const [gameState, setGameState] = useState(null);
  const [globalState, setGlobalState] = useState('hide');
  const [mapKey, setMapKey] = useState(0);
  const [slideDir, setSlideDir] = useState('in');
  const [isLastAnswerCorrect, setIsLastAnswerCorrect] = useState(true);
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

      
      <div className="min-h-screen w-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center relative justify-center p-6">

        {globalName === '' ? (
          <Register
            globalName={globalName}
            setGlobalName={setGlobalName}
            setGameState={setGameState}
          />
        ) : (
          
          <div className="absolute flex flex-col lg:flex-row items-center z-3 justify-center gap-8 w-full">

            
            <div
              key={mapKey}
              className={`flex-none ${slideDir === 'in' ? 'kmap-slide-in' : 'kmap-slide-out'}`}
            >
              <Kmap
                dont_cares={gameState.q_dont_cares}
                form={gameState.q_form}
                num_var={gameState.q_num_var}
                terms={gameState.q_terms}
                groupings={gameState.q_groupings}
                globalState={globalState}
                showGroupings={gameState?.difficulty !== 4 || globalState !== 'show' || isLastAnswerCorrect}
              />
            </div>

            
            <div className="hidden lg:block w-px self-stretch bg-cyan-500/20" />

        
            <div className="flex-none w-full max-w-md card-fade-in mb-10">
              {gameState?.is_time_attack ? (
                <TimeAttackCard
                  gameState={gameState}
                  setGlobalState={setGlobalState}
                  globalState={globalState}
                  setGameState={setGameState}
                />
              ) : (
                <AnswerCard
                  gameState={gameState}
                  setGlobalState={setGlobalState}
                  globalState={globalState}
                  setGameState={setGameState}
                  setIsLastAnswerCorrect={setIsLastAnswerCorrect}
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
            by Francois Abedejos | Updated by Shaira Rodriguez | Updated by Isaac Sy
          </div>
        </div>
      </div>
    </>
  );
}

export default App