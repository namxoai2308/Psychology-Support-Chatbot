# 🤖 Student Psychological Chatbot

AI-powered chatbot for student psychological support with RAG (Retrieval-Augmented Generation) system.

## ✨ Features

### For Students

- 👩‍🏫 **"Cô Xiêm"** - AI teacher with empathy and warmth
- 💝 **24/7 psychological support** - Like talking to a real teacher
- 🧠 **Context-aware** - Remembers entire conversation
- 📚 **Smart information** - Uses school documents naturally
- 😊 **Friendly interface** - ChatGPT-like with personality

### For Teachers
- Upload school documents (PDF - text or scanned)
- View all student chat histories
- Manage documents

### Technical
- **AI Personality**: "Cô Mai" - Empathetic teacher persona
- **Natural RAG**: Context injection without revealing sources
- **Smart Search**: Multi-factor relevance scoring for Vietnamese
- **PDF Processing**: PyPDF2 (fast) + Optional DeepSeek Vision OCR (for scans)
- **Chat Memory**: Gemini ChatSession API with 10-message context
- **Database**: SQLite with SQLAlchemy ORM

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- Gemini API Key (free): https://makersuite.google.com/app/apikey

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your GEMINI_API_KEY

# Run
python main.py
```

### 2. Frontend Setup

```bash
cd frontend

# Install
npm install

# Run
npm start
```

### 3. Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

---

## 📁 Project Structure

```
Chatbot/
├── backend/
│   ├── app/                    # Clean architecture ✅
│   │   ├── core/              # Config, database, security
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas (auth, chat, document, teacher)
│   │   ├── services/          # Business logic (Gemini AI, RAG)
│   │   ├── api/               # API dependencies
│   │   └── utils/             # Utilities (DeepSeek OCR)
│   │
│   ├── routers/               # API routes (working)
│   │   ├── auth_router.py
│   │   ├── chat_router.py
│   │   ├── document_router.py
│   │   └── teacher_router.py
│   │
│   ├── uploads/               # Uploaded PDFs
│   ├── main.py                # FastAPI entry point ⭐
│   ├── run.py                 # Alternative entry
│   ├── init_db.py             # Database initialization
│   ├── test_chat_history.py   # Test script
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── context/           # React context (Auth)
│   │   ├── pages/             # Pages (Login, Register, Chat, Dashboard)
│   │   ├── services/          # API client
│   │   ├── App.js
│   │   └── index.js
│   ├── public/
│   └── package.json
│
└── README.md                  # This file (ONLY documentation)
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (for PDF scan processing)
DEEPSEEK_API_KEY=your_deepseek_key_here
USE_DEEPSEEK_OCR=false

# Authentication
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Database
DATABASE_URL=sqlite:///./chatbot.db

# CORS
FRONTEND_URL=http://localhost:3000
```

### Getting API Keys

**Gemini (Required - FREE):**
1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API key"
3. Copy and paste into `.env`

**DeepSeek (Optional - for PDF scans):**
1. Visit: https://platform.deepseek.com/
2. Create account and get API key
3. Add to `.env` if needed

---

## 💡 Usage

### Create Accounts

**Teacher Account:**
- Register at http://localhost:3000/register
- Set role to "teacher"

**Student Account:**
- Register at http://localhost:3000/register
- Set role to "student"

### Upload Documents (Teacher)

1. Login as teacher
2. Go to "Documents" tab
3. Upload PDF files
4. Documents will be processed and indexed

### Chat (Student)

1. Login as student
2. Create new chat session
3. Start chatting!
4. AI will automatically use school documents when relevant

---

## 🔧 Development

### Backend

```bash
# Run with auto-reload
cd backend
uvicorn app.main:app --reload

# Or
python main.py
```

### Frontend

```bash
cd frontend
npm start
```

### Database

```bash
# Initialize database
cd backend
python init_db.py

# View database
sqlite3 chatbot.db
```

---

## 🛠️ Tech Stack

### Backend
- FastAPI - Web framework
- SQLAlchemy - ORM
- SQLite - Database
- Gemini API - AI responses
- PyPDF2 - PDF processing
- LangChain - Text chunking
- JWT - Authentication

### Frontend
- React - UI framework
- Axios - HTTP client
- Context API - State management

---

## 📊 Features in Detail

### RAG System
- **Keyword-based search** (no embedding API needed)
- **Automatic chunking** with LangChain
- **Context injection** into AI prompts
- **No quota limits** - completely free

### Chat Memory
- **ChatSession API** for proper context
- **Last 10 messages** remembered
- **No repeated greetings**

### PDF Processing
- **PyPDF2**: Fast, for text PDFs (default)
- **DeepSeek OCR**: For scanned/image PDFs (optional)
- **Auto-fallback**: Always works

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check dependencies
pip install -r requirements.txt

# Check API key
cat .env | grep GEMINI_API_KEY

# Check port
lsof -i :8000  # Kill if needed: kill <PID>
```

### Frontend won't start

```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Check backend is running
curl http://localhost:8000/
```

### Chat doesn't remember context

```bash
# Update dependencies
pip install --upgrade google-generativeai

# Restart backend
pkill -f "python main.py"
python main.py
```

### PDF upload fails

**For text PDFs:** Should work by default

**For scanned PDFs:**
1. Install poppler: `sudo apt-get install poppler-utils`
2. Get DeepSeek API key
3. Set `USE_DEEPSEEK_OCR=true` in `.env`
4. Restart backend

---

## 📈 Roadmap

- [x] Basic chat with Gemini
- [x] User authentication
- [x] RAG system (keyword-based)
- [x] DeepSeek Vision OCR
- [x] Chat history context
- [x] Teacher dashboard
- [ ] Semantic search (embeddings)
- [ ] Export chat history
- [ ] Voice chat
- [ ] Mobile app

---

## 📄 License

MIT License - Free to use and modify

---

## 🙏 Credits

- **Gemini API** - Google AI
- **DeepSeek** - DeepSeek AI
- **LangChain** - Text processing
- **FastAPI** - Backend framework
- **React** - Frontend framework

---

**Made with ❤️ for students**

Last updated: October 28, 2025
