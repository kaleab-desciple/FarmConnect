import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fieldApi } from '@/app/services/api';
import type { Field } from '@shared/farm';

const FieldDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [field, setField] = useState<Field | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchField = async () => {
      if (!id) return;
      try {
        setIsLoading(true);
        const response = await fieldApi.getById(id);
        setField(response.data);
      } catch (err) {
        console.error('Failed to load field details', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchField();
  }, [id]);

  if (isLoading) {
    return <div className="p-8 text-center animate-pulse">Loading field data...</div>;
  }

  if (!field) {
    return <div className="p-8 text-center text-red-500">Field not found</div>;
  }

  return (
    <div className="flex flex-col min-h-screen bg-[#f8f9fa] pb-24 pt-16">
      {/* Header */}
      <div className="bg-white px-4 py-3 border-b border-gray-200 sticky top-16 z-30 shadow-sm flex items-center justify-between">
        <button onClick={() => navigate(-1)} className="text-gray-500 font-bold active:scale-95">
          ← Back
        </button>
        <h1 className="text-lg font-bold text-gray-900 truncate px-4">{field.name}</h1>
        <button className="text-gray-500 text-xl font-bold active:scale-95">
          ⚙
        </button>
      </div>

      <div className="p-4 space-y-6 flex-1">
        {/* Vigor Trend (NDVI Graph Placeholder) */}
        <section className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="p-3 border-b border-gray-100 bg-gray-50/50 flex justify-between items-center">
            <h2 className="font-bold text-sm text-gray-700">📈 VIGOR TREND</h2>
            <span className="text-[10px] text-gray-500 uppercase">Past 30 Days</span>
          </div>
          <div className="p-4 h-32 flex items-center justify-center relative">
            {/* SVG line graph placeholder */}
            <svg viewBox="0 0 100 40" className="w-full h-full stroke-green-600 fill-none" preserveAspectRatio="none">
              <path d="M0 35 L20 30 L40 32 L60 15 L80 10 L100 12" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M0 40 L0 35 L20 30 L40 32 L60 15 L80 10 L100 12 L100 40 Z" fill="url(#grad)" stroke="none" opacity="0.2"/>
              <defs>
                <linearGradient id="grad" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stopColor="#16a34a"/>
                  <stop offset="100%" stopColor="#ffffff" stopOpacity="0"/>
                </linearGradient>
              </defs>
            </svg>
            <div className="absolute inset-0 flex items-center justify-center opacity-0 hover:opacity-100 bg-white/80 transition-opacity backdrop-blur-sm cursor-pointer">
              <span className="text-xs font-bold text-green-800">Tap for full breakdown</span>
            </div>
          </div>
        </section>

        {/* Quick Log Clipboard */}
        <section className="bg-white rounded-xl shadow-sm border border-gray-100 p-3 flex gap-2 overflow-x-auto no-scrollbar">
          <button className="flex-none flex items-center gap-2 bg-blue-50 text-blue-700 border border-blue-200 px-3 py-2 rounded-lg text-sm font-bold shadow-sm active:scale-95 whitespace-nowrap">
            <span className="text-lg">💧</span> Log Irrigation
          </button>
          <button className="flex-none flex items-center gap-2 bg-yellow-50 text-yellow-700 border border-yellow-200 px-3 py-2 rounded-lg text-sm font-bold shadow-sm active:scale-95 whitespace-nowrap">
            <span className="text-lg">🧪</span> Log Fertilizer
          </button>
          <button className="flex-none flex items-center gap-2 bg-gray-50 text-gray-700 border border-gray-200 px-3 py-2 rounded-lg text-sm font-bold shadow-sm active:scale-95 whitespace-nowrap">
            <span className="text-lg">📝</span> More...
          </button>
        </section>

        {/* Lifecycle Timeline */}
        <section>
          <h2 className="font-bold text-sm text-gray-700 mb-3 px-1 uppercase">⏳ Crop Lifecycle</h2>
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
            <div className="relative border-l-2 border-gray-200 ml-3 space-y-6 pb-2">
              
              {/* Timeline Item 1 */}
              <div className="relative pl-6">
                <span className="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-green-500 border-4 border-white shadow-sm"></span>
                <span className="text-[10px] font-bold text-green-600 uppercase tracking-wider">Today</span>
                <h3 className="font-bold text-gray-900 mt-1">Check-in Required</h3>
                <p className="text-xs text-gray-500 mt-1">Expected Stage: Fruiting</p>
                <div className="mt-2 flex gap-2">
                  <button className="px-3 py-1.5 bg-green-700 text-white rounded text-xs font-bold flex-1 active:scale-95">Confirm Stage</button>
                  <button className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded text-xs font-bold flex-1 active:scale-95">Report Delay</button>
                </div>
              </div>

              {/* Timeline Item 2 */}
              <div className="relative pl-6">
                <span className="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-blue-500 border-4 border-white shadow-sm"></span>
                <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Yesterday • 14:30</span>
                <h3 className="font-bold text-gray-900 mt-1">Fertilizer Applied</h3>
                <p className="text-xs text-gray-500 mt-1">20L NPK Fertilizer (Worker: John)</p>
              </div>

              {/* Timeline Item 3 */}
              <div className="relative pl-6">
                <span className="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-red-500 border-4 border-white shadow-sm"></span>
                <span className="text-[10px] font-bold text-red-500 uppercase tracking-wider">3 Days Ago • Auto Alert</span>
                <h3 className="font-bold text-red-700 mt-1">Frost Warning</h3>
                <p className="text-xs text-red-600/80 mt-1">Temperatures dropped below 0°C at 04:00 AM.</p>
              </div>

              {/* Timeline Item 4 */}
              <div className="relative pl-6">
                <span className="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-gray-400 border-4 border-white shadow-sm"></span>
                <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">12 Days Ago</span>
                <h3 className="font-bold text-gray-900 mt-1">Planted</h3>
                <p className="text-xs text-gray-500 mt-1">5000 Seeds (Variety: Roma)</p>
              </div>

            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default FieldDetailsPage;
