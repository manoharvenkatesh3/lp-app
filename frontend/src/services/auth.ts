import api from './api';
import { User, AuthTokens, UserRole } from '@/types';

export const authService = {
  async login(email: string, password: string): Promise<AuthTokens> {
    const response = await api.post<AuthTokens>('/auth/login', { email, password });
    return response.data;
  },

  async register(email: string, username: string, password: string, role: UserRole): Promise<User> {
    const response = await api.post<User>('/auth/register', { email, username, password, role });
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  async detectRole(): Promise<{ role: UserRole; permissions: string[] }> {
    const response = await api.get('/auth/role');
    return response.data;
  },
};
