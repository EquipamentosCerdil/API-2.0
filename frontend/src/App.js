import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dashboardData, setDashboardData] = useState(null);

  // Verificar se já está logado ao carregar a página
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      verifyToken(token);
    }
  }, []);

  const verifyToken = async (token) => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/verify-token`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.data.authenticated) {
        setIsAuthenticated(true);
        loadDashboard(token);
      }
    } catch (error) {
      localStorage.removeItem('auth_token');
      setIsAuthenticated(false);
    }
  };

  const loadDashboard = async (token) => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/dashboard`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setDashboardData(response.data);
    } catch (error) {
      console.error('Erro ao carregar dashboard:', error);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${BACKEND_URL}/api/login`, {
        username: username,
        password: password
      });

      const { access_token } = response.data;
      localStorage.setItem('auth_token', access_token);
      setIsAuthenticated(true);
      
      // Limpar campos
      setUsername('');
      setPassword('');
      
      // Carregar dashboard
      loadDashboard(access_token);
      
    } catch (error) {
      setError(error.response?.data?.detail || 'Erro ao fazer login');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    setIsAuthenticated(false);
    setDashboardData(null);
    setUsername('');
    setPassword('');
  };

  if (isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-100">
        <div className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <h1 className="text-3xl font-bold text-gray-900">Dashboard Admin</h1>
              <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
              >
                Logout
              </button>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
              {dashboardData ? (
                <div className="text-center">
                  <h2 className="text-2xl font-bold text-green-600 mb-4">
                    ✅ Login realizado com sucesso!
                  </h2>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                    <p className="text-lg text-gray-700 mb-2">
                      <strong>Mensagem:</strong> {dashboardData.message}
                    </p>
                    <p className="text-sm text-gray-500">
                      <strong>Usuário:</strong> {dashboardData.user}
                    </p>
                    <p className="text-sm text-gray-500">
                      <strong>Timestamp:</strong> {new Date(dashboardData.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <div className="mt-6">
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">
                      🎉 Sistema de Login Funcionando Perfeitamente!
                    </h3>
                    <p className="text-gray-600">
                      Você está autenticado e pode acessar o sistema.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="mt-4 text-gray-600">Carregando dashboard...</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Login do Sistema
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Digite suas credenciais para acessar
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <form className="space-y-6" onSubmit={handleLogin}>
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                Usuário
              </label>
              <div className="mt-1">
                <input
                  id="username"
                  name="username"
                  type="text"
                  autoComplete="username"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="Digite: admin"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Senha
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="Digite: admin"
                />
              </div>
            </div>

            {error && (
              <div className="rounded-md bg-red-50 p-4">
                <div className="text-sm text-red-800">
                  {error}
                </div>
              </div>
            )}

            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
              <p className="text-sm text-blue-800">
                <strong>Credenciais de teste:</strong><br />
                Usuário: <code className="bg-blue-100 px-1 rounded">admin</code><br />
                Senha: <code className="bg-blue-100 px-1 rounded">admin</code>
              </p>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {loading ? 'Entrando...' : 'Entrar'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;
