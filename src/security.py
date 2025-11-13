"""Security utilities for file validation and sanitization."""
import os
from typing import Tuple, Optional
from werkzeug.datastructures import FileStorage

# Try to import python-magic, but make it optional
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

# Known malicious file signatures (magic bytes)
SUSPICIOUS_SIGNATURES = [
    b'MZ',  # Executable
    b'PK\x03\x04',  # ZIP (could contain executables)
]

# Safe MIME types for documents
ALLOWED_MIMETYPES = {
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # DOCX
    'application/msword',  # DOC
}

def validate_file_content(file: FileStorage, allowed_extensions: set) -> Tuple[bool, Optional[str]]:
    """
    Validate file content beyond just extension checking.
    
    Args:
        file: The uploaded file object
        allowed_extensions: Set of allowed file extensions
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Reset file pointer
    file.seek(0)
    
    # Read file signature (first 8 bytes)
    signature = file.read(8)
    file.seek(0)
    
    # Check for suspicious signatures
    for sus_sig in SUSPICIOUS_SIGNATURES:
        if signature.startswith(sus_sig):
            return False, "File appears to be an executable or compressed archive"
    
    # Validate MIME type using python-magic if available
    if HAS_MAGIC:
        try:
            mime = magic.from_buffer(file.read(2048), mime=True)
            file.seek(0)
            
            if mime not in ALLOWED_MIMETYPES:
                return False, f"Invalid file type. Detected: {mime}"
        except Exception as e:
            # Log but don't fail on magic detection errors
            print(f"Warning: MIME detection failed: {e}")
    else:
        # python-magic not installed, skip MIME validation
        pass
    
    # Basic size validation (already checked, but double-check)
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    # Reject empty files
    if size == 0:
        return False, "File is empty"
    
    # Reject suspiciously small files (< 100 bytes unlikely to be valid doc)
    if size < 100:
        return False, "File is too small to be a valid document"
    
    # Reject suspiciously large files (> 20MB)
    if size > 20 * 1024 * 1024:
        return False, "File exceeds maximum size limit"
    
    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and other attacks.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove dangerous characters
    dangerous_chars = ['..', '/', '\\', '\x00', '\n', '\r']
    for char in dangerous_chars:
        filename = filename.replace(char, '')
    
    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 200:
        name = name[:200]
    
    return f"{name}{ext}"


def validate_pdf_structure(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate PDF file structure to detect corrupted or malicious PDFs.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        with open(file_path, 'rb') as f:
            # Check PDF header
            header = f.read(5)
            if not header.startswith(b'%PDF-'):
                return False, "Invalid PDF header"
            
            # Check for EOF marker
            f.seek(-1024, os.SEEK_END)
            tail = f.read()
            if b'%%EOF' not in tail:
                return False, "PDF file appears corrupted (missing EOF marker)"
        
        return True, None
    except Exception as e:
        return False, f"PDF validation failed: {str(e)}"
