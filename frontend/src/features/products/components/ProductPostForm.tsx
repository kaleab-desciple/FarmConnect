import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const ProductPostForm: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      navigate(-1);
    }, 800);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <h2 className="font-bold text-gray-800 mb-1">List on Marketplace</h2>
      <p className="text-xs text-gray-500 mb-6">Select from your available QC-approved inventory to post a sale listing.</p>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-bold text-gray-700 mb-2">Available Inventory</label>
          <select className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-gray-800 font-bold focus:ring-2 focus:ring-green-500 focus:border-green-500">
             <option>Tomatoes - Grade A (800 KG Available)</option>
             <option>Corn - Yellow Standard (2000 KG Available)</option>
          </select>
        </div>

        <div>
           <label className="block text-sm font-bold text-gray-700 mb-2">Quantity to List (KG)</label>
           <input type="number" defaultValue="800" className="w-full bg-white border border-gray-200 rounded-lg p-3 text-gray-800 font-bold focus:ring-2 focus:ring-green-500" />
        </div>

        <div>
           <label className="block text-sm font-bold text-gray-700 mb-2">Price per KG (USD)</label>
           <input type="number" step="0.01" placeholder="e.g. 1.50" className="w-full bg-white border border-gray-200 rounded-lg p-3 text-gray-800 font-bold focus:ring-2 focus:ring-green-500" />
        </div>

        <div>
          <label className="block text-sm font-bold text-gray-700 mb-2">Delivery Options</label>
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-sm text-gray-700">
              <input type="checkbox" defaultChecked className="text-green-600 focus:ring-green-500 rounded" /> Let buyer arrange delivery via FarmConnect Drivers
            </label>
            <label className="flex items-center gap-2 text-sm text-gray-700">
              <input type="checkbox" className="text-green-600 focus:ring-green-500 rounded" /> I will deliver myself
            </label>
          </div>
        </div>

        <button 
          type="submit" 
          disabled={loading}
          className={`w-full py-3 mt-2 rounded-xl font-bold text-white uppercase tracking-wider text-sm shadow-sm transition-all ${
            loading ? 'bg-green-600/70 cursor-not-allowed' : 'bg-green-700 active:scale-[0.98]'
          }`}
        >
          {loading ? 'Posting...' : 'Post Listing'}
        </button>
      </form>
    </div>
  );
};

export default ProductPostForm;
