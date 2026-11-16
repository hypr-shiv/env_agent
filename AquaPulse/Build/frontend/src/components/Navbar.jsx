import React from 'react';
import { Waves, MapPin, Globe, ShieldCheck, AlertCircle } from 'lucide-react';
import { PALGHAR_LOCATIONS } from '../data/mockData';

export default function Navbar({ selectedLocation, onSelectLocation, language, onSelectLanguage, isBackendOnline }) {
  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-ocean-800/80 px-4 lg:px-8 py-3">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
        {/* Brand identity */}
        <div className="flex items-center gap-3 w-full sm:w-auto justify-between sm:justify-start">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 border border-cyan-400/30">
              <Waves className="w-6 h-6 text-white animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold tracking-tight text-white bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-sky-300 to-white">
                  AquaPulse
                </span>
                <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-700/50">
                  Palghar AI
                </span>
              </div>
              <p className="text-xs text-ocean-300 hidden sm:block">Smart Fisheries & Coastal Safety System</p>
            </div>
          </div>

          {/* Mobile status indicator */}
          <div className="sm:hidden flex items-center gap-1.5 text-xs">
            <span className={`w-2 h-2 rounded-full ${isBackendOnline ? 'bg-emerald-400 animate-beacon' : 'bg-cyan-400'}`}></span>
            <span className="text-slate-300 text-[11px]">{isBackendOnline ? 'Live AI' : 'Verified Data'}</span>
          </div>
        </div>

        {/* Global Controls: Location selector, Language, Status */}
        <div className="flex items-center gap-3 w-full sm:w-auto justify-end flex-wrap">
          {/* Location Selector */}
          <div className="flex items-center gap-1.5 bg-ocean-900/90 border border-ocean-700/70 rounded-lg px-2.5 py-1.5 text-xs shadow-inner">
            <MapPin className="w-3.5 h-3.5 text-cyan-400" />
            <select
              value={selectedLocation}
              onChange={(e) => onSelectLocation(e.target.value)}
              className="bg-transparent text-slate-200 font-medium focus:outline-none cursor-pointer pr-1"
            >
              {PALGHAR_LOCATIONS.map((loc) => (
                <option key={loc.id} value={loc.name} className="bg-ocean-900 text-slate-100">
                  {loc.name} ({loc.marathi})
                </option>
              ))}
            </select>
          </div>

          {/* Language Switcher */}
          <div className="flex items-center bg-ocean-900/90 border border-ocean-700/70 rounded-lg p-0.5 text-xs">
            <button
              onClick={() => onSelectLanguage('en')}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                language === 'en' ? 'bg-cyan-500 text-ocean-950 font-bold shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              EN
            </button>
            <button
              onClick={() => onSelectLanguage('hi')}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                language === 'hi' ? 'bg-cyan-500 text-ocean-950 font-bold shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              हिंदी
            </button>
            <button
              onClick={() => onSelectLanguage('mr')}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                language === 'mr' ? 'bg-cyan-500 text-ocean-950 font-bold shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              मराठी
            </button>
          </div>

          {/* Desktop Status Badge */}
          <div className="hidden sm:flex items-center gap-2 bg-ocean-900/90 border border-ocean-700/70 rounded-lg px-3 py-1.5 text-xs">
            <span className={`w-2 h-2 rounded-full ${isBackendOnline ? 'bg-emerald-400 animate-beacon' : 'bg-cyan-400'}`}></span>
            <span className="font-medium text-slate-200">
              {isBackendOnline ? 'FastAPI Connected' : 'Palghar Baseline'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}

