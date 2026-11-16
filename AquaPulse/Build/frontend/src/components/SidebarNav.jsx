import React from 'react';
import {
  MessageSquare,
  ScanEye,
  CloudSun,
  ShieldAlert,
  TrendingUp,
  Droplets,
  Award,
  FileText,
  PhoneCall
} from 'lucide-react';

export const NAV_ITEMS = [
  { id: 'chat', label: 'AI Coastal Assistant', marathi: 'एआय सहाय्यक', icon: MessageSquare, badge: 'Tri-Lingual' },
  { id: 'vision', label: 'Fish Species Vision', marathi: 'मासे ओळख (व्हिजन)', icon: ScanEye, badge: 'MobileNet + Gemma' },
  { id: 'weather', label: 'Weather & Tides', marathi: 'हवामान आणि भरती', icon: CloudSun, badge: 'Safe-to-Sail' },
  { id: 'disaster', label: 'Safety & Disaster', marathi: 'आपत्ती चेतावणी', icon: ShieldAlert, badge: 'Alerts' },
  { id: 'market', label: 'Mandi Auction Rates', marathi: 'बाजार भाव', icon: TrendingUp, badge: 'Satpati / Dahanu' },
  { id: 'environment', label: 'Coastal Ecology', marathi: 'पाण्याची गुणवत्ता', icon: Droplets, badge: 'WQI 78' },
  { id: 'schemes', label: 'Govt Schemes', marathi: 'सरकारी योजना', icon: Award, badge: 'PMMSY 60%' },
  { id: 'complaint', label: 'Complaint Grievance', marathi: 'तक्रार निवारण', icon: FileText, badge: 'MMFRA' }
];

export default function SidebarNav({ activeTab, onSelectTab, language }) {
  return (
    <aside className="w-full lg:w-72 flex-shrink-0 flex flex-col gap-4">
      {/* Navigation Card */}
      <div className="glass-panel rounded-2xl p-3 shadow-xl">
        <div className="px-3 py-2 text-[11px] font-semibold uppercase tracking-wider text-ocean-300 flex items-center justify-between">
          <span>Mission Modules</span>
          <span className="text-[10px] bg-ocean-800 px-2 py-0.5 rounded text-cyan-300">8 Modules</span>
        </div>

        <nav className="space-y-1 mt-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-left text-xs sm:text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-600/30 to-blue-600/20 text-cyan-300 border border-cyan-500/40 shadow-md shadow-cyan-950/50'
                    : 'text-slate-300 hover:bg-ocean-800/60 hover:text-white'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                  <div>
                    <div className="font-semibold">{item.label}</div>
                    {language !== 'en' && (
                      <div className="text-[11px] text-ocean-300">{item.marathi}</div>
                    )}
                  </div>
                </div>

                {item.badge && (
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                      isActive
                        ? 'bg-cyan-400/20 text-cyan-200 border border-cyan-400/30'
                        : 'bg-ocean-900 text-slate-400'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Emergency Distress Assistance Card */}
      <div className="glass-panel rounded-2xl p-4 border border-rose-500/30 bg-gradient-to-br from-rose-950/40 to-ocean-900/80 shadow-lg">
        <div className="flex items-center gap-2.5 text-rose-400 mb-2">
          <PhoneCall className="w-4 h-4 animate-bounce" />
          <span className="text-xs font-bold uppercase tracking-wider">Palghar Coastal SOS</span>
        </div>
        <p className="text-xs text-slate-300 mb-3 leading-relaxed">
          In case of sea emergency or engine failure off Satpati/Dahanu, contact Palghar District Disaster Cell:
        </p>
        <div className="flex items-center justify-between bg-rose-950/80 border border-rose-500/40 rounded-xl px-3 py-2 text-rose-200">
          <span className="text-xs font-semibold">Toll-Free Helpline:</span>
          <span className="text-sm font-mono font-bold tracking-wider text-rose-300">1077 / 112</span>
        </div>
      </div>
    </aside>
  );
}

