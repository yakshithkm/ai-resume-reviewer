"""Tests for API error handling in app.py."""
import os
import pytest
from io import BytesIO
from src.app import app
from src.resume_parser.parser import ResumeParser
from src.scorer.scorer import ResumeScorer

def create_test_file(filename='test.pdf', content=b'test content'):
    """Create a test file for upload."""
    return (BytesIO(content), filename)

@pytest.fixture
def client():
    """Create a test client with CSRF disabled."""
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True
    app.config['VALIDATE_PDF'] = False  # Skip PDF structure validation in tests
    with app.test_client() as client:
        yield client

def test_upload_missing_files(client):
    """Test error when files are missing."""
    response = client.post('/upload', data={})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'missing_fields' in data['error']['details']
    assert set(data['error']['details']['missing_fields']) == {'resume', 'job_description'}

def test_upload_empty_files(client):
    """Test error when files are empty."""
    data = {
        'resume': (BytesIO(b''), ''),
        'job_description': (BytesIO(b''), '')
    }
    response = client.post('/upload', data=data)
    assert response.status_code == 400
    assert 'Resume is required' in response.get_json()['error']['message']

def test_upload_invalid_extensions(client):
    """Test error when file types are not allowed."""
    data = {
        'resume': create_test_file('test.exe'),
        'job_description': create_test_file('test.bat')
    }
    response = client.post('/upload', data=data)
    assert response.status_code == 400
    assert 'Invalid file type' in response.get_json()['error']['message']

def test_upload_too_large(client):
    """Test error when files are too large."""
    # Create a file larger than MAX_CONTENT_LENGTH
    large_content = b'x' * (11 * 1024 * 1024)  # 11MB
    data = {
        'resume': create_test_file(content=large_content),
        'job_description': create_test_file()
    }
    response = client.post('/upload', data=data)
    assert response.status_code == 413  # Request Entity Too Large
    assert 'too large' in response.get_json()['error']['message'].lower()

def test_successful_upload_cleanup(client, tmpdir, monkeypatch):
    """Test that uploaded files are cleaned up after processing."""
    # Override upload folder for testing
    app.config['UPLOAD_FOLDER'] = str(tmpdir)
    
    # Create valid-looking PDF content with basic structure
    pdf_content = (
        b'%PDF-1.4\n'
        b'1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n'
        b'2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n'
        b'3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\n'
        b'xref\n0 4\n0000000000 65535 f\n\n'
        b'trailer<</Size 4/Root 1 0 R>>\n'
        b'startxref\n0\n%%EOF\n'
    )
    
    # Mock ResumeParser methods
    def mock_extract_text(self, path):
        return "Sample resume text with skills like Python and Java"
    
    def mock_get_sections(self):
        return {
            'summary': {
                'text': 'Sample professional summary',
                'bullet_points': []
            },
            'experience': {
                'text': 'Sample work experience',
                'bullet_points': ['Led development team', 'Improved processes']
            },
            'education': {
                'text': 'Sample education details',
                'bullet_points': []
            },
            'skills': {
                'text': 'Python, Java, and other skills',
                'bullet_points': ['Python', 'Java']
            }
        }
    
    def mock_get_skills(self):
            return {'Python': 1, 'Java': 1}
    
    def mock_get_contact_info(self):
        return {
            'email': 'test@example.com',
            'phone': '123-456-7890',
            'linkedin': None,
            'github': None
        }
    
    def mock_init(self):
        self.text = "Sample resume text with skills like Python and Java"
        self._text = "Sample resume text with skills like Python and Java"
        self._skills = ['Python', 'Java']
        return self
    
    def mock_parse_resume(self, file_path=None):
        self.text = "Sample resume text with skills like Python and Java"
        return mock_get_sections(self)
    
    # Mock ResumeParser
    monkeypatch.setattr(ResumeParser, '__init__', mock_init)
    monkeypatch.setattr(ResumeParser, 'extract_text_from_pdf', mock_extract_text)
    monkeypatch.setattr(ResumeParser, 'extract_text_from_docx', mock_extract_text)
    monkeypatch.setattr(ResumeParser, 'parse_resume', mock_parse_resume)
    monkeypatch.setattr(ResumeParser, 'get_skills', mock_get_skills)
    monkeypatch.setattr(ResumeParser, 'get_contact_info', mock_get_contact_info)
    monkeypatch.setattr(ResumeParser, 'text', "Sample resume text with skills like Python and Java", raising=False)
    
    # Mock ResumeScorer methods
    def mock_compute_similarity(self, **kwargs):
        return 0.75
    
    def mock_get_important_terms(self, **kwargs):
        return {
            'resume_terms': ['Python', 'Java'],
            'job_terms': ['Python', 'Java']
        }

    def mock_generate_feedback(self, **kwargs):
        resume_skills = {'Python': 1, 'Java': 1} if 'resume_skills' not in kwargs else kwargs['resume_skills']
        job_skills = {'Python': 1, 'Java': 1} if 'job_skills' not in kwargs else kwargs['job_skills']
        return {
            'match_percentage': 0.75,
            'missing_skills': [],
            'overall_feedback': 'Good match',
            'suggestions': [],
            'key_terms': ['Python', 'Java']
        }
    
    # Mock ResumeScorer
    monkeypatch.setattr(ResumeScorer, 'compute_similarity', mock_compute_similarity)
    monkeypatch.setattr(ResumeScorer, 'get_important_terms', mock_get_important_terms)
    monkeypatch.setattr(ResumeScorer, 'generate_feedback', mock_generate_feedback)
    
    data = {
        'resume': create_test_file(content=pdf_content),
        'job_description': create_test_file(content=pdf_content)
    }
    
    response = client.post('/upload', data=data)
    
    # Check response
    assert response.status_code == 200, f"Response: {response.get_json()}"
    data = response.get_json()
    assert data['message'] == 'Analysis completed successfully'
    assert 'analysis' in data
    
    # Verify files were cleaned up
    files = os.listdir(str(tmpdir))
    assert not files, "Upload folder should be empty after processing"