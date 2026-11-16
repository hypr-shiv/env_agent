import React, { useState } from 'react';
import {
  Award,
  CheckCircle2,
  ExternalLink,
  Users,
  Building,
  HelpCircle,
  FileCheck
} from 'lucide-react';
import { BASELINE_GOVT_SCHEMES } from '../data/mockData';

export default function SchemesDashboard({ selectedLocation }) {
  const schemes = BASELINE_GOVT_SCHEMES;
  const [selectedCategory, setSelectedCategory] = useState('all');

  return (
    <div className="space-y-6">
      {/* Schemes Header */}
      <div className="glass-panel rounded-2xl p-6 border border-cyan-500/30 bg-gradient-to-r from-ocean-900 via-ocean-850 to-ocean-900 shadow-xl">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-cyan-500/20 border border-cyan-400/40 flex items-center justify-center text-cyan-400 flex-shrink-0 shadow-lg">
              <Award className="w-8 h-8" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs uppercase font-extrabold tracking-wider bg-cyan-950 text-cyan-300 border border-cyan-800 px-2.5 py-0.5 rounded-full">
                  Financial Empowerment
                </span>
                <span className="text-xs text-slate-400">Palghar District Fisheries Office</span>
              </div>
              <h1 className="text-2xl font-extrabold text-white mt-1">
                Government Fisheries Schemes & Subsidies (PMMSY / KCC)
              </h1>
              <p className="text-xs text-slate-300 mt-1 max-w-xl">
                Verified financial assistance, motorization grants, and 60% priority subsidies for women, SC, and ST
                fishermen across Palghar district.
              </p>
            </div>
          </div>

          <div className="bg-ocean-950/80 border border-cyan-700/60 rounded-xl p-3 text-right flex-shrink-0">
            <span className="text-[10px] text-slate-400 uppercase">Priority Women / SC / ST Subsidy</span>
            <div className="text-2xl font-bold font-mono text-emerald-400">Up to 60%</div>
            <span className="text-[10px] text-slate-300">General Category: 40%</span>
          </div>
        </div>
      </div>

      {/* Schemes Cards List */}
      <div className="space-y-4">
        {schemes.map((scheme) => (
          <div
            key={scheme.code}
            className="glass-panel glass-panel-hover rounded-2xl p-6 border border-ocean-800 space-y-4 shadow-lg"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-ocean-800 pb-3">
              <div>
                <span className="text-[10px] text-cyan-400 font-mono font-bold uppercase">{scheme.code}</span>
                <h3 className="text-lg font-bold text-white mt-0.5">{scheme.name}</h3>
                <span className="text-xs text-slate-400">{scheme.ministry}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-3 py-1 rounded-lg bg-emerald-950 text-emerald-300 border border-emerald-700/60 text-xs font-bold font-mono">
                  Women / ST: {scheme.subsidy_women_sc_st}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="bg-ocean-950/80 p-3.5 rounded-xl border border-ocean-800 space-y-1.5">
                <div className="font-semibold text-slate-300 flex items-center gap-1.5">
                  <Users className="w-4 h-4 text-cyan-400" /> Eligible Beneficiaries:
                </div>
                <p className="text-slate-300 leading-relaxed text-[11px]">{scheme.beneficiary_type}</p>
                <div className="pt-1 text-[11px] text-slate-400">
                  <span className="text-slate-300 font-medium">Requirements:</span> {scheme.key_requirements}
                </div>
              </div>

              <div className="bg-ocean-950/80 p-3.5 rounded-xl border border-ocean-800 space-y-1.5">
                <div className="font-semibold text-slate-300 flex items-center gap-1.5">
                  <Building className="w-4 h-4 text-emerald-400" /> General Category Subsidy:
                </div>
                <p className="text-emerald-300 font-mono font-bold text-sm">{scheme.subsidy_general}</p>
                <div className="pt-1 text-[11px] text-slate-400">
                  <span className="text-slate-300 font-medium">Application Portal / Office:</span>
                  <div className="text-cyan-300 truncate">{scheme.application_portal}</div>
                </div>
              </div>
            </div>

            <div className="pt-2 flex items-center justify-between text-xs border-t border-ocean-800">
              <span className="text-slate-400 text-[11px]">Assistance Available at Palghar Fisheries Cooperative</span>
              <a
                href={scheme.application_portal.startsWith('http') ? scheme.application_portal : '#'}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1 text-cyan-400 hover:text-cyan-300 font-semibold text-xs"
              >
                Apply Online / Guidelines <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

