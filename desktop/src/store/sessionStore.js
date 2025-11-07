import { create } from 'zustand';

// FSM states
const STATES = {
  IDLE: 'idle',
  ACCESS_PENDING: 'access_pending',
  ACCESS_GRANTED: 'access_granted',
  DICTATING: 'dictating',
  PAUSED: 'paused',
  REVIEW: 'review',
  SENDING: 'sending',
  COMPLETED: 'completed',
  ERROR: 'error'
};

export const useSessionStore = create((set, get) => ({
  // State
  state: STATES.IDLE,
  
  // Access request data
  accessRequestId: null,
  grantId: null,
  
  // Patient data
  patient: null,
  visitId: null,
  appointmentId: null,
  
  // Dictation data
  transcript: '',
  structuredData: {},
  audioDuration: 0,
  language: 'ru',
  
  // Error
  error: null,
  
  // Actions
  startAccessRequest: (iin) => {
    set({
      state: STATES.ACCESS_PENDING,
      error: null
    });
  },
  
  setAccessRequestId: (id) => set({ accessRequestId: id }),
  
  onAccessGranted: (grantId, patient, visitId, appointmentId) => {
    set({
      state: STATES.ACCESS_GRANTED,
      grantId,
      patient,
      visitId,
      appointmentId,
      error: null
    });
  },
  
  onAccessDenied: () => {
    set({
      state: STATES.IDLE,
      error: 'Доступ отклонён пациентом',
      accessRequestId: null
    });
  },
  
  onAccessExpired: () => {
    set({
      state: STATES.IDLE,
      error: 'Время ожидания истекло',
      accessRequestId: null
    });
  },
  
  startDictation: () => {
    set({
      state: STATES.DICTATING,
      transcript: '',
      audioDuration: 0,
      error: null
    });
  },
  
  pauseDictation: () => {
    if (get().state === STATES.DICTATING) {
      set({ state: STATES.PAUSED });
    }
  },
  
  resumeDictation: () => {
    if (get().state === STATES.PAUSED) {
      set({ state: STATES.DICTATING });
    }
  },
  
  updateTranscript: (text) => {
    set(state => ({
      transcript: state.transcript + ' ' + text
    }));
  },
  
  setTranscript: (text) => set({ transcript: text }),
  
  updateAudioDuration: (duration) => set({ audioDuration: duration }),
  
  finishDictation: () => {
    set({ state: STATES.REVIEW });
  },
  
  setStructuredData: (data) => set({ structuredData: data }),
  
  startSending: () => set({ state: STATES.SENDING }),
  
  onSendSuccess: () => {
    set({
      state: STATES.COMPLETED,
      error: null
    });
  },
  
  onSendError: (error) => {
    set({
      state: STATES.ERROR,
      error: error || 'Ошибка отправки'
    });
  },
  
  reset: () => {
    set({
      state: STATES.IDLE,
      accessRequestId: null,
      grantId: null,
      patient: null,
      visitId: null,
      appointmentId: null,
      transcript: '',
      structuredData: {},
      audioDuration: 0,
      language: 'ru',
      error: null
    });
  },
  
  setLanguage: (lang) => set({ language: lang }),
}));

export { STATES };

