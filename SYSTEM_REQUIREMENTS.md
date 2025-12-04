# AI Resume Reviewer - System Requirements

## Hardware Requirements

### Minimum Requirements
- **Processor:** Dual-core CPU (2.0 GHz or higher)
- **RAM:** 4 GB
- **Storage:** 2 GB available disk space
- **Display:** 1280x720 resolution
- **Network:** Internet connection for initial setup and package downloads

### Recommended Requirements
- **Processor:** Quad-core CPU (2.5 GHz or higher)
- **RAM:** 8 GB or more
- **Storage:** 5 GB available disk space (includes space for logs and uploaded files)
- **Display:** 1920x1080 resolution or higher
- **Network:** Broadband internet connection

### Server Deployment (Production)
- **Processor:** 4+ cores (for concurrent requests)
- **RAM:** 16 GB or more
- **Storage:** 20 GB SSD (for better I/O performance)
- **Network:** High-speed internet with static IP
- **Optional:** Redis server for rate limiting (can be on same or separate machine)

---

## Software Requirements

### Operating System
- **Windows:** Windows 10/11 (64-bit)
- **macOS:** macOS 10.15 (Catalina) or later
- **Linux:** Ubuntu 20.04 LTS or later, Debian 10+, CentOS 8+, or equivalent

### Core Dependencies

#### Python
- **Version:** Python 3.9, 3.10, 3.11, 3.12, or 3.13
- **Verified on:** Python 3.13.7 (latest tested)
- **Package Manager:** pip (included with Python)

#### Web Server
- **Development:** Flask built-in server (Werkzeug)
- **Production:** Gunicorn (Linux/macOS) or Waitress (Windows)

### Python Packages (from requirements.txt)

#### Web Framework
- `flask==3.0.0` - Core web framework
- `flask-wtf>=1.2.1` - CSRF protection and form handling
- `werkzeug==3.0.1` - WSGI utilities

#### NLP & Machine Learning
- `spacy>=3.7.2` - Natural language processing
- `scikit-learn==1.3.2` - Machine learning algorithms
- `numpy>=1.26.0` - Numerical computing

#### Document Processing
- `python-docx==1.0.1` - Microsoft Word (.docx) file parsing
- `pdfminer.six==20221105` - PDF text extraction
- `PyPDF2>=3.0.1` - PDF validation and processing

#### Security & Rate Limiting
- `flask-limiter>=3.6.0` - API rate limiting
- `redis>=5.0.1` - Redis client for rate limiting storage

#### Utilities
- `python-dateutil>=2.8.2` - Date/time utilities
- `python-dotenv==1.0.0` - Environment variable management
- `flask-uploads==0.2.1` - File upload handling

#### Testing
- `pytest==7.4.3` - Testing framework

### Additional Dependencies (Auto-installed)

#### spaCy Language Model
- **Model:** `en_core_web_sm` (English small model)
- **Size:** ~12 MB
- **Installation:** Automatically downloaded via `python -m spacy download en_core_web_sm`

### Web Browser (Client-side)

#### Supported Browsers
- **Google Chrome:** Version 90 or later (Recommended)
- **Mozilla Firefox:** Version 88 or later
- **Microsoft Edge:** Version 90 or later (Chromium-based)
- **Safari:** Version 14 or later (macOS/iOS)

#### JavaScript Libraries (CDN - No installation needed)
- Chart.js 4.4.0 - Data visualization
- Chart.js DataLabels Plugin 2.2.0 - Chart labels
- jsPDF 2.5.1 - PDF generation
- html2pdf.js 0.10.1 - HTML to PDF conversion
- Font Awesome 6.4.0 - Icons

### Optional Software

#### Redis Server (for Production Rate Limiting)
- **Version:** Redis 6.0 or later
- **Purpose:** Distributed rate limiting storage
- **Installation:**
  - Windows: Redis for Windows or WSL
  - Linux: `sudo apt install redis-server`
  - macOS: `brew install redis`
- **Alternative:** In-memory rate limiting (default, no Redis needed)

#### Database (Optional - Currently uses SQLite)
- **Current:** SQLite 3 (built into Python, no installation needed)
- **Future:** PostgreSQL 12+ or MySQL 8+ for production scaling

#### Development Tools (Optional)
- **Git:** Version control (for cloning repository)
- **VS Code:** Code editor with Python extension
- **Postman:** API testing

---

## System Architecture

### Application Stack
```
┌─────────────────────────────────────┐
│         Client (Browser)            │
│  HTML5 | CSS3 | JavaScript | Chart.js│
└─────────────────┬───────────────────┘
                  │ HTTP/HTTPS
┌─────────────────▼───────────────────┐
│         Flask Application            │
│  ├─ Routes (app.py)                 │
│  ├─ CSRF Protection (Flask-WTF)     │
│  ├─ Rate Limiting (Flask-Limiter)   │
│  └─ Security (security.py)          │
└─────────────────┬───────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼────┐  ┌────▼────┐  ┌────▼────┐
│ NLP    │  │Document │  │Database │
│(spaCy) │  │Parsers  │  │(SQLite) │
│ML      │  │DOCX/PDF │  │Session  │
│scikit  │  │         │  │Storage  │
└────────┘  └─────────┘  └─────────┘
```

### File Storage
- **Uploads:** `data/uploads/` (temporary, auto-cleanup)
- **Database:** `data/resume_analyzer.db` (SQLite)
- **Logs:** `data/logs/app.log` (rotating, max 2MB × 5 files)
- **Models:** `~/.cache/spacy/` (spaCy models)

---

## Network Requirements

### Ports
- **Development:** 5000 (Flask default, configurable)
- **Production:** 80 (HTTP), 443 (HTTPS recommended)
- **Redis:** 6379 (if using Redis for rate limiting)

### Firewall Rules (Production)
- Allow inbound TCP on port 80 (HTTP)
- Allow inbound TCP on port 443 (HTTPS)
- Allow outbound TCP on port 443 (for CDN resources)
- Allow internal connection to Redis port 6379 (if using)

### External Dependencies (CDN)
- `cdnjs.cloudflare.com` - Chart.js, jsPDF
- `fonts.googleapis.com` - Web fonts (optional)

---

## Disk Space Breakdown

### Installation
- Python packages: ~500 MB
- spaCy language model: ~12 MB
- Application code: ~5 MB
- **Total:** ~520 MB

### Runtime
- Upload storage (temporary): 100 MB (auto-cleanup)
- Database: 10 MB (grows with usage)
- Logs: 10 MB (rotating, max 5 files × 2 MB)
- **Total:** ~120 MB

### Recommended Total: 2 GB minimum, 5 GB recommended

---

## Performance Characteristics

### Processing Speed
- **Resume parsing:** 1-3 seconds per document
- **Analysis computation:** 0.5-2 seconds
- **PDF export:** 2-4 seconds
- **Batch processing:** 5-15 seconds for 3-5 resumes

### Concurrent Users
- **Development server:** 1-5 concurrent users
- **Production (Gunicorn 4 workers):** 20-50 concurrent users
- **Production (scaled):** 100+ with load balancer

### Memory Usage
- **Base application:** 150-200 MB
- **Per request:** 20-50 MB (temporary)
- **spaCy model loaded:** 100 MB (persistent)
- **Total typical:** 300-500 MB

---

## Security Requirements

### Environment Variables (required for production)
```env
SECRET_KEY=<strong-random-key-min-32-chars>
FLASK_DEBUG=false
SESSION_COOKIE_SECURE=true  # For HTTPS
WTF_CSRF_ENABLED=true
ENABLE_HSTS=true  # For HTTPS
```

### SSL/TLS (Production Recommended)
- **Certificate:** Valid SSL certificate (Let's Encrypt recommended)
- **Protocol:** TLS 1.2 or higher
- **Cipher Suites:** Strong encryption only

### File Permissions
- Application files: Read-only for web server user
- Upload directory: Read/write for web server user
- Database: Read/write for web server user
- Logs: Write for web server user

---

## Compliance & Standards

### File Format Support
- **Resume/Job Description:**
  - PDF (.pdf)
  - Microsoft Word (.docx, .doc)
  - Plain text (.txt)
  - Rich Text Format (.rtf)
- **Maximum file size:** 10 MB per file

### Web Standards
- HTML5
- CSS3 (with CSS Grid and Flexbox)
- ECMAScript 6+ (ES6)
- Responsive Web Design (mobile-first)

### Accessibility
- ARIA labels for screen readers
- Keyboard navigation support
- Color contrast ratios (WCAG 2.1 Level AA)

---

## Version Compatibility Matrix

| Component | Minimum | Recommended | Tested |
|-----------|---------|-------------|--------|
| Python | 3.9 | 3.11+ | 3.13.7 |
| Flask | 3.0.0 | 3.0.0+ | 3.0.0 |
| spaCy | 3.7.2 | 3.7.2+ | 3.7.6 |
| scikit-learn | 1.3.2 | 1.3.2+ | 1.3.2 |
| Redis | 6.0 | 7.0+ | Optional |
| Chrome | 90 | Latest | 120+ |
| Firefox | 88 | Latest | 121+ |
| Edge | 90 | Latest | 120+ |

---

## Installation Verification

After installation, verify requirements:

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Verify spaCy model
python -m spacy validate

# Test application startup
python src/app.py
```

Expected output: Server running on http://127.0.0.1:5000

---

## Troubleshooting Common Issues

### spaCy Installation Fails
- **Python 3.13:** Use `spacy>=3.7.2` (tested working)
- **No C compiler:** Install Microsoft C++ Build Tools (Windows) or build-essential (Linux)

### Redis Connection Errors
- Set `RATELIMIT_STORAGE_URI=memory://` in .env to use in-memory rate limiting

### Port 5000 Already in Use
- Change port: `flask run --port 5001`
- Or kill process using port 5000

### PDF Parsing Errors
- Install `poppler-utils` (Linux) or `poppler` (macOS via Homebrew)
- For Windows, PDFMiner.six should work without additional tools

---

**Last Updated:** December 1, 2025  
**Application Version:** 1.0.0  
**Python Version Tested:** 3.13.7
