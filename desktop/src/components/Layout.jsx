import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useSessionStore } from '../store/sessionStore';

function Layout() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { state, reset } = useSessionStore();

  const handleLogout = () => {
    logout();
    reset();
    navigate('/login');
  };

  const handleReset = () => {
    reset();
    navigate('/patient-access');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Header */}
      <header style={{
        backgroundColor: '#2c3e50',
        color: 'white',
        padding: '1rem 2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '1.5rem' }}>Медицинская диктовка</h1>
          <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem', opacity: 0.8 }}>
            {user?.full_name || user?.username} • {user?.organization_name}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <div style={{
            backgroundColor: 'rgba(255,255,255,0.1)',
            padding: '0.5rem 1rem',
            borderRadius: '4px',
            fontSize: '0.875rem'
          }}>
            Статус: {state === 'idle' ? 'Ожидание' : state === 'access_pending' ? 'Запрос доступа' : state === 'access_granted' ? 'Доступ выдан' : state === 'dictating' ? 'Диктовка' : state === 'paused' ? 'Пауза' : state === 'review' ? 'Просмотр' : state === 'sending' ? 'Отправка' : state === 'completed' ? 'Завершено' : 'Ошибка'}
          </div>
          {state !== 'idle' && state !== 'access_pending' && (
            <button
              onClick={handleReset}
              style={{
                backgroundColor: '#e74c3c',
                color: 'white',
                border: 'none',
                padding: '0.5rem 1rem',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.875rem'
              }}
            >
              Новый приём
            </button>
          )}
          <button
            onClick={handleLogout}
            style={{
              backgroundColor: 'transparent',
              color: 'white',
              border: '1px solid white',
              padding: '0.5rem 1rem',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.875rem'
            }}
          >
            Выход
          </button>
        </div>
      </header>

      {/* Main content */}
      <main style={{ flex: 1, overflow: 'auto', backgroundColor: '#ecf0f1' }}>
        <Outlet />
      </main>
    </div>
  );
}

export default Layout;

