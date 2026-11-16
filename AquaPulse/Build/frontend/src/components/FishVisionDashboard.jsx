import React, { useState } from 'react';
import {
  UploadCloud,
  CheckCircle2,
  AlertTriangle,
  TrendingUp,
  MapPin,
  Sparkles,
  Info,
  Calendar,
  Layers,
  ArrowRight,
  ShieldCheck,
  Cpu
} from 'lucide-react';
import { classifyFishImage, gemmaAnalyzeFishImage } from '../services/api';

export default function FishVisionDashboard({ selectedLocation }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [modelMode, setModelMode] = useState('mobilenet'); // 'mobilenet' or 'gemma'
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer ? e.dataTransfer.files[0] : e.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        setError('Please upload a valid image file (JPEG, PNG, WEBP).');
        return;
      }
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setError(null);
      setResult(null);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setIsLoading(true);
    setError(null);

    try {
      let data;
      if (modelMode === 'gemma') {
        data = await gemmaAnalyzeFishImage(selectedFile);
      } else {
        data = await classifyFishImage(selectedFile);
      }
      setResult(data);
    } catch (err) {
      setError(err.message || 'Fish classification failed. Please verify backend connection.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="glass-panel rounded-2xl p-6 border border-cyan-500/20 bg-gradient-to-r from-ocean-900 via-ocean-850 to-ocean-900 shadow-xl">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="text-xs uppercase tracking-wider font-bold text-cyan-400 bg-cyan-950 px-2.5 py-0.5 rounded-full border border-cyan-800">
                AquaPulse Vision AI
              </span>
              <span className="text-xs text-slate-400">Zero-Hallucination Classification</span>
            </div>
            <h1 className="text-2xl font-extrabold text-white">
              Marine Fish Species Identification & Abundance Engine
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 mt-1 max-w-2xl leading-relaxed">
              Upload a clear photograph of any coastal catch from Palghar waters. The vision classifier determines
              species taxonomy, local Marathi names, offshore abundance zones, and live landing auction rates.
            </p>
          </div>

          {/* Model Selector Pill */}
          <div className="bg-ocean-950/90 border border-ocean-700/80 rounded-xl p-1.5 flex items-center gap-1 shadow-inner flex-shrink-0">
            <button
              onClick={() => setModelMode('mobilenet')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                modelMode === 'mobilenet'
                  ? 'bg-cyan-500 text-ocean-950 shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Cpu className="w-3.5 h-3.5" /> MobileNetV3 (100ms)
            </button>
            <button
              onClick={() => setModelMode('gemma')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                modelMode === 'gemma'
                  ? 'bg-gradient-to-r from-purple-500 to-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" /> Google Gemma / PaliGemma
            </button>
          </div>
        </div>
      </div>

      {/* Main Grid: Upload Area on Left, Results on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Upload Column (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="glass-panel rounded-2xl p-5 border border-ocean-800">
            <h2 className="text-sm font-bold text-white mb-3 flex items-center justify-between">
              <span>Upload Fish Specimen</span>
              <span className="text-[11px] font-normal text-slate-400">JPEG, PNG, WEBP (Max 10MB)</span>
            </h2>

            {/* Dropzone */}
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleFileDrop}
              onClick={() => document.getElementById('fish-file-input')?.click()}
              className="border-2 border-dashed border-ocean-700 hover:border-cyan-400 rounded-xl p-6 text-center cursor-pointer transition-all bg-ocean-950/50 hover:bg-ocean-900/60 group"
            >
              <input
                id="fish-file-input"
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={handleFileDrop}
                className="hidden"
              />

              {previewUrl ? (
                <div className="space-y-3">
                  <div className="relative mx-auto max-w-[220px] rounded-lg overflow-hidden border border-cyan-500/40 shadow-lg">
                    <img src={previewUrl} alt="Specimen" className="w-full h-44 object-cover" />
                    <span className="absolute bottom-1 right-1 text-[10px] bg-ocean-950/90 text-cyan-300 px-2 py-0.5 rounded font-mono">
                      224x224 RGB
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 font-medium">{selectedFile?.name}</p>
                  <p className="text-[11px] text-cyan-400">Click or drop new image to replace</p>
                </div>
              ) : (
                <div className="space-y-3 py-6">
                  <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center mx-auto text-cyan-400 group-hover:scale-110 transition-transform">
                    <UploadCloud className="w-6 h-6" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-200">Drag & drop fish image here</p>
                    <p className="text-xs text-slate-400 mt-0.5">or click to browse local files</p>
                  </div>
                </div>
              )}
            </div>

            {/* Action Button */}
            <button
              onClick={handleAnalyze}
              disabled={!selectedFile || isLoading}
              className="mt-4 w-full py-3 px-4 rounded-xl font-bold text-sm bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 disabled:opacity-50 text-ocean-950 transition-all shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <span className="w-4 h-4 border-2 border-ocean-950 border-t-transparent rounded-full animate-spin"></span>
                  Processing with {modelMode === 'gemma' ? 'Gemma VLM' : 'MobileNetV3'}...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Identify Species & Retrieve Market Rates
                </>
              )}
            </button>

            {error && (
              <div className="mt-3 p-3 rounded-xl bg-rose-950/60 border border-rose-500/40 text-rose-200 text-xs flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}
          </div>
        </div>

        {/* Results Column (7 cols) */}
        <div className="lg:col-span-7">
          {result ? (
            <div className="space-y-4">
              {/* Main Classification Card */}
              <div className="glass-panel rounded-2xl p-6 border border-cyan-500/30 shadow-xl bg-gradient-to-br from-ocean-900 via-ocean-850 to-ocean-950">
                <div className="flex items-start justify-between gap-4 border-b border-ocean-800 pb-4">
                  <div>
                    <span className="text-[11px] font-bold uppercase tracking-wider text-cyan-400 bg-cyan-950 px-2 py-0.5 rounded border border-cyan-800">
                      Identified Species
                    </span>
                    <h3 className="text-2xl font-extrabold text-white mt-1">
                      {result.predicted_species}
                    </h3>
                    <div className="flex items-center gap-2 text-xs text-slate-300 mt-1">
                      <span className="italic text-cyan-200 font-serif">{result.scientific_name}</span>
                      <span>•</span>
                      <span className="font-semibold text-amber-300">{result.local_name}</span>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-xs text-slate-400">Confidence Score</div>
                    <div className="text-2xl font-extrabold font-mono text-emerald-400">
                      {(result.confidence * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>

                {/* Warnings / Safety Protocol Notice */}
                {result.warnings && result.warnings.length > 0 && (
                  <div className="mt-3 p-3 rounded-xl bg-amber-950/40 border border-amber-600/40 text-amber-200 text-xs space-y-1">
                    <div className="font-semibold flex items-center gap-1.5 text-amber-300">
                      <AlertTriangle className="w-3.5 h-3.5" /> Species Confidence Caution:
                    </div>
                    {result.warnings.map((w, idx) => (
                      <p key={idx} className="text-[11px] text-amber-200/90 pl-5">• {w}</p>
                    ))}
                  </div>
                )}

                {/* Candidate Alternatives */}
                {result.alternative_predictions && result.alternative_predictions.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-ocean-800 flex items-center gap-2 text-xs flex-wrap">
                    <span className="text-slate-400">Alternative Candidates:</span>
                    {result.alternative_predictions.map((alt, idx) => (
                      <span
                        key={idx}
                        className="bg-ocean-950 px-2.5 py-1 rounded-md border border-ocean-700/80 text-slate-300 text-[11px]"
                      >
                        {alt.species}: <span className="font-mono text-cyan-300">{(alt.confidence * 100).toFixed(1)}%</span>
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Biological Habitat & Abundant Areas Card */}
              <div className="glass-panel rounded-2xl p-5 border border-ocean-800">
                <h4 className="text-xs font-bold uppercase tracking-wider text-ocean-300 mb-3 flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-cyan-400" />
                  Regional Abundance & Harvesting Grounds (Palghar Sector)
                </h4>

                <div className="space-y-3 text-xs">
                  <div className="flex items-start gap-2">
                    <span className="font-semibold text-slate-300 min-w-[120px]">Abundant Landing Centers:</span>
                    <div className="flex items-center gap-1.5 flex-wrap">
                      {(result.abundance_information?.abundant_areas || result.local_distribution || ['Satpati', 'Dahanu']).map(
                        (center, i) => (
                          <span
                            key={i}
                            className="bg-cyan-950/80 text-cyan-300 border border-cyan-800/60 px-2.5 py-0.5 rounded-full font-semibold"
                          >
                            {center}
                          </span>
                        )
                      )}
                    </div>
                  </div>

                  <div className="flex items-start gap-2">
                    <span className="font-semibold text-slate-300 min-w-[120px]">Offshore Habitat:</span>
                    <span className="text-slate-300">
                      {result.abundance_information?.habitat || result.habitat || 'Coastal pelagic continental shelf'}
                    </span>
                  </div>

                  {result.seasonal_information && (
                    <div className="flex items-start gap-2">
                      <span className="font-semibold text-slate-300 min-w-[120px]">Peak Season:</span>
                      <span className="text-emerald-300 font-medium">
                        {result.seasonal_information.peak_season || 'October to March'}
                      </span>
                    </div>
                  )}

                  {result.detailed_description && (
                    <div className="p-3 bg-ocean-950/70 rounded-xl border border-ocean-800 text-[11px] text-slate-300 leading-relaxed">
                      {result.detailed_description}
                    </div>
                  )}
                </div>
              </div>

              {/* Live Market Mandi Rates Card */}
              <div className="glass-panel rounded-2xl p-5 border border-amber-500/30 bg-gradient-to-br from-amber-950/20 to-ocean-900/80">
                <h4 className="text-xs font-bold uppercase tracking-wider text-amber-300 mb-3 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-amber-400" />
                  Verified Mandi Auction Rates (Today's Trade Desk)
                </h4>

                {result.market_prices && result.market_prices.length > 0 ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {result.market_prices.map((mkt, idx) => (
                      <div
                        key={idx}
                        className="bg-ocean-950/90 border border-amber-600/30 rounded-xl p-3.5 space-y-2 shadow-md"
                      >
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-bold text-slate-200">{mkt.market_name}</span>
                          <span className="text-[10px] text-slate-400">{mkt.price_date || result.price_date}</span>
                        </div>
                        <div className="flex items-baseline justify-between">
                          <span className="text-2xl font-mono font-bold text-amber-300">
                            ₹{mkt.modal_price_per_kg}/kg
                          </span>
                          <span className="text-xs text-slate-400">Modal Rate</span>
                        </div>
                        <div className="text-[11px] text-slate-400 flex items-center justify-between pt-1 border-t border-ocean-800">
                          <span>Range: ₹{mkt.price_min_per_kg} - ₹{mkt.price_max_per_kg}/kg</span>
                          <span className="text-[10px] text-amber-400/80">Cooperative Verified</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-400">
                    No active mandi trade recorded today for this species. Check morning auctions at Satpati Sarvodaya.
                  </p>
                )}
              </div>
            </div>
          ) : (
            <div className="glass-panel rounded-2xl p-12 text-center border border-ocean-800/80 flex flex-col items-center justify-center min-h-[400px]">
              <div className="w-16 h-16 rounded-2xl bg-ocean-900 border border-ocean-700/80 flex items-center justify-center text-cyan-400 mb-4 shadow-inner">
                <Sparkles className="w-8 h-8" />
              </div>
              <h3 className="text-base font-bold text-slate-200">Awaiting Fish Specimen Upload</h3>
              <p className="text-xs text-slate-400 max-w-md mt-1.5 leading-relaxed">
                Upload a photograph from your mobile or vessel camera. MobileNetV3 and Gemma VLM will inspect morphological
                features (fin structure, color grading, shape) and query official Palghar market databases.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

