"""
Module for extracting and processing bullet points from resume text.
Provides utilities for identifying and formatting bullet points consistently.
"""
import re
from typing import List, Tuple

class BulletPointExtractor:
    """Extract and process bullet points from resume text."""
    
    # Common bullet point markers and their variations
    BULLET_PATTERNS = [
        # Unicode bullets
        r'[•·‣⁃◦○●◆▪▫▶►→⚫⚬]\s+',  # Various bullet symbols
        # ASCII bullets
        r'[-\*\+]\s+',              # Hyphen, asterisk, plus
        # Numbered lists
        r'[\d]{1,2}[\.\)]\s+',      # 1. or 1) style
        r'[\d]{1,2}[\.\)]-\s+',     # 1.- or 1)- style
        r'[\w][\.\)]\s+',           # a. or a) style
        r'[\w][\.\)]-\s+',          # a.- or a)- style
        # Indented variations
        r'^\s+[-\*\+•·]\s+',        # Indented bullets
        r'^\s+[\d]{1,2}\.\s+',      # Indented numbers
        # Special cases
        r'→\s+',                    # Arrow
        r'✓\s+',                    # Checkmark
        r'☐\s+',                    # Checkbox
    ]
    
    # Compiled regex pattern for all bullet variations
    BULLET_REGEX = re.compile('|'.join(BULLET_PATTERNS), re.MULTILINE)
    
    # Pattern to identify the start of bullet points
    BULLET_START_PATTERNS = [
        r'achievements?:?\s*$',
        r'responsibilities?:?\s*$',
        r'duties?:?\s*$',
        r'accomplishments?:?\s*$',
        r'tasks?:?\s*$',
        r'projects?:?\s*$',
        r'highlights?:?\s*$',
    ]
    
    # Compiled regex for bullet point starters
    BULLET_START_REGEX = re.compile('|'.join(BULLET_START_PATTERNS), re.IGNORECASE)
    
    @classmethod
    def extract_bullet_points(cls, text: str) -> List[str]:
        """
        Extract bullet points from text, handling various bullet point formats.
        
        Args:
            text: Input text containing bullet points
            
        Returns:
            List of extracted bullet points with consistent formatting
        """
        lines = text.split('\n')
        bullet_points: List[str] = []
        current_bullet = None
        in_list = False  # Track if we're inside a bullet list section

        # simple patterns
        numbered_re = re.compile(r'^\s*[\d]+[\.\)]\s+')
        letter_re = re.compile(r'^\s*[a-zA-Z]\)\s+')
        bullet_char_re = re.compile(r'^\s*[\u2022\u00B7\-\*\u25CB\u25AA\u25E6\u2192]\s+')

        for i, raw in enumerate(lines):
            if raw is None:
                continue
            line = raw.rstrip('\r').rstrip('\n')
            stripped = line.strip()
            if not stripped:
                continue

            # Preserve nested headings (e.g., "Programming Languages:") when
            # they appear either inside a bullet list or are immediately
            # followed by bullet markers. This allows headings that precede
            # a list to be included as their own bullet item.
            if stripped.endswith(':'):
                # Lookahead to see if next non-empty line is a bullet marker
                next_is_bullet = False
                for j in range(i + 1, len(lines)):
                    nl = lines[j].strip()
                    if not nl:
                        continue
                    if bullet_char_re.match(nl) or numbered_re.match(nl) or letter_re.match(nl):
                        next_is_bullet = True
                    break

                # Skip top-level headers (they are section markers, not list headings)
                top_level_headers = {
                    'experience', 'education', 'skills', 'summary', 'contact',
                    'work', 'work experience', 'key achievements', 'project highlights',
                    'achievements', 'projects'
                }
                low = stripped.lower().rstrip(':').strip()
                if low in top_level_headers:
                    continue

                if in_list or next_is_bullet:
                    # finalize any current bullet
                    if current_bullet:
                        bullet_points.append(current_bullet.strip())
                        current_bullet = None
                    # include the nested heading as its own bullet-like item
                    bullet_points.append(stripped)
                    continue

            # Check for bullet markers
            bullet_marker = bullet_char_re.match(line) or numbered_re.match(line) or letter_re.match(line)
            if bullet_marker:
                in_list = True  # Found first bullet in a list
                if current_bullet:
                    bullet_points.append(current_bullet.strip())
                current_bullet = line[bullet_marker.end():].strip()
                continue

            # Handle nested bullet list indentation and continuation
            leading_ws = len(line) - len(line.lstrip(' '))
            if current_bullet and (leading_ws > 0 or stripped[0].islower() if stripped else False):
                current_bullet += ' ' + stripped
                continue

            # Handle non-bullet content
            if current_bullet:
                bullet_points.append(current_bullet.strip())
                current_bullet = None

        # Add final bullet point if needed
        if current_bullet:
            bullet_points.append(current_bullet.strip())

        return cls._clean_bullet_points(bullet_points)
    
    @classmethod
    def _clean_bullet_points(cls, bullet_points: List[str]) -> List[str]:
        """
        Clean and normalize extracted bullet points.
        
        Args:
            bullet_points: List of extracted bullet points
            
        Returns:
            List of cleaned and normalized bullet points
        """
        cleaned = []
        for point in bullet_points:
            # Remove only bullet markers while preserving special characters
            point = re.sub(r'^[\u2022\u00B7\-\*\u25CB\u25AA\u25E6\u2192]\s+', '', point)
            point = re.sub(r'^\s*[\d]+[\.\)]\s+', '', point)  # Remove numbered bullets
            point = re.sub(r'^\s*[a-zA-Z]\)\s+', '', point)   # Remove letter bullets
            
            # Clean up whitespace
            point = ' '.join(point.split())
            
            # Skip empty points or just punctuation
            if not point or point in [':', '.']:
                continue

            # If this is a heading (ends with ':'), keep it as-is
            if point.endswith(':'):
                cleaned.append(point)
                continue

            # Format bullet points (non-heading lines)
            if len(point) > 0:
                # Capitalize first letter
                point = point[0].upper() + point[1:]
                # Add period if missing
                if not point.endswith(('.', '!', '?', ':')):
                    point += '.'
            
            if point:
                cleaned.append(point)
        
        return cleaned
    
    @classmethod
    def format_bullet_points(cls, bullet_points: List[str]) -> List[str]:
        """
        Format bullet points consistently with bullet character.
        
        Args:
            bullet_points: List of bullet points to format
            
        Returns:
            List of formatted bullet points
        """
        return [f"• {point}" for point in bullet_points]