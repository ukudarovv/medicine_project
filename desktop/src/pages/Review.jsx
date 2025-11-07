import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSessionStore } from '../store/sessionStore';
import apiClient from '../services/api';

function Review() {
  const navigate = useNavigate();
  const {
    patient,
    visitId,
    transcript,
    audioDuration,
    language,
    setTranscript,
    setStructuredData,
    setLanguage,
    startSending,
    onSendSuccess,
    onSendError,
    reset
  } = useSessionStore();

  const [diagnosis, setDiagnosis] = useState('');
  const [recommendations, setRecommendations] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!transcript.trim()) {
      setError('Транскрипт не может быть пустым');
      return;
    }

    setError(null);
    setLoading(true);
    startSending();

    try {
      // Prepare structured data
      const structuredData = {};
      if (diagnosis) structuredData.diagnosis = diagnosis;
      if (recommendations) structuredData.recommendations = recommendations;

      setStructuredData(structuredData);

      // Save visit note
      await apiClient.saveVisitNote({
        visit_id: visitId,
        raw_transcript: transcript,
        structured_data: structuredData,
        language,
        audio_duration: audioDuration,
        metadata: {
          created_via: 'desktop_app',
          timestamp: new Date().toISOString()
        }
      });

      onSendSuccess();
      
      // Show success message
      alert('Запись успешно отправлена!');
      
      // Reset session and go to start
      reset();
      navigate('/patient-access');
    } catch (err) {
      console.error('Send error:', err);
      const errorMsg = err.response?.data?.detail || err.message || 'Ошибка отправки';
      setError(errorMsg);
      onSendError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/dictation');
  };

  if (!patient) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <p>Нет данных пациента.</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem', maxWidth: '900px', margin: '0 auto' }}>
      <h2 style={{ marginBottom: '1.5rem', color: '#2c3e50' }}>Просмотр и отправка записи</h2>

      {error && (
        <div style={{
          backgroundColor: '#fee',
          color: '#c33',
          padding: '1rem',
          borderRadius: '4px',
          marginBottom: '1.5rem'
        }}>
          {error}
        </div>
      )}

      {/* Patient info summary */}
      <div style={{
        backgroundColor: 'white',
        padding: '1rem',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        marginBottom: '1.5rem',
        fontSize: '0.875rem'
      }}>
        <strong>Пациент:</strong> {patient.full_name} • <strong>Возраст:</strong> {patient.age} лет • <strong>ИИН:</strong> {patient.iin_masked}
      </div>

      {/* Language selection */}
      <div style={{
        backgroundColor: 'white',
        padding: '1.5rem',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        marginBottom: '1.5rem'
      }}>
        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
          Язык диктовки
        </label>
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          disabled={loading}
          style={{
            padding: '0.75rem',
            border: '1px solid #ddd',
            borderRadius: '4px',
            fontSize: '1rem',
            width: '200px'
          }}
        >
          <option value="ru">Русский</option>
          <option value="kk">Қазақ</option>
        </select>
      </div>

      {/* Transcript */}
      <div style={{
        backgroundColor: 'white',
        padding: '1.5rem',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        marginBottom: '1.5rem'
      }}>
        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
          Транскрипт записи
        </label>
        <textarea
          value={transcript}
          onChange={(e) => setTranscript(e.target.value)}
          disabled={loading}
          placeholder="Редактируйте транскрипт при необходимости..."
          style={{
            width: '100%',
            minHeight: '200px',
            padding: '1rem',
            border: '1px solid #ddd',
            borderRadius: '4px',
            fontSize: '1rem',
            lineHeight: '1.6',
            fontFamily: 'inherit',
            resize: 'vertical'
          }}
        />
      </div>

      {/* Structured fields */}
      <div style={{
        backgroundColor: 'white',
        padding: '1.5rem',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        marginBottom: '1.5rem'
      }}>
        <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.125rem', color: '#2c3e50' }}>Структурированные данные (опционально)</h3>
        
        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
            Диагноз
          </label>
          <input
            type="text"
            value={diagnosis}
            onChange={(e) => setDiagnosis(e.target.value)}
            disabled={loading}
            placeholder="Диагноз..."
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '1rem'
            }}
          />
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
            Рекомендации
          </label>
          <textarea
            value={recommendations}
            onChange={(e) => setRecommendations(e.target.value)}
            disabled={loading}
            placeholder="Рекомендации для пациента..."
            style={{
              width: '100%',
              minHeight: '100px',
              padding: '0.75rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '1rem',
              lineHeight: '1.6',
              fontFamily: 'inherit',
              resize: 'vertical'
            }}
          />
        </div>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
        <button
          onClick={handleBack}
          disabled={loading}
          style={{
            padding: '0.875rem 2rem',
            backgroundColor: '#95a5a6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontSize: '1rem',
            fontWeight: '500',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          Назад
        </button>

        <button
          onClick={handleSubmit}
          disabled={loading || !transcript.trim()}
          style={{
            padding: '0.875rem 2rem',
            backgroundColor: loading || !transcript.trim() ? '#95a5a6' : '#27ae60',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontSize: '1rem',
            fontWeight: '500',
            cursor: loading || !transcript.trim() ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Отправка...' : 'Отправить в ERP'}
        </button>
      </div>
    </div>
  );
}

export default Review;

