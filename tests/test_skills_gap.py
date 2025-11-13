"""
Tests for the enhanced skills gap analysis functionality.
"""
import pytest
from scorer.scorer import ResumeScorer

@pytest.fixture
def scorer():
    """Create a ResumeScorer instance for testing."""
    return ResumeScorer()

def test_skills_gap_analysis(scorer):
    """Test the detailed skills gap analysis functionality."""
    resume_text = """
    Experienced software engineer with 5 years of experience in Python development.
    Strong skills in: Python, JavaScript, SQL
    Additional experience with: Docker, AWS
    """
    
    job_text = """
    Required Skills:
    - Python (must have)
    - TensorFlow (essential)
    - SQL
    
    Nice to have:
    - AWS
    - Kubernetes
    - React
    """
    
    analysis = scorer.get_skills_gap_analysis(resume_text, job_text)
    
    # Check critical missing skills
    assert "tensorflow" in [s.lower() for s in analysis['gaps']['critical_missing']], \
        "TensorFlow should be identified as a critical missing skill"
    
    # Check nice to have missing skills
    assert "kubernetes" in [s.lower() for s in analysis['gaps']['nice_to_have_missing']], \
        "Kubernetes should be identified as a nice-to-have missing skill"
    assert "react" in [s.lower() for s in analysis['gaps']['nice_to_have_missing']], \
        "React should be identified as a nice-to-have missing skill"
    
    # Check matched skills
    assert "python" in [s.lower() for s in analysis['matches']['matched_skills']], \
        "Python should be identified as a matched skill"
    assert "sql" in [s.lower() for s in analysis['matches']['matched_skills']], \
        "SQL should be identified as a matched skill"
    assert "aws" in [s.lower() for s in analysis['matches']['matched_skills']], \
        "AWS should be identified as a matched skill"
    
    # Check additional skills
    assert "javascript" in [s.lower() for s in analysis['matches']['additional_skills']], \
        "JavaScript should be identified as an additional skill"
    assert "docker" in [s.lower() for s in analysis['matches']['additional_skills']], \
        "Docker should be identified as an additional skill"

def test_skills_gap_empty_texts(scorer):
    """Test skills gap analysis with empty texts."""
    analysis = scorer.get_skills_gap_analysis("", "")
    
    assert len(analysis['gaps']['critical_missing']) == 0, \
        "Empty texts should result in no critical missing skills"
    assert len(analysis['gaps']['nice_to_have_missing']) == 0, \
        "Empty texts should result in no nice-to-have missing skills"
    assert len(analysis['matches']['matched_skills']) == 0, \
        "Empty texts should result in no matched skills"
    assert len(analysis['matches']['additional_skills']) == 0, \
        "Empty texts should result in no additional skills"