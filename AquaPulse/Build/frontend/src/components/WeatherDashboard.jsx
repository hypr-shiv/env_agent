import React from 'react';
import {
  Wind,
  Compass,
  Waves,
  Thermometer,
  Eye,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Anchor,
  Navigation,
  Info
} from 'lucide-react';
import { BASELINE_WEATHER } from '../data/mockData';

export default function WeatherDashboard({ selectedLocation }) {
  const data = BASELINE_WEATHER;

  return (
    <div className="space-y-6">
      {/* Top Banner: Safe to Sail Matrix Status */}
      <div className="glass-panel rounded-2xl p-6 border border-emerald-500/30 bg-gradient-to-r from-emerald-950/40 via-ocean-900 to-ocean-850 shadow-xl">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-emerald-500/20 border border-emerald-400/40 flex items-center justify-center text-emerald-400 flex-shrink-0 shadow-lg shadow-emerald-500/10">
              <CheckCircle2 className="w-8 h-8 animate-beacon" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs uppercase font-extrabold tracking-wider bg-emerald-950 text-emerald-300 border border-emerald-700/60 px-2.5 py-0.5 rounded-full">
                  Safe-To-Sail Index
                </span>
                <span className="text-xs text-slate-400 flex items-center gap-1">
                  <Clock className="w-3 h-3" /> {data.timestamp}
                </span>
              </div>
              <h1 className="text-2xl font-extrabold text-white mt-1">
                Navigational Conditions: <span className="text-emerald-400">FAVORABLE (SAFE)</span>
              </h1>
              <p className="text-xs text-slate-300 mt-1 max-w-xl">
                Sea surface conditions along {selectedLocation} are calm to moderate. Permitted for all craft categories
                with standard safety equipment compliance.
              </p>
            </div>
          </div>

          <div className="bg-ocean-950/80 border border-ocean-700/80 rounded-xl px-4 py-2.5 text-right flex-shrink-0">
            <span className="text-[11px] text-slate-400">Monitored Coastline</span>
            <div className="text-base font-bold text-white">{selectedLocation} Bunder, Palghar</div>
          </div>
        </div>
      </div>

      {/* Primary Weather Telemetry Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Wind Speed */}
        <div className="glass-panel rounded-2xl p-4 border border-ocean-800 flex items-center gap-3.5">
          <div className="w-11 h-11 rounded-xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <Wind className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[11px] text-slate-400 font-medium">Wind Velocity</span>
            <div className="text-lg font-bold font-mono text-white">{data.wind_speed_knots} Knots</div>
            <span className="text-[10px] text-ocean-300">{data.wind_direction}</span>
          </div>
        </div>

        {/* Wave Height */}
        <div className="glass-panel rounded-2xl p-4 border border-ocean-800 flex items-center gap-3.5">
          <div className="w-11 h-11 rounded-xl bg-blue-500/15 border border-blue-500/30 flex items-center justify-center text-blue-400">
            <Waves className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[11px] text-slate-400 font-medium">Significant Wave Height</span>
            <div className="text-lg font-bold font-mono text-white">{data.wave_height_meters} Meters</div>
            <span className="text-[10px] text-emerald-400">Normal Swell</span>
          </div>
        </div>

        {/* Sea Surface Temp */}
        <div className="glass-panel rounded-2xl p-4 border border-ocean-800 flex items-center gap-3.5">
          <div className="w-11 h-11 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400">
            <Thermometer className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[11px] text-slate-400 font-medium">Sea Surface Temp</span>
            <div className="text-lg font-bold font-mono text-white">{data.sea_surface_temp_c} °C</div>
            <span className="text-[10px] text-slate-400">Thermal Front Active</span>
          </div>
        </div>

        {/* Visibility */}
        <div className="glass-panel rounded-2xl p-4 border border-ocean-800 flex items-center gap-3.5">
          <div className="w-11 h-11 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Eye className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[11px] text-slate-400 font-medium">Navigational Visibility</span>
            <div className="text-lg font-bold font-mono text-white">{data.visibility_km} km</div>
            <span className="text-[10px] text-emerald-400">Clear Horizon</span>
          </div>
        </div>
      </div>

      {/* Vessel Class Advisory & Tidal Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Vessel Advisory Breakdown (7 cols) */}
        <div className="lg:col-span-7 glass-panel rounded-2xl p-5 border border-ocean-800 space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-wider text-ocean-300 flex items-center gap-2">
            <Anchor className="w-4 h-4 text-cyan-400" />
            Palghar Multi-Vessel Category Sailing Matrix
          </h2>

          <div className="space-y-3">
            {Object.entries(data.vessel_advisories).map(([key, item]) => (
              <div
                key={key}
                className="bg-ocean-950/80 border border-ocean-800 rounded-xl p-3.5 flex items-center justify-between text-xs"
              >
                <div>
                  <div className="font-bold text-white text-sm">{item.name}</div>
                  <div className="text-[11px] text-slate-400 mt-0.5">{item.note}</div>
                </div>
                <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-700/60 font-bold text-[11px]">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  {item.status}
                </div>
              </div>
            ))}
          </div>

          <div className="p-3 bg-ocean-950/60 rounded-xl border border-ocean-800 text-[11px] text-slate-400 flex items-start gap-2">
            <Info className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
            <span>
              All motorized and mechanized crafts departing {selectedLocation} are legally required under MMFRA to carry
              Type-1 Life Jackets, distress flares, and functioning VHF marine radio on Channel 16.
            </span>
          </div>
        </div>

        {/* Tide Forecast Table (5 cols) */}
        <div className="lg:col-span-5 glass-panel rounded-2xl p-5 border border-ocean-800 space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-wider text-ocean-300 flex items-center gap-2">
            <Navigation className="w-4 h-4 text-cyan-400" />
            Palghar Coastal Tidal Prediction
          </h2>

          <div className="grid grid-cols-2 gap-3">
            <div className="bg-ocean-950/90 border border-cyan-800/40 rounded-xl p-3 text-center">
              <span className="text-[10px] text-slate-400 font-semibold uppercase">Next High Tide</span>
              <div className="text-xl font-bold font-mono text-cyan-300 mt-1">{data.tides.next_high_tide.time}</div>
              <span className="text-xs text-slate-300 font-mono">{data.tides.next_high_tide.height}</span>
            </div>

            <div className="bg-ocean-950/90 border border-ocean-800 rounded-xl p-3 text-center">
              <span className="text-[10px] text-slate-400 font-semibold uppercase">Next Low Tide</span>
              <div className="text-xl font-bold font-mono text-slate-200 mt-1">{data.tides.next_low_tide.time}</div>
              <span className="text-xs text-slate-400 font-mono">{data.tides.next_low_tide.height}</span>
            </div>
          </div>

          <div className="p-3.5 bg-cyan-950/40 border border-cyan-700/30 rounded-xl text-xs text-cyan-200 space-y-1">
            <div className="font-semibold text-cyan-300">Creek & Harbor Navigability:</div>
            <p className="text-[11px] text-slate-300 leading-relaxed">{data.tides.creek_navigability}</p>
          </div>

          <div className="text-[10px] text-slate-500 pt-1 border-t border-ocean-800">
            Source: {data.source}
          </div>
        </div>
      </div>
    </div>
  );
}

