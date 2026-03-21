import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import RoleSelector from './RoleSelector';
import { registerSchema } from '@utils/validation';
import { api } from '@/app/services/api';

type RegisterValues = z.infer<typeof registerSchema>;

const RegisterForm: React.FC = () => {
  const [step, setStep] = useState<1 | 2>(1);
  const [role, setRole] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const { register, handleSubmit, formState: { errors } } = useForm<RegisterValues>({
    resolver: zodResolver(registerSchema)
  });

  const handleRoleSelect = (selectedRole: string) => {
    setRole(selectedRole);
    setStep(2);
  };

  const onSubmit = async (data: RegisterValues) => {
    setIsLoading(true);
    setError('');
    try {
      // Create user endpoint might live at /api/v1/users and create Keycloak credentials
      await api.post('/api/v1/users', { ...data, role });
      alert('Registration successful! Please login.');
      // typically navigate to /login here
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed.');
    } finally {
      setIsLoading(false);
    }
  };

  if (step === 1) {
    return (
      <div className="flex justify-center mt-10">
        <RoleSelector onSelect={handleRoleSelect} />
      </div>
    );
  }

  return (
    <div className="w-full max-w-md bg-white rounded-2xl shadow-xl overflow-hidden mx-auto mt-10">
      <div className="bg-green-800 p-6">
        <div className="flex items-center gap-2 mb-2">
          <button onClick={() => setStep(1)} className="text-white opacity-80 hover:opacity-100">← Back</button>
        </div>
        <h1 className="text-2xl font-bold text-white">Create Account</h1>
        <p className="text-green-100/80">Registering as a {role}</p>
      </div>

      <div className="p-8">
        {error && (
          <div className="bg-red-50 text-red-700 p-3 rounded mb-4 text-sm font-bold">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-1">Full Name</label>
            <input 
              {...register('name')}
              className="w-full touch-target border border-gray-300 rounded-lg px-4"
              placeholder="John Doe"
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-gray-700 mb-1">Email</label>
            <input 
              type="email"
              {...register('email')}
              className="w-full touch-target border border-gray-300 rounded-lg px-4"
              placeholder="john@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-gray-700 mb-1">Password</label>
            <input 
              type="password"
              {...register('password')}
              className="w-full touch-target border border-gray-300 rounded-lg px-4"
              placeholder="••••••••"
            />
          </div>

          <button 
            type="submit" 
            disabled={isLoading}
            className="w-full touch-target bg-green-700 text-white rounded-lg font-bold text-lg hover:bg-green-800 mt-6"
          >
            {isLoading ? 'Creating Account...' : 'Complete Registration'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default RegisterForm;
