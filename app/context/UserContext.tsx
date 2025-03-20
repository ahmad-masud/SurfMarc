'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  full_name: string;
  access_token: string;
  created_at: string;
}

interface UserContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
  updateProfile: (data: { full_name: string; email: string }) => Promise<void>;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session
    const token = localStorage.getItem('token');
    if (token) {
      fetchUserData(token);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserData = async (token: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/users/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        localStorage.removeItem('token');
      }
    } catch (error) {
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const response = await fetch('http://localhost:8000/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    localStorage.setItem('token', data.access_token);
    await fetchUserData(data.access_token);
  };

  const register = async (email: string, password: string, fullName: string) => {
    const response = await fetch('http://localhost:8000/api/v1/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password, full_name: fullName }),
    });

    if (!response.ok) {
      throw new Error('Registration failed');
    }

    const data = await response.json();
    localStorage.setItem('token', data.access_token);
    await fetchUserData(data.access_token);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  const updateProfile = async (data: { full_name: string; email: string }) => {
    const token = localStorage.getItem('token');
    if (!token) throw new Error('Not authenticated');

    const response = await fetch('http://localhost:8000/api/v1/users/me', {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Failed to update profile');
    }

    const updatedUser = await response.json();
    setUser(updatedUser);
  };

  return (
    <UserContext.Provider value={{ user, loading, login, register, logout, updateProfile }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
} 