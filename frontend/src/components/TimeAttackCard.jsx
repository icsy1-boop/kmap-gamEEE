import React, { useState, useEffect } from 'react'


const TIME_LIMIT = 30;


const TimeAttackCard = ({ gameState, setGlobalState, globalState, setGameState }) => {
    const [answer, setAnswer] = useState('');
    const [errorS, setErrorS] = useState(false);
    const [response, setResponse] = useState(null);
    const [errorMessage, setErrorMessage] = useState("");
    const [timeRemaining, setTimeRemaining] = useState(TIME_LIMIT);
    const [questionsAnswered, setQuestionsAnswered] = useState(0);
    const [gameOver, setGameOver] = useState(false);
    const [isValid, setIsValid] = useState(true);
    const [resultVisible, setResultVisible] = useState(false);
    const [leaderboard, setLeaderboard] = useState([]);

    // Timer
    useEffect(() => {
        if (gameOver || timeRemaining <= 0) {
            if (timeRemaining <= 0 && !gameOver) {
                finishTimeAttack();
            }
            return;
        }

        const interval = setInterval(() => {
            setTimeRemaining(prev => {
                if (prev <= 1) {
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);

        return () => clearInterval(interval);
    }, [gameOver, timeRemaining]);

    // When result shows, animate it in
    useEffect(() => {
        if (response) {
            setResultVisible(false);
            const t = setTimeout(() => setResultVisible(true), 30);
            return () => clearTimeout(t);
        } else {
            setResultVisible(false);
        }
    }, [response]);

    const checkAnswer = async () => {
        if (answer === '') {
            setErrorS(true);
            return;
        }

        try {
            // TODO: Change to https://kmap-gameee.vercel.app/check-time-attack
            const response = await fetch("http://localhost:8000/check-time-attack", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    username: gameState.username,
                    difficulty: gameState.difficulty,
                    questions_solved: questionsAnswered,
                    time_remaining: timeRemaining,
                    q_num_var: gameState.q_num_var,
                    q_form: gameState.q_form,
                    q_terms: gameState.q_terms,
                    q_dont_cares: gameState.q_dont_cares,
                    answer: answer
                }),
            });

            const data = await response.json();
            console.log("Check answer response:", data);

            if (data.result !== 1) {
                // Wrong answer - game over
                setIsValid(false);
                setGameOver(true);
                setResponse(data);
                return;
            }

            // Correct answer
            setQuestionsAnswered(data.questions_solved);
            setAnswer("");
            setErrorS(false);
            setErrorMessage("");
            
            // Update game state with new question
            setGameState({
                ...gameState,
                q_num_var: data.q_num_var,
                q_form: data.q_form,
                q_terms: data.q_terms,
                q_dont_cares: data.q_dont_cares
            });
            
            setResponse(data);
        } catch (error) {
            console.error("Error checking answer:", error);
            setErrorMessage("Failed to submit answer");
        }
    };

    const finishTimeAttack = async () => {
        setGameOver(true);
        try {
            // TODO: Change to https://kmap-gameee.vercel.app/finish-time-attack
            const response = await fetch("http://localhost:8000/finish-time-attack", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    username: gameState.username,
                    difficulty: gameState.difficulty,
                    questions_solved: questionsAnswered,
                    is_valid: isValid
                }),
            });

            const data = await response.json();
            console.log("Finish time attack:", data);
            setLeaderboard(data.leaderboard);
        } catch (error) {
            console.error("Error finishing time attack:", error);
        }
    };

    const isCorrect = response && response["result"] == 1;
    const difficultyMap = { 1: 'Easy', 2: 'Medium', 3: 'Hard' };

    if (gameOver) {
        return (
            <div className='w-full px-2 sm:px-4 md:px-6 mx-auto'>
                <div className="w-full p-5 sm:p-8 md:p-10 from-slate-800 via-slate-900 to-slate-800 backdrop-blur-lg rounded-2xl shadow-2xl border-2 border-violet-500/95">
                    <div className="text-center mb-6">
                        <h1 className={`text-4xl sm:text-5xl md:text-6xl font-bold text-transparent bg-clip-text mb-4 ${
                            isValid ? 'bg-gradient-to-r from-violet-400 to-blue-400' : 'bg-gradient-to-r from-red-400 to-pink-400'
                        }`}>
                            {isValid ? 'Time\'s Up!' : 'Game Over!'}
                        </h1>
                        <p className="text-slate-300 text-lg sm:text-xl">
                            {isValid 
                                ? `Great job, ${gameState.username}!` 
                                : `Wrong answer!`
                            }
                        </p>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-6">
                        <div className={`p-4 rounded-xl border-2 ${
                            isValid 
                                ? 'bg-violet-900/30 border-violet-500/50' 
                                : 'bg-red-900/30 border-red-500/50'
                        }`}>
                            <p className="text-slate-400 text-sm mb-1">Questions Solved</p>
                            <p className={`text-3xl font-bold ${isValid ? 'text-violet-400' : 'text-red-400'}`}>
                                {questionsAnswered}
                            </p>
                        </div>
                        <div className={`p-4 rounded-xl border-2 ${
                            isValid 
                                ? 'bg-blue-900/30 border-blue-500/50' 
                                : 'bg-slate-900/30 border-slate-500/50'
                        }`}>
                            <p className="text-slate-400 text-sm mb-1">
                                {isValid ? 'Rank' : 'Status'}
                            </p>
                            <p className={`text-3xl font-bold ${isValid ? 'text-blue-400' : 'text-slate-400'}`}>
                                {isValid ? '#' + (leaderboard.findIndex(e => e.username === gameState.username) + 1 || '—') : 'Invalid'}
                            </p>
                        </div>
                    </div>

                    {isValid && (
                        <div className="mb-6">
                            <h2 className="text-xl font-bold text-cyan-400 mb-4">Leaderboard ({difficultyMap[gameState.difficulty]})</h2>
                            <div className="space-y-2">
                                {leaderboard && leaderboard.map((entry, idx) => (
                                    <div 
                                        key={idx}
                                        className={`flex justify-between p-3 rounded-lg transition-all ${
                                            entry.username === gameState.username
                                                ? 'bg-violet-900/40 border-2 border-violet-500/50'
                                                : 'bg-slate-800/50 border border-slate-600'
                                        }`}
                                    >
                                        <div className="flex items-center gap-3">
                                            <span className="font-bold text-slate-300 w-6">#{idx + 1}</span>
                                            <span className={`font-semibold ${
                                                entry.username === gameState.username ? 'text-violet-300' : 'text-slate-300'
                                            }`}>
                                                {entry.username}
                                            </span>
                                        </div>
                                        <span className={`font-bold ${
                                            entry.username === gameState.username ? 'text-violet-400' : 'text-cyan-400'
                                        }`}>
                                            {entry.questions_solved} solved
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    <button
                        type="button"
                        onClick={() => window.location.reload()}
                        className="w-full px-6 sm:px-8 py-3 sm:py-4 font-bold text-sm sm:text-base md:text-lg
                            rounded-xl shadow-lg transition-all duration-200 transform
                            hover:scale-[1.02] active:scale-[0.98] border text-white
                            bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500
                            shadow-violet-500/30 hover:shadow-violet-500/50"
                    >
                        Play Again
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className='w-full px-2 sm:px-4 md:px-6 mx-auto'>
            <div className="w-full p-5 sm:p-8 md:p-10 from-slate-800 via-slate-900 to-slate-800 backdrop-blur-lg rounded-2xl shadow-2xl border-2 border-violet-500/95">
                
                <div className="mb-4 flex justify-between items-center">
                    <div>
                        <p className="text-left text-slate-400 text-sm sm:text-base md:text-lg">
                            {gameState.username} • {difficultyMap[gameState.difficulty]}
                        </p>
                    </div>
                    <div className="flex gap-6 items-center">
                        <div className="text-right">
                            <p className="text-slate-400 text-xs">Questions Solved</p>
                            <p className='text-2xl font-bold text-violet-400'>{questionsAnswered}</p>
                        </div>
                        <div className="text-right">
                            <p className="text-slate-400 text-xs">Time Remaining</p>
                            <p className={`text-2xl font-bold ${
                                timeRemaining <= 10 ? 'text-red-400 animate-pulse' : 'text-cyan-400'
                            }`}>
                                {timeRemaining}s
                            </p>
                        </div>
                    </div>
                </div>

                {response && (
                    <div
                        className="overflow-hidden transition-all duration-500 ease-out mb-4"
                        style={{
                            maxHeight: resultVisible ? '100px' : '0px',
                            opacity: resultVisible ? 1 : 0,
                        }}
                    >
                        <div className={`px-5 py-4 rounded-2xl border-2 text-center
                            ${isCorrect
                                ? 'bg-emerald-900/30 border-emerald-500/50 shadow-lg shadow-emerald-500/20'
                                : 'bg-red-900/30 border-red-500/50 shadow-lg shadow-red-500/20'
                            }`}
                        >
                            <h1 className={`text-2xl sm:text-3xl font-semibold
                                ${isCorrect ? 'text-emerald-400' : 'text-red-400'}`}
                            >
                                {isCorrect ? 'Correct!' : 'Wrong!'}
                            </h1>
                        </div>
                    </div>
                )}

                <div className="text-center mb-5 sm:mb-6">
                    <p className="text-slate-400 text-sm sm:text-base md:text-lg">
                        Find the{' '}
                        <span className='font-bold text-cyan-400'>
                            {gameState.q_form == "min" ? "SOP" : "POS"}
                        </span>{' '}
                        expression
                    </p>
                </div>

                <div className="relative my-4">
                    {errorMessage && (
                        <div className="absolute left-0 -top-7 text-xs bg-red-500 text-white px-2 py-1 rounded shadow-md z-10 whitespace-nowrap">
                            {errorMessage}
                        </div>
                    )}
                    <input
                        type="text"
                        value={answer}
                        onChange={(e) => {
                            setAnswer(e.target.value);
                            setErrorS(false);
                            setErrorMessage("");
                        }}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter') checkAnswer();
                        }}
                        placeholder="e.g., AB+BC'+A'C, (AB)(D')"
                        className={`w-full px-4 sm:px-6 py-3 sm:py-4 bg-slate-900/50 border-2
                            ${errorS ? "border-red-400" : "border-slate-400/30"}
                            rounded-xl text-white text-sm sm:text-base md:text-lg placeholder-slate-500
                            focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20
                            transition-all duration-200 shadow-inner`}
                        disabled={false}
                    />
                    <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-violet-500/5 to-blue-500/5 pointer-events-none"></div>
                </div>

                <button
                    type="button"
                    onClick={checkAnswer}
                    className={`w-full px-6 sm:px-8 py-3 sm:py-4 font-bold text-sm sm:text-base md:text-lg
                        rounded-xl shadow-lg transition-all duration-200 transform
                        hover:scale-[1.02] active:scale-[0.98] border text-white
                        bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 shadow-violet-500/30 hover:shadow-violet-500/50
                        `}
                >
                    Submit Answer
                </button>
            </div>
        </div>
    );
};

export default TimeAttackCard
