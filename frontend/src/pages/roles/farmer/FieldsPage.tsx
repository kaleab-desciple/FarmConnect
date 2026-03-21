import React, { useEffect, useState } from 'react';
import FieldList from '@features/fields/components/FieldList';
import FieldMap from '@features/fields/components/FieldMap';
import { farmApi } from '@/app/services/api';
import { useAuthStore } from '@/app/store/useAuthStore';
import type { Farm, Field } from '@shared/farm';

const FieldsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'list' | 'map'>('list');
  const [farmId, setFarmId] = useState<string | null>(null); // null means "All Farms"
  const [farms, setFarms] = useState<Farm[]>([]);
  const [fields, setFields] = useState<Field[]>([]);
  
  useEffect(() => {
    const fetchFarms = async () => {
      try {
        const response = await farmApi.getAll();
        const items = response.data.items || [];
        setFarms(items);
      } catch (error) {
        console.error("Could not fetch farms", error);
      }
    };
    fetchFarms();
  }, []);

  return (
    <div className="flex flex-col min-h-screen bg-[#f8f9fa] pb-24 pt-16">
      {/* Fixed Header Content */}
      <div className="bg-white px-4 py-3 border-b border-gray-200 sticky top-16 z-30 shadow-sm">
        <div className="flex justify-between items-center mb-3">
          <h1 className="text-xl font-bold text-gray-900">My Fields</h1>
          <button className="w-8 h-8 rounded-full bg-green-100 text-green-800 flex items-center justify-center font-bold text-xl leading-none border border-green-200 shadow-sm active:scale-95">
            +
          </button>
        </div>
        
        {/* Farm Selector (Only show if multiple farms exist) */}
        {farms.length > 1 && (
          <div className="flex gap-2 overflow-x-auto pb-3 mb-1 no-scrollbar -mx-1 px-1">
            <button 
              onClick={() => setFarmId(null)}
              className={`px-3 py-1.5 rounded-full text-xs font-bold whitespace-nowrap transition-all border ${farmId === null ? 'bg-green-800 text-white border-green-800 shadow-sm' : 'bg-white text-gray-600 border-gray-200'}`}
            >
              All My Fields
            </button>
            {farms.map(farm => (
              <button 
                key={farm.id}
                onClick={() => setFarmId(farm.id)}
                className={`px-3 py-1.5 rounded-full text-xs font-bold whitespace-nowrap transition-all border ${farmId === farm.id ? 'bg-green-800 text-white border-green-800 shadow-sm' : 'bg-white text-gray-600 border-gray-200'}`}
              >
                {farm.name}
              </button>
            ))}
          </div>
        )}
        
        {/* Toggle Switch */}
        <div className="flex bg-gray-100 p-1 rounded-lg">
          <button 
            className={`flex-1 py-1.5 text-sm font-bold rounded-md transition-all ${activeTab === 'list' ? 'bg-white shadow-sm text-green-800' : 'text-gray-500'}`}
            onClick={() => setActiveTab('list')}
          >
            List View
          </button>
          <button 
            className={`flex-1 py-1.5 text-sm font-bold rounded-md transition-all ${activeTab === 'map' ? 'bg-white shadow-sm text-green-800' : 'text-gray-500'}`}
            onClick={() => setActiveTab('map')}
          >
            Map View
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="p-4 flex-1 flex flex-col">
        {activeTab === 'list' ? (
          <FieldList farmId={farmId} />
        ) : (
          <div className="flex-1 min-h-[400px]">
             {/* Note: Map needs fields, we might want to lift state up. */}
            <FieldMap fields={fields} />
          </div>
        )}
      </div>
    </div>
  );
};

export default FieldsPage;
