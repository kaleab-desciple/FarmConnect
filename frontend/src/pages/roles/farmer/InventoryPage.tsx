import React, { useState } from 'react';
import InventoryList from '@features/inventory/components/InventoryList';

const InventoryPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'funnel' | 'inputs'>('funnel');

  return (
    <div className="flex flex-col min-h-screen bg-[#f8f9fa] pb-24 pt-16">
      {/* Header */}
      <div className="bg-white px-4 py-3 border-b border-gray-200 sticky top-16 z-30 shadow-sm">
        <div className="flex justify-between items-center mb-3">
          <h1 className="text-xl font-bold text-gray-900">Inventory Management</h1>
        </div>
        
        {/* Toggle Switch */}
        <div className="flex bg-gray-100 p-1 rounded-lg">
          <button 
            className={`flex-1 py-1.5 text-sm font-bold rounded-md transition-all ${activeTab === 'funnel' ? 'bg-white shadow-sm text-green-800' : 'text-gray-500'}`}
            onClick={() => setActiveTab('funnel')}
          >
            Produce Funnel
          </button>
          <button 
            className={`flex-1 py-1.5 text-sm font-bold rounded-md transition-all ${activeTab === 'inputs' ? 'bg-white shadow-sm text-green-800' : 'text-gray-500'}`}
            onClick={() => setActiveTab('inputs')}
          >
            Farm Inputs (Seeds/Fertilizer)
          </button>
        </div>
      </div>

      <div className="p-4 flex-1">
        {activeTab === 'funnel' ? (
          <InventoryList />
        ) : (
           <div className="p-8 text-center bg-white rounded-xl border border-gray-100 flex flex-col items-center shadow-sm">
             <span className="text-4xl mb-4">🧪</span>
             <h3 className="text-lg font-bold text-gray-800 mb-2">Inputs Tracker</h3>
             <p className="text-gray-500 text-sm">Manage your seeds, fertilizers, and equipment logic here.</p>
           </div>
        )}
      </div>
    </div>
  );
};

export default InventoryPage;
