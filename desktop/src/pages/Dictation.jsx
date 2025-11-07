import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSessionStore } from '../store/sessionStore';

function Dictation() {
  const navigate = useNavigate();
  const {
    state,
    patient,
    visitId,
    transcript,
    updateTranscript,
    setTranscript,
    startDictation,
    pauseDictation,
    resumeDictation,
    finishDictation
  } = useSessionStore();

  const [isRecording, setIsRecording] = useState(false);
  const [startTime, setStartTime] = useState(null);
  const [duration, setDuration] = useState(0);

  // Timer
  useEffect(() => {
    let interval;
    if (isRecording && startTime) {
      interval = setInterval(() => {
        setDuration(Math.floor((Date.now() - startTime) / 1000));
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isRecording, startTime]);

  const handleStartRecording = () => {
    startDictation();
    setIsRecording(true);
    setStartTime(Date.now());
  };

  const handlePauseRecording = () => {
    pauseDictation();
    setIsRecording(false);
  };

  const handleResumeRecording = () => {
    resumeDictation();
    setIsRecording(true);
    setStartTime(Date.now() - duration * 1000);
  };

  const handleStopAndReview = () => {
    finishDictation();
    setIsRecording(false);
    navigate('/review');
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!patient) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <p>Нет данных пациента. Вернитесь к запросу доступа.</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem', maxWidth: '900px', margin: '0 auto' }}>
      {/* Patient info */}
      <div style={{
        backgroundColor: 'white',
        padding: '1.5rem',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        marginBottom: '1.5rem'
      }}>
        <h3 style={{ margin: '0 0 1rem 0', color: '#2c3e50' }}>Информация о пациенте</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.875rem' }}>
          <div>
            <strong>ФИО:</strong> {patient.full_name}
          </div>
          <div>
            <strong>Возраст:</strong> {patient.age} лет
          </div>
          <div>
            <strong>Дата рождения:</strong> {patient.birth_date}
          </div>
          <div>
            <strong>ИИН:</strong> {patient.iin_masked}
          </div>
        </div>
      </div>

      {/* Recording controls */}
      <div style={{
        backgroundColor: 'white',
        padding: '2rem',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        marginBottom: '1.5rem',
        textAlign: 'center'
      }}>
        <div style={{
          fontSize: '3rem',
          fontWeight: 'bold',
          color: isRecording ? '#e74c3c' : '#95a5a6',
          marginBottom: '1rem',
          fontVariantNumeric: 'tabular-nums'
        }}>
          {formatDuration(duration)}
        </div>

        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '1rem',
          marginBottom: '1.5rem'
        }}>
          {!isRecording && state === 'dictating' && (
            <button
              onClick={handleResumeRecording}
              style={{
                padding: '1rem 2rem',
                backgroundColor: '#2ecc71',
                color: 'white',
                border: 'none',
                borderRadius: '50px',
                fontSize: '1.125rem',
                fontWeight: '500',
                cursor: 'pointer',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
              }}
            >
              ▶ Продолжить
            </button>
          )}

          {!isRecording && state !== 'dictating' && (
            <button
              onClick={handleStartRecording}
              style={{
                padding: '1rem 2rem',
                backgroundColor: '#e74c3c',
                color: 'white',
                border: 'none',
                borderRadius: '50px',
                fontSize: '1.125rem',
                fontWeight: '500',
                cursor: 'pointer',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
              }}
            >
              ● Начать запись
            </button>
          )}

          {isRecording && (
            <button
              onClick={handlePauseRecording}
              style={{
                padding: '1rem 2rem',
                backgroundColor: '#f39c12',
                color: 'white',
                border: 'none',
                borderRadius: '50px',
                fontSize: '1.125rem',
                fontWeight: '500',
                cursor: 'pointer',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
              }}
            >
              ‖ Пауза
            </button>
          )}

          {state === 'dictating' && (
            <button
              onClick={handleStopAndReview}
              style={{
                padding: '1rem 2rem',
                backgroundColor: '#3498db',
                color: 'white',
                border: 'none',
                borderRadius: '50px',
                fontSize: '1.125rem',
                fontWeight: '500',
                cursor: 'pointer',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
              }}
            >
              ■ Завершить
            </button>
          )}
        </div>

        <div style={{ fontSize: '0.875rem', color: '#7f8c8d' }}>
          {isRecording ? (
            <span style={{ color: '#e74c3c' }}>● Идёт запись...</span>
          ) : state === 'dictating' ? (
            'Запись на паузе'
          ) : (
            'Готов к началу записи'
          )}
        </div>
      </div>

      {/* Live transcript */}
      <div style={{
        backgroundColor: 'white',
        padding: '1.5rem',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <h3 style={{ margin: '0 0 1rem 0', color: '#2c3e50' }}>Транскрипт</h3>
        <textarea
          value={transcript}
          onChange={(e) => setTranscript(e.target.value)}
          placeholder="Транскрипт появится здесь во время диктовки..."
          readOnly={isRecording}
          style={{
            width: '100%',
            minHeight: '300px',
            padding: '1rem',
            border: '1px solid #ddd',
            borderRadius: '4px',
            fontSize: '1rem',
            lineHeight: '1.6',
            fontFamily: 'inherit',
            resize: 'vertical'
          }}
        />
        <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.75rem', color: '#7f8c8d', fontStyle: 'italic' }}>
          Примечание: В полной версии здесь будет real-time распознавание речи через Vosk
        </p>
      </div>
    </div>
  );
}

export default Dictation;

