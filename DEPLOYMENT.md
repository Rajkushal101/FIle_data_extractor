# 🚀 Deployment & Testing Guide

## Quick Start (5 Minutes)

### Step 1: Install Dependencies

**Backend:**
```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

---

## Step 2: Environment Configuration

### Backend Environment (.env)

Create `backend/.env`:

```env
# Application
DEBUG=True
SECRET_KEY=your-secret-key-here-minimum-32-characters-long

# Database (SQLite for development)
DATABASE_URL=sqlite:///./app.db

# API Keys (Optional - for cloud AI)
GROQ_API_KEY=your-groq-key
GEMINI_API_KEY=your-gemini-key

# Ollama (Local AI)
OLLAMA_ENABLED=False
OLLAMA_HOST=http://localhost:11434

# CORS
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend Environment (.env.local)

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Step 3: Initialize Database

```bash
cd backend

# With venv activated
python -c "from app.core.database import init_db; init_db()"
```

**Expected output:**
```
✅ Database initialized successfully
```

---

## Step 4: Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

uvicorn main:app --reload
```

**Expected:** Server running at `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Expected:** App running at `http://localhost:3000`

---

## Step 5: Test the Application

### 1. Test Landing Page
- Open http://localhost:3000
- Should see animated gradient background
- Click "Start Extracting" button

### 2. Test Registration
- Navigate to http://localhost:3000/auth/register
- Fill form:
  - Email: test@example.com
  - Username: testuser
  - Password: testpassword123
- Click "Create Account"
- Should redirect to dashboard

### 3. Test Dashboard
- Should see welcome message with username
- View stats cards (all should be 0)
- Click "Process New Document"

### 4. Test Document Processing
- Upload a simple PDF or image
- Select note style
- Click "Generate Notes"
- Download exported files

### 5. Test API Directly

**Health Check:**
```bash
curl http://localhost:8000/api/health
```

**Register User:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"api@test.com\",\"username\":\"apiuser\",\"password\":\"test123456\"}"
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"api@test.com\",\"password\":\"test123456\"}"
```

---

## Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'X'`
**Solution:**
```bash
pip install -r requirements.txt
```

**Problem:** Database errors
**Solution:**
```bash
# Reset database (DEVELOPMENT ONLY)
python -c "from app.core.database import reset_db; reset_db()"
```

**Problem:** WeasyPrint installation fails
**Solution (Windows):**
1. Download GTK3 installer: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
2. Install GTK3
3. Retry: `pip install weasyprint`

**Problem:** Port 8000 already in use
**Solution:**
```bash
uvicorn main:app --reload --port 8001
# Update frontend .env.local accordingly
```

### Frontend Issues

**Problem:** `Error: Cannot find module 'next'`
**Solution:**
```bash
npm install
```

**Problem:** API connection errors
**Solution:**
- Verify backend is running at http://localhost:8000
- Check CORS settings in `backend/config.py`
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`

**Problem:** Dark mode not working
**Solution:**
- Check browser settings (prefers-color-scheme)
- Tailwind dark mode is set to 'media' in `tailwind.config.js`

---

## Production Deployment

### Option 1: Docker (Recommended)

**Create docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/fileextractor
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=fileextractor
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Deploy:**
```bash
docker-compose up -d
```

### Option 2: Cloud Platform (Vercel + Railway)

**Frontend (Vercel):**
1. Push to GitHub
2. Connect to Vercel
3. Set environment variable: `NEXT_PUBLIC_API_URL`
4. Deploy

**Backend (Railway):**
1. Connect GitHub repo
2. Add PostgreSQL database
3. Set environment variables
4. Deploy

### Option 3: Traditional VPS

**Backend (Ubuntu):**
```bash
# Install Python
sudo apt update
sudo apt install python3.10 python3-pip nginx

# Deploy app
cd /var/www/file_data_extractor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Use systemd service
sudo systemctl enable fileextractor
sudo systemctl start fileextractor
```

---

## Performance Tips

### 1. Use PostgreSQL in Production
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/fileextractor
```

### 2. Enable Redis Caching (Future)
```bash
# Install Redis
sudo apt install redis-server

# Configure in backend
REDIS_URL=redis://localhost:6379
```

### 3. Use Ollama for Local AI
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull qwen2.5-vl:7b
ollama pull llama3.1:8b

# Enable in .env
OLLAMA_ENABLED=True
```

---

## Security Checklist

- [ ] Set strong `SECRET_KEY` (32+ characters)
- [ ] Use PostgreSQL in production (not SQLite)
- [ ] Enable HTTPS (SSL certificate)
- [ ] Set `DEBUG=False` in production
- [ ] Configure proper CORS origins
- [ ] Enable rate limiting
- [ ] Regular database backups
- [ ] Keep dependencies updated

---

## Monitoring

### Check Application Health
```bash
curl http://localhost:8000/api/health
```

### View Logs
```bash
# Backend logs
tail -f backend/logs/app.log

# Frontend logs (dev)
# Visible in terminal where npm run dev is running
```

### Database Queries
```bash
# Connect to SQLite
sqlite3 backend/app.db

# Check users
SELECT * FROM users;

# Check documents
SELECT * FROM documents;
```

---

## Next Steps

1. **Test thoroughly** - Try all features
2. **Add sample data** - Create test documents
3. **Customize branding** - Update colors, logos
4. **Deploy to staging** - Test in production-like environment
5. **Get feedback** - Share with early users
6. **Monitor performance** - Check response times
7. **Scale as needed** - Add workers, caching

---

## Support

- **Documentation:** See README.md
- **API Docs:** http://localhost:8000/docs (FastAPI automatic docs)
- **Issues:** Report bugs and feature requests

---

**🎉 Congratulations! Your industry-level document extraction platform is ready!**
