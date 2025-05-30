import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const baseURL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Configurar axios com o token
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Verificar se o token ainda é válido
      fetchUserData();
    } else {
      delete axios.defaults.headers.common['Authorization'];
      setLoading(false);
    }
  }, [token]);

  const fetchUserData = async () => {
    try {
      const response = await axios.get(`${baseURL}/api/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Erro ao buscar dados do usuário:', error);
      logout(); // Token inválido, fazer logout
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      // Use URLSearchParams for application/x-www-form-urlencoded format
      const params = new URLSearchParams();
      params.append('username', username);
      params.append('password', password);

      console.log('Tentando login com:', { username, password });
      console.log('URL da API:', `${baseURL}/api/login`);
      
      const response = await axios.post(`${baseURL}/api/login`, params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      console.log('Resposta do login:', response.data);
      
      const { access_token } = response.data;
      setToken(access_token);
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Buscar dados do usuário após login
      await fetchUserData();
      
      return { success: true };
    } catch (error) {
      console.error('Erro no login:', error);
      console.error('Detalhes do erro:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Erro ao fazer login' 
      };
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
  };

  const value = {
    token,
    user,
    login,
    logout,
    loading,
    isAuthenticated: !!token && !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
