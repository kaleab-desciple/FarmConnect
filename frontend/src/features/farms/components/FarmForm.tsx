import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { formatCoordinate } from '@/shared/utils/formatters';
import { farmCreateSchema } from '@utils/validation';

// Define a type based on the schema if it's not exported
type FarmFormValues = z.infer<typeof farmCreateSchema>;

interface FarmFormProps {
  onSubmit: (data: FarmFormValues) => void;
  isLoading?: boolean;
}

const FarmForm: React.FC<FarmFormProps> = ({ onSubmit, isLoading }) => {
  const [step, setStep] = useState<1 | 2>(1);
  const [markedLocation, setMarkedLocation] = useState<{lat: number, lng: number} | null>(null);

  const { register, handleSubmit, setValue, formState: { errors } } = useForm<FarmFormValues>({
    resolver: zodResolver(farmCreateSchema),
    defaultValues: {
      name: '',
      location_address: '',
    }
  });

  const handleMapClick = (e: React.MouseEvent<HTMLDivElement>) => {
    // Simulated map click - in reality this would use Leaflet events
    const lat = 9.000 + Math.random() * 0.1;
    const lng = 38.700 + Math.random() * 0.1;
    setMarkedLocation({ lat, lng });
    setValue('location_lat', lat);
    setValue('location_lng', lng);
  };

  const handleNextStep = () => {
    if (markedLocation) {
      setStep(2);
    } else {
      alert("Please pin your farm location on the map first.");
    }
  };

  const submitForm = (data: FarmFormValues) => {
    onSubmit(data);
  };

  return (
    <div className="bg-white rounded-xl shadow-md border border-gray-100 p-4 max-w-md mx-auto">
      <h2 className="text-xl font-bold text-green-900 mb-4">
        {step === 1 ? 'Step 1: Locate Your Farm' : 'Step 2: Farm Details'}
      </h2>
      
      <form onSubmit={handleSubmit(submitForm)} className="space-y-4">
        {step === 1 && (
          <div className="space-y-4">
            <p className="text-sm text-gray-600 mb-2">
              Tap on the map to drop a pin where your farm is located.
            </p>
            
            {/* Simulated Map First Onboarding */}
            <div 
              onClick={handleMapClick}
              className="w-full h-64 bg-green-50 rounded-lg border-2 border-dashed border-green-300 relative cursor-pointer flex items-center justify-center overflow-hidden"
            >
              <div className="absolute inset-0 opacity-30 bg-[url('https://www.transparenttextures.com/patterns/cartographer.png')]" />
              
              {markedLocation ? (
                <>
                  <div className="absolute flex flex-col items-center animate-bounce">
                    <span className="text-3xl drop-shadow-md">📍</span>
                  </div>
                  <div className="absolute bottom-2 right-2 bg-white/90 px-2 py-1 text-xs rounded shadow font-mono">
                    {formatCoordinate(markedLocation.lat)}, {formatCoordinate(markedLocation.lng)}
                  </div>
                </>
              ) : (
                <span className="text-green-800 font-bold opacity-50 z-10">
                  Tap to drop pin
                </span>
              )}
            </div>

            {errors.location_lat && (
              <p className="text-red-500 text-xs mt-1">Location is required</p>
            )}

            <button 
              type="button" 
              onClick={handleNextStep}
              className={`w-full touch-target rounded-lg font-bold text-white transition-opacity ${markedLocation ? 'bg-green-700' : 'bg-gray-400 cursor-not-allowed'}`}
            >
              Next: Basic Details ➔
            </button>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4 animate-fadeIn">
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-1">Farm Name</label>
              <input 
                {...register('name')}
                placeholder="e.g. Green Acres"
                className="w-full touch-target border border-gray-300 rounded-lg px-4 focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
              {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-bold text-gray-700 mb-1">Nearest Town / Region (Optional)</label>
              <input 
                {...register('location_address')}
                placeholder="e.g. Oromia Region"
                className="w-full touch-target border border-gray-300 rounded-lg px-4 focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
            </div>

            <div className="flex gap-2 pt-4">
              <button 
                type="button" 
                onClick={() => setStep(1)}
                className="flex-1 touch-target bg-gray-100 text-gray-700 rounded-lg font-bold hover:bg-gray-200"
              >
                Back
              </button>
              <button 
                type="submit" 
                disabled={isLoading}
                className="flex-[2] touch-target bg-green-700 text-white rounded-lg font-bold hover:bg-green-800 disabled:opacity-50"
              >
                {isLoading ? 'Saving...' : 'Create Farm ✔'}
              </button>
            </div>
          </div>
        )}
      </form>
    </div>
  );
};

export default FarmForm;
