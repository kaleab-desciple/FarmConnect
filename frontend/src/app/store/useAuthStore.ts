import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi } from '../services/api';
import { api } from '../services/api';
import type { User } from '../../../shared/ts/user'; // Ensure this matches actual shared type location

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  login: (credentials: { email: string; password: string }) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (credentials) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.login(credentials);
          const { access_token, user } = response.data;
          
          // Set token in axial instance automatically
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false
          });
        } catch (error: any) {
          set({ 
            error: error.response?.data?.detail || 'Login failed. Please check your credentials.',
            isLoading: false 
          });
          throw error;
        }
      },

      logout: () => {
        delete api.defaults.headers.common['Authorization'];
        set({ user: null, token: null, isAuthenticated: false });
      },

      clearError: () => set({ error: null })
    }),
    {
      name: 'auth-storage',
      // Only persist the token and basic user info, not loading/error states
      partialize: (state) => ({ user: state.user, token: state.token, isAuthenticated: state.isAuthenticated })
    }
  )
);

// Subscribe to auth token changes to update axios default headers on reload
useAuthStore.subscribe((state) => {
  if (state.token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${state.token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
});
