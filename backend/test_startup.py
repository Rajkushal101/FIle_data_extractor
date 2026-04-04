"""
Quick Test Script
Tests if the backend can start and imports work correctly
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print("=" * 60)
print("🧪 Testing File Data Extractor Backend")
print("=" * 60)

# Test 1: Configuration
print("\n1️⃣ Testing Configuration...")
try:
    from config import settings
    print(f"✅ Config loaded: {settings.APP_NAME} v{settings.VERSION}")
    print(f"   - Debug Mode: {settings.DEBUG}")
    print(f"   - Ollama Enabled: {settings.OLLAMA_ENABLED}")
    print(f"   - Max File Size: {settings.MAX_FILE_SIZE / (1024**2):.1f}MB")
except Exception as e:
    print(f"❌ Config Error: {e}")
    sys.exit(1)

# Test 2: Models
print("\n2️⃣ Testing Models...")
try:
    from app.models import Document, ProcessingResult, User
    print("✅ All models imported successfully")
except Exception as e:
    print(f"❌ Model Error: {e}")

# Test 3: Services
print("\n3️⃣ Testing Services...")
try:
    from app.services.pdf_extractor import PDFExtractor
    from app.services.docx_extractor import DOCXExtractor
    from app.services.pptx_extractor import PPTXExtractor
    from app.services.image_extractor import ImageExtractor
    from app.services.ai_processor import AIProcessor
    from app.services.note_generator import NoteGenerator
    from app.services.math_detector import MathDetector
    print("✅ All services imported successfully")
except Exception as e:
    print(f"❌ Service Error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Routes
print("\n4️⃣ Testing Routes...")
try:
    from app.routes import document_processing, health, user
    print("✅ All routes imported successfully")
except Exception as e:
    print(f"❌ Route Error: {e}")

# Test 5: Utils
print("\n5️⃣ Testing Utilities...")
try:
    from app.utils.file_handler import save_upload_file, cleanup_temp_file
    from app.utils.validators import validate_file
    from app.utils.logger import setup_logging
    print("✅ All utilities imported successfully")
except Exception as e:
    print(f"❌ Utility Error: {e}")

# Test 6: Main App
print("\n6️⃣ Testing Main Application...")
try:
    from main import app
    print(f"✅ FastAPI app created: {app.title}")
    print(f"   Routes available:")
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"   - {route.path}")
except Exception as e:
    print(f"❌ Main App Error: {e}")
    import traceback
    traceback.print_exc()

# Test 7: API Keys
print("\n7️⃣ Checking API Keys...")
api_keys_ok = True
if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_key_here":
    print("⚠️  Groq API key not configured")
    api_keys_ok = False
else:
    print(f"✅ Groq API key configured ({settings.GROQ_API_KEY[:10]}...)")

if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_key_here":
    print("⚠️  Gemini API key not configured")
    api_keys_ok = False
else:
    print(f"✅ Gemini API key configured ({settings.GEMINI_API_KEY[:10]}...)")

# Test 8: Directories
print("\n8️⃣ Checking Directories...")
import os
for directory in [settings.UPLOAD_DIR, settings.TEMP_DIR]:
    if os.path.exists(directory):
        print(f"✅ Directory exists: {directory}")
    else:
        print(f"❌ Directory missing: {directory}")

# Summary
print("\n" + "=" * 60)
print("📊 Test Summary")
print("=" * 60)
if api_keys_ok:
    print("✅ All critical tests passed!")
    print("\n🚀 Ready to start the server:")
    print("   uvicorn main:app --reload")
else:
    print("⚠️  Tests passed but API keys need configuration")
    print("\n📝 Next steps:")
    print("   1. Edit backend/.env and add your API keys")
    print("   2. Run: uvicorn main:app --reload")

print("\n💡 Access the app:")
print(f"   - API Docs: http://localhost:{settings.PORT}/docs")
print(f"   - Health Check: http://localhost:{settings.PORT}/api/health")
print("=" * 60)
