import React, { useState } from 'react';
import FarmerOrderHistory from '@features/orders/components/FarmerOrderHistory';
import ProductPostForm from '@features/products/components/ProductPostForm';

const FarmerOrderPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'orders' | 'market'>('orders');

  return (
    <div className="flex flex-col min-h-screen bg-[#f8f9fa] pb-24 pt-16">
      {/* Header */}
      <div className="bg-white px-4 py-3 border-b border-gray-200 sticky top-16 z-30 shadow-sm">
        <div className="flex justify-between items-center mb-3">
          <h1 className="text-xl font-bold text-gray-900">Market & Orders</h1>
        </div>
        
        {/* Toggle Switch */}
        <div className="flex bg-gray-100 p-1 rounded-lg">
          <button 
            className={`flex-1 py-1.5 text-sm font-bold rounded-md transition-all ${activeTab === 'orders' ? 'bg-white shadow-sm text-green-800' : 'text-gray-500'}`}
            onClick={() => setActiveTab('orders')}
          >
            Active Orders
          </button>
          <button 
            className={`flex-1 py-1.5 text-sm font-bold rounded-md transition-all ${activeTab === 'market' ? 'bg-white shadow-sm text-green-800' : 'text-gray-500'}`}
            onClick={() => setActiveTab('market')}
          >
            Post to Market
          </button>
        </div>
      </div>

      <div className="p-4 flex-1 mt-2">
        {activeTab === 'orders' ? (
          <FarmerOrderHistory />
        ) : (
          <ProductPostForm />
        )}
      </div>
    </div>
  );
};

export default FarmerOrderPage;
