import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { chatAPI } from '../services/api';
import ReactMarkdown from 'react-markdown';
import './Chat.css';

function Chat() {
  const { user, logout } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
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

  return (
    <div className="chat-container">
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
    </div>
  );
}

export default Chat;


