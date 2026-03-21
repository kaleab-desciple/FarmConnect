import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const DailyLogForm: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [logType, setLogType] = useState('irrigation');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      navigate(-1);
    }, 800);
  };

  return (
    <div className="flex flex-col min-h-screen bg-[#f8f9fa] pb-24 pt-16">
      <div className="bg-white px-4 py-3 border-b border-gray-200 sticky top-16 z-30 shadow-sm flex items-center justify-between">
        <button onClick={() => navigate(-1)} className="text-gray-500 font-bold active:scale-95">
          ← Cancel
        </button>
        <h1 className="text-lg font-bold text-gray-900 truncate px-4">Daily Activity Log</h1>
        <button className="text-green-700 font-bold active:scale-95" onClick={handleSubmit}>
          Save
        </button>
      </div>

      <div className="p-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <form onSubmit={handleSubmit} className="space-y-6">
            
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2">Activity Type</label>
              <div className="grid grid-cols-2 gap-3">
                <button type="button" onClick={() => setLogType('irrigation')} className={`py-3 rounded-lg border flex flex-col items-center gap-1 active:scale-95 transition-all ${logType === 'irrigation' ? 'bg-blue-50 border-blue-500 text-blue-800 font-bold shadow-sm' : 'bg-white border-gray-200 text-gray-500 hover:bg-gray-50'}`}>
                  <span className="text-2xl">💧</span> <span className="text-xs">Irrigation</span>
                </button>
                <button type="button" onClick={() => setLogType('fertilizer')} className={`py-3 rounded-lg border flex flex-col items-center gap-1 active:scale-95 transition-all ${logType === 'fertilizer' ? 'bg-yellow-50 border-yellow-500 text-yellow-800 font-bold shadow-sm' : 'bg-white border-gray-200 text-gray-500 hover:bg-gray-50'}`}>
                  <span className="text-2xl">🧪</span> <span className="text-xs">Fertilizer/Chemicals</span>
                </button>
                <button type="button" onClick={() => setLogType('scouting')} className={`py-3 rounded-lg border flex flex-col items-center gap-1 active:scale-95 transition-all ${logType === 'scouting' ? 'bg-green-50 border-green-500 text-green-800 font-bold shadow-sm' : 'bg-white border-gray-200 text-gray-500 hover:bg-gray-50'}`}>
                  <span className="text-2xl">🔍</span> <span className="text-xs">Scouting</span>
                </button>
                <button type="button" onClick={() => setLogType('other')} className={`py-3 rounded-lg border flex flex-col items-center gap-1 active:scale-95 transition-all ${logType === 'other' ? 'bg-gray-100 border-gray-500 text-gray-800 font-bold shadow-sm' : 'bg-white border-gray-200 text-gray-500 hover:bg-gray-50'}`}>
                  <span className="text-2xl">📝</span> <span className="text-xs">Other Tasks</span>
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2">Field / Target Area</label>
              <select className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-gray-800 font-bold focus:ring-2 focus:ring-green-500 focus:border-green-500">
                <option>North Field</option>
                <option>East Field</option>
                <option>South Field</option>
                <option>All Fields</option>
              </select>
            </div>

            {logType === 'irrigation' && (
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Duration / Volume (Optional)</label>
                <input type="text" placeholder="e.g. 2 hours" className="w-full bg-white border border-gray-200 rounded-lg p-3 text-gray-800 focus:ring-2 focus:ring-green-500" />
              </div>
            )}

            {logType === 'fertilizer' && (
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">Product Applied</label>
                <input type="text" placeholder="e.g. NPK 20-20-20" className="w-full bg-white border border-gray-200 rounded-lg p-3 text-gray-800 focus:ring-2 focus:ring-green-500 mb-3" />
                <label className="block text-sm font-bold text-gray-700 mb-2">Amount</label>
                <input type="text" placeholder="e.g. 50 L" className="w-full bg-white border border-gray-200 rounded-lg p-3 text-gray-800 focus:ring-2 focus:ring-green-500" />
              </div>
            )}

            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2">Notes</label>
              <textarea 
                placeholder="Any observations or issues?"
                className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-gray-800 text-sm focus:ring-2 focus:ring-green-500 focus:border-green-500 h-24 resize-none"
              />
            </div>

            <button 
              type="submit" 
              disabled={loading}
              className={`w-full py-4 rounded-xl font-bold text-white uppercase tracking-wider text-sm shadow-md transition-all ${
                loading ? 'bg-green-600/70 cursor-not-allowed' : 'bg-green-700 active:scale-[0.98]'
              }`}
            >
              {loading ? 'Saving...' : 'Save Activity Log'}
            </button>

          </form>
        </div>
      </div>
    </div>
  );
};

export default DailyLogForm;
