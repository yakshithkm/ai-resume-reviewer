"""
Module for industry-specific keyword analysis and matching.
"""
from typing import Dict, List, Set, Tuple
import re
from collections import defaultdict
import spacy

class IndustryKeywordAnalyzer:
    """Analyze industry-specific keywords in resumes and job descriptions."""
    
    def __init__(self):
        """Initialize the analyzer with industry knowledge bases."""
        self.nlp = spacy.load('en_core_web_sm')
        
        # Define industry sectors and their common terms
        self.industry_terms = {
            'software': {
                'languages': {
                    'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'Go',
                    'Scala', 'PHP', 'Swift', 'Kotlin', 'TypeScript', 'SQL'
                },
                'frameworks': {
                    'React', 'Angular', 'Vue', 'Django', 'Flask', 'Spring',
                    'Node.js', 'Express', 'ASP.NET', 'Rails', 'Laravel'
                },
                'tools': {
                    'Git', 'Docker', 'Kubernetes', 'Jenkins', 'JIRA', 'AWS',
                    'Azure', 'GCP', 'Linux', 'REST', 'GraphQL', 'CI/CD'
                },
                'concepts': {
                    'Agile', 'Scrum', 'TDD', 'DevOps', 'Microservices',
                    'Cloud Computing', 'Distributed Systems', 'API Design'
                }
            },
            'data_science': {
                'skills': {
                    'Machine Learning', 'Deep Learning', 'NLP', 'Neural Networks',
                    'Statistical Analysis', 'Data Mining', 'Big Data'
                },
                'tools': {
                    'TensorFlow', 'PyTorch', 'scikit-learn', 'Pandas', 'NumPy',
                    'R', 'Hadoop', 'Spark', 'Tableau', 'Power BI'
                },
                'techniques': {
                    'Regression', 'Classification', 'Clustering', 'Time Series',
                    'Feature Engineering', 'A/B Testing', 'Cross Validation'
                }
            },
            'cloud': {
                'platforms': {
                    'AWS', 'Azure', 'GCP', 'OpenStack', 'VMware',
                    'Oracle Cloud', 'IBM Cloud'
                },
                'services': {
                    'EC2', 'S3', 'Lambda', 'ECS', 'EKS', 'RDS', 'DynamoDB',
                    'Azure Functions', 'Cosmos DB', 'App Engine'
                },
                'concepts': {
                    'IaaS', 'PaaS', 'SaaS', 'Serverless', 'Containers',
                    'Microservices', 'Auto Scaling', 'Load Balancing'
                }
            },
            'cybersecurity': {
                'domains': {
                    'Network Security', 'Application Security', 'Cloud Security',
                    'Identity Management', 'Incident Response', 'Forensics'
                },
                'tools': {
                    'Wireshark', 'Nmap', 'Metasploit', 'Burp Suite',
                    'SIEM', 'IDS/IPS', 'Firewall', 'Antivirus'
                },
                'concepts': {
                    'Encryption', 'Authentication', 'Authorization', 'Zero Trust',
                    'Vulnerability Assessment', 'Penetration Testing'
                }
            }
        }
        
        # Common industry buzzwords and their weights
        self.industry_buzzwords = {
            'innovative': 0.5,
            'cutting-edge': 0.5,
            'scalable': 0.7,
            'robust': 0.6,
            'enterprise': 0.8,
            'mission-critical': 0.7,
            'state-of-the-art': 0.5,
            'next-generation': 0.4,
            'world-class': 0.4,
            'bleeding-edge': 0.3
        }
    
    def detect_industry(self, text: str) -> List[Tuple[str, float]]:
        """
        Detect the most likely industry sectors based on keyword matches.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of (industry, confidence) tuples, sorted by confidence
        """
        text_lower = text.lower()
        industry_scores = defaultdict(float)
        
        # Calculate scores for each industry
        for industry, categories in self.industry_terms.items():
            total_terms = 0
            matched_terms = 0
            
            for category_terms in categories.values():
                for term in category_terms:
                    total_terms += 1
                    if term.lower() in text_lower:
                        matched_terms += 1
            
            if total_terms > 0:
                industry_scores[industry] = matched_terms / total_terms
        
        # Convert to list and sort by confidence
        scored_industries = [
            (industry, score) 
            for industry, score in industry_scores.items()
            if score > 0.1  # Minimum threshold
        ]
        
        return sorted(scored_industries, key=lambda x: x[1], reverse=True)
    
    def extract_industry_keywords(self, text: str, industries: List[str] = None) -> Dict[str, List[str]]:
        """
        Extract industry-specific keywords from text.
        
        Args:
            text: Text to analyze
            industries: Optional list of industries to focus on
            
        Returns:
            Dictionary mapping categories to found keywords
        """
        text_lower = text.lower()
        found_terms = defaultdict(list)
        
        # If no industries specified, analyze all
        if not industries:
            industries = list(self.industry_terms.keys())
        
        # Look for terms from specified industries
        for industry in industries:
            if industry in self.industry_terms:
                for category, terms in self.industry_terms[industry].items():
                    for term in terms:
                        if term.lower() in text_lower:
                            found_terms[f"{industry}_{category}"].append(term)
        
        return dict(found_terms)
    
    def analyze_keyword_match(self, resume_text: str, job_text: str) -> Dict[str, any]:
        """
        Analyze how well industry keywords in resume match job requirements.
        
        Args:
            resume_text: The resume text
            job_text: The job description text
            
        Returns:
            Dictionary containing match analysis
        """
        # Detect relevant industries
        job_industries = [ind for ind, conf in self.detect_industry(job_text)]
        
        # Extract keywords from both texts
        job_keywords = self.extract_industry_keywords(job_text, job_industries)
        resume_keywords = self.extract_industry_keywords(resume_text, job_industries)
        
        # Calculate matches and gaps
        matches = defaultdict(list)
        gaps = defaultdict(list)
        extras = defaultdict(list)
        
        for category in job_keywords:
            if category in resume_keywords:
                # Find matching terms
                job_terms = set(job_keywords[category])
                resume_terms = set(resume_keywords[category])
                
                matches[category] = list(job_terms & resume_terms)
                gaps[category] = list(job_terms - resume_terms)
                extras[category] = list(resume_terms - job_terms)
        
        # Calculate match scores
        category_scores = {}
        overall_score = 0.0
        total_categories = 0
        
        for category in job_keywords:
            if category in matches:
                total_terms = len(set(job_keywords[category]))
                if total_terms > 0:
                    score = len(matches[category]) / total_terms
                    category_scores[category] = score
                    overall_score += score
                    total_categories += 1
        
        if total_categories > 0:
            overall_score /= total_categories
        
        # Check for buzzword usage
        buzzwords = []
        for word, weight in self.industry_buzzwords.items():
            if word in job_text.lower():
                buzzwords.append({
                    'term': word,
                    'weight': weight,
                    'in_resume': word in resume_text.lower()
                })
        
        return {
            'industries': job_industries,
            'matches': {
                'matching_keywords': dict(matches),
                'missing_keywords': dict(gaps),
                'additional_keywords': dict(extras)
            },
            'scores': {
                'category_scores': category_scores,
                'overall_match': overall_score
            },
            'buzzwords': buzzwords
        }
    
    def suggest_keyword_improvements(self, analysis: Dict[str, any]) -> List[str]:
        """
        Generate suggestions for improving keyword matches.
        
        Args:
            analysis: Output from analyze_keyword_match
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        # Suggest adding missing keywords by category
        for category, terms in analysis['matches']['missing_keywords'].items():
            if terms:
                industry = category.split('_')[0]
                category_name = category.split('_')[1]
                if len(terms) > 3:
                    # If many terms are missing, suggest top 3 most important ones
                    terms_list = ', '.join(list(terms)[:3]) + ", and others"
                else:
                    terms_list = ', '.join(terms)
                suggestions.append(
                    f"Consider adding these {industry} {category_name} keywords " +
                    f"if you have experience with them: {terms_list}"
                )
        
        # Group and suggest buzzwords by importance
        important_buzzwords = []
        nice_to_have_buzzwords = []
        for b in analysis['buzzwords']:
            if not b['in_resume']:
                if b['weight'] >= 0.7:
                    important_buzzwords.append(b['term'])
                elif b['weight'] >= 0.5:
                    nice_to_have_buzzwords.append(b['term'])
        
        if important_buzzwords:
            suggestions.append(
                "Important: Your resume would be stronger with these key industry terms: " +
                ', '.join(important_buzzwords)
            )
        if nice_to_have_buzzwords:
            suggestions.append(
                "Optional: Consider these additional industry terms where relevant: " +
                ', '.join(nice_to_have_buzzwords)
            )
        
        # Suggest based on category scores
        low_scoring_categories = [
            cat for cat, score in analysis['scores']['category_scores'].items()
            if score < 0.5
        ]
        if low_scoring_categories:
            for category in low_scoring_categories:
                industry = category.split('_')[0]
                category_name = category.split('_')[1]
                suggestions.append(
                    f"Your {industry} {category_name} keyword match needs improvement. " +
                    f"Try to highlight more relevant experience in this area."
                )
        
        # Special suggestion for very low overall match
        if analysis['scores']['overall_match'] < 0.3:
            suggestions.append(
                "Warning: Your resume's keyword match with this job is quite low. " +
                "Consider tailoring it more specifically to the role's requirements."
            )
        
        return suggestions