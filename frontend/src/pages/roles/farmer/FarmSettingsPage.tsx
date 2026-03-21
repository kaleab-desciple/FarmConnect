import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import FarmSettings from '@features/farms/components/FarmSettings';
import { farmApi } from '@/app/services/api';
import type { Farm } from '@shared/farm';

const FarmSettingsPage: React.FC = () => {
  const { farmId } = useParams<{ farmId: string }>();
  const navigate = useNavigate();
  const [farm, setFarm] = useState<Farm | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchFarm = async () => {
      try {
        if (!farmId) throw new Error("Farm ID missing");
        const response = await farmApi.getById(farmId);
        setFarm(response.data);
      } catch (err) {
        console.error(err);
        setError('Failed to load farm settings.');
      } finally {
        setLoading(false);
      }
    };

    fetchFarm();
  }, [farmId]);

  if (loading) return <div className="p-8 text-center text-green-700 font-bold">Loading Farm Data...</div>;
  if (error || !farm) return <div className="p-8 text-center text-red-500 font-bold">{error || 'Farm not found'}</div>;

  return (
    <div className="p-4 md:p-8 max-w-2xl mx-auto space-y-6">
      <button 
        onClick={() => navigate('/farmer/dashboard')}
        className="text-green-700 font-bold hover:underline flex items-center gap-2"
      >
        <span>←</span> Back to Dashboard
      </button>

      <div className="bg-green-50 rounded-xl p-4 border border-green-200 flex items-center justify-between">
        <div>
          <h2 className="font-bold text-green-900 text-lg">Managing: {farm.name}</h2>
          <p className="text-sm text-green-700">Farm ID: {farm.id}</p>
        </div>
        <div className="text-4xl">🚜</div>
      </div>

      <FarmSettings farm={farm} onUpdate={(updatedFarm) => setFarm(updatedFarm)} />
      
      <div className="pt-8">
        <h3 className="font-bold text-red-700 mb-2 border-b border-red-200 pb-2">Danger Zone</h3>
        <button className="touch-target border border-red-500 text-red-600 rounded-lg hover:bg-red-50 font-bold">
          Delete Farm
        </button>
      </div>
    </div>
  );
};

export default FarmSettingsPage;
