
import React, { useState } from 'react'

const Register = ({ globalName, setGlobalName, setGameState }) => {

    const [difficulty, setDifficulty] = useState('medium')
    const [expandedSection, setExpandedSection] = useState('practice')

    // Organize difficulties by category
    const difficultyCategories = {
        practice: [
            { value: 'easy', label: 'Easy', color: 'emerald', description: '2-3 variables' },
            { value: 'medium', label: 'Medium', color: 'cyan', description: '3-4 variables' },
            { value: 'hard', label: 'Hard', color: 'amber', description: '5-6 variables' },
            { value: 'progressive', label: 'Progressive', color: 'purple', description: 'Adaptive difficulty' }
        ],
        timeAttack: [
            { value: 'timed', label: 'Timed Challenge', color: 'rose', description: 'Daily Timed Challenge!' },
            { value: 'time-attack-easy', label: 'Time Attack Easy', color: 'blue', description: 'Ranked Mode' },
            { value: 'time-attack-medium', label: 'Time Attack Medium', color: 'indigo', description: 'The better Ranked Mode' },
            { value: 'time-attack-hard', label: 'Time Attack Hard', color: 'violet', description: 'Adel\'s Children only' }
        ]
    }



    const getDifficultyColor = (diff) => {
        const colors = {
            easy: 'from-emerald-600 to-green-600 border-emerald-500/50',
            medium: 'from-cyan-600 to-blue-600 border-cyan-500/50',
            hard: 'from-amber-600 to-orange-600 border-amber-500/50',
            timed: 'from-rose-600 to-pink-600 border-rose-500/50',
            progressive: 'from-purple-600 to-pink-600 border-purple-500/50',
            'time-attack-easy': 'from-blue-600 to-cyan-600 border-blue-500/50',
            'time-attack-medium': 'from-indigo-600 to-blue-600 border-indigo-500/50',
            'time-attack-hard': 'from-violet-600 to-purple-600 border-violet-500/50'
        }
        return colors[diff] || colors.medium
    }


    const createUser = async (username, difficulty) => {
        try {
            // TODO: Change to https://kmap-gameee.vercel.app/user
            
            // Map difficulty values
            let difficultyValue = difficulty;
            let apiEndpoint = "http://localhost:8000/user";
            
            if (difficulty === 'time-attack-easy') {
                difficultyValue = 'time-attack-easy';
                apiEndpoint = "http://localhost:8000/start-time-attack";
            } else if (difficulty === 'time-attack-medium') {
                difficultyValue = 'time-attack-medium';
                apiEndpoint = "http://localhost:8000/start-time-attack";
            } else if (difficulty === 'time-attack-hard') {
                difficultyValue = 'time-attack-hard';
                apiEndpoint = "http://localhost:8000/start-time-attack";
            }
            
            const timeAttackDifficultyMap = {
                'time-attack-easy': 1,
                'time-attack-medium': 2,
                'time-attack-hard': 3
            };
            
            const payload = difficultyValue.startsWith('time-attack') 
                ? { username, difficulty: timeAttackDifficultyMap[difficultyValue], is_time_attack: true }
                : { username, difficulty };
            
            const response = await fetch(apiEndpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();
            // Add flag for time attack mode
            if (difficultyValue.startsWith('time-attack')) {
                data.is_time_attack = true;
                data.difficulty_name = difficultyValue;
            }
            
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

                    {/* Practice Section */}
                    <div className="border border-cyan-500/30 rounded-xl overflow-hidden">
                        <button
                            onClick={() => setExpandedSection(expandedSection === 'practice' ? null : 'practice')}
                            className="w-full px-4 py-3 bg-cyan-900/20 hover:bg-cyan-900/30 flex items-center justify-between transition-all"
                        >
                            <span className="font-semibold text-cyan-300">Practice Modes</span>
                            <svg className={`w-5 h-5 text-cyan-300 transition-transform ${expandedSection === 'practice' ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                            </svg>
                        </button>
                        {expandedSection === 'practice' && (
                            <div className="p-3 space-y-2 bg-slate-900/50">
                                {difficultyCategories.practice.map((diff) => (
                                    <button
                                        key={diff.value}
                                        type="button"
                                        onClick={() => setDifficulty(diff.value)}
                                        className={`w-full p-3 rounded-lg border-2 transition-all duration-200 text-left ${
                                            difficulty === diff.value
                                                ? `bg-gradient-to-br ${getDifficultyColor(diff.value)} shadow-lg border-opacity-100`
                                                : 'bg-slate-800/50 border-slate-600 hover:border-slate-500 hover:bg-slate-800/70'
                                        }`}
                                    >
                                        <div className={`font-semibold ${
                                            difficulty === diff.value ? 'text-white' : 'text-slate-300'
                                        }`}>
                                            {diff.label}
                                        </div>
                                        <div className={`text-xs ${
                                            difficulty === diff.value ? 'text-white/70' : 'text-slate-500'
                                        }`}>
                                            {diff.description}
                                        </div>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Time Attack Section */}
                    <div className="border border-violet-500/30 rounded-xl overflow-hidden">
                        <button
                            onClick={() => setExpandedSection(expandedSection === 'timeAttack' ? null : 'timeAttack')}
                            className="w-full px-4 py-3 bg-violet-900/20 hover:bg-violet-900/30 flex items-center justify-between transition-all"
                        >
                            <span className="font-semibold text-violet-300">Time Attack</span>
                            <svg className={`w-5 h-5 text-violet-300 transition-transform ${expandedSection === 'timeAttack' ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                            </svg>
                        </button>
                        {expandedSection === 'timeAttack' && (
                            <div className="p-3 space-y-2 bg-slate-900/50">
                                {difficultyCategories.timeAttack.map((diff) => (
                                    <button
                                        key={diff.value}
                                        type="button"
                                        onClick={() => setDifficulty(diff.value)}
                                        className={`w-full p-3 rounded-lg border-2 transition-all duration-200 text-left ${
                                            difficulty === diff.value
                                                ? `bg-gradient-to-br ${getDifficultyColor(diff.value)} shadow-lg border-opacity-100`
                                                : 'bg-slate-800/50 border-slate-600 hover:border-slate-500 hover:bg-slate-800/70'
                                        }`}
                                    >
                                        <div className={`font-semibold ${
                                            difficulty === diff.value ? 'text-white' : 'text-slate-300'
                                        }`}>
                                            {diff.label}
                                        </div>
                                        <div className={`text-xs ${
                                            difficulty === diff.value ? 'text-white/70' : 'text-slate-500'
                                        }`}>
                                            {diff.description}
                                        </div>
                                    </button>
                                ))}
                            </div>
                        )}
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
