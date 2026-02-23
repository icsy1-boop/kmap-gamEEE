
import React, { useState } from 'react'

const Register = ({ globalName, setGlobalName, setGameState }) => {

    const [difficulty, setDifficulty] = useState('medium')

    const difficulties = [
        { value: 'easy', label: 'Easy', color: 'emerald', description: '2-3 variables' },
        { value: 'medium', label: 'Medium', color: 'cyan', description: '3-4 variables' },
        { value: 'hard', label: 'Hard', color: 'amber', description: '5-6 variables' },
        { value: 'timed', label: 'Timed Challenge', color: 'rose', description: 'Daily Timed Challenge!' },
        { value: 'progressive', label: 'Progressive', color: 'purple', description: 'Adaptive difficulty' }
    ]



    const getDifficultyColor = (diff) => {
        const colors = {
            easy: 'from-emerald-600 to-green-600 border-emerald-500/50',
            medium: 'from-cyan-600 to-blue-600 border-cyan-500/50',
            hard: 'from-amber-600 to-orange-600 border-amber-500/50',
            timed: 'from-rose-600 to-pink-600 border-rose-500/50',
            progressive: 'from-purple-600 to-pink-600 border-purple-500/50'
        }
        return colors[diff] || colors.medium
    }


    const createUser = async (username, difficulty) => {
        try {
            // TODO: Change to https://kmap-gameee.vercel.app/user
            const response = await fetch("http://localhost:8000/user", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ username, difficulty }),
            });

            const data = await response.json();
            // console.log("New user:", data);
            setGlobalName(username);
            setGameState(data);
            return data;
        } catch (error) {
            console.error(error);
        }
    };

    const [name, setName] = useState('')

    return (
      <div className="w-full max-w-2xl mx-auto p-8 bg-gradient-to-br from-slate-800/95 via-slate-900/95 to-slate-800/95 backdrop-blur-xl rounded-3xl shadow-2xl border-2 border-cyan-500/30">
            
                <div className="text-center mb-8">
                    
                    <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-blue-300 mb-2">
                        K-Map GamEEE
                    </h2>
                    <p className="text-slate-400">
                        Enter your name and choose your challenge level
                    </p>
                </div>

               
                <div className="space-y-2">
                    <label className="block text-cyan-300 font-semibold text-sm uppercase tracking-wide">
                        Username
                    </label>
                    <div className="relative">
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="Enter your username..."
                            className="w-full px-6 py-4 bg-slate-900/50 border-2 border-slate-600 rounded-xl text-white text-lg placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 transition-all duration-200 shadow-inner"
                            required
                        />
                        <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-cyan-500/5 to-blue-500/5 pointer-events-none"></div>
                    </div>
                </div>

                <div className="space-y-3">
                    <label className="block text-cyan-300 font-semibold text-sm uppercase tracking-wide my-3">
                        Select Difficulty
                    </label>
                    <div className="grid grid-cols-2 gap-3">
                        {difficulties.map((diff) => (
                            <button
                                key={diff.value}
                                type="button"
                                onClick={() => setDifficulty(diff.value)}
                                className={`p-4 rounded-xl border-2 transition-all duration-200 ${
                                    difficulty === diff.value
                                        ? `bg-gradient-to-br ${getDifficultyColor(diff.value)} shadow-lg scale-105`
                                        : 'bg-slate-800/50 border-slate-600 hover:border-slate-500 hover:bg-slate-800/70'
                                }`}
                            >
                                <div className="text-left">
                                    <div className={`font-bold text-lg ${
                                        difficulty === diff.value ? 'text-white' : 'text-slate-300'
                                    }`}>
                                        {diff.label}
                                    </div>
                                    <div className={`text-sm ${
                                        difficulty === diff.value ? 'text-white/80' : 'text-slate-500'
                                    }`}>
                                        {diff.description}
                                    </div>
                                </div>
                                {difficulty === diff.value && (
                                    <div className="absolute top-2 right-2">
                                        <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                        </svg>
                                    </div>
                                )}
                            </button>
                        ))}
                    </div>
                </div>

                <button
                    type="submit"
                    disabled={!name.trim()}
                    onClick={() => {createUser(name, difficulty)}}
                    className={`w-full px-8 py-5 bg-gradient-to-r ${getDifficultyColor(difficulty)} text-white font-bold my-5 text-xl rounded-xl shadow-2xl transition-all duration-200 transform ${
                        name.trim() 
                            ? 'hover:scale-[1.02] active:scale-[0.98] cursor-pointer' 
                            : 'opacity-50 cursor-not-allowed'
                    }`}
                >
                    <span className="flex items-center justify-center gap-2">
                        Start Training
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                        </svg>
                    </span>
                </button>
            
        </div>
    )
}

export default Register
