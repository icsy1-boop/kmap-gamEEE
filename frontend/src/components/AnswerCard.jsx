import React, { useState, useEffect } from 'react'

const AnswerCard = ({ onSubmit, gameState, setGlobalState, globalState, setGameState }) => {
    const [answer, setAnswer] = useState('');
    const [errorS, setErrorS] = useState(false);
    const [response, setResponse] = useState(null);
    const [errorMessage, setErrorMessage] = useState("");
    const [resultVisible, setResultVisible] = useState(false);
    const [elapsedSeconds, setElapsedSeconds] = useState(0);
    const [timedFinished, setTimedFinished] = useState(false);
    const [finishError, setFinishError] = useState("");

    // Animate the result banner in whenever globalState flips to "show"
    useEffect(() => {
        if (globalState === 'show') {
            setResultVisible(false);
            // tiny delay so the CSS transition fires from the hidden state
            const t = setTimeout(() => setResultVisible(true), 30);
            return () => clearTimeout(t);
        } else {
            setResultVisible(false);
        }
    }, [globalState]);

    // Timer for timed mode
    useEffect(() => {
        if (gameState.difficulty !== 4 || timedFinished || globalState === "show") return;
        
        const interval = setInterval(() => {
            setElapsedSeconds(prev => prev + 1);
        }, 1000);
        
        return () => clearInterval(interval);
    }, [gameState.difficulty, timedFinished, globalState]);

    const checkAnswer = async (userData, type = 0) => {
        if (answer === '') {
            setErrorS(true);
        } else {
            try {
                // TODO: Change to https://kmap-gameee.vercel.app/game
                const response = await fetch("http://localhost:8000/game", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ type: type, user: userData }),
                });
                const data = await response.json();
                console.log(data);
                return data;
            } catch (error) {
                console.error("Error:", error);
            }
        }
    };

    const formatTime = (seconds) => {
        if (seconds === undefined || seconds === null || isNaN(seconds)) {
            return '0s';
        }
        const secondsNum = Number(seconds);
        const hours = Math.floor(secondsNum / 3600);
        const minutes = Math.floor((secondsNum % 3600) / 60);
        const secs = secondsNum % 60;
        
        if (hours > 0) {
            return `${hours}h ${minutes}m ${secs}s`;
        } else if (minutes > 0) {
            return `${minutes}m ${secs}s`;
        } else {
            return `${secs}s`;
        }
    };

    const handleSubmit = async () => {
        const userPayload = { ...gameState, answer: answer };
        if (globalState === "hide") {
            if (answer !== '') {
                const result = await checkAnswer(userPayload, 0);
                if (result["result"] == 0 || result["result"] == 1) {
                    setGlobalState("show");
                    setResponse(result);
                } else {
                    setGlobalState("hide");
                    setErrorS(true);
                    setErrorMessage("Incorrect format (check variables or operators)");
                }
            } else {
                setErrorS(true);
                setErrorMessage("Input something!");
            }
        } else {
            const meow = { ...gameState, result: response["result"] };
            setGlobalState("hide");
            const result = await checkAnswer(meow, 1);
            setAnswer("");
            setGameState(result.user);
            console.log(result);
        }
    };

    const handleFinishTimed = async () => {
        // When finishing timed challenge, use the elapsed time tracked on the frontend
        // This is more accurate than recalculating on the backend
        try {
            setFinishError("");
            console.log("Finishing timed challenge with:", {
                username: gameState.username,
                score: gameState.score,
                difficulty: gameState.difficulty,
                elapsed_seconds: elapsedSeconds
            });
            
            // TODO: Change to https://kmap-gameee.vercel.app/finish-timed
            const response = await fetch("http://localhost:8000/finish-timed", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    username: gameState.username,
                    score: gameState.score,
                    difficulty: gameState.difficulty,
                    elapsed_seconds: elapsedSeconds
                }),
            });
            
            if (!response.ok) {
                console.error("Response not ok:", response.status, response.statusText);
                const errorData = await response.json();
                console.error("Error data:", errorData);
                setFinishError(errorData.error || `Server error: ${response.status}`);
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log("Finish timed result:", result);
            setTimedFinished(true);
            setGlobalState("timed-finished");
            setResponse(result);
        } catch (error) {
            console.error("Error finishing timed challenge:", error);
            setFinishError(error.message || "Failed to finish challenge");
        }
    };

    const isCorrect = response && response["result"] == 1;

    if (timedFinished && response) {
        // Show timed challenge completion screen
        return (
            <div className='w-full px-2 sm:px-4 md:px-6 mx-auto'>
                <div className="w-full p-5 sm:p-8 md:p-10 from-slate-800 via-slate-900 to-slate-800 backdrop-blur-lg rounded-2xl shadow-2xl border-2 border-rose-500/95">
                    <div className="text-center mb-6">
                        <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-rose-400 to-pink-400 mb-4">
                            Challenge Complete!
                        </h1>
                        <p className="text-slate-300 text-lg sm:text-xl">
                            Great job, {gameState.username}!
                        </p>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-6">
                        <div className="p-4 rounded-xl bg-rose-900/30 border-2 border-rose-500/50">
                            <p className="text-slate-400 text-sm mb-1">Time</p>
                            <p className="text-3xl font-bold text-rose-400">{formatTime(response.elapsed_seconds)}</p>
                        </div>
                        <div className="p-4 rounded-xl bg-blue-900/30 border-2 border-blue-500/50">
                            <p className="text-slate-400 text-sm mb-1">Rank</p>
                            <p className="text-3xl font-bold text-blue-400">#{response.rank}</p>
                        </div>
                    </div>

                    <div className="mb-6">
                        <h2 className="text-xl font-bold text-cyan-400 mb-4">Leaderboard</h2>
                        <div className="space-y-2">
                            {response.leaderboard && response.leaderboard.map((entry, idx) => (
                                <div 
                                    key={idx}
                                    className={`flex justify-between p-3 rounded-lg transition-all ${
                                        entry.username === gameState.username
                                            ? 'bg-rose-900/40 border-2 border-rose-500/50'
                                            : 'bg-slate-800/50 border border-slate-600'
                                    }`}
                                >
                                    <div className="flex items-center gap-3">
                                        <span className="font-bold text-slate-300 w-6">#{idx + 1}</span>
                                        <span className={`font-semibold ${
                                            entry.username === gameState.username ? 'text-rose-300' : 'text-slate-300'
                                        }`}>
                                            {entry.username}
                                        </span>
                                    </div>
                                    <span className={`font-bold ${
                                        entry.username === gameState.username ? 'text-rose-400' : 'text-cyan-400'
                                    }`}>
                                        {formatTime(entry.completion_time_seconds)}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <button
                        type="button"
                        onClick={() => window.location.reload()}
                        className="w-full px-6 sm:px-8 py-3 sm:py-4 font-bold text-sm sm:text-base md:text-lg
                            rounded-xl shadow-lg transition-all duration-200 transform
                            hover:scale-[1.02] active:scale-[0.98] border text-white
                            bg-gradient-to-r from-rose-600 to-pink-600 hover:from-rose-500 hover:to-pink-500
                            shadow-rose-500/30 hover:shadow-rose-500/50"
                    >
                        Play Again Tomorrow
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className='w-full px-2 sm:px-4 md:px-6 mx-auto'>

            <div
                className="overflow-hidden transition-all duration-500 ease-out"
                style={{
                    maxHeight: globalState === 'show' && resultVisible ? '160px' : '0px',
                    opacity: globalState === 'show' && resultVisible ? 1 : 0,
                    transform: globalState === 'show' && resultVisible
                        ? 'translateY(0) scale(1)'
                        : 'translateY(-12px) scale(0.97)',
                }}
            >
                <div className={`mb-4 px-5 py-4 rounded-2xl border-2 text-center
                    ${isCorrect
                        ? 'bg-emerald-900/30 border-emerald-500/50 shadow-lg shadow-emerald-500/20'
                        : 'bg-red-900/30 border-red-500/50 shadow-lg shadow-red-500/20'
                    }`}
                >
                    <h1 className={`text-2xl sm:text-3xl md:text-4xl font-semibold mb-2
                        ${isCorrect ? 'text-emerald-400' : 'text-red-400'}`}
                    >
                        {isCorrect ? 'Correct!' : 'Wrong!'}
                    </h1>
                    {!(gameState.difficulty === 4 && !isCorrect) && (
                        <p className='text-cyan-400 font-bold text-sm sm:text-base'>
                            Correct answer(s):{' '}
                            <span className='text-amber-50 font-normal'>
                                {response && response["answers"].join(', ')}
                            </span>
                        </p>
                    )}
                </div>
            </div>

            <div className="w-full p-5 sm:p-8 md:p-10 from-slate-800 via-slate-900 to-slate-800 backdrop-blur-lg rounded-2xl shadow-2xl border-2 border-cyan-500/95">
                
                {finishError && (
                    <div className="mb-4 p-4 rounded-xl bg-red-900/30 border-2 border-red-500/50">
                        <p className="text-red-400 font-semibold text-sm">
                            Error: {finishError}
                        </p>
                    </div>
                )}
                
                <div className="mb-3 flex w-full justify-between items-center">
                    <p className="text-left text-slate-400 text-sm sm:text-base md:text-lg truncate max-w-[50%]">
                        {gameState.username}
                    </p>
                    <div className="flex gap-4 items-center">
                        <p className="text-right text-slate-400 text-sm sm:text-base md:text-lg">
                            Score: <span className='font-bold text-cyan-400'>{gameState.score}</span>
                        </p>
                        {gameState.difficulty === 4 && (
                            <p className="text-right text-slate-400 text-sm sm:text-base md:text-lg">
                                Time: <span className='font-bold text-rose-400'>{formatTime(elapsedSeconds)}</span>
                            </p>
                        )}
                    </div>
                </div>

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
                            if (e.key === 'Enter' && globalState !== 'show') handleSubmit();
                        }}
                        placeholder="e.g., AB+BC'+A'C, (AB)(D')"
                        className={`w-full px-4 sm:px-6 py-3 sm:py-4 bg-slate-900/50 border-2
                            ${errorS ? "border-red-400" : "border-slate-400/30"}
                            rounded-xl text-white text-sm sm:text-base md:text-lg placeholder-slate-500
                            focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20
                            transition-all duration-200 shadow-inner
                            ${globalState === "show" ? "pointer-events-none opacity-60" : ""}`}
                        disabled={gameState.difficulty === 4 && globalState === "show"}
                    />
                    <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-cyan-500/5 to-blue-500/5 pointer-events-none"></div>
                </div>

                <button
                    type="button"
                    onClick={() => {
                        console.log("Button clicked. difficulty:", gameState.difficulty, "globalState:", globalState, "isCorrect:", isCorrect);
                        // For timed mode, only allow finishing if answer was correct
                        if (gameState.difficulty === 4 && globalState === "show" && isCorrect) {
                            console.log("Calling handleFinishTimed");
                            handleFinishTimed();
                        } else {
                            console.log("Calling handleSubmit");
                            handleSubmit();
                        }
                    }}
                    className={`w-full px-6 sm:px-8 py-3 sm:py-4 font-bold text-sm sm:text-base md:text-lg
                        rounded-xl shadow-lg transition-all duration-200 transform
                        hover:scale-[1.02] active:scale-[0.98] border text-white
                        ${gameState.difficulty === 4 && globalState === "show" && isCorrect
                            ? "bg-gradient-to-r from-rose-600 to-pink-600 hover:from-rose-500 hover:to-pink-500 shadow-rose-500/30 hover:shadow-rose-500/50"
                            : globalState === "hide"
                            ? "bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 shadow-cyan-500/30 hover:shadow-cyan-500/50"
                            : "bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-500 hover:to-emerald-500 shadow-emerald-500/30 hover:shadow-emerald-500/50"
                        }`}
                >
                    {gameState.difficulty === 4 && globalState === "show" && isCorrect ? "Finish Challenge" : gameState.difficulty === 4 && globalState === "show" ? "Try Again" : globalState === "hide" ? "Submit Answer" : "Next Map"}
                </button>
            </div>
        </div>
    );
};

export default AnswerCard