"""
Tests for the experience matching functionality.
"""
import pytest
from experience_matcher import ExperienceMatcher

@pytest.fixture
def matcher():
    """Create an ExperienceMatcher instance for testing."""
    return ExperienceMatcher()

def test_extract_years_of_experience(matcher):
    """Test extracting years of experience from text."""
    # Test various year patterns
    assert matcher.extract_years_of_experience("5+ years of experience") == 5
    assert matcher.extract_years_of_experience("Minimum 3 years required") == 3
    assert matcher.extract_years_of_experience("Experience: 7 years") == 7
    assert matcher.extract_years_of_experience("At least 10 years") == 10
    
    # Test with surrounding text
    text = "Looking for a developer with 8+ years of Python experience"
    assert matcher.extract_years_of_experience(text) == 8
    
    # Test with no years mentioned
    assert matcher.extract_years_of_experience("Experienced developer") is None

def test_detect_experience_level(matcher):
    """Test experience level detection."""
    # Test clear cases
    entry_text = "Entry level position for recent graduates"
    level, conf = matcher.detect_experience_level(entry_text)
    assert level == "entry"
    assert conf > 0.5
    
    senior_text = "Senior developer position requiring expert knowledge"
    level, conf = matcher.detect_experience_level(senior_text)
    assert level == "senior"
    assert conf > 0.5
    
    # Test mixed signals
    mixed_text = "Mid-level position with some senior responsibilities"
    level, conf = matcher.detect_experience_level(mixed_text)
    assert level in ["mid", "senior"]
    
    # Test with no clear indicators
    vague_text = "Software developer position"
    level, conf = matcher.detect_experience_level(vague_text)
    assert conf < 0.5

def test_role_progression(matcher):
    """Test extracting role progression."""
    resume = """
    Work Experience
    
    Senior Software Engineer at Tech Corp (2020-Present)
    Lead development team of 5 engineers
    
    Software Developer at StartUp Inc (2018-2020)
    Full-stack development
    
    Junior Developer at First Co (2016-2018)
    Entry level position
    """
    
    roles = matcher.extract_role_progression(resume)
    
    # Should find at least 2 roles
    assert len(roles) >= 2
    
    # Roles should be in ascending level order
    levels = [role['level'] for role in roles]
    assert sorted(levels) == levels
    
    # Should identify senior role
    assert any('senior' in role['title'].lower() for role in roles)

def test_experience_match_analysis(matcher):
    """Test full experience matching analysis."""
    job_text = """
    Position: Senior Software Engineer
    Required:
    - 5+ years of experience in software development
    - Proven leadership experience
    - Strong technical background
    """
    
    resume_text = """
    Work Experience:
    
    Senior Software Engineer (2020-Present)
    - Leading team of developers
    - Architecting solutions
    
    Software Developer (2018-2020)
    - Full-stack development
    """
    
    analysis = matcher.analyze_experience_match(resume_text, job_text)
    
    # Check structure
    assert 'match' in analysis
    assert 'details' in analysis
    assert 'feedback' in analysis
    
    # Check match scores
    assert analysis['match']['years'] >= 0.5  # Matches requirements
    assert analysis['match']['level'] >= 0.6  # Similar level
    assert analysis['match']['overall'] >= 0.5  # Good overall match
    
    # Check extracted details
    job_reqs = analysis['details']['job_requirements']
    assert job_reqs['years'] == 5
    assert job_reqs['level'] == 'senior'
    
    # Check role detection
    roles = analysis['details']['resume_experience']['roles']
    assert len(roles) >= 1  # Should find at least one role
    assert any('senior' in role['title'].lower() for role in roles)

def test_experience_mismatch(matcher):
    """Test analysis of mismatched experience levels."""
    job_text = """
    Senior Architect Position
    Minimum 10 years of experience required
    Expert-level technical leadership
    """
    
    resume_text = """
    Junior Developer with 2 years of experience
    Currently working on web applications
    """
    
    analysis = matcher.analyze_experience_match(resume_text, job_text)
    
    # Should indicate low match scores
    assert analysis['match']['years'] < 0.5
    assert analysis['match']['level'] < 0.5
    assert analysis['match']['overall'] < 0.5
    
    # Should provide feedback about the mismatch
    assert any('10' in f for f in analysis['feedback'])  # Years mismatch
    assert any('senior' in f.lower() for f in analysis['feedback'])  # Level mismatch