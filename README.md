# AI Resume Reviewer

An intelligent, professional system that analyzes resumes against job descriptions using advanced NLP and ML techniques. Features a modern, interactive dashboard with real-time visualizations and export capabilities.

## ✨ Key Features

### 📊 Advanced Analytics
- **AI-Powered Matching**: NLP-based resume-job description similarity analysis
- **Skills Gap Analysis**: Identifies matching and missing skills
- **Action Verb Enhancement**: Suggests stronger action verbs for bullet points
- **Contact Information Extraction**: Automatically extracts emails, phone, LinkedIn, GitHub
- **Education & Experience Parsing**: Structured extraction of education and work history

### 📈 Interactive Visualizations
- **Circular Score Gauge**: Color-coded match percentage (green/yellow/red)
- **Skills Distribution Chart**: Pie chart showing matching vs missing skills
- **Match Analysis Bar Chart**: Visual representation of your score vs perfect score
- **Key Terms Importance**: Bar chart of most important terms from job description
- **Skills Radar Chart**: Multi-dimensional skills comparison across categories

### 💾 Export & Sharing
- **Export to PDF**: Download complete analysis report as PDF
- **Export to JSON**: Save raw data for further processing
- **Print-Friendly**: Optimized for printing

### 🎨 Modern UI/UX
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Drag-and-Drop Upload**: Intuitive file upload interface
- **Real-Time Progress**: Upload progress bar with percentage
- **Tabbed Interface**: Organized sections (Overview, Skills, Verbs, Suggestions)
- **Smooth Animations**: Professional transitions and effects

## Setup Instructions

1. Create a Python virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
.\venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment (optional but recommended):
Create a `.env` file at the project root based on `.env.example` and set values:
```
SECRET_KEY=your-secret
FLASK_DEBUG=1
# Use Redis for distributed rate limiting (recommended in prod):
# RATELIMIT_STORAGE_URI=redis://localhost:6379/0
# ENABLE_HSTS=1  # when serving over HTTPS
```

5. Download spaCy language model:
```bash
python -m spacy download en_core_web_sm
```

6. Run the application:
```bash
cd src
python app.py
```

The application will be available at `http://localhost:5000`

### Operational Endpoints
- Health check: `GET /healthz` → `{ "status": "ok" }`
- Upload analysis: `POST /upload`
- Batch upload: `POST /batch-upload`

### Rate Limiting
- Defaults: `200 per day`, `50 per hour`; `10 per minute` on `/upload`, `5 per minute` on `/batch-upload`.
- Configure via env: `DEFAULT_RATE_LIMIT_DAILY`, `DEFAULT_RATE_LIMIT_HOURLY`, `RATELIMIT_STORAGE_URI`.

## 🛠️ Technology Stack

### Backend
- **Flask**: Web framework
- **spaCy**: NLP processing and entity recognition
- **scikit-learn**: ML algorithms for similarity scoring
- **PyPDF2/pdfminer**: PDF text extraction
- **python-docx**: DOCX document parsing
- **dateutil**: Date parsing and handling

### Frontend
- **HTML5/CSS3**: Modern semantic markup
- **Vanilla JavaScript**: No framework dependencies
- **Chart.js**: Interactive charts and visualizations
- **Font Awesome**: Professional icons
- **html2pdf.js**: Client-side PDF generation

### Features & Capabilities
- **Caching System**: MD5-based file caching for performance
- **PhraseMatcher**: Custom skill pattern matching
- **Regex Patterns**: Fallback extraction methods
- **Cloud Tool Detection**: Auto-categorization (Docker, K8s, AWS, etc.)
- **Verb Strength Analysis**: Weak/strong verb categorization
- **Bullet Point Extraction**: Multiple format support (•, -, numbers)

## Project Structure

```
AI_Resume_Reviewer/
├── data/               # Storage for uploads and training data
├── docs/              # Documentation (including SRS)
├── src/               # Source code
│   ├── static/        # Static files (CSS, JS)
│   ├── templates/     # HTML templates
│   └── app.py         # Main Flask application
└── tests/             # Test files
```

## Features

- Upload and parse resumes (PDF/DOCX)
- Extract key information using NLP
- Compare with job descriptions
- Generate similarity scores
- Provide actionable feedback

## Technologies Used

- Python 3.8+
- Flask
- spaCy
- scikit-learn
- PDF/DOCX parsing libraries