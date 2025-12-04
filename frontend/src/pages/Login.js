import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Auth.css';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await login({ username, password });
      if (response.user.role === 'teacher') {
        navigate('/teacher');
      } else {
        navigate('/chat');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Đăng nhập thất bại');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <div className="auth-header">
          <h1>🎓 Chatbot Tâm Lý</h1>
          <p>Hỗ trợ tâm lý học sinh</p>
        </div>
        
        <form onSubmit={handleSubmit} className="auth-form">
          <h2>Đăng Nhập</h2>
          
          {error && <div className="error-message">{error}</div>}
          
          <div className="form-group">
            <label>Tên đăng nhập</label>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Nhập tên đăng nhập" required />
          </div>
          
          <div className="form-group">
            <label>Mật khẩu</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Nhập mật khẩu" required />
          </div>
          
          <button type="submit" disabled={loading} className="auth-button">
            {loading ? 'Đang đăng nhập...' : 'Đăng Nhập'}
          </button>
          
          <p className="auth-link">
            Chưa có tài khoản? <Link to="/register">Đăng ký ngay</Link>
          </p>
        </form>
      </div>
    </div>
  );
}

export default Login;
