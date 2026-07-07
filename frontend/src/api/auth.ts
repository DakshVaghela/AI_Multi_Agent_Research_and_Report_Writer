import { apiClient } from './client';

export interface AuthUser {
  id: string;
  name: string;
  email: string;
}

const SESSION_KEY = 'nexus_session_user';

export async function signup(name: string, email: string, password: string): Promise<AuthUser> {
  const response = await apiClient.post<AuthUser>('/auth/signup', {
    name,
    email,
    password,
  });
  
  const user = response.data;
  localStorage.setItem(SESSION_KEY, JSON.stringify(user));
  return user;
}

export async function login(email: string, password: string): Promise<AuthUser> {
  const response = await apiClient.post<AuthUser>('/auth/login', {
    email,
    password,
  });

  const user = response.data;
  localStorage.setItem(SESSION_KEY, JSON.stringify(user));
  return user;
}

export function logout(): void {
  localStorage.removeItem(SESSION_KEY);
}

export function getCurrentUser(): AuthUser | null {
  const userJson = localStorage.getItem(SESSION_KEY);
  if (!userJson) return null;
  try {
    return JSON.parse(userJson);
  } catch {
    return null;
  }
}
