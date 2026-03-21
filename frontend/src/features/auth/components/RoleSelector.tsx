import React, { useState } from 'react';

const roles = [
  { id: 'FARMER', title: 'I am a Farmer', icon: '👨‍🌾', desc: 'Sell your crops directly to reliable buyers.' },
  { id: 'MERCHANT', title: 'I am a Buyer', icon: '🛒', desc: 'Purchase bulk agricultural products securely.' },
  { id: 'DELIVERY', title: 'I am a Driver', icon: '🚚', desc: 'Earn money delivering goods locally.' }
];

interface RoleSelectorProps {
  onSelect: (role: string) => void;
}

const RoleSelector: React.FC<RoleSelectorProps> = ({ onSelect }) => {
  const [selectedRole, setSelectedRole] = useState<string | null>(null);

  const handleContinue = () => {
    if (selectedRole) onSelect(selectedRole);
  };

  return (
    <div className="w-full max-w-md bg-white p-8 rounded-2xl shadow-xl">
      <h2 className="text-2xl font-bold text-gray-900 mb-2">How will you use FarmConnect?</h2>
      <p className="text-gray-600 mb-6">Select your primary role to customize your experience.</p>
      
      <div className="space-y-4">
        {roles.map(r => (
          <div 
            key={r.id} 
            onClick={() => setSelectedRole(r.id)}
            className={`touch-target p-4 rounded-xl border-2 flex items-center gap-4 cursor-pointer transition-all ${
              selectedRole === r.id 
                ? 'border-green-600 bg-green-50 shadow-md ring-1 ring-green-600' 
                : 'border-gray-200 hover:border-green-300'
            }`}
          >
            <span className="text-3xl">{r.icon}</span>
            <div>
              <h3 className="font-bold text-gray-900">{r.title}</h3>
              <p className="text-sm text-gray-500">{r.desc}</p>
            </div>
          </div>
        ))}
      </div>

      <button 
        onClick={handleContinue}
        disabled={!selectedRole}
        className={`w-full touch-target mt-8 text-white rounded-lg font-bold text-lg transition-colors ${
          selectedRole ? 'bg-green-700 hover:bg-green-800' : 'bg-gray-300 cursor-not-allowed'
        }`}
      >
        Continue ➔
      </button>
    </div>
  );
};

export default RoleSelector;
