"""
Tests for the industry keyword analysis functionality.
"""
import pytest
from keyword_analyzer import IndustryKeywordAnalyzer

@pytest.fixture
def analyzer():
    """Create an IndustryKeywordAnalyzer instance for testing."""
    return IndustryKeywordAnalyzer()

def test_industry_detection(analyzer):
    """Test detecting industry from text."""
    # Test software development text
    software_text = """
    Looking for a senior Python developer with experience in
    Django, React, and AWS. Must know Git and CI/CD practices.
    """
    industries = analyzer.detect_industry(software_text)
    assert len(industries) > 0
    assert 'software' == industries[0][0]  # First result should be software
    
    # Test data science text
    data_text = """
    Data Scientist position requiring expertise in Machine Learning,
    TensorFlow, and statistical analysis. Experience with scikit-learn
    and Pandas required.
    """
    industries = analyzer.detect_industry(data_text)
    assert len(industries) > 0
    assert 'data_science' == industries[0][0]  # First result should be data science

def test_keyword_extraction(analyzer):
    """Test extracting industry-specific keywords."""
    text = """
    Full Stack Developer with 5 years experience in Python and JavaScript.
    Built scalable web applications using Django and React.
    Implemented CI/CD pipelines with Jenkins and Docker.
    """
    
    keywords = analyzer.extract_industry_keywords(text, ['software'])
    
    # Should find programming languages
    assert any('Python' in terms for terms in keywords.values())
    assert any('JavaScript' in terms for terms in keywords.values())
    
    # Should find frameworks
    assert any('Django' in terms for terms in keywords.values())
    assert any('React' in terms for terms in keywords.values())
    
    # Should find tools
    assert any('Docker' in terms for terms in keywords.values())
    assert any('Jenkins' in terms for terms in keywords.values())

def test_keyword_match_analysis(analyzer):
    """Test analyzing keyword matches between resume and job."""
    job_text = """
    Senior Software Engineer
    Required Skills:
    - Python, JavaScript
    - React, Django
    - AWS, Docker
    - CI/CD experience
    """
    
    resume_text = """
    Software Engineer with experience in:
    - Python and JavaScript development
    - React.js for frontend
    - Basic Docker knowledge
    """
    
    analysis = analyzer.analyze_keyword_match(resume_text, job_text)
    
    # Check structure
    assert 'industries' in analysis
    assert 'matches' in analysis
    assert 'scores' in analysis
    
    # Should identify matching keywords
    matches = analysis['matches']['matching_keywords']
    assert any('Python' in terms for terms in matches.values())
    assert any('React' in terms for terms in matches.values())
    
    # Should identify gaps
    gaps = analysis['matches']['missing_keywords']
    assert any('Django' in terms for terms in gaps.values())
    assert any('AWS' in terms for terms in gaps.values())

def test_keyword_suggestions(analyzer):
    """Test generating keyword improvement suggestions."""
    job_text = """
    We are seeking an innovative software architect to drive cutting-edge development.
    
    Required Skills:
    - Expert in Java programming
    - Cloud platforms (AWS and Azure)
    - DevOps and CI/CD
    
    Nice to have:
    - Python knowledge
    - Microservices architecture
    """
    
    resume_text = """
    Software Developer

    Technical Skills:
    - Strong Python development
    - Basic CI/CD experience
    - Some cloud knowledge
    
    Experience:
    - Built and maintained web applications
    - Worked with small development teams
    """
    
    analysis = analyzer.analyze_keyword_match(resume_text, job_text)
    suggestions = analyzer.suggest_keyword_improvements(analysis)
    
    # Check for missing technical skills suggestions
    missing_tech = False
    for suggestion in suggestions:
        if 'Java' in suggestion:
            missing_tech = True
            break
    assert missing_tech, "Should suggest Java as missing skill"
    
    # Check for cloud platforms suggestion
    cloud_suggestion = False
    for suggestion in suggestions:
        if ('AWS' in suggestion and 'Azure' in suggestion):
            cloud_suggestion = True
            break
    assert cloud_suggestion, "Should suggest AWS and Azure as missing skills"
    
    # Check for buzzword suggestions
    buzzword_suggestion = False
    for suggestion in suggestions:
        if 'innovative' in suggestion.lower() or 'cutting-edge' in suggestion.lower():
            buzzword_suggestion = True
            break
    assert buzzword_suggestion, "Should suggest incorporating key buzzwords"

def test_empty_inputs(analyzer):
    """Test handling of empty inputs."""
    analysis = analyzer.analyze_keyword_match("", "")
    
    # Should return valid structure with empty results
    assert 'industries' in analysis
    assert len(analysis['industries']) == 0
    assert 'matches' in analysis
    assert 'scores' in analysis
    assert analysis['scores']['overall_match'] == 0.0