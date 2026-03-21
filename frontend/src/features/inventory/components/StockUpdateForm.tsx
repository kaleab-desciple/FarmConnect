import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const StockUpdateForm: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  // Form state
  const [targetCrop, setTargetCrop] = useState('North Field - Tomatoes');
  const [yieldWeight, setYieldWeight] = useState<number>(2500);
  const [notes, setNotes] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setLoading(false);
      // In a real app we'd redirect to the inventory page or show a toast
      navigate('/farmer/inventory');
    }, 800);
  };

  return (
    <div className="flex flex-col min-h-screen bg-[#f8f9fa] pb-24 pt-16">
      {/* Header */}
      <div className="bg-white px-4 py-3 border-b border-gray-200 sticky top-16 z-30 shadow-sm flex items-center justify-between">
        <button onClick={() => navigate(-1)} className="text-gray-500 font-bold active:scale-95">
          ← Back
        </button>
        <h1 className="text-lg font-bold text-gray-900 truncate px-4">End of Day Log</h1>
        <button className="text-green-700 font-bold active:scale-95" onClick={handleSubmit}>
          Done
        </button>
      </div>

      <div className="p-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h2 className="font-bold text-gray-800 mb-1">Yield Only, Quality Later</h2>
          <p className="text-xs text-gray-500 mb-6">Log the gross harvest weight now. Quality Control (QC) will assess and list it on the marketplace.</p>

          <form onSubmit={handleSubmit} className="space-y-6">
            
            {/* Target Crop Selector */}
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2">Target Crop</label>
              <select 
                value={targetCrop}
                onChange={(e) => setTargetCrop(e.target.value)}
                className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-gray-800 font-bold focus:ring-2 focus:ring-green-500 focus:border-green-500"
              >
                <option value="North Field - Tomatoes">North Field - Tomatoes (Harvesting)</option>
                <option value="East Field - Corn">East Field - Corn (Fruiting)</option>
              </select>
            </div>

            {/* Yield Weight Input */}
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2">Gross Yield Weight (KG)</label>
              <div className="flex items-center gap-4">
                <button 
                  type="button"
                  onClick={() => setYieldWeight(Math.max(0, yieldWeight - 100))}
                  className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center font-bold text-xl text-gray-600 active:scale-95 border border-gray-200"
                >
                  -
                </button>
                <input 
                  type="number" 
                  value={yieldWeight}
                  onChange={(e) => setYieldWeight(Number(e.target.value))}
                  className="flex-1 bg-white border-2 border-green-600 rounded-lg p-3 text-center text-xl font-bold text-green-900 shadow-sm"
                  min="0"
                />
                <button 
                  type="button"
                  onClick={() => setYieldWeight(yieldWeight + 100)}
                  className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center font-bold text-xl text-gray-600 active:scale-95 border border-gray-200"
                >
                  +
                </button>
              </div>
            </div>

            {/* Notes */}
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2">Notes (Optional)</label>
              <textarea 
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="A bit muddy today, might need washing..."
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
              {loading ? 'Logging...' : 'LOG HARVEST & MOVE TO QC'}
            </button>

          </form>
        </div>
      </div>
    </div>
  );
};

export default StockUpdateForm;
