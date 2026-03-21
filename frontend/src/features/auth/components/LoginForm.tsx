import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate } from 'react-router-dom';
import { loginSchema } from '@utils/validation';
import { useAuthStore } from '@/app/store/useAuthStore';
import { z } from 'zod';

type LoginValues = z.infer<typeof loginSchema>;

const LoginForm: React.FC = () => {
  const navigate = useNavigate();
  const { login, isLoading, error, clearError } = useAuthStore();

  const { register, handleSubmit, formState: { errors } } = useForm<LoginValues>({
    resolver: zodResolver(loginSchema)
  });

  const onSubmit = async (data: LoginValues) => {
    try {
      await login(data);
      // Determine dashboard based on role
      const role = useAuthStore.getState().user?.role;
      if (role === 'FARMER') navigate('/farmer/dashboard');
      else if (role === 'MERCHANT') navigate('/merchant/marketplace');
      else if (role === 'DELIVERY') navigate('/delivery/available');
      else navigate('/'); // Fallback
    } catch (err) {
      // Error is handled in the store
    }
  };

  return (
    <div className="w-full max-w-md bg-white rounded-2xl shadow-xl overflow-hidden">
      <div className="bg-green-800 p-6 text-center">
        <h1 className="text-3xl font-bold text-white mb-2">FarmConnect</h1>
        <p className="text-green-100/80">Login to your account</p>
      </div>

      <div className="p-8">
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded">
            <div className="flex justify-between">
              <p className="text-sm text-red-700 font-medium">{error}</p>
              <button onClick={clearError} className="text-red-500 hover:text-red-700">×</button>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-2">Email Address</label>
            <input 
              type="email"
              {...register('email')}
              className="w-full touch-target border border-gray-300 rounded-lg px-4 focus:ring-2 focus:ring-green-500 focus:border-green-500"
              placeholder="farmer@example.com"
            />
            {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-bold text-gray-700 mb-2">Password</label>
            <input 
              type="password"
              {...register('password')}
              className="w-full touch-target border border-gray-300 rounded-lg px-4 focus:ring-2 focus:ring-green-500 focus:border-green-500"
              placeholder="••••••••"
            />
            {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password.message}</p>}
          </div>

          <button 
            type="submit" 
            disabled={isLoading}
            className="w-full touch-target bg-green-700 text-white rounded-lg font-bold text-lg hover:bg-green-800 disabled:opacity-50 transition-colors shadow-md mt-4"
          >
            {isLoading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Don't have an account?{' '}
            <button className="text-green-700 font-bold hover:underline">
              Register here
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;
