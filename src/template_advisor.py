"""Resume template and formatting recommendations."""
from typing import Dict, List, Any

# ATS-friendly templates and best practices
TEMPLATE_RECOMMENDATIONS = {
    'modern_professional': {
        'name': 'Modern Professional',
        'description': 'Clean, ATS-friendly format with clear sections',
        'features': [
            'Single column layout for better ATS parsing',
            'Clear section headers (Experience, Education, Skills)',
            'Standard fonts (Arial, Calibri, Times New Roman)',
            'Bullet points for achievements',
            '0.5-1 inch margins',
            'No tables, text boxes, or graphics that confuse ATS'
        ],
        'recommended_for': ['Technical roles', 'Corporate positions', 'Entry to mid-level'],
        'ats_score': 95
    },
    'executive': {
        'name': 'Executive',
        'description': 'Leadership-focused format highlighting strategic achievements',
        'features': [
            'Executive summary at the top',
            'Emphasis on leadership and business impact',
            'Quantified achievements with metrics',
            'Board positions and speaking engagements',
            'Professional affiliations',
            'Two-page format acceptable'
        ],
        'recommended_for': ['C-suite', 'Senior management', '15+ years experience'],
        'ats_score': 90
    },
    'technical': {
        'name': 'Technical/Developer',
        'description': 'Skills-first format for technical professionals',
        'features': [
            'Technical skills section prominently placed',
            'Project highlights with technologies used',
            'GitHub/Portfolio links',
            'Certifications and technical training',
            'Clear technology stack for each role',
            'Keywords aligned with job descriptions'
        ],
        'recommended_for': ['Software engineers', 'IT professionals', 'Data scientists'],
        'ats_score': 92
    },
    'creative': {
        'name': 'Creative Professional',
        'description': 'Portfolio-focused with personality (use carefully)',
        'features': [
            'Portfolio link prominently displayed',
            'Skills and tools section',
            'Project-based experience format',
            'Minimal color accents (if any)',
            'Still ATS-compatible formatting',
            'Links to work samples'
        ],
        'recommended_for': ['Designers', 'Writers', 'Marketing professionals'],
        'ats_score': 85
    }
}

def analyze_resume_format(resume_text: str, contact_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze resume format and provide improvement suggestions.
    
    Args:
        resume_text: Full text of the resume
        contact_info: Extracted contact information
    
    Returns:
        Dictionary with formatting recommendations
    """
    issues = []
    suggestions = []
    score = 100
    
    # Check for contact information
    if not contact_info.get('email'):
        issues.append('Missing email address')
        suggestions.append('Add a professional email address at the top')
        score -= 10
    
    if not contact_info.get('phone'):
        issues.append('Missing phone number')
        suggestions.append('Include a phone number for easy contact')
        score -= 5
    
    # Check resume length (rough estimate)
    word_count = len(resume_text.split())
    if word_count < 200:
        issues.append('Resume appears too short')
        suggestions.append('Expand on your experience and achievements (aim for 400-800 words)')
        score -= 15
    elif word_count > 1500:
        issues.append('Resume may be too long')
        suggestions.append('Condense to 1-2 pages (800-1200 words) for better readability')
        score -= 10
    
    # Check for action verbs (already done in verb enhancement)
    # Check for quantifiable achievements
    has_numbers = any(char.isdigit() for char in resume_text)
    if not has_numbers:
        issues.append('No quantifiable achievements found')
        suggestions.append('Add metrics and numbers (e.g., "Increased sales by 25%", "Managed team of 10")')
        score -= 15
    
    # Check for common ATS-unfriendly elements (basic text analysis)
    if '|' in resume_text or '┃' in resume_text:
        issues.append('May contain tables or columns that confuse ATS')
        suggestions.append('Use simple bullet points instead of tables or multi-column layouts')
        score -= 10
    
    # Check for appropriate section headers
    common_sections = ['experience', 'education', 'skills']
    lower_text = resume_text.lower()
    missing_sections = [s for s in common_sections if s not in lower_text]
    
    if missing_sections:
        issues.append(f'Missing common sections: {", ".join(missing_sections)}')
        suggestions.append(f'Add sections for: {", ".join(missing_sections).title()}')
        score -= 10
    
    # Positive feedback
    strengths = []
    if contact_info.get('email') and contact_info.get('phone'):
        strengths.append('Contact information is complete')
    
    if 400 <= word_count <= 1200:
        strengths.append('Resume length is appropriate')
    
    if has_numbers:
        strengths.append('Includes quantifiable achievements')
    
    return {
        'format_score': max(0, score),
        'issues': issues,
        'suggestions': suggestions,
        'strengths': strengths,
        'word_count': word_count
    }

def get_template_recommendation(
    similarity_score: float,
    resume_skills: List[str],
    job_description: str = ""
) -> Dict[str, Any]:
    """
    Recommend best resume template based on analysis.
    
    Args:
        similarity_score: Match score with job description
        resume_skills: List of skills from resume
        job_description: Job description text
    
    Returns:
        Recommended template with explanation
    """
    job_lower = job_description.lower()
    
    # Detect job type
    is_technical = any(keyword in job_lower for keyword in [
        'engineer', 'developer', 'programmer', 'software', 'data scientist', 'devops'
    ])
    
    is_executive = any(keyword in job_lower for keyword in [
        'chief', 'director', 'vp', 'vice president', 'head of', 'executive'
    ])
    
    is_creative = any(keyword in job_lower for keyword in [
        'designer', 'creative', 'writer', 'artist', 'marketing', 'brand'
    ])
    
    # Recommend template
    if is_executive:
        template_key = 'executive'
    elif is_technical:
        template_key = 'technical'
    elif is_creative:
        template_key = 'creative'
    else:
        template_key = 'modern_professional'
    
    template = TEMPLATE_RECOMMENDATIONS[template_key].copy()
    
    # Add personalized advice
    if similarity_score < 60:
        template['priority_advice'] = [
            'Restructure resume to emphasize skills matching the job description',
            'Use keywords from the job posting throughout your resume',
            'Quantify achievements relevant to this role'
        ]
    elif similarity_score < 80:
        template['priority_advice'] = [
            'Good match! Fine-tune keywords to improve ATS compatibility',
            'Add more specific examples of relevant experience'
        ]
    else:
        template['priority_advice'] = [
            'Excellent match! Maintain current keyword usage',
            'Ensure formatting is ATS-friendly for submission'
        ]
    
    return {
        'recommended_template': template,
        'alternative_templates': [
            TEMPLATE_RECOMMENDATIONS[k] for k in TEMPLATE_RECOMMENDATIONS.keys()
            if k != template_key
        ][:2]  # Show 2 alternatives
    }

def get_ats_tips() -> List[str]:
    """Get general ATS-friendly formatting tips."""
    return [
        'Use standard section headers: Summary, Experience, Education, Skills',
        'Avoid headers, footers, tables, and text boxes',
        'Use standard fonts: Arial, Calibri, Times New Roman (10-12pt)',
        'Save as .docx or .pdf (check job posting requirements)',
        'Use standard bullet points (•, -, or *)',
        'Spell out acronyms at least once',
        'Include keywords from job description naturally',
        'Use reverse chronological order for experience',
        'Avoid images, logos, and graphics',
        'Keep margins between 0.5-1 inch',
        'Use simple formatting (bold for headers, regular for text)',
        'Test your resume with an ATS checker before submitting'
    ]
