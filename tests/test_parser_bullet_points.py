"""
Tests for resume parser functionality with bullet point extraction.
"""
import unittest
from src.resume_parser.parser import ResumeParser

class TestResumeParserBulletPoints(unittest.TestCase):
    """Test cases for ResumeParser bullet point functionality."""
    
    def setUp(self):
        """Set up test cases."""
        self.parser = ResumeParser()
        
    def test_experience_bullet_points(self):
        """Test extracting bullet points from experience section."""
        self.parser.text = """
        Work Experience
        
        Senior Software Engineer at TechCorp
        • Led development of cloud-based platform
        • Implemented CI/CD pipeline
        • Mentored junior developers
        
        Software Engineer at StartupCo
        - Developed RESTful APIs
        - Improved test coverage by 40%
        - Optimized database queries
        """
        
        sections = self.parser.parse_resume()
        self.assertIn('experience', sections)
        self.assertIn('bullet_points', sections['experience'])
        
        bullet_points = sections['experience']['bullet_points']
        expected = [
            "Led development of cloud-based platform.",
            "Implemented CI/CD pipeline.",
            "Mentored junior developers.",
            "Developed RESTful APIs.",
            "Improved test coverage by 40%.",
            "Optimized database queries."
        ]
        
        self.assertEqual(bullet_points, expected)
    
    def test_education_bullet_points(self):
        """Test extracting bullet points from education section."""
        self.parser.text = """
        Education
        
        University of Technology
        Master of Computer Science
        • Specialized in Machine Learning
        • Research assistant in NLP lab
        • Published 2 conference papers
        
        Tech College
        Bachelor of Engineering
        - Dean's List all semesters
        - Led student coding club
        - Completed capstone project
        """
        
        sections = self.parser.parse_resume()
        self.assertIn('education', sections)
        self.assertIn('bullet_points', sections['education'])
        
        bullet_points = sections['education']['bullet_points']
        expected = [
            "Specialized in Machine Learning.",
            "Research assistant in NLP lab.",
            "Published 2 conference papers.",
            "Dean's List all semesters.",
            "Led student coding club.",
            "Completed capstone project."
        ]
        
        self.assertEqual(bullet_points, expected)
    
    def test_skills_bullet_points(self):
        """Test extracting bullet points from skills section."""
        self.parser.text = """
        Skills
        
        Programming Languages:
        • Python (Expert)
        • Java (Advanced)
        • JavaScript (Intermediate)
        
        Tools and Technologies:
        - Git
        - Docker
        - Kubernetes
        """
        
        sections = self.parser.parse_resume()
        self.assertIn('skills', sections)
        self.assertIn('bullet_points', sections['skills'])
        
        bullet_points = sections['skills']['bullet_points']
        expected = [
            "Programming Languages:",
            "Python (Expert).",
            "Java (Advanced).",
            "JavaScript (Intermediate).",
            "Tools and Technologies:",
            "Git.",
            "Docker.",
            "Kubernetes."
        ]
        
        self.assertEqual(bullet_points, expected)
    
    def test_mixed_section_bullet_points(self):
        """Test extracting bullet points from multiple sections."""
        self.parser.text = """
        Experience
        Software Engineer
        • Built scalable APIs
        • Led team of 3
        
        Education
        University
        - Bachelor's in CS
        - Dean's List
        
        Skills
        • Python
        • Java
        """
        
        sections = self.parser.parse_resume()
        
        # Check experience bullets
        self.assertIn('experience', sections)
        experience_bullets = sections['experience']['bullet_points']
        self.assertEqual(experience_bullets, [
            "Built scalable APIs.",
            "Led team of 3."
        ])
        
        # Check education bullets
        self.assertIn('education', sections)
        education_bullets = sections['education']['bullet_points']
        self.assertEqual(education_bullets, [
            "Bachelor's in CS.",
            "Dean's List."
        ])
        
        # Check skills bullets
        self.assertIn('skills', sections)
        skills_bullets = sections['skills']['bullet_points']
        self.assertEqual(skills_bullets, [
            "Python.",
            "Java."
        ])
    
    def test_no_bullet_points(self):
        """Test sections without bullet points."""
        self.parser.text = """
        Summary
        Experienced software engineer with passion for clean code.
        
        Contact
        email@example.com
        (123) 456-7890
        """
        
        sections = self.parser.parse_resume()
        
        # Check summary section has no bullets
        self.assertIn('summary', sections)
        self.assertEqual(sections['summary']['bullet_points'], [])
        
        # Check contact section has no bullets
        self.assertIn('contact', sections)
        self.assertEqual(sections['contact']['bullet_points'], [])