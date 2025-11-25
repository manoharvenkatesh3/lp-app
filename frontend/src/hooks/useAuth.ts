import { create } from 'zustand';
import { User, UserRole } from '@/types';
import { tokenStorage } from '@/utils/tokenStorage';
import { authService } from '@/services/auth';

interface AuthState {
  user: User | null;
  role: UserRole | null;
  permissions: string[];
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
  hasPermission: (permission: string) => boolean;
}

export const useAuth = create<AuthState>((set, get) => ({
  user: null,
  role: null,
  permissions: [],
  isAuthenticated: false,
  isLoading: true,

  login: async (email: string, password: string) => {
    try {
      const tokens = await authService.login(email, password);
      tokenStorage.setTokens(tokens.access_token, tokens.refresh_token);
      
      const user = await authService.getCurrentUser();
      const roleData = await authService.detectRole();
      
      set({
        user,
        role: roleData.role,
        permissions: roleData.permissions,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      tokenStorage.clearTokens();
      throw error;
    }
  },

  logout: () => {
    tokenStorage.clearTokens();
    set({
      user: null,
      role: null,
      permissions: [],
      isAuthenticated: false,
    });
  },

  loadUser: async () => {
    if (!tokenStorage.hasToken()) {
      set({ isLoading: false, isAuthenticated: false });
      return;
    }

    try {
      const user = await authService.getCurrentUser();
      const roleData = await authService.detectRole();
      
      set({
        user,
        role: roleData.role,
        permissions: roleData.permissions,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      tokenStorage.clearTokens();
      set({ isLoading: false, isAuthenticated: false });
    }
  },

  hasPermission: (permission: string) => {
    const { permissions } = get();
    return permissions.includes(permission);
  },
}));
