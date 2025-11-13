"""
Tests for bullet point extraction functionality.
"""
import unittest
from src.resume_parser.bullet_extractor import BulletPointExtractor

class TestBulletPointExtractor(unittest.TestCase):
    """Test cases for BulletPointExtractor class."""
    
    def setUp(self):
        """Set up test cases."""
        self.extractor = BulletPointExtractor()
    
    def test_extract_bullet_points_with_bullets(self):
        """Test extracting bullet points with bullet characters."""
        text = """Experience:
        • Led team of 5 developers on cloud migration project
        • Implemented CI/CD pipeline using Jenkins
        • Reduced deployment time by 60%"""
        
        expected = [
            "Led team of 5 developers on cloud migration project.",
            "Implemented CI/CD pipeline using Jenkins.",
            "Reduced deployment time by 60%."
        ]
        
        result = self.extractor.extract_bullet_points(text)
        self.assertEqual(result, expected)
    
    def test_extract_bullet_points_with_dashes(self):
        """Test extracting bullet points with dashes."""
        text = """Key Achievements:
        - Increased test coverage to 95%
        - Fixed 100+ critical bugs
        - Mentored 3 junior developers"""
        
        expected = [
            "Increased test coverage to 95%.",
            "Fixed 100+ critical bugs.",
            "Mentored 3 junior developers."
        ]
        
        result = self.extractor.extract_bullet_points(text)
        self.assertEqual(result, expected)
    
    def test_extract_bullet_points_with_numbers(self):
        """Test extracting bullet points with numbers."""
        text = """Project Highlights:
        1. Designed scalable microservices architecture
        2. Implemented OAuth2 authentication
        3. Deployed to AWS using Terraform"""
        
        expected = [
            "Designed scalable microservices architecture.",
            "Implemented OAuth2 authentication.",
            "Deployed to AWS using Terraform."
        ]
        
        result = self.extractor.extract_bullet_points(text)
        self.assertEqual(result, expected)
    
    def test_extract_bullet_points_mixed_formats(self):
        """Test extracting bullet points with mixed formats."""
        text = """Experience:
        • Backend Development
        - Python/Django API development
        1. Implemented RESTful endpoints
        * Wrote comprehensive tests
        → Deployed to production"""
        
        expected = [
            "Backend Development.",
            "Python/Django API development.",
            "Implemented RESTful endpoints.",
            "Wrote comprehensive tests.",
            "Deployed to production."
        ]
        
        result = self.extractor.extract_bullet_points(text)
        self.assertEqual(result, expected)
    
    def test_format_bullet_points(self):
        """Test formatting bullet points consistently."""
        bullet_points = [
            "Led development team.",
            "Implemented new features.",
            "Improved performance."
        ]
        
        expected = [
            "• Led development team.",
            "• Implemented new features.",
            "• Improved performance."
        ]
        
        result = self.extractor.format_bullet_points(bullet_points)
        self.assertEqual(result, expected)
    
    def test_multiline_bullet_points(self):
        """Test extracting bullet points that span multiple lines."""
        text = """Experience:
        • Led development team working on 
          high-performance trading platform
        • Implemented advanced features for
          real-time market data analysis"""
        
        expected = [
            "Led development team working on high-performance trading platform.",
            "Implemented advanced features for real-time market data analysis."
        ]
        
        result = self.extractor.extract_bullet_points(text)
        self.assertEqual(result, expected)
    
    def test_nested_bullet_points(self):
        """Test extracting nested bullet points."""
        text = """Skills:
        • Programming Languages:
          - Python
          - Java
          - JavaScript
        • Tools:
          - Git
          - Docker
          - Jenkins"""
        
        expected = [
            "Programming Languages:",
            "Python.",
            "Java.",
            "JavaScript.",
            "Tools:",
            "Git.",
            "Docker.",
            "Jenkins."
        ]
        
        result = self.extractor.extract_bullet_points(text)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()