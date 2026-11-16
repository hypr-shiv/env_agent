import React from 'react';
import {
  ShieldAlert,
  AlertTriangle,
  Radio,
  PhoneCall,
  MapPin,
  Clock,
  CheckSquare,
  ExternalLink
} from 'lucide-react';
import { BASELINE_DISASTER_ALERTS } from '../data/mockData';

export default function DisasterDashboard({ selectedLocation }) {
  const alerts = BASELINE_DISASTER_ALERTS;

  return (
    <div className="space-y-6">
      {/* Disaster Header */}
      <div className="glass-panel rounded-2xl p-6 border border-amber-500/30 bg-gradient-to-r from-amber-950/40 via-ocean-900 to-ocean-850 shadow-xl">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-amber-500/20 border border-amber-400/40 flex items-center justify-center text-amber-400 flex-shrink-0 shadow-lg">
              <ShieldAlert className="w-8 h-8 animate-beacon" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs uppercase font-extrabold tracking-wider bg-amber-950 text-amber-300 border border-amber-700/60 px-2.5 py-0.5 rounded-full">
                  Coastal Safety Monitor
                </span>
                <span className="text-xs text-slate-400">Palghar District Emergency Network</span>
              </div>
              <h1 className="text-2xl font-extrabold text-white mt-1">
                Active Maritime Alerts & Severe Weather Notices
              </h1>
              <p className="text-xs text-slate-300 mt-1 max-w-xl">
                Continuous surveillance for cyclone tracks, tsunami warnings, and high swell wave surges across North
                Maharashtra coastline.
              </p>
            </div>
          </div>

          <div className="bg-rose-950/80 border border-rose-500/40 rounded-xl p-3 text-right flex-shrink-0">
            <span className="text-[10px] text-rose-300 uppercase font-bold">24x7 Emergency Control Room</span>
            <div className="text-lg font-mono font-extrabold text-rose-200">1077 (District Cell)</div>
          </div>
        </div>
      </div>

      {/* Active Alerts List */}
      <div className="space-y-4">
        {alerts.map((alert) => (
          <div
            key={alert.id}
            className="glass-panel rounded-2xl p-5 border border-amber-500/40 bg-gradient-to-br from-amber-950/20 to-ocean-900 shadow-lg space-y-3"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-ocean-800 pb-3">
              <div className="flex items-center gap-2.5">
                <span className="px-2.5 py-1 rounded-md text-xs font-bold uppercase bg-amber-500 text-ocean-950 shadow">
                  {alert.severity} Alert
                </span>
                <h3 className="text-base font-bold text-white">{alert.headline}</h3>
              </div>
              <div className="flex items-center gap-3 text-xs text-slate-400">
                <span className="flex items-center gap-1 font-mono text-[11px]">
                  <Clock className="w-3.5 h-3.5 text-amber-400" /> Issued: {alert.issued_at}
                </span>
              </div>
            </div>

            <p className="text-xs sm:text-sm text-slate-200 leading-relaxed">{alert.description}</p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 text-xs">
              <div className="bg-ocean-950/70 p-2.5 rounded-xl border border-ocean-800 flex items-center gap-2">
                <MapPin className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                <div>
                  <span className="text-slate-400">Affected Harbors:</span>
                  <div className="font-semibold text-slate-200">{alert.affected_locations.join(', ')}</div>
                </div>
              </div>

              <div className="bg-ocean-950/70 p-2.5 rounded-xl border border-ocean-800 flex items-center gap-2">
                <Radio className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <div>
                  <span className="text-slate-400">Validity Period:</span>
                  <div className="font-semibold text-slate-200 font-mono text-[11px]">Until {alert.valid_until}</div>
                </div>
              </div>
            </div>

            <div className="text-[11px] text-ocean-400 pt-1 flex items-center justify-between border-t border-ocean-800/60">
              <span>Issuing Authority: {alert.source}</span>
              <span className="text-emerald-400 font-semibold flex items-center gap-1">
                Emergency Frequency: VHF Ch-16
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Safety Protocol Checklist for Fishermen */}
      <div className="glass-panel rounded-2xl p-5 border border-ocean-800 space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-ocean-300 flex items-center gap-2">
          <CheckSquare className="w-4 h-4 text-cyan-400" />
          Mandatory Pre-Sailing Safety Checklist for Palghar Fishermen
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div className="p-3 bg-ocean-950/80 rounded-xl border border-ocean-800 space-y-1">
            <div className="font-bold text-white">1. Vessel Communication</div>
            <p className="text-slate-400 text-[11px]">
              Inspect VHF Marine Radio on Ch-16 and ensure Distress Alert Transmitter (DAT) is charged.
            </p>
          </div>

          <div className="p-3 bg-ocean-950/80 rounded-xl border border-ocean-800 space-y-1">
            <div className="font-bold text-white">2. Life Saving Appliances</div>
            <p className="text-slate-400 text-[11px]">
              Minimum 1 ISI-marked Type-1 Life Jacket per crew member and 2 orange smoke distress signals.
            </p>
          </div>

          <div className="p-3 bg-ocean-950/80 rounded-xl border border-ocean-800 space-y-1">
            <div className="font-bold text-white">3. Harbor Manifest</div>
            <p className="text-slate-400 text-[11px]">
              Log vessel departure and expected return time with Satpati or Dahanu cooperative society token office.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

