"""
Tests for the resume scoring module.
"""
import pytest
from scorer.scorer import ResumeScorer

@pytest.fixture
def scorer():
    """Create a ResumeScorer instance for testing."""
    return ResumeScorer()

def test_similarity_score(scorer):
    """Test similarity scoring between resume and job description."""
    resume_text = """
    Experienced software engineer with 5 years of experience in Python development.
    Skills: Python, JavaScript, SQL, Docker, AWS
    Led development of machine learning models using TensorFlow.
    """
    
    job_text = """
    Looking for a Python developer with machine learning experience.
    Required skills: Python, TensorFlow, SQL
    Nice to have: AWS, Docker
    """
    
    similarity = scorer.compute_similarity(resume_text, job_text)
    
    # Should have high similarity due to matching skills
    assert 0.35 <= similarity <= 1.0, f"Similarity score {similarity} is too low"

def test_important_terms(scorer):
    """Test extraction of important terms."""
    resume_text = "Experienced Python developer with AWS and Docker experience"
    job_text = "Looking for Python developer with cloud experience"
    
    scorer.compute_similarity(resume_text, job_text)
    terms = scorer.get_important_terms(n_terms=5)
    
    assert 'python' in [term.lower() for term in terms['resume_terms']]
    assert 'python' in [term.lower() for term in terms['job_terms']]
    assert len(terms['resume_terms']) == 5
    assert len(terms['job_terms']) == 5

def test_missing_skills(scorer):
    """Test identification of missing skills."""
    resume_skills = ['Python', 'JavaScript', 'SQL']
    job_skills = ['Python', 'Java', 'C++', 'SQL']
    
    missing = scorer.get_missing_skills(resume_skills, job_skills)
    
    assert 'Java' in missing
    assert 'C++' in missing
    assert 'Python' not in missing
    assert 'SQL' not in missing

def test_feedback_generation(scorer):
    """Test feedback generation."""
    resume_text = "Python developer with SQL experience"
    job_text = "Looking for Python developer with Java experience"
    
    similarity = scorer.compute_similarity(resume_text, job_text)
    terms = scorer.get_important_terms()
    
    feedback = scorer.generate_feedback(
        similarity_score=similarity,
        resume_skills=['Python', 'SQL'],
        job_skills=['Python', 'Java'],
        important_terms=terms
    )
    
    assert 'match_percentage' in feedback
    assert 'overall_feedback' in feedback
    assert 'missing_skills' in feedback
    assert 'suggestions' in feedback
    assert isinstance(feedback['suggestions'], list)
    assert 'Java' in feedback['missing_skills']