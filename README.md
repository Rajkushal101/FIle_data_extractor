# File Data Extractor - AI-Powered Document Processing

Transform your documents into structured notes with AI-powered extraction and formatting.

## ✨ Features

- **Multi-Format Support**: PDF, DOCX, PPTX, Images (PNG, JPG)
- **Large File Support**: Upload files up to 50MB
- **AI Note Generation**: Structured, Cornell, Outline, Mindmap styles
- **Math Preservation**: Detects and preserves LaTeX expressions
- **Math-to-Text Export**: Converts equations into readable plain text for TXT export
- **Multiple Export Formats**: PDF, DOCX, Markdown, LaTeX
- **Multi-Provider AI Routing**: NVIDIA NIM, Groq, and Gemini fallback support
- **Strict Provider Mode**: Lock processing to NVIDIA for full-run consistency (no mid-process fallback)
- **Deep Text Enhancement**: Verify and improve extracted text quality using powerful NVIDIA models
- **User Authentication**: Secure JWT-based login system
- **Document Management**: History, sharing, and search
- **Modern UI**: Premium dark mode interface with animations

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Windows/macOS/Linux

### Installation

**1. Clone the repository:**
```bash
git clone https://github.com/yourusername/file_data_extractor.git
cd file_data_extractor
```

**2. Backend Setup:**
```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

**3. Configure Environment:**

Create `backend/.env`:
```env
# Get free API keys:
# Groq: https://console.groq.com
# Gemini: https://makersuite.google.com
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
NVIDIA_ENABLED=true
NVIDIA_API_KEY=your_nvidia_api_key
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL_ENHANCEMENT=meta/llama-3.1-405b-instruct
PRIMARY_AI_PROVIDER=nvidia
STRICT_AI_PROVIDER=true

SECRET_KEY=your-secret-key-at-least-32-chars
DEBUG=True
```

**4. Initialize Database:**
```bash
python -c "from app.core.database import init_db; init_db()"
```

**5. Start Backend:**
```bash
uvicorn main:app --reload
```

**6. Frontend Setup (New Terminal):**
```bash
cd frontend
npm install
npm run dev
```

**7. Open Application:**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## 📖 Usage

1. **Register/Login** at http://localhost:3000/auth/register
2. **Upload Document** - Drag & drop or browse
3. **Select Note Style** - Choose from 4 AI-powered styles
4. **Generate Notes** - AI processes and structures content
5. **Export** - Download in your preferred format

## 🛠️ Tech Stack

**Backend:**
- FastAPI - High-performance API
- SQLAlchemy - Database ORM
- WeasyPrint - PDF generation
- python-docx - Word export
- Groq/Gemini - AI processing

**Frontend:**
- Next.js 14 - React framework
- TailwindCSS - Styling
- TypeScript - Type safety

## 📚 API Documentation

Interactive API docs available at: http://localhost:8000/docs

### Key Endpoints:
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/process-document` - Upload & process
- `POST /api/enhance-text` - Verify and deeply enhance extracted/plain text
- `POST /api/export/pdf` - Export as PDF
- `POST /api/export/math-text` - Export plain text with math converted to readable text
- `GET /api/documents` - List documents

## 🔧 Troubleshooting

### PDF Export Not Working (Windows)
PDF export requires GTK3 libraries:
1. Download: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
2. Install GTK3 runtime
3. Restart backend

### Port Already in Use
```bash
# Change backend port
uvicorn main:app --reload --port 8001

# Update frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8001
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- FastAPI for the amazing framework
- Next.js team for React tooling
- Groq & Google for AI APIs
- WeasyPrint for PDF generation

## 📧 Support

- Issues: https://github.com/yourusername/file_data_extractor/issues
- Email: your.email@example.com

---

**Made with ❤️ for students and professionals**
