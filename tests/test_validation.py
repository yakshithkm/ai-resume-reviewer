"""Tests for validation utilities and API error handling."""
import os
import pytest
from io import BytesIO
from src.validation import validate_file_upload, validate_file_size, ValidationError, error_response

class MockFileStorage:
    """Mock Werkzeug's FileStorage for testing."""
    def __init__(self, filename: str = '', content: bytes = b''):
        self.filename = filename
        self.stream = BytesIO(content)
        self._size = len(content)
    
    def seek(self, offset: int, whence: int = 0):
        self.stream.seek(offset, whence)
    
    def tell(self):
        return self._size

def test_validate_file_upload_success():
    """Test successful file validation."""
    file = MockFileStorage(filename='test.pdf', content=b'test content')
    filename, ext = validate_file_upload(file, 'Resume', {'pdf', 'docx'})
    assert filename == 'test.pdf'
    assert ext == 'pdf'

def test_validate_file_upload_no_file():
    """Test validation when no file is provided."""
    with pytest.raises(ValidationError) as exc:
        validate_file_upload(None, 'Resume', {'pdf', 'docx'})
    assert 'Resume is required' in str(exc.value)

def test_validate_file_upload_empty_filename():
    """Test validation with empty filename."""
    file = MockFileStorage(filename='')
    with pytest.raises(ValidationError) as exc:
        validate_file_upload(file, 'Resume', {'pdf', 'docx'})
    assert 'No Resume file selected' in str(exc.value)

def test_validate_file_upload_no_extension():
    """Test validation when file has no extension."""
    file = MockFileStorage(filename='testfile')
    with pytest.raises(ValidationError) as exc:
        validate_file_upload(file, 'Resume', {'pdf', 'docx'})
    assert 'must have a file extension' in str(exc.value)

def test_validate_file_upload_invalid_extension():
    """Test validation with disallowed extension."""
    file = MockFileStorage(filename='test.txt')
    with pytest.raises(ValidationError) as exc:
        validate_file_upload(file, 'Resume', {'pdf', 'docx'})
    assert 'Invalid file type' in str(exc.value)

def test_validate_file_size_success():
    """Test file size validation success."""
    file = MockFileStorage(content=b'x' * 1024 * 1024)  # 1MB
    validate_file_size(file, 2)  # 2MB limit
    assert True  # No exception raised

def test_validate_file_size_too_large():
    """Test file size validation failure."""
    file = MockFileStorage(content=b'x' * (3 * 1024 * 1024))  # 3MB
    with pytest.raises(ValidationError) as exc:
        validate_file_size(file, 2)  # 2MB limit
    assert 'exceeds maximum allowed size' in str(exc.value)

def test_error_response_basic():
    """Test basic error response generation."""
    response, code = error_response('Test error')
    assert response['error']['message'] == 'Test error'
    assert response['error']['status_code'] == 400
    assert code == 400

def test_error_response_with_details():
    """Test error response with additional details."""
    response, code = error_response(
        'Test error',
        details={'field': 'test', 'reason': 'invalid'},
        status_code=422
    )
    assert response['error']['message'] == 'Test error'
    assert response['error']['status_code'] == 422
    assert response['error']['details']['field'] == 'test'
    assert code == 422