import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import SidebarNav from './components/SidebarNav';
import ChatInterface from './components/ChatInterface';
import FishVisionDashboard from './components/FishVisionDashboard';
import WeatherDashboard from './components/WeatherDashboard';
import DisasterDashboard from './components/DisasterDashboard';
import MarketDashboard from './components/MarketDashboard';
import EnvironmentDashboard from './components/EnvironmentDashboard';
import SchemesDashboard from './components/SchemesDashboard';
import ComplaintDashboard from './components/ComplaintDashboard';
import { checkBackendHealth } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [selectedLocation, setSelectedLocation] = useState('Satpati');
  const [language, setLanguage] = useState('en');
  const [isBackendOnline, setIsBackendOnline] = useState(false);

  useEffect(() => {
    async function verifyHealth() {
      const health = await checkBackendHealth();
      setIsBackendOnline(health?.status === 'healthy');
    }
    verifyHealth();
    const timer = setInterval(verifyHealth, 15000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-ocean-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-white">
      {/* Top Ocean Navigation */}
      <Navbar
        selectedLocation={selectedLocation}
        onSelectLocation={setSelectedLocation}
        language={language}
        onSelectLanguage={setLanguage}
        isBackendOnline={isBackendOnline}
      />

      {/* Main Mission Control Layout */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 flex flex-col lg:flex-row gap-6">
        {/* Module Selector Sidebar */}
        <SidebarNav
          activeTab={activeTab}
          onSelectTab={setActiveTab}
          language={language}
        />

        {/* Dynamic Operational Pane */}
        <section className="flex-1 min-w-0">
          {activeTab === 'chat' && (
            <ChatInterface selectedLocation={selectedLocation} language={language} />
          )}

          {activeTab === 'vision' && (
            <FishVisionDashboard selectedLocation={selectedLocation} />
          )}

          {activeTab === 'weather' && (
            <WeatherDashboard selectedLocation={selectedLocation} />
          )}

          {activeTab === 'disaster' && (
            <DisasterDashboard selectedLocation={selectedLocation} />
          )}

          {activeTab === 'market' && (
            <MarketDashboard selectedLocation={selectedLocation} />
          )}

          {activeTab === 'environment' && (
            <EnvironmentDashboard selectedLocation={selectedLocation} />
          )}

          {activeTab === 'schemes' && (
            <SchemesDashboard selectedLocation={selectedLocation} />
          )}

          {activeTab === 'complaint' && (
            <ComplaintDashboard selectedLocation={selectedLocation} />
          )}
        </section>
      </main>

      {/* Modern Coastal Footer */}
      <footer className="border-t border-ocean-800/80 glass-panel py-6 px-4 mt-8 text-center text-xs text-slate-400">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-200">AquaPulse</span>
            <span>• Palghar Coastal Mission Control</span>
          </div>

          <div className="flex items-center gap-4 text-[11px] text-ocean-300">
            <span>IMD Mumbai</span>
            <span>•</span>
            <span>INCOIS Hyderabad</span>
            <span>•</span>
            <span>ICAR-CMFRI</span>
            <span>•</span>
            <span>MPCB</span>
            <span>•</span>
            <span>Maharashtra Fisheries</span>
          </div>

          <div className="text-[11px] text-slate-400">
            Designed for Fishermen of Satpati, Dahanu, Arnala, Kelve & Vasai
          </div>
        </div>
      </footer>
    </div>
  );
}

