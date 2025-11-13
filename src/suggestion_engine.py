"""
Module for generating resume section improvement suggestions.
"""
from typing import Dict, List, Optional
import re
from collections import Counter

class SuggestionEngine:
    """Generate targeted suggestions for improving resume sections."""
    
    def __init__(self):
        """Initialize the suggestion engine."""
        # Define primary section headers (exact matches)
        self.section_headers = {
            'education': ['education'],
            'experience': ['experience', 'work experience', 'employment history'],
            'skills': ['skills', 'technical skills', 'core competencies'],
            'projects': ['projects', 'portfolio'],
            'summary': ['summary', 'professional summary', 'profile']
        }
        
        # Define additional patterns for fuzzy matching
        self.section_patterns = {
            'education': r'education|academic|degree|university|college|school',
            'experience': r'experience|work|employment|job|position|career',
            'skills': r'skills|technologies|tools|programming|languages',
            'projects': r'projects|portfolio|achievements|accomplishments',
            'summary': r'summary|objective|profile|about',
        }
        
        self.section_requirements = {
            'education': [
                'degree name',
                'field of study',
                'university name',
                'graduation year',
                'GPA (if notable)',
                'relevant coursework',
                'academic achievements'
            ],
            'experience': [
                'company name',
                'job title',
                'employment dates',
                'location',
                'key responsibilities',
                'quantifiable achievements',
                'technologies used'
            ],
            'skills': [
                'technical skills',
                'soft skills',
                'certifications',
                'proficiency levels',
                'tools and technologies',
                'languages'
            ],
            'projects': [
                'project name',
                'technologies used',
                'role/responsibilities',
                'outcome/impact',
                'timeline',
                'team size'
            ],
            'summary': [
                'years of experience',
                'key expertise areas',
                'notable achievements',
                'career objectives',
                'unique value proposition'
            ]
        }
    
    def identify_sections(self, text: str) -> Dict[str, str]:
        """
        Identify different sections in the resume text.
        
        Args:
            text: The full resume text
            
        Returns:
            Dictionary mapping section names to their content
        """
        sections = {}
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        # Remove leading/trailing whitespace from entire text
        text = '\n'.join(line for line in lines)
        sections_text = [section.strip() for section in text.split('\n\n') if section.strip()]
        
        # Process each potential section
        for section_text in sections_text:
            lines = section_text.split('\n')
            first_line = lines[0].strip().lower()
            content_lines = [line.strip() for line in lines[1:] if line.strip()]
            
            # Identify section type from first line
            section_type = None
            
            # Check exact matches first
            for section, headers in self.section_headers.items():
                if any(header == first_line for header in headers):
                    section_type = section
                    break
                    
            # Then try pattern matches
            if not section_type:
                for section, pattern in self.section_patterns.items():
                    if re.search(pattern, first_line):
                        section_type = section
                        break
            
            # If we found a section type and have content, add it
            if section_type and content_lines:
                sections[section_type] = '\n'.join(content_lines)        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
            
        return sections
    
    def analyze_section(self, section: str, content: str, job_requirements: str) -> List[str]:
        """
        Analyze a resume section and generate improvement suggestions.
        
        Args:
            section: The name of the section (education, experience, etc.)
            content: The content of the section
            job_requirements: The job description requirements
            
        Returns:
            List of suggestions for improving the section
        """
        suggestions = []
        requirements = self.section_requirements.get(section, [])
        
        # Check for missing required elements
        for req in requirements:
            if not any(keyword in content.lower() for keyword in req.lower().split()):
                suggestions.append(f"Add {req} to your {section} section")
        
        # Section-specific analysis
        if section == 'experience':
            # Check for quantifiable achievements
            if not re.search(r'\d+%|\d+x|\$\d+|\d+ \w+', content):
                suggestions.append("Add quantifiable achievements (e.g., increased efficiency by 25%, managed $1M budget)")
                
            # Check for action verbs at the start of bullets
            lines = content.split('\n')
            for line in lines:
                if line.strip().startswith('•') and not re.match(r'•\s*(Led|Developed|Implemented|Created|Managed|Improved)', line):
                    suggestions.append("Start bullet points with strong action verbs (e.g., Led, Developed, Implemented)")
                    break
        
        elif section == 'skills':
            # Extract skills from job requirements
            job_skills = set(re.findall(r'\b\w+\b', job_requirements.lower()))
            content_skills = set(re.findall(r'\b\w+\b', content.lower()))
            
            # Find important skills from job that are missing
            important_missing = job_skills - content_skills
            if important_missing:
                suggestions.append(f"Consider adding these relevant skills if you have them: {', '.join(important_missing)}")
        
        elif section == 'education':
            # Check for GPA if mentioned in job
            if 'gpa' in job_requirements.lower() and 'gpa' not in content.lower():
                suggestions.append("Include GPA if it's 3.0 or higher")
                
            # Check for relevant coursework
            if 'coursework' not in content.lower():
                suggestions.append("List relevant coursework that aligns with job requirements")
        
        elif section == 'summary':
            # Check for years of experience
            if not re.search(r'\d+ years?', content):
                suggestions.append("Mention your years of experience in the summary")
                
            # Check for alignment with job requirements
            job_keywords = Counter(re.findall(r'\b\w+\b', job_requirements.lower()))
            most_common_job_reqs = {word for word, count in job_keywords.most_common(5)}
            summary_words = set(re.findall(r'\b\w+\b', content.lower()))
            
            missing_key_terms = most_common_job_reqs - summary_words
            if missing_key_terms:
                suggestions.append(f"Align summary with job requirements by mentioning: {', '.join(missing_key_terms)}")
        
        return suggestions
    
    def generate_suggestions(self, resume_text: str, job_description: str) -> Dict[str, List[str]]:
        """
        Generate improvement suggestions for all resume sections.
        
        Args:
            resume_text: The full text of the resume
            job_description: The job description text
            
        Returns:
            Dictionary mapping section names to lists of suggestions
        """
        sections = self.identify_sections(resume_text)
        suggestions = {}
        
        for section, content in sections.items():
            section_suggestions = self.analyze_section(section, content, job_description)
            if section_suggestions:
                suggestions[section] = section_suggestions
                
        # Check for missing sections
        for section in self.section_patterns:
            if section not in sections:
                suggestions[section] = [f"Add a {section.title()} section to your resume"]
        
        return suggestions