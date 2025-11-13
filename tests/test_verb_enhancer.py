"""
Tests for the ActionVerbEnhancer class.
"""
import pytest
from src.verb_enhancer import ActionVerbEnhancer

@pytest.fixture
def enhancer():
    """Create an ActionVerbEnhancer instance for testing."""
    return ActionVerbEnhancer()

def test_identify_bullet_points(enhancer):
    """Test bullet point identification with various markers."""
    text = """
    • First bullet
    - Second bullet
    * Third bullet
    1. Fourth bullet
    ⦁ Fifth bullet
    """
    
    points = enhancer.identify_bullet_points(text)
    assert len(points) == 5
    assert "First bullet" in points
    assert "Second bullet" in points
    assert "Third bullet" in points
    assert "Fourth bullet" in points
    assert "Fifth bullet" in points

def test_extract_leading_verb(enhancer):
    """Test extraction of leading verbs from bullet points."""
    text = "Developed a new feature"
    verb, start, end = enhancer.extract_leading_verb(text)
    assert verb == "Developed"
    assert start == 0
    assert end == 9

def test_no_leading_verb(enhancer):
    """Test handling of text without a leading verb."""
    text = "Great team player"
    verb, start, end = enhancer.extract_leading_verb(text)
    assert verb is None
    assert start == -1
    assert end == -1

def test_categorize_verb(enhancer):
    """Test verb categorization."""
    # Test strong leadership verb
    categories = enhancer.categorize_verb("spearheaded")
    assert ("leadership", "strong") in categories
    
    # Test weak technical verb
    categories = enhancer.categorize_verb("used")
    assert ("technical", "weak") in categories
    
    # Test uncategorized verb
    categories = enhancer.categorize_verb("xyz")
    assert len(categories) == 0

def test_suggest_stronger_verbs(enhancer):
    """Test verb improvement suggestions."""
    # Test weak verb
    suggestions = enhancer.suggest_stronger_verbs("helped")
    assert len(suggestions) > 0
    assert all(s in enhancer.action_verbs["leadership"]["strong"] for s in suggestions)
    
    # Test unknown verb
    suggestions = enhancer.suggest_stronger_verbs("xyz")
    assert len(suggestions) == 0

def test_enhance_bullet_point_weak_verb(enhancer):
    """Test enhancement of bullet point with weak verb."""
    result = enhancer.enhance_bullet_point("Helped team with project")
    assert result["has_verb"]
    assert result["verb"] == "Helped"
    assert result["strength"] == "weak"
    assert len(result["suggestions"]) > 0
    assert len(result["examples"]) > 0

def test_enhance_bullet_point_strong_verb(enhancer):
    """Test enhancement of bullet point with strong verb."""
    result = enhancer.enhance_bullet_point("Spearheaded development initiative")
    assert result["has_verb"]
    assert result["verb"] == "Spearheaded"
    assert result["strength"] == "strong"
    assert "suggestions" not in result

def test_enhance_bullet_point_no_verb(enhancer):
    """Test enhancement of bullet point without verb."""
    result = enhancer.enhance_bullet_point("Expert in Python")
    assert not result["has_verb"]
    assert "suggestion" in result

def test_enhance_bullet_points(enhancer):
    """Test enhancement of multiple bullet points."""
    text = """
    • Helped with project planning
    • Spearheaded new initiative
    • Python expert
    """
    
    results = enhancer.enhance_bullet_points(text)
    assert len(results) == 3
    
    # Check weak verb enhancement
    assert results[0]["strength"] == "weak"
    assert "suggestions" in results[0]
    
    # Check strong verb
    assert results[1]["strength"] == "strong"
    
    # Check missing verb
    assert not results[2]["has_verb"]

def test_summarize_enhancements_empty(enhancer):
    """Test enhancement summary with no bullet points."""
    summary = enhancer.summarize_enhancements([])
    assert summary["status"] == "No bullet points found"
    assert len(summary["suggestions"]) > 0

def test_summarize_enhancements(enhancer):
    """Test enhancement summary with mixed bullet points."""
    enhancements = [
        # Strong verb
        {
            "has_verb": True,
            "verb": "Spearheaded",
            "strength": "strong"
        },
        # Weak verb
        {
            "has_verb": True,
            "verb": "helped",
            "strength": "weak"
        },
        # Missing verb
        {
            "has_verb": False
        }
    ]
    
    summary = enhancer.summarize_enhancements(enhancements)
    assert summary["stats"]["total_points"] == 3
    assert summary["stats"]["verb_usage"]["strong"] == 1
    assert summary["stats"]["verb_usage"]["weak"] == 1
    assert summary["stats"]["verb_usage"]["missing"] == 1
    assert len(summary["suggestions"]) > 0
    assert summary["status"] == "needs_improvement"

def test_multi_word_verbs(enhancer):
    """Test handling of multi-word verb phrases."""
    text = "Was responsible for project delivery"
    result = enhancer.enhance_bullet_point(text)
    assert result["has_verb"]
    assert result["strength"] == "weak"
    assert len(result["suggestions"]) > 0

    def test_verb_with_particle(enhancer):
        """Test handling of verbs with particles."""
        text = "Set up new development environment"
        result = enhancer.enhance_bullet_point(text)
        assert result["has_verb"]
        # Should identify "Set up" as the verb phrase
        assert result["verb"] == "Set up"
        
def test_bullet_point_real_examples(enhancer):
    """Test with real-world resume bullet points."""
    examples = [
        "Developed scalable microservices architecture",
        "Managed team of 5 developers",
        "Helped improve system performance",
        "Was responsible for deployment automation",
        "Worked on critical features"
    ]
    
    for example in examples:
        result = enhancer.enhance_bullet_point(example)
        assert result["has_verb"]
        assert "verb" in result
        assert "strength" in result