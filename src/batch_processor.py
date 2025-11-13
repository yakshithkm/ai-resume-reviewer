"""Batch processing utilities for analyzing multiple resumes."""
from typing import List, Dict, Any
import os
from resume_parser.parser import ResumeParser
from scorer.scorer import ResumeScorer
from verb_enhancer import ActionVerbEnhancer

def process_resume_batch(
    resume_paths: List[str],
    job_desc_path: str,
    app_logger
) -> List[Dict[str, Any]]:
    """
    Process multiple resumes against a single job description.
    
    Args:
        resume_paths: List of file paths to resume files
        job_desc_path: Path to job description file
        app_logger: Application logger instance
    
    Returns:
        List of analysis results, one per resume
    """
    results = []
    
    # Parse job description once
    job_parser = ResumeParser()
    job_sections = job_parser.parse_resume(job_desc_path)
    required_skills = job_parser.get_skills()
    job_text = job_parser.text
    
    for resume_path in resume_paths:
        try:
            # Parse resume
            parser = ResumeParser()
            resume_sections = parser.parse_resume(resume_path)
            contact_info = parser.get_contact_info()
            resume_skills = parser.get_skills()
            
            # Calculate similarity
            scorer = ResumeScorer()
            similarity = scorer.compute_similarity(
                resume_text=parser.text,
                job_text=job_text
            )
            
            # Get important terms
            important_terms = scorer.get_important_terms(n_terms=10)
            
            # Generate feedback
            feedback = scorer.generate_feedback(
                similarity_score=similarity,
                resume_skills={s: 1 for s in resume_skills},
                job_skills={s: 1 for s in required_skills},
                important_terms=important_terms
            )
            
            # Calculate matching and missing skills
            matching_skills = []
            missing_skills = []
            
            resume_skills_lower = {s.lower() for s in resume_skills}
            for skill in required_skills:
                if skill.lower() in resume_skills_lower:
                    matching_skills.append(skill)
                else:
                    missing_skills.append(skill)
            
            # Build analysis result
            analysis = {
                'filename': os.path.basename(resume_path),
                'similarity': similarity,
                'matching_skills': matching_skills,
                'missing_skills': missing_skills,
                'resume_skills': resume_skills,
                'required_skills': required_skills,
                'contact_info': contact_info,
                'feedback': feedback,
                'important_terms': important_terms
            }
            
            # Try action verb enhancement (non-fatal if fails)
            try:
                enhancer = ActionVerbEnhancer()
                verb_enhancements = enhancer.enhance_bullet_points(parser.text)
                analysis['verb_enhancements'] = verb_enhancements
            except Exception as e:
                app_logger.warning(f"Verb analysis failed for {resume_path}: {str(e)}")
                analysis['verb_enhancements'] = []
                analysis['warnings'] = ["Action verb analysis could not be completed"]
            
            results.append({
                'success': True,
                'analysis': analysis
            })
            
        except Exception as e:
            app_logger.error(f"Failed to process resume {resume_path}: {str(e)}")
            results.append({
                'success': False,
                'filename': os.path.basename(resume_path),
                'error': str(e)
            })
    
    return results

def get_batch_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate summary statistics for batch processing results.
    
    Args:
        results: List of analysis results
    
    Returns:
        Summary statistics
    """
    total = len(results)
    successful = sum(1 for r in results if r.get('success', False))
    failed = total - successful
    
    if successful > 0:
        scores = [r['analysis']['similarity'] for r in results if r.get('success', False)]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)
        
        # Find best candidate
        best_candidate = max(
            (r for r in results if r.get('success', False)),
            key=lambda r: r['analysis']['similarity']
        )
    else:
        avg_score = 0
        max_score = 0
        min_score = 0
        best_candidate = None
    
    return {
        'total_resumes': total,
        'successful': successful,
        'failed': failed,
        'average_score': round(avg_score, 2),
        'max_score': round(max_score, 2),
        'min_score': round(min_score, 2),
        'best_candidate': best_candidate['analysis']['filename'] if best_candidate else None
    }
