import React from 'react';
import {
  Droplets,
  Activity,
  Compass,
  CheckCircle2,
  Calendar,
  Layers,
  Sparkles,
  Info
} from 'lucide-react';
import { BASELINE_ENVIRONMENT } from '../data/mockData';

export default function EnvironmentDashboard({ selectedLocation }) {
  const env = BASELINE_ENVIRONMENT;

  return (
    <div className="space-y-6">
      {/* Environment Header */}
      <div className="glass-panel rounded-2xl p-6 border border-cyan-500/30 bg-gradient-to-r from-ocean-900 via-ocean-850 to-ocean-900 shadow-xl">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-cyan-500/20 border border-cyan-400/40 flex items-center justify-center text-cyan-400 flex-shrink-0 shadow-lg">
              <Droplets className="w-8 h-8 animate-beacon" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs uppercase font-extrabold tracking-wider bg-cyan-950 text-cyan-300 border border-cyan-800 px-2.5 py-0.5 rounded-full">
                  Marine Environmental Telemetry
                </span>
                <span className="text-xs text-slate-400">MPCB Coastal Station Bulletin</span>
              </div>
              <h1 className="text-2xl font-extrabold text-white mt-1">
                Water Quality Index & Potential Fishing Zone (PFZ)
              </h1>
              <p className="text-xs text-slate-300 mt-1 max-w-xl">
                Real-time satellite ocean color boundaries and benthic water quality monitoring along Palghar offshore
                waters.
              </p>
            </div>
          </div>

          <div className="bg-ocean-950/80 border border-cyan-700/60 rounded-xl p-3 text-right flex-shrink-0">
            <span className="text-[10px] text-slate-400 uppercase">Coastal Water Quality Index</span>
            <div className="text-2xl font-bold font-mono text-cyan-300">{env.wqi} / 100</div>
            <span className="text-[10px] text-emerald-400 font-semibold">{env.wqi_status}</span>
          </div>
        </div>
      </div>

      {/* Parameter Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Dissolved Oxygen */}
        <div className="glass-panel rounded-2xl p-4 border border-ocean-800 space-y-1">
          <span className="text-[11px] text-slate-400">Dissolved Oxygen (DO)</span>
          <div className="text-xl font-bold font-mono text-emerald-400">{env.dissolved_oxygen_mg_l} mg/L</div>
          <span className="text-[10px] text-slate-400">Optimal for pelagic marine fauna</span>
        </div>

        {/* pH Level */}
        <div className="glass-panel rounded-2xl p-4 border border-ocean-800 space-y-1">
          <span className="text-[11px] text-slate-400">Seawater pH</span>
          <div className="text-xl font-bold font-mono text-cyan-300">{env.ph_level}</div>
          <span className="text-[10px] text-emerald-400">Standard Marine Alkaline Range</span>
        </div>

        {/* Chlorophyll-a */}
        <div className="glass-panel rounded-2xl p-4 border border-ocean-800 space-y-1">
          <span className="text-[11px] text-slate-400">Chlorophyll-a Biomass</span>
          <div className="text-xl font-bold font-mono text-amber-300">{env.chlorophyll_a_mg_m3} mg/m³</div>
          <span className="text-[10px] text-cyan-400">High Phytoplankton Bloom</span>
        </div>

        {/* Salinity */}
        <div className="glass-panel rounded-2xl p-4 border border-ocean-800 space-y-1">
          <span className="text-[11px] text-slate-400">Salinity</span>
          <div className="text-xl font-bold font-mono text-slate-200">{env.salinity_ppt} ppt</div>
          <span className="text-[10px] text-slate-400">Normal Coastal Oceanic Range</span>
        </div>
      </div>

      {/* PFZ Potential Fishing Zone Card */}
      <div className="glass-panel rounded-2xl p-5 border border-cyan-500/30 bg-gradient-to-br from-cyan-950/30 to-ocean-900/80 space-y-3">
        <div className="flex items-center justify-between border-b border-ocean-800 pb-3">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-cyan-400" />
            <h3 className="text-sm font-bold text-white">INCOIS Potential Fishing Zone (PFZ) Oceanic Front</h3>
          </div>
          <span className="text-xs bg-cyan-950 text-cyan-300 border border-cyan-800 px-2.5 py-0.5 rounded-full font-semibold">
            Active Satellite Front
          </span>
        </div>

        <p className="text-xs sm:text-sm text-slate-200 leading-relaxed">{env.pfz_status}</p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 text-xs">
          <div className="bg-ocean-950/80 p-3 rounded-xl border border-ocean-800">
            <span className="text-slate-400 text-[10px] uppercase font-semibold">Recommended Bearing</span>
            <div className="font-bold text-cyan-300 mt-0.5">265° WSW from Satpati Harbor</div>
          </div>

          <div className="bg-ocean-950/80 p-3 rounded-xl border border-ocean-800">
            <span className="text-slate-400 text-[10px] uppercase font-semibold">Operating Depth</span>
            <div className="font-bold text-slate-200 mt-0.5">28 to 36 meters water column</div>
          </div>

          <div className="bg-ocean-950/80 p-3 rounded-xl border border-ocean-800">
            <span className="text-slate-400 text-[10px] uppercase font-semibold">Target Commercial Species</span>
            <div className="font-bold text-emerald-300 mt-0.5">Silver Pomfret, Indian Mackerel</div>
          </div>
        </div>

        <div className="text-[10px] text-slate-400 pt-2 border-t border-ocean-800">
          Source: {env.source} (Sampled: {env.sampling_date})
        </div>
      </div>
    </div>
  );
}

