import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { teacherAPI, documentAPI } from '../services/api';
import ReactMarkdown from 'react-markdown';
import './TeacherDashboard.css';

function TeacherDashboard() {
  const { user, logout } = useAuth();
  const [students, setStudents] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [selectedSession, setSelectedSession] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('students');
  const [documents, setDocuments] = useState([]);
  const [uploadingDoc, setUploadingDoc] = useState(false);
  const [ratings, setRatings] = useState([]);
  const [ratingStats, setRatingStats] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(window.innerWidth > 768);

  useEffect(() => {
    loadStudentsHistory();
    loadDocuments();
    loadRatings();
  }, []);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 768) setSidebarOpen(true);
      else setSidebarOpen(false);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const loadStudentsHistory = async () => {
    setLoading(true);
    try {
      const response = await teacherAPI.getAllStudentsHistory();
      setStudents(response.data);
    } catch (error) {
      console.error('Error loading students:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadDocuments = async () => {
    try {
      const response = await documentAPI.getDocuments();
      setDocuments(response.data);
    } catch (error) {
      console.error('Error loading documents:', error);
    }
  };

  const loadRatings = async () => {
    try {
      const [ratingsRes, statsRes] = await Promise.all([
        teacherAPI.getAllRatings(),
        teacherAPI.getRatingStats()
      ]);
      setRatings(ratingsRes.data);
      setRatingStats(statsRes.data);
    } catch (error) {
      console.error('Error loading ratings:', error);
    }
  };

  const viewSessionDetails = async (sessionId) => {
    try {
      const response = await teacherAPI.getSessionDetails(sessionId);
      setSelectedSession(response.data);
    } catch (error) {
      console.error('Error loading session details:', error);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    if (!file.name.endsWith('.pdf')) {
      alert('Chỉ chấp nhận file PDF');
      return;
    }

    setUploadingDoc(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      await documentAPI.upload(formData);
      alert('Upload tài liệu thành công!');
      loadDocuments();
    } catch (error) {
      console.error('Error uploading document:', error);
      alert('Upload thất bại: ' + (error.response?.data?.detail || 'Lỗi không xác định'));
    } finally {
      setUploadingDoc(false);
      event.target.value = '';
    }
  };

  return (
    <div className="teacher-dashboard">
      {sidebarOpen && window.innerWidth <= 768 && (
        <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />
      )}
      <div className={`teacher-sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header-mobile">
          <button className="sidebar-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>☰</button>
          <h2>👨‍🏫 Dashboard</h2>
        </div>
        <div className="teacher-header">
          <h2>👨‍🏫 Dashboard Giáo Viên</h2>
        </div>

        <div className="teacher-tabs">
          <button className={`tab-btn ${activeTab === 'students' ? 'active' : ''}`} onClick={() => setActiveTab('students')}>
            👥 Học Sinh
          </button>
          <button className={`tab-btn ${activeTab === 'documents' ? 'active' : ''}`} onClick={() => setActiveTab('documents')}>
            📄 Tài Liệu
          </button>
          <button className={`tab-btn ${activeTab === 'ratings' ? 'active' : ''}`} onClick={() => setActiveTab('ratings')}>
            ⭐ Đánh Giá
          </button>
        </div>

        {activeTab === 'students' && (
          <div className="students-list">
            {loading ? (
              <div className="loading">Đang tải...</div>
            ) : (
              students.map((student) => (
                <div
                  key={student.user_id}
                  className={`student-item ${selectedStudent?.user_id === student.user_id ? 'active' : ''}`}
                  onClick={() => { setSelectedStudent(student); setSelectedSession(null); }}
                >
                  <div className="student-info">
                    <div className="student-name">{student.full_name || student.username}</div>
                    <div className="student-email">{student.email}</div>
                  </div>
                  <div className="student-stats">{student.sessions.length} cuộc trò chuyện</div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="documents-section">
            <div className="upload-section">
              <label className="upload-btn">
                {uploadingDoc ? 'Đang upload...' : '📤 Upload PDF'}
                <input type="file" accept=".pdf" onChange={handleFileUpload} disabled={uploadingDoc} style={{ display: 'none' }} />
              </label>
              <p className="upload-note">Upload file PDF về trường để chatbot có thể trả lời câu hỏi</p>
            </div>

            <div className="documents-list">
              <h3>Tài liệu đã upload</h3>
              {documents.length === 0 ? (
                <p className="no-docs">Chưa có tài liệu nào</p>
              ) : (
                documents.map((doc) => (
                  <div key={doc.id} className="document-item">
                    <div className="doc-icon">📄</div>
                    <div className="doc-info">
                      <div className="doc-name">{doc.filename}</div>
                      <div className="doc-date">{new Date(doc.uploaded_at).toLocaleString('vi-VN')}</div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {activeTab === 'ratings' && (
          <div className="ratings-section">
            {ratingStats && (
              <div className="rating-stats-card">
                <h3>Thống kê đánh giá</h3>
                <div className="stats-grid">
                  <div className="stat-item">
                    <div className="stat-value">{ratingStats.total_ratings}</div>
                    <div className="stat-label">Tổng đánh giá</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-value">{ratingStats.average_rating || 0}</div>
                    <div className="stat-label">Điểm trung bình</div>
                  </div>
                </div>
                <div className="rating-distribution">
                  <h4>Phân bố đánh giá</h4>
                  {[5, 4, 3, 2, 1].map((star) => (
                    <div key={star} className="distribution-item">
                      <span className="star-label">{star} sao</span>
                      <div className="distribution-bar">
                        <div 
                          className="distribution-fill"
                          style={{ 
                            width: ratingStats.total_ratings > 0 
                              ? `${(ratingStats.rating_distribution[star] / ratingStats.total_ratings) * 100}%` 
                              : '0%' 
                          }}
                        />
                      </div>
                      <span className="distribution-count">{ratingStats.rating_distribution[star] || 0}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="ratings-list">
              <h3>Đánh giá gần đây</h3>
              {ratings.length === 0 ? (
                <p className="no-ratings">Chưa có đánh giá nào</p>
              ) : (
                ratings.map((rating) => (
                  <div key={rating.id} className="rating-item">
                    <div className="rating-header">
                      <div className="rating-stars-display">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <span key={star} className={star <= rating.rating ? 'star-filled' : 'star-empty'}>★</span>
                        ))}
                      </div>
                      <div className="rating-date">{new Date(rating.created_at).toLocaleString('vi-VN')}</div>
                    </div>
                    {rating.feedback && (
                      <div className="rating-feedback-text">{rating.feedback}</div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-name">{user?.full_name || user?.username}</div>
            <div className="user-role">👨‍🏫 Giáo viên</div>
          </div>
          <button className="logout-btn" onClick={logout}>Đăng xuất</button>
        </div>
      </div>

      <div className="teacher-main">
        <div className="teacher-main-header">
          {window.innerWidth <= 768 && (
            <button className="sidebar-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>☰</button>
          )}
        </div>
        {!selectedStudent && activeTab === 'students' ? (
          <div className="empty-state">
            <h2>Chọn một học sinh để xem lịch sử trò chuyện</h2>
            <p>Danh sách học sinh được hiển thị ở bên trái</p>
          </div>
        ) : activeTab === 'documents' ? (
          <div className="empty-state">
            <h2>📚 Quản Lý Tài Liệu</h2>
            <p>Upload các file PDF về trường để chatbot có thể cung cấp thông tin chính xác</p>
          </div>
        ) : activeTab === 'ratings' ? (
          <div className="empty-state">
            <h2>⭐ Đánh Giá Chatbot</h2>
            <p>Xem thống kê và đánh giá từ học sinh ở sidebar bên trái</p>
          </div>
        ) : selectedSession ? (
          <div className="session-details">
            <div className="session-header">
              <button className="back-btn" onClick={() => setSelectedSession(null)}>← Quay lại</button>
              <h2>{selectedSession.title}</h2>
              <div className="session-date">{new Date(selectedSession.created_at).toLocaleString('vi-VN')}</div>
            </div>

            <div className="messages-container">
              {selectedSession.messages.map((message) => (
                <div key={message.id} className={`message ${message.role}`}>
                  <div className="message-avatar">{message.role === 'user' ? '👤' : '🤖'}</div>
                  <div className="message-content">
                    <div className="message-meta">
                      <span className="message-role">{message.role === 'user' ? 'Học sinh' : 'Chatbot'}</span>
                      <span className="message-time">{new Date(message.created_at).toLocaleTimeString('vi-VN')}</span>
                    </div>
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="sessions-grid">
            <h2>Lịch sử trò chuyện của {selectedStudent.full_name || selectedStudent.username}</h2>
            {selectedStudent.sessions.length === 0 ? (
              <p className="no-sessions">Học sinh chưa có cuộc trò chuyện nào</p>
            ) : (
              <div className="sessions-list-teacher">
                {selectedStudent.sessions.map((session) => (
                  <div key={session.id} className="session-card" onClick={() => viewSessionDetails(session.id)}>
                    <div className="session-card-header">
                      <h3>{session.title}</h3>
                      <div className="session-card-date">{new Date(session.created_at).toLocaleDateString('vi-VN')}</div>
                    </div>
                    <div className="session-card-body">
                      <div className="session-messages-count">{session.messages.length} tin nhắn</div>
                      <div className="session-last-update">Cập nhật: {new Date(session.updated_at).toLocaleString('vi-VN')}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default TeacherDashboard;


