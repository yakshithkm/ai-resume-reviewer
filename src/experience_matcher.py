"""
Module for detecting and matching experience levels between resumes and job requirements.
"""
from typing import Dict, Tuple, Optional, List
import re
import spacy

class ExperienceMatcher:
    """Analyze and match experience requirements between resumes and jobs."""
    
    def __init__(self):
        """Initialize the experience matcher with NLP model."""
        self.nlp = spacy.load('en_core_web_sm')
        
        # Common patterns for experience requirements
        self.year_patterns = [
            r'(\d+)[\+]?\s*(?:years?|yrs?).+?experience',
            r'experience.+?(\d+)[\+]?\s*(?:years?|yrs?)',
            r'(\d+)[\+]?\s*(?:years?|yrs?).+?background',
            r'minimum.+?(\d+)[\+]?\s*(?:years?|yrs?)',
            r'at least.+?(\d+)[\+]?\s*(?:years?|yrs?)',
            r'(\d+)[\+]?\s*(?:years?|yrs?).+?minimum'
        ]
        
        # Experience level classifications
        self.level_terms = {
            'entry': [
                'entry level', 'junior', 'fresh graduate', 'recent graduate',
                'no experience required', '0-2 years', 'starting position'
            ],
            'mid': [
                'mid level', 'intermediate', 'associate', '2-5 years',
                '3-5 years', 'experienced'
            ],
            'senior': [
                'senior', 'lead', 'principal', 'architect', '5+ years',
                '7+ years', '10+ years', 'expert'
            ]
        }
        
        # Role hierarchy for experience relevance
        self.role_hierarchy = {
            'intern': 0,
            'trainee': 0,
            'junior': 1,
            'associate': 2,
            'developer': 2,
            'engineer': 2,
            'analyst': 2,
            'consultant': 2,
            'senior': 3,
            'lead': 4,
            'manager': 4,
            'architect': 4,
            'principal': 5,
            'director': 5,
            'head': 5,
            'chief': 6,
            'vp': 6,
            'president': 6
        }
    
    def extract_years_of_experience(self, text: str) -> Optional[int]:
        """
        Extract the number of years of experience from text.
        
        Args:
            text: Text to analyze for experience requirements
            
        Returns:
            Number of years if found, None otherwise
        """
        # Try all patterns
        for pattern in self.year_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                try:
                    years = int(match.group(1))
                    return years
                except (ValueError, IndexError):
                    continue
        return None
    
    def detect_experience_level(self, text: str) -> Tuple[str, float]:
        """
        Determine the experience level from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (level, confidence)
            Level is one of: entry, mid, senior
            Confidence is between 0 and 1
        """
        text_lower = text.lower()
        matches = {
            level: sum(1 for term in terms if term in text_lower)
            for level, terms in self.level_terms.items()
        }
        
        if not any(matches.values()):
            # Default to mid-level with low confidence if no matches
            return ('mid', 0.3)
            
        # Get level with most matches
        max_matches = max(matches.values())
        best_level = max(matches.items(), key=lambda x: x[1])[0]
        
        # Calculate confidence based on number of matches
        confidence = min(1.0, max_matches / 3)  # Cap at 1.0
        
        return (best_level, confidence)
    
    def extract_role_progression(self, text: str) -> List[Dict[str, str]]:
        """
        Extract career progression from work experience.
        
        Args:
            text: Resume text to analyze
            
        Returns:
            List of roles with titles and levels
        """
        doc = self.nlp(text)
        roles = []
        
        # Regular expressions for common job title patterns
        title_patterns = [
            r'(?:senior|lead|principal|junior)?\s*(?:software|systems?)?\s*(?:engineer|developer|architect)',
            r'(?:technical|team|project)?\s*(?:lead|manager|director)',
            r'(?:full\s*stack|backend|frontend)\s*(?:engineer|developer)',
            r'(?:data|machine learning|devops)\s*(?:engineer|scientist|specialist)'
        ]
        
        # Look for job titles and dates
        for sent in doc.sents:
            sent_text = sent.text.lower()
            
            # Try to find job titles using patterns
            for pattern in title_patterns:
                matches = re.finditer(pattern, sent_text, re.IGNORECASE)
                for match in matches:
                    title = match.group(0)
                    
                    # Determine level based on role hierarchy
                    max_level = 0
                    for role, level in self.role_hierarchy.items():
                        if role in title.lower() and level > max_level:
                            max_level = level
                            
                    # Adjust level based on surrounding context
                    context = sent_text.replace(title.lower(), '')
                    for role, level in self.role_hierarchy.items():
                        if role in context and level > max_level:
                            max_level = level
                            
                    roles.append({
                        'title': title,
                        'level': max_level
                    })
                    break  # Take only first match per pattern
            
            # Also look for direct role hierarchy terms
            if not any(role['title'].lower() in sent_text.lower() for role in roles):
                for role, level in self.role_hierarchy.items():
                    if role in sent_text:
                        # Try to get broader context for the title
                        words = sent_text.split()
                        try:
                            idx = [i for i, w in enumerate(words) if role in w][0]
                            start = max(0, idx - 2)
                            end = min(len(words), idx + 3)
                            title = ' '.join(words[start:end])
                        except IndexError:
                            title = role
                            
                        roles.append({
                            'title': title.strip(),
                            'level': level
                        })
        
        return sorted(roles, key=lambda x: x['level'])
    
    def analyze_experience_match(self, resume_text: str, job_text: str) -> Dict[str, any]:
        """
        Analyze how well resume experience matches job requirements.
        
        Args:
            resume_text: The resume text
            job_text: The job description text
            
        Returns:
            Dictionary containing match analysis
        """
        # Extract years of experience
        job_years = self.extract_years_of_experience(job_text)
        resume_years = self.extract_years_of_experience(resume_text)
        
        # Detect experience levels
        job_level, job_confidence = self.detect_experience_level(job_text)
        resume_level, resume_confidence = self.detect_experience_level(resume_text)
        
        # Extract role progression
        roles = self.extract_role_progression(resume_text)
        current_level = roles[-1]['level'] if roles else 1
        
        # Calculate match scores
        years_match = 1.0
        if job_years and resume_years:
            years_match = min(1.0, resume_years / job_years)
        
        level_match = 1.0
        level_values = {'entry': 1, 'mid': 2, 'senior': 3}
        if job_level in level_values and resume_level in level_values:
            level_diff = abs(level_values[job_level] - level_values[resume_level])
            level_match = max(0.0, 1.0 - (level_diff * 0.3))
        
        # Generate feedback
        feedback = []
        if job_years and (not resume_years or resume_years < job_years):
            feedback.append(f"Job requires {job_years}+ years of experience")
            
        if job_level != resume_level and job_confidence > 0.5:
            feedback.append(f"Job requires {job_level}-level experience")
            
        if roles:
            max_role = roles[-1]['title']
            feedback.append(f"Most senior role: {max_role}")
        
        return {
            'match': {
                'years': years_match,
                'level': level_match,
                'overall': (years_match + level_match) / 2
            },
            'details': {
                'job_requirements': {
                    'years': job_years,
                    'level': job_level,
                    'confidence': job_confidence
                },
                'resume_experience': {
                    'years': resume_years,
                    'level': resume_level,
                    'confidence': resume_confidence,
                    'roles': roles
                }
            },
            'feedback': feedback
        }