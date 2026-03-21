import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const InventoryList: React.FC = () => {
  const navigate = useNavigate();
  // Mock data representing the "Inventory Funnel"
  const [funnelData] = useState([
    { id: 1, status: 'Pending QC Grading', amount: 2500, unit: 'KG', type: 'Tomatoes', date: 'Today' },
    { id: 2, status: 'Available to Sell', amount: 800, unit: 'KG', type: 'Tomatoes', date: 'Yesterday' },
    { id: 3, status: 'Reserved in Carts', amount: 200, unit: 'KG', type: 'Tomatoes - Roma', date: '2 days ago' },
    { id: 4, status: 'Sold & Pending Dispatch', amount: 400, unit: 'KG', type: 'Corn', date: 'Last Week' },
  ]);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="font-bold text-gray-800 text-sm uppercase">Quick Actions</h2>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={() => navigate('/farmer/harvest/new')}
            className="flex-1 bg-green-50 text-green-800 border-green-200 border rounded-xl p-3 flex flex-col items-center justify-center gap-2 active:scale-95 transition-transform shadow-sm"
          >
            <span className="text-2xl">🧺</span>
            <span className="text-xs font-bold">Log Harvest</span>
          </button>
          
          <button 
            className="flex-1 bg-blue-50 text-blue-800 border-blue-200 border rounded-xl p-3 flex flex-col items-center justify-center gap-2 active:scale-95 transition-transform shadow-sm"
          >
            <span className="text-2xl">📦</span>
            <span className="text-xs font-bold">Log Inputs</span>
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <h2 className="font-bold text-gray-800 text-sm uppercase mb-4">📊 Inventory Funnel</h2>
        <div className="space-y-4">
          {funnelData.map((item, index) => (
            <div key={item.id} className="relative">
              {/* Connector line for the funnel */}
              {index !== 0 && (
                <div className="absolute -top-4 left-[20px] h-4 w-px bg-gray-200"></div>
              )}
              
              <div className="flex items-center gap-4 bg-gray-50 border border-gray-100 rounded-lg p-3">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-white shadow-sm flex-none
                  ${index === 0 ? 'bg-orange-500' : index === 1 ? 'bg-green-600' : index === 2 ? 'bg-blue-500' : 'bg-gray-800'}`}>
                  {index === 0 ? 'QC' : index === 1 ? '✓' : index === 2 ? '🛒' : '🚚'}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-baseline mb-1">
                    <h3 className="font-bold text-gray-900 text-sm truncate">{item.status}</h3>
                    <span className="font-bold text-gray-600 whitespace-nowrap ml-2">
                      {item.amount.toLocaleString()} <span className="text-xs">{item.unit}</span>
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 truncate">{item.type} • {item.date}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default InventoryList;
