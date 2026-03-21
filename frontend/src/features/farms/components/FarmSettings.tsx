import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { farmApi } from '@/app/services/api';
import type { Farm, FarmUpdate } from '@shared/farm';

interface FarmSettingsProps {
  farm: Farm;
  onUpdate: (updatedFarm: Farm) => void;
}

const FarmSettings: React.FC<FarmSettingsProps> = ({ farm, onUpdate }) => {
  const [isSaving, setIsSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  
  const { register, handleSubmit, formState: { errors } } = useForm<FarmUpdate>({
    defaultValues: {
      name: farm.name,
      location_address: farm.location_address,
      total_area_ha: farm.total_area_ha,
    }
  });

  const submitUpdate = async (data: Partial<FarmUpdate>) => {
    setIsSaving(true);
    setSuccessMsg('');
    try {
      // Clean up empty fields to ensure partial update
      const updateData = Object.fromEntries(
        Object.entries(data).filter(([_, v]) => v != null && v !== '')
      ) as Partial<FarmUpdate>;
      
      const response = await farmApi.update(farm.id, updateData);
      onUpdate(response.data);
      setSuccessMsg('Settings updated successfully!');
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err) {
      console.error(err);
      alert('Failed to update farm settings');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md border border-gray-100 p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-6">Farm Settings</h3>
      
      <form onSubmit={handleSubmit(submitUpdate)} className="space-y-6">
        <div>
          <label className="block text-sm font-bold text-gray-700 mb-2">Farm Name</label>
          <input 
            {...register('name')}
            className="w-full touch-target border border-gray-300 rounded-lg px-4 focus:ring-2 focus:ring-green-500 focus:border-green-500"
          />
        </div>

        <div>
          <label className="block text-sm font-bold text-gray-700 mb-2">Location / Region</label>
          <input 
            {...register('location_address')}
            className="w-full touch-target border border-gray-300 rounded-lg px-4 focus:ring-2 focus:ring-green-500 focus:border-green-500"
          />
        </div>

        <div>
           <label className="block text-sm font-bold text-gray-700 mb-2">Total Area (Hectares)</label>
           <input 
             type="number"
             step="0.1"
             {...register('total_area_ha', { valueAsNumber: true })}
             className="w-full touch-target border border-gray-300 rounded-lg px-4 focus:ring-2 focus:ring-green-500 focus:border-green-500"
           />
        </div>

        <div className="pt-4 flex items-center justify-between border-t border-gray-100">
          <span className="text-green-600 font-bold text-sm">
            {successMsg}
          </span>
          <button 
            type="submit" 
            disabled={isSaving}
            className="touch-target bg-green-700 text-white rounded-lg font-bold hover:bg-green-800 disabled:opacity-50 min-w-[120px]"
          >
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default FarmSettings;
