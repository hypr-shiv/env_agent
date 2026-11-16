import React, { useState } from 'react';
import {
  FileText,
  AlertCircle,
  CheckCircle2,
  Clock,
  Send,
  Shield,
  MapPin,
  Ship,
  PhoneCall
} from 'lucide-react';
import { BASELINE_COMPLAINTS } from '../data/mockData';

export default function ComplaintDashboard({ selectedLocation }) {
  const [complaints, setComplaints] = useState(BASELINE_COMPLAINTS);
  const [category, setCategory] = useState('Illegal Night Trawling within 5 Nautical Miles');
  const [harbor, setHarbor] = useState(selectedLocation);
  const [vesselNumber, setVesselNumber] = useState('');
  const [description, setDescription] = useState('');
  const [submittedTicket, setSubmittedTicket] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!description.trim()) return;

    const newTicketId = `AQ-PLG-${new Date().getFullYear()}-${Math.floor(1000 + Math.random() * 9000)}`;
    const newComplaint = {
      ticket_id: newTicketId,
      category,
      location: `Offshore ${harbor}`,
      reported_at: 'Just Now',
      status: 'Received & Queued',
      timeline: [
        { step: 'Report Registered', time: 'Just Now', done: true },
        { step: 'Enforcement Wing Verification', time: 'Pending', done: false },
        { step: 'Coastal Patrol Boat Assigned', time: 'Pending', done: false },
        { step: 'Interception & Resolution', time: 'Pending', done: false }
      ],
      enforcement_cell: 'Maharashtra Department of Fisheries Enforcement Wing (Palghar Unit)'
    };

    setComplaints([newComplaint, ...complaints]);
    setSubmittedTicket(newTicketId);
    setDescription('');
    setVesselNumber('');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel rounded-2xl p-6 border border-rose-500/30 bg-gradient-to-r from-rose-950/30 via-ocean-900 to-ocean-850 shadow-xl">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-rose-500/20 border border-rose-400/40 flex items-center justify-center text-rose-400 flex-shrink-0 shadow-lg">
              <Shield className="w-8 h-8" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs uppercase font-extrabold tracking-wider bg-rose-950 text-rose-300 border border-rose-700/60 px-2.5 py-0.5 rounded-full">
                  Coastal Law Enforcement
                </span>
                <span className="text-xs text-slate-400">Maharashtra Marine Fishing Regulation Act (MMFRA)</span>
              </div>
              <h1 className="text-2xl font-extrabold text-white mt-1">
                Illegal Fishing & Coastal Grievance Redressal
              </h1>
              <p className="text-xs text-slate-300 mt-1 max-w-xl">
                File incident reports for illegal mechanised trawling in traditional zones (&lt;5 nm), bull trawling,
                high-intensity LED fishing, or net destruction off Palghar coast.
              </p>
            </div>
          </div>

          <div className="bg-ocean-950/80 border border-rose-700/60 rounded-xl p-3 text-right flex-shrink-0">
            <span className="text-[10px] text-slate-400 uppercase">Enforcement Control</span>
            <div className="text-sm font-bold text-rose-300">Fisheries Patrol Unit MH-04</div>
            <span className="text-[10px] text-slate-400">24x7 Marine Police Dispatch</span>
          </div>
        </div>
      </div>

      {/* Main Grid: Registration Form on Left, Active Tracking on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Registration Form (5 cols) */}
        <div className="lg:col-span-5 glass-panel rounded-2xl p-6 border border-ocean-800 space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <FileText className="w-4 h-4 text-cyan-400" />
            Register Incident Report
          </h2>

          {submittedTicket && (
            <div className="p-3.5 bg-emerald-950/60 border border-emerald-500/40 rounded-xl text-xs text-emerald-200 space-y-1">
              <div className="font-bold flex items-center gap-1.5 text-emerald-300">
                <CheckCircle2 className="w-4 h-4" /> Incident Successfully Logged!
              </div>
              <p className="text-[11px]">
                Your tracking ID is <span className="font-mono font-bold text-white">{submittedTicket}</span>. Forwarded to
                Maharashtra Fisheries Enforcement Wing.
              </p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3.5 text-xs">
            <div>
              <label className="block text-slate-300 font-semibold mb-1">Violation Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-ocean-950 border border-ocean-700 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-400"
              >
                <option>Illegal Night Trawling within 5 Nautical Miles</option>
                <option>Purse-Seine Net Operation in Territorial Waters</option>
                <option>Prohibited High-Power LED Light Fishing</option>
                <option>Destruction of Traditional Dol Net / Gillnet by Mechanized Craft</option>
                <option>Juvenile Fish Catching Below Minimum Legal Size (MLS)</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Landing Area / Coast</label>
                <input
                  type="text"
                  value={harbor}
                  onChange={(e) => setHarbor(e.target.value)}
                  placeholder="e.g. Satpati Bunder"
                  className="w-full bg-ocean-950 border border-ocean-700 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-400"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Offending Boat Reg No (If Seen)</label>
                <input
                  type="text"
                  value={vesselNumber}
                  onChange={(e) => setVesselNumber(e.target.value)}
                  placeholder="e.g. MH-04-MM-2219"
                  className="w-full bg-ocean-950 border border-ocean-700 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-400 font-mono"
                />
              </div>
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1">Incident Description & Distance from Shore</label>
              <textarea
                rows={3}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe estimated distance offshore, direction, time of sighting, and damage caused..."
                required
                className="w-full bg-ocean-950 border border-ocean-700 rounded-xl p-3 text-slate-200 focus:outline-none focus:border-cyan-400"
              />
            </div>

            <button
              type="submit"
              className="w-full py-2.5 px-4 rounded-xl font-bold bg-gradient-to-r from-rose-500 to-red-600 hover:from-rose-400 hover:to-red-500 text-white shadow-lg shadow-rose-900/30 transition-all flex items-center justify-center gap-2"
            >
              <Send className="w-4 h-4" />
              Dispatch Incident Report
            </button>
          </form>
        </div>

        {/* Incident Tracking Timeline (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          <h2 className="text-sm font-bold text-white flex items-center justify-between">
            <span>Recent Grievance Tracking Timeline</span>
            <span className="text-xs text-slate-400 font-normal">Active Palghar Cases</span>
          </h2>

          <div className="space-y-4">
            {complaints.map((c) => (
              <div
                key={c.ticket_id}
                className="glass-panel rounded-2xl p-5 border border-ocean-800 space-y-3.5 shadow-md"
              >
                <div className="flex items-center justify-between border-b border-ocean-800 pb-2.5">
                  <div>
                    <span className="text-xs font-mono font-bold text-cyan-300">{c.ticket_id}</span>
                    <h3 className="text-sm font-bold text-white mt-0.5">{c.category}</h3>
                  </div>
                  <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-ocean-950 text-cyan-300 border border-cyan-800">
                    {c.status}
                  </span>
                </div>

                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-cyan-400" /> {c.location}
                  </span>
                  <span className="flex items-center gap-1 font-mono text-[11px]">
                    <Clock className="w-3.5 h-3.5" /> {c.reported_at}
                  </span>
                </div>

                {/* Progress Timeline */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 text-[11px]">
                  {c.timeline.map((step, idx) => (
                    <div
                      key={idx}
                      className={`p-2 rounded-lg border ${
                        step.done
                          ? 'bg-emerald-950/60 border-emerald-500/40 text-emerald-200'
                          : 'bg-ocean-950/60 border-ocean-800 text-slate-500'
                      }`}
                    >
                      <div className="font-semibold">{step.step}</div>
                      <div className="text-[10px] text-slate-400 mt-0.5">{step.time}</div>
                    </div>
                  ))}
                </div>

                <div className="text-[10px] text-slate-400 pt-1 border-t border-ocean-800 flex items-center justify-between">
                  <span>Enforcement Wing: {c.enforcement_cell}</span>
                  <span className="text-cyan-400 font-semibold">MMFRA Sec-4 Violation</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

