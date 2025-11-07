import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';

// Pages
import Login from './pages/Login';
import PatientAccess from './pages/PatientAccess';
import Dictation from './pages/Dictation';
import Review from './pages/Review';

// Components
import Layout from './components/Layout';

function App() {
  const { token, user } = useAuthStore();
  const isAuthenticated = !!token && !!user;

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      
      {/* Protected routes */}
      {isAuthenticated ? (
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/patient-access" replace />} />
          <Route path="patient-access" element={<PatientAccess />} />
          <Route path="dictation" element={<Dictation />} />
          <Route path="review" element={<Review />} />
        </Route>
      ) : (
        <Route path="*" element={<Navigate to="/login" replace />} />
      )}
    </Routes>
  );
}

export default App;

