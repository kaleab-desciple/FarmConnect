import React, { useState } from 'react';
import FarmForm from './FarmForm';
import { farmApi } from '@/app/services/api';
import { formatCoordinate } from '@/shared/utils/formatters';
import type { Farm, FarmCreate } from '@shared/farm';

const FarmList: React.FC = () => {
  const [isCreating, setIsCreating] = useState(false);
  const [farms, setFarms] = useState<Farm[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  React.useEffect(() => {
    const fetchFarms = async () => {
      try {
        setIsLoading(true);
        const response = await farmApi.getAll();
        // Backend returns PaginatedResponse<Farm>: { items: [...], total, ... }
        setFarms(response.data.items ?? []);
      } catch (err) {
        console.error('Failed to fetch farms:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchFarms();
  }, []);

  const handleCreateSubmit = async (data: Partial<FarmCreate>) => {
    try {
      if (!data.name || data.location_lat === undefined || data.location_lng === undefined) {
        throw new Error("Missing required farm data");
      }
      
      const response = await farmApi.create(data as FarmCreate);
      setFarms((prev: Farm[]) => [...prev, response.data]);
      setIsCreating(false);
      alert('Farm created successfully!');
    } catch (err) {
      console.error(err);
      alert('Failed to create farm');
    }
  };

  if (isLoading) {
    return <div className="p-8 text-center animate-pulse">Loading farms...</div>;
  }

  if (isCreating) {
    return (
      <div className="p-4">
        <button 
          onClick={() => setIsCreating(false)}
          className="mb-4 text-green-700 font-bold"
        >
          ← Back to List
        </button>
        <FarmForm onSubmit={handleCreateSubmit} />
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold text-green-900">Your Farms</h2>
        <button 
          onClick={() => setIsCreating(true)}
          className="touch-target bg-green-700 text-white rounded-lg font-bold hover:bg-green-800"
        >
          + Add Farm
        </button>
      </div>

      {farms.length === 0 ? (
        <div className="bg-white p-8 rounded-xl text-center border-2 border-dashed border-gray-200">
          <span className="text-4xl block mb-2">🚜</span>
          <p className="text-gray-500 font-medium">You haven't added any farms yet.</p>
          <p className="text-sm text-gray-400 mt-1">Tap the button above to locate your farm on the map.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {farms.map(farm => (
            <div key={farm.id} className="bg-white p-4 rounded-xl border border-green-100 shadow-sm flex items-center gap-4">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center text-xl">
                📍
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-gray-900">{farm.name}</h3>
                <p className="text-xs text-gray-500">
                  {formatCoordinate(farm.location_lat)}, {formatCoordinate(farm.location_lng)}
                </p>
                {farm.location_address && (
                  <p className="text-xs text-gray-500">{farm.location_address}</p>
                )}
              </div>
              <button className="touch-target text-green-700 font-bold border border-green-200 rounded-lg hover:bg-green-50">
                Manage
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FarmList;
