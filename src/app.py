from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect, CSRFError
import os
import uuid
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from resume_parser.parser import ResumeParser
from scorer.scorer import ResumeScorer
from verb_enhancer import ActionVerbEnhancer
from validation import validate_file_upload, validate_file_size, ValidationError, error_response
from security import validate_file_content, sanitize_filename, validate_pdf_structure
from database import save_analysis, get_session_history, get_analysis_by_id
from batch_processor import process_resume_batch, get_batch_summary
from template_advisor import analyze_resume_format, get_template_recommendation, get_ats_tips

# Load environment variables from .env if present
load_dotenv()

# Create upload folder path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure session security
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', '0') == '1'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=int(os.environ.get('SESSION_LIFETIME_HOURS', '24')))

# Configure CSRF protection
app.config['WTF_CSRF_ENABLED'] = os.environ.get('WTF_CSRF_ENABLED', '1') == '1'
app.config['WTF_CSRF_TIME_LIMIT'] = None  # No time limit on tokens
csrf = CSRFProtect(app)

# Configure logging (rotating file handler)
logs_dir = os.path.join(BASE_DIR, 'data', 'logs')
os.makedirs(logs_dir, exist_ok=True)
log_file = os.path.join(logs_dir, 'app.log')
handler = RotatingFileHandler(log_file, maxBytes=2 * 1024 * 1024, backupCount=5)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Application startup at %s', datetime.now(timezone.utc).isoformat())

# Configure rate limiting
limiter_storage_uri = os.environ.get('RATELIMIT_STORAGE_URI', '').strip()
if not limiter_storage_uri:
    # Prefer Redis if REDIS_URL provided, else fall back to memory
    redis_url = os.environ.get('REDIS_URL', '').strip()
    limiter_storage_uri = f"redis://{redis_url}" if redis_url else "memory://"

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[
        os.environ.get('DEFAULT_RATE_LIMIT_DAILY', '200 per day'),
        os.environ.get('DEFAULT_RATE_LIMIT_HOURLY', '50 per hour')
    ],
    storage_uri=limiter_storage_uri
)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt', 'rtf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Basic security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=()'
    # Only set HSTS if enabled and over HTTPS
    if os.environ.get('ENABLE_HSTS', '0') == '1':
        response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains; preload'
    return response

# Simple health endpoint
@app.route('/healthz', methods=['GET'])
@csrf.exempt  # Exempt health check from CSRF
def healthz():
    return jsonify({'status': 'ok'}), 200

# Error handlers
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return error_response(
        'CSRF validation failed',
        details={'message': 'Invalid or missing CSRF token. Please refresh the page and try again.'},
        status_code=400
    )

@app.errorhandler(429)
def rate_limit_handler(e):
    return error_response(
        'Too many requests',
        details={'message': 'Rate limit exceeded. Please wait and try again.'},
        status_code=429
    )

@app.errorhandler(404)
def not_found_handler(e):
    return error_response('Not found', status_code=404)

def allowed_file(filename: str) -> bool:
    """
    Check if a filename has an allowed extension.
    
    Args:
        filename: The filename to check
        
    Returns:
        bool: True if the file extension is allowed, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # Initialize session ID if not present
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/history', methods=['GET'])
def get_history():
    """Get analysis history for current session."""
    if 'session_id' not in session:
        return jsonify({'history': []})
    
    history = get_session_history(session['session_id'])
    return jsonify({'history': history})

@app.route('/analysis/<int:analysis_id>', methods=['GET'])
def get_saved_analysis(analysis_id):
    """Retrieve a saved analysis by ID."""
    analysis = get_analysis_by_id(analysis_id)
    if not analysis:
        return error_response('Analysis not found', status_code=404)
    
    # Security: verify the analysis belongs to this session
    if 'session_id' in session and analysis['session_id'] == session['session_id']:
        return jsonify({'analysis': analysis})
    else:
        return error_response('Unauthorized', status_code=403)

@app.route('/batch-upload', methods=['POST'])
@limiter.limit("5 per minute")  # Even stricter for batch processing
def batch_upload():
    """
    Handle batch resume upload and analysis.
    
    Expects:
        - Multiple resume files
        - One job_description file
    
    Returns:
        JSON with batch analysis results and summary
    """
    try:
        if 'job_description' not in request.files:
            return error_response('Job description file is required')
        
        # Get all resume files
        resume_files = request.files.getlist('resume')
        if not resume_files or len(resume_files) == 0:
            return error_response('At least one resume file is required')
        
        if len(resume_files) > 10:
            return error_response('Maximum 10 resumes allowed per batch')
        
        job_desc = request.files['job_description']
        
        # Validate job description
        try:
            job_desc_filename, job_desc_ext = validate_file_upload(
                job_desc, 'Job Description', ALLOWED_EXTENSIONS
            )
            validate_file_size(job_desc, app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024))
            is_valid, error_msg = validate_file_content(job_desc, ALLOWED_EXTENSIONS)
            if not is_valid:
                return error_response(error_msg)
            job_desc_filename = sanitize_filename(job_desc_filename)
        except ValidationError as e:
            return error_response(str(e))
        
        # Save job description
        job_desc_path = os.path.join(app.config['UPLOAD_FOLDER'], job_desc_filename)
        job_desc.save(job_desc_path)
        
        # Validate and save all resumes
        resume_paths = []
        resume_filenames = []
        try:
            for resume_file in resume_files:
                try:
                    resume_filename, resume_ext = validate_file_upload(
                        resume_file, 'Resume', ALLOWED_EXTENSIONS
                    )
                    validate_file_size(resume_file, app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024))
                    is_valid, error_msg = validate_file_content(resume_file, ALLOWED_EXTENSIONS)
                    if not is_valid:
                        raise ValidationError(f"{resume_file.filename}: {error_msg}")
                    
                    resume_filename = sanitize_filename(resume_filename)
                    resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
                    resume_file.save(resume_path)
                    
                    resume_paths.append(resume_path)
                    resume_filenames.append(resume_filename)
                except ValidationError as e:
                    # Clean up already saved files
                    for path in resume_paths:
                        if os.path.exists(path):
                            os.remove(path)
                    if os.path.exists(job_desc_path):
                        os.remove(job_desc_path)
                    return error_response(str(e))
            
            # Process batch
            results = process_resume_batch(resume_paths, job_desc_path, app.logger)
            summary = get_batch_summary(results)
            
            # Save each successful analysis to database
            if 'session_id' not in session:
                session['session_id'] = str(uuid.uuid4())
            
            for result in results:
                if result.get('success', False):
                    try:
                        save_analysis(
                            session_id=session['session_id'],
                            resume_filename=result['analysis']['filename'],
                            job_desc_filename=job_desc_filename,
                            similarity_score=result['analysis']['similarity'],
                            analysis_data=result['analysis']
                        )
                    except Exception as e:
                        app.logger.error(f"Failed to save batch analysis: {str(e)}")
            
            return jsonify({
                'message': f'Batch analysis completed: {summary["successful"]}/{summary["total_resumes"]} successful',
                'results': results,
                'summary': summary
            })
            
        finally:
            # Clean up all uploaded files
            for path in resume_paths:
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception as e:
                    app.logger.error(f"Failed to remove {path}: {str(e)}")
            
            try:
                if os.path.exists(job_desc_path):
                    os.remove(job_desc_path)
            except Exception as e:
                app.logger.error(f"Failed to remove job desc: {str(e)}")
    
    except Exception as e:
        app.logger.error(f"Batch processing error: {str(e)}", exc_info=True)
        return error_response(
            'Batch processing failed',
            details={'error': str(e)},
            status_code=500
        )

@app.route('/upload', methods=['POST'])
@limiter.limit("10 per minute")  # Stricter limit for upload endpoint
def upload_file():
    """
    Handle file upload and analysis endpoint.
    
    Rate limit: 10 uploads per minute per IP address
    
    Expects:
        - resume file (PDF/DOCX)
        - job_description file (PDF/DOCX)
    
    Returns:
        JSON response with analysis results or error details
    """
    try:
        # Validate required files are present
        if 'resume' not in request.files or 'job_description' not in request.files:
            return error_response(
                'Both resume and job description files are required',
                details={
                    'missing_fields': [
                        f for f in ['resume', 'job_description']
                        if f not in request.files
                    ]
                }
            )
        
        resume = request.files['resume']
        job_desc = request.files['job_description']
        
        try:
            # Validate resume file
            resume_filename, resume_ext = validate_file_upload(
                resume, 'Resume', ALLOWED_EXTENSIONS
            )
            validate_file_size(resume, app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024))
            
            # Security validation for resume content
            is_valid, error_msg = validate_file_content(resume, ALLOWED_EXTENSIONS)
            if not is_valid:
                return error_response(error_msg)
            
            # Sanitize filename
            resume_filename = sanitize_filename(resume_filename)
            
            # Validate job description file
            job_desc_filename, job_desc_ext = validate_file_upload(
                job_desc, 'Job Description', ALLOWED_EXTENSIONS
            )
            validate_file_size(job_desc, app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024))
            
            # Security validation for job description content
            is_valid, error_msg = validate_file_content(job_desc, ALLOWED_EXTENSIONS)
            if not is_valid:
                return error_response(error_msg)
            
            # Sanitize filename
            job_desc_filename = sanitize_filename(job_desc_filename)
        except ValidationError as e:
            return error_response(str(e))
        
        # Save files
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
        job_desc_path = os.path.join(app.config['UPLOAD_FOLDER'], job_desc_filename)
        
        resume.save(resume_path)
        job_desc.save(job_desc_path)
        
        # Additional validation for PDF structure (skip in testing)
        if resume_ext == 'pdf' and not app.config.get('TESTING', False):
            is_valid, error_msg = validate_pdf_structure(resume_path)
            if not is_valid:
                os.remove(resume_path)  # Clean up
                return error_response(error_msg)
        
        if job_desc_ext == 'pdf' and not app.config.get('TESTING', False):
            is_valid, error_msg = validate_pdf_structure(job_desc_path)
            if not is_valid:
                os.remove(resume_path)
                os.remove(job_desc_path)
                return error_response(error_msg)
        
        # Process resume
        parser = ResumeParser()
        resume_sections = parser.parse_resume(resume_path)
        contact_info = parser.get_contact_info()
        resume_skills = parser.get_skills()
        
        # Process job description
        job_parser = ResumeParser()
        job_sections = job_parser.parse_resume(job_desc_path)
        required_skills = job_parser.get_skills()
        
        try:
            # Calculate similarity score
            scorer = ResumeScorer()
            similarity = scorer.compute_similarity(
                resume_text=parser.text,
                job_text=job_parser.text
            )
            
            # Get important terms
            important_terms = scorer.get_important_terms(n_terms=10)
            
            # Generate feedback
            feedback = scorer.generate_feedback(
                similarity_score=similarity,
                    resume_skills={s: 1 for s in resume_skills},
                    job_skills={s: 1 for s in required_skills},
                important_terms=important_terms
            )
            
            # Prepare response
            analysis = {
                'resume': {
                    'contact': contact_info,
                    'sections': resume_sections,
                    'skills': resume_skills
                },
                'job_description': {
                    'sections': job_sections,
                    'required_skills': required_skills
                },
                'matching_skills': [
                    skill for skill in (resume_skills.keys() if isinstance(resume_skills, dict) else resume_skills) or []
                    if (isinstance(skill, str) and 
                        any(isinstance(req_skill, str) and 
                            skill.lower() == req_skill.lower()
                            for req_skill in (required_skills.keys() if isinstance(required_skills, dict) else required_skills) or []))
                ],
                'missing_skills': feedback['missing_skills'],
                'similarity': feedback['match_percentage'],
                'feedback': {
                    'overall': feedback['overall_feedback'],
                    'suggestions': feedback['suggestions'],
                    'key_terms': feedback['key_terms']
                }
            }
                # Run action verb enhancement
            try:
                enhancer = ActionVerbEnhancer()
                verb_enhancements = enhancer.enhance_bullet_points(parser.text)
                analysis['verb_enhancements'] = verb_enhancements
            except Exception as e:
                # Non-fatal: skip verb analysis but log the error
                app.logger.warning(f"Verb analysis failed: {str(e)}")
                analysis['verb_enhancements'] = []
                analysis['warnings'] = analysis.get('warnings', []) + [
                    "Action verb analysis could not be completed"
                ]
            
            # Add resume format analysis
            try:
                format_analysis = analyze_resume_format(parser.text, contact_info)
                analysis['format_analysis'] = format_analysis
            except Exception as e:
                app.logger.warning(f"Format analysis failed: {str(e)}")
                analysis['format_analysis'] = None
            
            # Add template recommendations
            try:
                template_rec = get_template_recommendation(
                    similarity_score=similarity,
                    resume_skills=resume_skills,
                    job_description=job_parser.text
                )
                analysis['template_recommendation'] = template_rec
                analysis['ats_tips'] = get_ats_tips()
            except Exception as e:
                app.logger.warning(f"Template recommendation failed: {str(e)}")
                analysis['template_recommendation'] = None
                analysis['ats_tips'] = []
                
        except Exception as e:
            return error_response(
                'Error analyzing documents',
                details={'error': str(e)},
                status_code=500
            )
        finally:
            # Clean up uploaded files
            try:
                if os.path.exists(resume_path):
                    os.remove(resume_path)
                if os.path.exists(job_desc_path):
                    os.remove(job_desc_path)
            except Exception as e:
                app.logger.error(f"Failed to clean up uploaded files: {str(e)}")
        
        # Save analysis to database
        try:
            if 'session_id' not in session:
                session['session_id'] = str(uuid.uuid4())
            
            analysis_id = save_analysis(
                session_id=session['session_id'],
                resume_filename=resume_filename,
                job_desc_filename=job_desc_filename,
                similarity_score=similarity,
                analysis_data=analysis
            )
            analysis['id'] = analysis_id
        except Exception as e:
            app.logger.error(f"Failed to save analysis to database: {str(e)}")
            # Non-fatal: continue even if save fails
        
        return jsonify({
            'message': 'Analysis completed successfully',
            'analysis': analysis
        })
        
    except RequestEntityTooLarge:
        return error_response(
            'File too large',
            details={
                'message': 'One or both files exceed the 10MB size limit',
                'max_size': '10MB',
                'suggestion': 'Please reduce the file size and try again'
            },
            status_code=413
        )
    except ValidationError as e:
        # Already handled above, but catch here for safety
        return error_response(str(e), status_code=400)
    except FileNotFoundError as e:
        app.logger.error(f"File not found error: {str(e)}")
        return error_response(
            'File processing error',
            details={
                'message': 'Unable to locate uploaded file',
                'suggestion': 'Please try uploading again'
            },
            status_code=500
        )
    except PermissionError as e:
        app.logger.error(f"Permission error: {str(e)}")
        return error_response(
            'File access error',
            details={
                'message': 'Server lacks permission to process the file',
                'suggestion': 'Please contact support if this persists'
            },
            status_code=500
        )
    except Exception as e:
        app.logger.error(f"Unexpected error in upload_file: {str(e)}", exc_info=True)
        
        # Provide more helpful error message based on error type
        error_details = {
            'message': str(e),
            'type': type(e).__name__
        }
        
        # Add helpful suggestions for common errors
        if 'PDF' in str(e) or 'pdf' in str(e):
            error_details['suggestion'] = 'The PDF file may be corrupted or password-protected. Try converting it to a new PDF.'
        elif 'docx' in str(e).lower() or 'word' in str(e).lower():
            error_details['suggestion'] = 'The Word document may be corrupted. Try saving it as a new file or converting to PDF.'
        else:
            error_details['suggestion'] = 'Please try again with different files or contact support.'
        
        return error_response(
            'Analysis failed',
            details=error_details,
            status_code=500
        )

if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    app.run(debug=debug)