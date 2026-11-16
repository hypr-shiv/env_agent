import React, { useState } from 'react';
import {
  TrendingUp,
  DollarSign,
  Calendar,
  Building2,
  Search,
  Filter,
  ArrowUpRight,
  ShieldCheck,
  MapPin
} from 'lucide-react';
import { BASELINE_MARKET_PRICES } from '../data/mockData';

export default function MarketDashboard({ selectedLocation }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMarket, setSelectedMarket] = useState('All');

  const markets = ['All', 'Satpati', 'Dahanu', 'Arnala'];

  const filteredPrices = BASELINE_MARKET_PRICES.filter((p) => {
    const matchesSearch =
      p.species_english.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.species_local.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesMarket =
      selectedMarket === 'All' || p.market_name.toLowerCase().includes(selectedMarket.toLowerCase());
    return matchesSearch && matchesMarket;
  });

  return (
    <div className="space-y-6">
      {/* Market Header */}
      <div className="glass-panel rounded-2xl p-6 border border-amber-500/30 bg-gradient-to-r from-amber-950/30 via-ocean-900 to-ocean-850 shadow-xl">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="text-xs uppercase font-extrabold tracking-wider bg-amber-950 text-amber-300 border border-amber-700/60 px-2.5 py-0.5 rounded-full">
                Mandi Auction Desk
              </span>
              <span className="text-xs text-slate-400">Cooperative Society Verified Rates</span>
            </div>
            <h1 className="text-2xl font-extrabold text-white">
              Daily Landing Center Wholesale Rates (Palghar District)
            </h1>
            <p className="text-xs text-slate-300 mt-1 max-w-xl">
              Transparent morning open outcry and electronic auction records from Satpati Sarvodaya, Dahanu Mandi, and
              Arnala Bunder. Free of unrecorded middlemen deductions.
            </p>
          </div>

          <div className="flex items-center gap-2 bg-ocean-950/80 border border-ocean-700 rounded-xl px-4 py-2.5 flex-shrink-0 text-xs">
            <Calendar className="w-4 h-4 text-amber-400" />
            <div>
              <div className="text-[10px] text-slate-400">Verified Auction Date</div>
              <div className="font-bold text-slate-200">06 Nov 2026 (Live Mandi)</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-panel rounded-2xl p-4 border border-ocean-800 flex flex-col sm:flex-row items-center justify-between gap-3">
        {/* Search Input */}
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search species (Pomfret, Bombil, Bangda)..."
            className="w-full bg-ocean-950 border border-ocean-700 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-400"
          />
        </div>

        {/* Mandi Filter Pills */}
        <div className="flex items-center gap-1.5 w-full sm:w-auto overflow-x-auto text-xs">
          <span className="text-slate-400 text-[11px] mr-1 flex items-center gap-1">
            <Filter className="w-3 h-3" /> Mandi:
          </span>
          {markets.map((m) => (
            <button
              key={m}
              onClick={() => setSelectedMarket(m)}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                selectedMarket === m
                  ? 'bg-amber-500 text-ocean-950 font-bold shadow'
                  : 'bg-ocean-900 text-slate-400 hover:text-slate-200'
              }`}
            >
              {m}
            </button>
          ))}
        </div>
      </div>

      {/* Price Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredPrices.map((item) => (
          <div
            key={item.id}
            className="glass-panel glass-panel-hover rounded-2xl p-5 border border-ocean-800 space-y-3"
          >
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] text-ocean-300 font-semibold uppercase">{item.market_name}</span>
                <h3 className="text-lg font-bold text-white mt-0.5">{item.species_english}</h3>
                <span className="text-xs font-semibold text-amber-300">{item.species_local}</span>
              </div>
              <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                {item.trend}
              </span>
            </div>

            <div className="p-3 bg-ocean-950/80 rounded-xl border border-ocean-800 flex items-baseline justify-between">
              <div>
                <span className="text-[10px] text-slate-400">Modal Auction Rate</span>
                <div className="text-2xl font-bold font-mono text-amber-300">₹{item.modal_price}</div>
              </div>
              <div className="text-right">
                <span className="text-[10px] text-slate-400">Range (Min - Max)</span>
                <div className="text-xs font-mono text-slate-300 mt-1">₹{item.price_min} - ₹{item.price_max}/kg</div>
              </div>
            </div>

            <div className="text-[10px] text-slate-400 flex items-center justify-between pt-1 border-t border-ocean-800/80">
              <span className="truncate max-w-[200px]">Source: {item.source}</span>
              <span className="text-cyan-400 font-semibold">{item.date}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

