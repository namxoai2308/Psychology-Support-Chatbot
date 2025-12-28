import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { chatAPI, default as api } from '../services/api';
import ReactMarkdown from 'react-markdown';
import './Chat.css';

function Chat() {
  const { user, logout } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(window.innerWidth > 768);
  const [showRatingPopup, setShowRatingPopup] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 768) setSidebarOpen(true);
      else setSidebarOpen(false);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadSessions = async () => {
    try {
      const response = await chatAPI.getSessions();
      setSessions(response.data);
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };

  const loadSession = async (sessionId) => {
    try {
      const response = await chatAPI.getSession(sessionId);
      setCurrentSession(response.data);
      setMessages(response.data.messages || []);
      // Check rating popup when loading session
      checkRatingPopup();
    } catch (error) {
      console.error('Error loading session:', error);
    }
  };

  const createNewChat = async () => {
    try {
      const response = await chatAPI.createSession({ title: 'Cuộc trò chuyện mới' });
      setSessions([response.data, ...sessions]);
      setCurrentSession(response.data);
      setMessages([]);
    } catch (error) {
      console.error('Error creating session:', error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || loading) return;

    let sessionToUse = currentSession;

    if (!sessionToUse) {
      try {
        const response = await chatAPI.createSession({ title: 'Cuộc trò chuyện mới' });
        sessionToUse = response.data;
        setCurrentSession(response.data);
        setSessions([response.data, ...sessions]);
      } catch (error) {
        console.error('Error creating session:', error);
        return;
      }
    }

    const userMessage = {
      role: 'user',
      content: inputMessage,
      created_at: new Date().toISOString(),
    };

    setMessages([...messages, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await chatAPI.sendMessage(sessionToUse.id, { content: inputMessage });
      setMessages((prev) => [...prev, response.data]);
      loadSessions();
      
      // Check if should show rating popup
      checkRatingPopup();
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkRatingPopup = async () => {
    try {
      const response = await chatAPI.getMessageCount();
      if (response.data.should_show_rating) {
        // Check localStorage to avoid showing multiple times
        const hasShownRating = localStorage.getItem(`rating_shown_${user.id}`);
        if (!hasShownRating) {
          setShowRatingPopup(true);
        }
      }
    } catch (error) {
      console.error('Error checking rating popup:', error);
    }
  };

  const deleteSession = async (sessionId) => {
    if (!window.confirm('Bạn có chắc muốn xóa cuộc trò chuyện này?')) return;
    try {
      await chatAPI.deleteSession(sessionId);
      setSessions(sessions.filter((s) => s.id !== sessionId));
      if (currentSession?.id === sessionId) {
        setCurrentSession(null);
        setMessages([]);
      }
    } catch (error) {
      console.error('Error deleting session:', error);
    }
  };

  const handleRatingSubmit = async (rating, feedback) => {
    try {
      await chatAPI.submitRating({ rating, feedback });
      setShowRatingPopup(false);
      // Mark as shown in localStorage
      localStorage.setItem(`rating_shown_${user.id}`, 'true');
    } catch (error) {
      console.error('Error submitting rating:', error);
    }
  };

  const handleRatingClose = () => {
    setShowRatingPopup(false);
    // Mark as shown even if user closes without rating
    localStorage.setItem(`rating_shown_${user.id}`, 'true');
  };

  const openPDF = async (documentId, filename) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        alert('Vui lòng đăng nhập lại');
        return;
      }
      
      // Use same base URL as api.js
      const apiUrl = process.env.REACT_APP_API_URL || 'https://psychology-support-chatbot.onrender.com';
      const url = `${apiUrl}/api/documents/${documentId}/download?inline=true`;
      
      // Fetch PDF with token first
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`Failed to load PDF: ${response.status} ${response.statusText}`);
      }
      
      // Create blob
      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      
      // Open new tab with blob URL
      const newWindow = window.open(blobUrl, '_blank', 'noopener,noreferrer');
      
      if (!newWindow) {
        // If popup blocked, try to open in same window
        window.location.href = blobUrl;
        return;
      }
      
      // Clean up blob URL when window closes
      const checkClosed = setInterval(() => {
        if (newWindow.closed) {
          window.URL.revokeObjectURL(blobUrl);
          clearInterval(checkClosed);
        }
      }, 1000);
      
      // Also clean up after 10 minutes as fallback
      setTimeout(() => {
        window.URL.revokeObjectURL(blobUrl);
        clearInterval(checkClosed);
      }, 600000);
      
    } catch (error) {
      console.error('Error opening PDF:', error);
      alert(`Không thể mở PDF: ${error.message}`);
    }
  };

  return (
    <div className="chat-container">
      {sidebarOpen && window.innerWidth <= 768 && (
        <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />
      )}
      <div className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <button className="new-chat-btn" onClick={createNewChat}>
            + Cuộc trò chuyện mới
          </button>
        </div>

        <div className="sessions-list">
          {sessions.map((session) => (
            <div
              key={session.id}
              className={`session-item ${currentSession?.id === session.id ? 'active' : ''}`}
              onClick={() => loadSession(session.id)}
            >
              <div className="session-title">{session.title}</div>
              <div className="session-actions">
                <button className="delete-btn" onClick={(e) => { e.stopPropagation(); deleteSession(session.id); }}>
                  🗑️
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-name">{user?.full_name || user?.username}</div>
            <div className="user-role">{user?.role === 'teacher' ? '👨‍🏫 Giáo viên' : '👨‍🎓 Học sinh'}</div>
          </div>
          <button className="logout-btn" onClick={logout}>Đăng xuất</button>
        </div>
      </div>

      <div className="chat-main">
        <div className="chat-header">
          <button className="sidebar-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>☰</button>
          <h2>{currentSession?.title || 'Chatbot Tâm Lý Học Sinh'}</h2>
        </div>

        <div className="messages-container">
          {messages.length === 0 && !currentSession && (
            <div className="welcome-message">
              <h1>🎓 Chatbot Tâm Lý</h1>
              <p>Xin chào! Tôi là chatbot hỗ trợ tâm lý cho học sinh. Bạn có thể chia sẻ mọi vấn đề với tôi.</p>
            </div>
          )}

          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-avatar">{message.role === 'user' ? '👤' : '🤖'}</div>
              <div className="message-content">
                <ReactMarkdown>{message.content}</ReactMarkdown>
                {message.sources && message.sources.length > 0 && (
                  <div className="message-sources">
                    <div className="sources-label">Tài liệu tham khảo:</div>
                    {message.sources.map((source, idx) => (
                      <button
                        key={idx}
                        onClick={() => openPDF(source.id, source.filename)}
                        className="source-link"
                        type="button"
                      >
                        📄 {source.filename}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="message assistant">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <form onSubmit={sendMessage} className="input-form">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Nhập tin nhắn của bạn..."
              disabled={loading}
            />
            <button type="submit" disabled={loading || !inputMessage.trim()}>
              {loading ? '⏳' : '➤'}
            </button>
          </form>
        </div>
      </div>

      {showRatingPopup && (
        <RatingPopup
          onClose={handleRatingClose}
          onSubmit={handleRatingSubmit}
        />
      )}
    </div>
  );
}

function RatingPopup({ onClose, onSubmit }) {
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [feedback, setFeedback] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (rating === 0) {
      alert('Vui lòng chọn số sao đánh giá');
      return;
    }
    setSubmitting(true);
    await onSubmit(rating, feedback || null);
    setSubmitting(false);
  };

  return (
    <div className="rating-popup-overlay" onClick={onClose}>
      <div className="rating-popup" onClick={(e) => e.stopPropagation()}>
        <button className="rating-popup-close" onClick={onClose}>×</button>
        <h3>Đánh giá Chatbot</h3>
        <p>Bạn hài lòng với trải nghiệm sử dụng chatbot không?</p>
        
        <div className="rating-stars">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              className={`star ${star <= (hoverRating || rating) ? 'active' : ''}`}
              onClick={() => setRating(star)}
              onMouseEnter={() => setHoverRating(star)}
              onMouseLeave={() => setHoverRating(0)}
              type="button"
            >
              ★
            </button>
          ))}
        </div>

        <textarea
          className="rating-feedback"
          placeholder="Chia sẻ thêm ý kiến của bạn (tùy chọn)..."
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          rows="3"
        />

        <div className="rating-popup-actions">
          <button className="rating-submit-btn" onClick={handleSubmit} disabled={submitting || rating === 0}>
            {submitting ? 'Đang gửi...' : 'Gửi đánh giá'}
          </button>
          <button className="rating-skip-btn" onClick={onClose}>
            Bỏ qua
          </button>
        </div>
      </div>
    </div>
  );
}

export default Chat;


