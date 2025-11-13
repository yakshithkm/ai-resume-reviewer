"""
Module for scoring resume-job matching using TF-IDF and cosine similarity.
"""
from typing import Dict, List, Tuple
from collections import Counter
import math
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

class ResumeScorer:
    """Score resumes against job descriptions using NLP techniques."""
    
    def __init__(self):
        """Initialize the resume scorer."""
        self.vectorizer = CountVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2)  # Include both unigrams and bigrams
        )
        self.resume_vector = None
        self.job_vector = None
        self.feature_names = None
    
    def compute_similarity(self, resume_text: str, job_text: str) -> float:
        """
        Compute similarity score between resume and job description.
        
        Args:
            resume_text: Full text of the resume
            job_text: Full text of the job description
            
        Returns:
            Similarity score between 0 and 1
        """
        # Create count matrix for both texts
        texts = [resume_text, job_text]
        try:
            count_matrix = self.vectorizer.fit_transform(texts)
            self.feature_names = self.vectorizer.get_feature_names_out()
        except ValueError:
            # Empty vocabulary (e.g., documents only contain stop words)
            # Set empty vectors and feature names so downstream callers
            # can handle missing features gracefully.
            self.feature_names = []
            self.resume_vector = []
            self.job_vector = []
            return 0.0
        
        # Store vectors for feature importance analysis and convert to arrays
        self.resume_vector = count_matrix[0].toarray()[0]
        self.job_vector = count_matrix[1].toarray()[0]
        
        # Calculate cosine similarity manually
        dot_product = np.dot(self.resume_vector, self.job_vector)
        resume_norm = np.linalg.norm(self.resume_vector)
        job_norm = np.linalg.norm(self.job_vector)
        
        # Avoid division by zero
        if resume_norm == 0 or job_norm == 0:
            return 0.0
            
        similarity = dot_product / (resume_norm * job_norm)
        
        return float(similarity)
    
    def get_important_terms(self, n_terms: int = 10) -> Dict[str, List[str]]:
        """
        Get most important terms from both resume and job description.
        
        Args:
            n_terms: Number of terms to return for each document
            
        Returns:
            Dictionary with important terms from resume and job
        """
        if self.resume_vector is None or self.job_vector is None:
            raise ValueError("Must compute similarity first")

        # If feature names are empty (e.g. vectorizer had empty vocabulary),
        # return empty term lists rather than raising or indexing errors.
        if getattr(self, 'feature_names', None) is None or len(self.feature_names) == 0:
            return {'resume_terms': [], 'job_terms': []}
        
        # Get top terms from resume
        resume_idx = np.argsort(self.resume_vector)[::-1]
        resume_terms = [self.feature_names[i] for i in resume_idx[:n_terms]]
        
        # Get top terms from job description
        job_idx = np.argsort(self.job_vector)[::-1]
        job_terms = [self.feature_names[i] for i in job_idx[:n_terms]]
        
        return {
            'resume_terms': resume_terms,
            'job_terms': job_terms
        }
    
    def get_skills_gap_analysis(self, resume_text: str, job_text: str) -> Dict[str, Dict[str, List[str]]]:
        """
        Perform detailed skills gap analysis between resume and job requirements.
        
        Args:
            resume_text: The full text of the resume
            job_text: The full text of the job description
            
        Returns:
            Dictionary containing:
            - critical_missing: List of critical skills missing from resume
            - nice_to_have_missing: List of nice-to-have skills missing
            - matched_skills: List of skills present in both
            - additional_skills: Skills in resume but not in job requirements
        """
        # Handle empty inputs
        empty_result = {
            'gaps': {'critical_missing': [], 'nice_to_have_missing': []},
            'matches': {'matched_skills': [], 'additional_skills': []}
        }
        if not resume_text.strip() or not job_text.strip():
            return empty_result
            
        # Extract skills using vectorizer
        if not hasattr(self, 'feature_names') or self.feature_names is None:
            try:
                self.compute_similarity(resume_text, job_text)
            except ValueError:
                return empty_result
            
        # Get skill frequencies
        resume_skills = {
            self.feature_names[i]: self.resume_vector[i]
            for i in range(len(self.feature_names))
            if self.resume_vector[i] > 0
        }
        
        job_skills = {
            self.feature_names[i]: self.job_vector[i]
            for i in range(len(self.feature_names))
            if self.job_vector[i] > 0
        }
        
        # Identify critical vs nice-to-have skills based on frequency and keywords
        critical_indicators = {'required', 'must', 'essential', 'necessary'}
        nice_to_have_indicators = {'preferred', 'nice', 'plus', 'helpful', 'desirable'}
        
        critical_skills = []
        nice_to_have_skills = []
        
        for skill, freq in job_skills.items():
            # Check surrounding context in job text to determine importance
            skill_idx = job_text.lower().find(skill.lower())
            if skill_idx >= 0:
                context = job_text[max(0, skill_idx-50):min(len(job_text), skill_idx+50)].lower()
                if any(ind in context for ind in critical_indicators):
                    critical_skills.append(skill)
                elif any(ind in context for ind in nice_to_have_indicators):
                    nice_to_have_skills.append(skill)
                else:
                    # If no explicit indicator, use frequency as a proxy
                    if freq > np.mean(list(job_skills.values())):
                        critical_skills.append(skill)
                    else:
                        nice_to_have_skills.append(skill)
        
        # Find gaps
        critical_missing = [
            skill for skill in critical_skills
            if skill.lower() not in {s.lower() for s in resume_skills.keys()}
        ]
        
        nice_to_have_missing = [
            skill for skill in nice_to_have_skills
            if skill.lower() not in {s.lower() for s in resume_skills.keys()}
        ]
        
        # Find matched and additional skills
        matched_skills = [
            skill for skill in resume_skills
            if skill.lower() in {s.lower() for s in job_skills.keys()}
        ]
        
        additional_skills = [
            skill for skill in resume_skills
            if skill.lower() not in {s.lower() for s in job_skills.keys()}
        ]
        
        return {
            'gaps': {
                'critical_missing': critical_missing,
                'nice_to_have_missing': nice_to_have_missing
            },
            'matches': {
                'matched_skills': matched_skills,
                'additional_skills': additional_skills
            }
        }
        
    def get_missing_skills(self, resume_skills: List[str], job_skills: List[str]) -> List[str]:
        """
        Identify required skills that are missing from the resume.
        
        Args:
            resume_skills: List of skills found in resume
            job_skills: List of skills required by job
            
        Returns:
            List of missing skills
        """
        resume_skills_lower = {skill.lower() for skill in resume_skills}
        return [
            skill for skill in job_skills
            if skill.lower() not in resume_skills_lower
        ]
    
    def generate_feedback(
        self,
        similarity_score: float,
        resume_skills: List[str],
        job_skills: List[str],
        important_terms: Dict[str, List[str]]
    ) -> Dict[str, any]:
        """
        Generate detailed feedback based on analysis.
        
        Args:
            similarity_score: Computed similarity score
            resume_skills: Skills found in resume
            job_skills: Skills required by job
            important_terms: Important terms from both documents
            
        Returns:
            Dictionary containing structured feedback
        """
        missing_skills = self.get_missing_skills(resume_skills, job_skills)
        
        # Calculate match percentage
        match_percentage = similarity_score * 100
        
        # Generate feedback based on score
        if match_percentage >= 80:
            overall_feedback = "Excellent match! Your resume aligns very well with the job requirements."
        elif match_percentage >= 60:
            overall_feedback = "Good match. Some adjustments could improve your alignment with the role."
        elif match_percentage >= 40:
            overall_feedback = "Moderate match. Consider highlighting more relevant experience and skills."
        else:
            overall_feedback = "Low match. Your resume might need significant updates to target this role."
        
        # Generate specific suggestions
        suggestions = []
        
        if missing_skills:
            suggestions.append(
                f"Add missing skills: {', '.join(missing_skills)}"
            )
        
        if match_percentage < 60:
            suggestions.append(
                "Emphasize these key terms from the job description: " +
                f"{', '.join(important_terms['job_terms'][:5])}"
            )
        
        if match_percentage < 80:
            suggestions.append(
                "Consider elaborating on your experience with: " +
                f"{', '.join(set(job_skills) & set(resume_skills))}"
            )
        
        return {
            'match_percentage': round(match_percentage, 1),
            'overall_feedback': overall_feedback,
            'missing_skills': missing_skills,
            'suggestions': suggestions,
            'key_terms': {
                'resume': important_terms['resume_terms'],
                'job': important_terms['job_terms']
            }
        }