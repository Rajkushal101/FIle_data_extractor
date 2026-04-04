# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.9+ installed
- Node.js 18+ installed
- Git installed

### 1. Clone & Setup (First Time Only)

**Windows:**
```cmd
cd D:\Projects\file_data_extractor
scripts\setup.bat
```

**Linux/Mac:**
```bash
cd /path/to/file_data_extractor
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 2. Configure API Keys

Edit `backend/.env`:
```env
# Get free API keys:
GROQ_API_KEY=your_key_here          # https://console.groq.com (14,400 req/day FREE)
GEMINI_API_KEY=your_key_here        # https://makersuite.google.com (1,500 req/day FREE)

# Optional - Use your RTX 4070 for FREE local processing:
OLLAMA_ENABLED=True
```

### 3. Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate    # Windows: venv\Scripts\activate
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 4. Open in Browser
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📁 Upload Your First Document

1. Go to http://localhost:3000/ai-notes
2. Drag & drop a PDF, DOCX, PPTX, or image
3. Click "Generate Notes"
4. Get AI-powered structured notes!

## 🎮 Use Your RTX 4070 (Optional but Recommended)

Install Ollama for 6-15x faster local processing:

```bash
# Linux/Mac:
./scripts/install_ollama.sh

# Windows:
# Download from https://ollama.com/download
# Then run:
ollama pull qwen2.5-vl:7b
ollama pull llama3.1:8b
```

Test GPU:
```bash
python scripts/test_gpu.py
```

## 🧪 Run Tests

```bash
cd backend
pytest tests/ -v
```

## 📚 Features

- ✅ PDF extraction with math equations
- ✅ Word/PowerPoint support
- ✅ Image OCR
- ✅ AI-powered note generation
- ✅ Export to Markdown, DOCX, PDF
- ✅ Local processing (RTX 4070)
- ✅ Cloud fallback (Groq/Gemini)

## 🆘 Troubleshooting

**Backend won't start:**
- Check Python version: `python --version` (need 3.9+)
- Activate venv: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

**Frontend won't start:**
- Check Node version: `node --version` (need 18+)
- Install dependencies: `npm install`
- Clear cache: `rm -rf .next node_modules && npm install`

**API keys not working:**
- Verify keys in `backend/.env`
- Restart backend server
- Check API quotas at provider websites

**GPU not detected:**
- Run `python scripts/test_gpu.py`
- Install NVIDIA drivers
- Install CUDA toolkit
- Install PyTorch with CUDA: `pip install torch --index-url https://download.pytorch.org/whl/cu121`

## 📖 More Documentation

- `docs/ARCHITECTURE.md` - System design
- `docs/API.md` - API reference
- `docs/DEVELOPMENT.md` - Development guide
- `docs/DEPLOYMENT.md` - Production deployment
- `production_plan.md` - Complete project plan

## 🎯 Your Advantages

1. **RTX 4070** - Process documents 6-15x faster than CPU
2. **16GB RAM** - Handle large documents easily
3. **1TB SSD** - Store AI models locally
4. **Free Tier APIs** - 15,000+ requests/day combined
5. **Local First** - Works offline with Ollama

## 💰 Cost Breakdown

- Development: $0 (all free tools)
- Local AI: $0 (use your GPU)
- Cloud APIs: $0 (free tiers)
- Deployment: $0 (Vercel + Render free tiers)

**Total: $0/month** 🎉

## 🚀 Next Steps

1. Upload test documents
2. Try different note templates
3. Customize prompts in `backend/app/services/ai_processor.py`
4. Add your own features
5. Deploy to production (see `docs/DEPLOYMENT.md`)

---

Need help? Check `PROJECT_STATUS.md` for detailed status and `production_plan.md` for the complete roadmap.
