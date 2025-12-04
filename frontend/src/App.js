import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Chat from './pages/Chat';
import TeacherDashboard from './pages/TeacherDashboard';
import { AuthProvider, useAuth } from './context/AuthContext';
import './App.css';

function PrivateRoute({ children, teacherOnly = false }) {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div className="loading">Đang tải...</div>;
  }
  
  if (!user) {
    return <Navigate to="/login" />;
  }
  
  if (teacherOnly && user.role !== 'teacher') {
    return <Navigate to="/chat" />;
  }
  
  return children;
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route 
              path="/chat" 
              element={
                <PrivateRoute>
                  <Chat />
                </PrivateRoute>
              } 
            />
            <Route 
              path="/teacher" 
              element={
                <PrivateRoute teacherOnly={true}>
                  <TeacherDashboard />
                </PrivateRoute>
              } 
            />
            <Route path="/" element={<Navigate to="/chat" />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;



