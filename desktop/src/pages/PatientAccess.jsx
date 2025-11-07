import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSessionStore } from '../store/sessionStore';
import apiClient from '../services/api';

function PatientAccess() {
  const navigate = useNavigate();
  const {
    state,
    accessRequestId,
    setAccessRequestId,
    onAccessGranted,
    onAccessDenied,
    onAccessExpired
  } = useSessionStore();

  const [iin, setIIN] = useState('');
  const [reason, setReason] = useState('Прием у врача');
  const [scopes, setScopes] = useState(['read_records', 'write_records']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pollingInterval, setPollingInterval] = useState(null);

  // Poll access request status
  useEffect(() => {
    if (accessRequestId && state === 'access_pending') {
      const interval = setInterval(async () => {
        try {
          const status = await apiClient.pollAccessRequestStatus(accessRequestId);
          
          if (status.status === 'approved') {
            // Access granted
            clearInterval(interval);
            apiClient.setGrantId(status.grant.grant_id);
            
            const patientContext = status.patient_context;
            onAccessGranted(
              status.grant.grant_id,
              patientContext,
              patientContext.visit_id,
              patientContext.appointment_id
            );
            
            navigate('/dictation');
          } else if (status.status === 'denied') {
            // Access denied
            clearInterval(interval);
            onAccessDenied();
          } else if (status.status === 'expired') {
            // Request expired
            clearInterval(interval);
            onAccessExpired();
          }
        } catch (err) {
          console.error('Polling error:', err);
        }
      }, 3000); // Poll every 3 seconds
      
      setPollingInterval(interval);
      
      return () => clearInterval(interval);
    }
  }, [accessRequestId, state]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // Search patient by IIN
      const patientSearch = await apiClient.searchPatientByIIN(iin);
      
      // Create access request
      const accessRequest = await apiClient.createAccessRequest({
        patient_iin: iin,
        scopes,
        reason,
        requested_duration_days: 1 // 1 day for desktop access
      });
      
      // Check if already approved (auto-approval mode)
      if (accessRequest.status === 'approved' && accessRequest.grant_id) {
        // Access already granted - skip polling, go directly to dictation
        const grantId = accessRequest.grant_id;
        apiClient.setGrantId(grantId);
        
        // Get patient data by grant
        const patientData = await apiClient.getPatientByGrant(grantId);
        
        onAccessGranted(
          grantId,
          patientData,
          patientData.visit_id,
          patientData.appointment_id
        );
        
        navigate('/dictation');
      } else {
        // Wait for approval via polling
        setAccessRequestId(accessRequest.id);
      }
    } catch (err) {
      console.error('Access request error:', err);
      setError(err.response?.data?.detail || err.message || 'Ошибка запроса доступа');
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    setAccessRequestId(null);
    setError(null);
    setIIN('');
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '600px', margin: '0 auto' }}>
      <h2 style={{ marginBottom: '2rem', color: '#2c3e50' }}>Запрос доступа к карте пациента</h2>

      {state === 'access_pending' ? (
        <div style={{
          backgroundColor: 'white',
          padding: '2rem',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          textAlign: 'center'
        }}>
          <div style={{
            width: '48px',
            height: '48px',
            border: '4px solid #3498db',
            borderTopColor: 'transparent',
            borderRadius: '50%',
            margin: '0 auto 1rem',
            animation: 'spin 1s linear infinite'
          }}></div>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#2c3e50' }}>Ожидание подтверждения пациента...</h3>
          <p style={{ margin: '0 0 1rem 0', color: '#7f8c8d' }}>
            На телефон пациента отправлен запрос с кодом подтверждения.
          </p>
          <p style={{ margin: '0 0 1.5rem 0', color: '#7f8c8d', fontSize: '0.875rem' }}>
            ID запроса: {accessRequestId}
          </p>
          <button
            onClick={handleRetry}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#e74c3c',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            Отменить
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} style={{
          backgroundColor: 'white',
          padding: '2rem',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          {error && (
            <div style={{
              backgroundColor: '#fee',
              color: '#c33',
              padding: '0.75rem',
              borderRadius: '4px',
              marginBottom: '1rem',
              fontSize: '0.875rem'
            }}>
              {error}
            </div>
          )}

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: '#2c3e50', fontWeight: '500' }}>
              ИИН пациента (12 цифр)
            </label>
            <input
              type="text"
              value={iin}
              onChange={(e) => setIIN(e.target.value.replace(/\D/g, '').slice(0, 12))}
              required
              disabled={loading}
              placeholder="000000000000"
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '1.125rem',
                fontFamily: 'monospace',
                letterSpacing: '2px'
              }}
            />
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: '#2c3e50', fontWeight: '500' }}>
              Причина запроса
            </label>
            <input
              type="text"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              required
              disabled={loading}
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '1rem'
              }}
            />
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: '#2c3e50', fontWeight: '500' }}>
              Запрашиваемые права
            </label>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {[
                { value: 'read_summary', label: 'Чтение краткой информации' },
                { value: 'read_records', label: 'Чтение медицинских записей' },
                { value: 'write_records', label: 'Создание медицинских записей' },
              ].map(scope => (
                <label key={scope.value} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                  <input
                    type="checkbox"
                    checked={scopes.includes(scope.value)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setScopes([...scopes, scope.value]);
                      } else {
                        setScopes(scopes.filter(s => s !== scope.value));
                      }
                    }}
                    disabled={loading}
                  />
                  <span>{scope.label}</span>
                </label>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || iin.length !== 12}
            style={{
              width: '100%',
              padding: '0.875rem',
              backgroundColor: (loading || iin.length !== 12) ? '#95a5a6' : '#3498db',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              fontSize: '1rem',
              fontWeight: '500',
              cursor: (loading || iin.length !== 12) ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? 'Отправка запроса...' : 'Запросить доступ'}
          </button>
        </form>
      )}

      <style>
        {`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
}

export default PatientAccess;

