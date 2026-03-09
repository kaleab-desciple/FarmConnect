import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { UserRole } from '../config/roles';

export interface User {
  id: string;
  email: string;
  name: string;
  phone?: string;
  role: UserRole;
  createdAt: string;
  metadata?: Record<string, unknown>;
}

interface AuthState {
  // State
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  lastActivity: number;
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setTokens: (token: string, refreshToken: string) => void;
  setUser: (user: User) => void;
  clearError: () => void;
  updateLastActivity: () => void;
  checkSession: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      lastActivity: Date.now(),
      
      // Login action
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/auth/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
          });
          
          if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Login failed');
          }
          
          const data = await response.json();
          
          set({
            user: data.user,
            token: data.access_token,
            refreshToken: data.refresh_token,
            isAuthenticated: true,
            isLoading: false,
            lastActivity: Date.now(),
          });
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : 'Login failed',
          });
          throw error;
        }
      },
      
      // Logout action
      logout: () => {
        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        });
      },
      
      // Set tokens (after refresh or initial login)
      setTokens: (token: string, refreshToken: string) => {
        set({ token, refreshToken });
      },
      
      // Set user directly
      setUser: (user: User) => {
        set({ user, isAuthenticated: true });
      },
      
      // Clear error
      clearError: () => {
        set({ error: null });
      },
      
      // Update last activity timestamp
      updateLastActivity: () => {
        set({ lastActivity: Date.now() });
      },
      
      // Check if session is still valid (within 24 hours)
      checkSession: () => {
        const { lastActivity, isAuthenticated } = get();
        const SESSION_TIMEOUT = 24 * 60 * 60 * 1000; // 24 hours
        
        if (!isAuthenticated) return false;
        
        if (Date.now() - lastActivity > SESSION_TIMEOUT) {
          get().logout();
          return false;
        }
        
        return true;
      },
    }),
    {
      name: 'farmconnect-auth',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Selectors
export const selectUser = (state: AuthState) => state.user;
export const selectIsAuthenticated = (state: AuthState) => state.isAuthenticated;
export const selectUserRole = (state: AuthState) => state.user?.role;
export const selectToken = (state: AuthState) => state.token;
