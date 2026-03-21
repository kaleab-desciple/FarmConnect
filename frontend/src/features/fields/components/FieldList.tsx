import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fieldApi } from '@/app/services/api';
import { formatArea } from '@/shared/utils/formatters';
import type { Field } from '@shared/farm';

interface FieldListProps {
  farmId?: string | null;
}

const FieldList: React.FC<FieldListProps> = ({ farmId }) => {
  const [fields, setFields] = useState<Field[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchFields = async () => {
      try {
        setIsLoading(true);
        // If farmId is null/undefined, getByFarmId will call backend without farm_id query param
        const response = await fieldApi.getByFarmId(farmId as string);
        const data = response.data;
        setFields(data.items ?? []);
      } catch (err: any) {
        console.error('Failed to fetch fields:', err);
        setError('Failed to load fields. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchFields();
  }, [farmId]);

  if (isLoading) {
    return <div className="p-8 text-center text-gray-500 animate-pulse">Loading fields...</div>;
  }

  if (error) {
    return <div className="p-4 bg-red-50 text-red-600 rounded-lg">{error}</div>;
  }

  if (fields.length === 0) {
    return (
      <div className="p-8 text-center bg-gray-50 rounded-xl border border-gray-100 flex flex-col items-center">
        <span className="text-4xl mb-4">🌾</span>
        <h3 className="text-lg font-bold text-gray-800 mb-2">No fields found</h3>
        <p className="text-gray-500 text-sm mb-4">You haven't defined any fields for this farm yet.</p>
        <button className="px-4 py-2 bg-green-700 text-white rounded-lg font-bold shadow-sm active:scale-95 transition-transform">
          Draw New Field
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {fields.map((field) => (
        <div 
          key={field.id} 
          onClick={() => navigate(`/farmer/fields/${field.id}`)}
          className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 flex items-center justify-between cursor-pointer active:scale-[0.98] transition-all"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-green-100 flex items-center justify-center text-green-800 font-bold border border-green-200">
              {formatArea(field.area_ha)}
            </div>
            <div>
              <h3 className="font-bold text-gray-900">{field.name}</h3>
              <p className="text-xs text-gray-500 capitalize">{field.soil_type || 'Unknown Soil'} • {field.irrigation_type || 'Rainfed'}</p>
            </div>
          </div>
          <div className="text-gray-400">
            ▶
          </div>
        </div>
      ))}
    </div>
  );
};

export default FieldList;
