"""Validation utilities for request input and file handling."""
import os
from typing import Dict, Tuple, Optional
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

def validate_file_upload(file: FileStorage, field_name: str, allowed_extensions: set) -> Tuple[str, str]:
    """
    Validate a file upload and return the secure filename and file extension.
    
    Args:
        file: The uploaded file object
        field_name: Name of the file field for error messages
        allowed_extensions: Set of allowed file extensions
        
    Returns:
        Tuple of (secure_filename, extension)
        
    Raises:
        ValidationError: If file validation fails
    """
    if not file:
        raise ValidationError(f"{field_name} is required")
    
    if file.filename == '':
        raise ValidationError(f"No {field_name} file selected")
    
    # Get the file extension
    if '.' not in file.filename:
        raise ValidationError(f"{field_name} must have a file extension")
    
    extension = file.filename.rsplit('.', 1)[1].lower()
    if extension not in allowed_extensions:
        raise ValidationError(
            f"Invalid file type for {field_name}. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    return secure_filename(file.filename), extension

def validate_file_size(file: FileStorage, max_size_mb: int) -> None:
    """
    Validate that a file is under the maximum allowed size.
    
    Args:
        file: The uploaded file object
        max_size_mb: Maximum allowed size in megabytes
        
    Raises:
        ValidationError: If file is too large
    """
    # Read file content length
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)  # Reset file pointer
    
    max_size_bytes = max_size_mb * 1024 * 1024
    if size > max_size_bytes:
        raise ValidationError(
            f"File size exceeds maximum allowed size of {max_size_mb}MB"
        )

def error_response(message: str, details: Optional[Dict] = None, status_code: int = 400) -> Tuple[Dict, int]:
    """
    Create a consistent error response format.
    
    Args:
        message: Main error message
        details: Optional dictionary of additional error details
        status_code: HTTP status code
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    response = {
        'message': message,
        'status_code': status_code
    }
    if details:
        response['details'] = details
    return response, status_code