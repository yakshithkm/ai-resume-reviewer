"""
Tests for the resume suggestion engine.
"""
import pytest
from suggestion_engine import SuggestionEngine

@pytest.fixture
def engine():
    """Create a SuggestionEngine instance for testing."""
    return SuggestionEngine()

def test_identify_sections(engine):
    """Test section identification in resume text."""
    resume_text = """Summary
Experienced software engineer with 5 years of Python development.

Experience
Senior Developer, TechCorp (2020-Present)
• Built scalable web applications

Skills
Python, JavaScript, SQL

Education
BS Computer Science, Tech University, 2018"""
    
    sections = engine.identify_sections(resume_text)
    
    assert 'summary' in sections
    assert 'experience' in sections
    assert 'skills' in sections
    assert 'education' in sections
    
    assert "5 years" in sections['summary']
    assert "TechCorp" in sections['experience']
    assert "Python" in sections['skills']
    assert "Tech University" in sections['education']

def test_section_analysis(engine):
    """Test section-specific analysis and suggestions."""
    job_description = """
    Required: 5+ years Python development experience
    Must have: AWS, Docker, Kubernetes
    Bachelor's degree in Computer Science
    Looking for someone who has led teams and can show quantifiable achievements
    """
    
    # Test experience section
    experience_content = """
    Software Engineer, TechCorp
    • Wrote code for web applications
    • Helped the team with projects
    """
    suggestions = engine.analyze_section('experience', experience_content, job_description)
    
    assert any('quantifiable' in s.lower() for s in suggestions)
    assert any('action verbs' in s.lower() for s in suggestions)
    
    # Test skills section
    skills_content = "Python, JavaScript, React"
    suggestions = engine.analyze_section('skills', skills_content, job_description)
    
    assert any('aws' in s.lower() for s in suggestions)
    assert any('docker' in s.lower() for s in suggestions)
    
    # Test education section
    education_content = "BS Computer Science, University"
    suggestions = engine.analyze_section('education', education_content, job_description)
    
    assert any('gpa' in s.lower() for s in suggestions)
    assert any('coursework' in s.lower() for s in suggestions)

def test_full_suggestions(engine):
    """Test end-to-end suggestion generation."""
    resume_text = """Summary
Software engineer with Python experience

Experience
Developer at TechCorp
• Wrote code
• Helped team

Skills
Python, JavaScript"""
    
    job_description = """Senior Python Developer
Required:
- 5+ years Python experience
- AWS, Docker expertise
- Bachelor's degree
- Leadership experience"""
    
    suggestions = engine.generate_suggestions(resume_text, job_description)
    
    # Should suggest adding education section
    assert 'education' in suggestions
    assert any('add' in s.lower() for s in suggestions['education'])
    
    # Should have suggestions for experience section
    assert 'experience' in suggestions
    
    # Should suggest improving skills section
    assert 'skills' in suggestions
    assert any('aws' in s.lower() for s in suggestions['skills'])
    
    # Should suggest adding missing skills
    assert 'skills' in suggestions
    assert any('aws' in s.lower() for s in suggestions['skills'])

def test_empty_inputs(engine):
    """Test handling of empty inputs."""
    suggestions = engine.generate_suggestions("", "")
    
    # Should suggest adding all major sections
    assert len(suggestions) > 0
    assert all(section in suggestions for section in ['education', 'experience', 'skills', 'summary'])