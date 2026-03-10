import React from 'react'

const About = ({ onBack }) => {
  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-6">
      <div className="w-full max-w-2xl p-8 md:p-10 rounded-3xl border-2 border-cyan-500/30 bg-slate-900/60 backdrop-blur-xl shadow-2xl">
        <div className="flex items-start justify-between gap-4 mb-6">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-blue-300">
              About K-Map GamEEE
            </h1>
            <p className="text-slate-400 mt-2">
              Git gud at solving donuts!
            </p>
          </div>
          <button
            type="button"
            onClick={onBack}
            className="px-4 py-2 rounded-lg border border-slate-500 text-slate-200 hover:bg-slate-800/60 transition"
          >
            Back
          </button>
        </div>

        <div className="space-y-4 text-slate-300">
          <div>
            <div className="text-sm uppercase tracking-wide text-cyan-300">Credits</div>
            <ul className="mt-2 space-y-1">
              <li>Adelson Chua — Complain Here</li>
              <li>Lawrence Quizon — If above not available</li>
              <li>Francois Abedejos — Actually complain here</li>
              <li>Shaira Rodriguez — Blame if u hate your 143 lab</li>
              <li>Isaac Sy — Just kidding, complain here</li>
            </ul>
          </div>

          <div>
            <div className="text-sm uppercase tracking-wide text-cyan-300">Purpose</div>
            <p className="mt-2">
              While K-map solvers are already present online, question generators are hard to find. K-map GamEEE allows EEE students to practice their Boolean minimization skills while flexing their knowledge in our game leaderboards!
            </p>
          </div>

          <div className="text-sm text-slate-400">
           Please Provide Feedback!
          </div>
        </div>
      </div>
    </div>
  )
}

export default About
