'use client';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { getAuthToken, removeAuthToken, setAuthToken } from '@/lib/utils';
import type { User } from '@/types/api';

export function useAuth() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getAuthToken();
    if (!token) {
      setLoading(false);
      return;
    }
    (api.me() as Promise<User>).then((u) => {
      setUser(u);
      setLoading(false);
    }).catch(() => {
      removeAuthToken();
      setLoading(false);
    });
  }, []);

  const login = async (username: string, password: string) => {
    const data = await api.login(username, password);
    setAuthToken(data.access_token);
    const u = await api.me() as User;
    setUser(u);
    router.push('/');
  };

  const logout = async () => {
    await api.logout().catch(() => {});
    removeAuthToken();
    setUser(null);
    router.push('/login');
  };

  return { user, loading, login, logout };
}
