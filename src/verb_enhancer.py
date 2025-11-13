"""
Module for suggesting stronger action verbs in resume bullet points.
"""
from typing import Dict, List, Tuple
import re
import spacy

class ActionVerbEnhancer:
    """Suggest stronger action verbs for resume bullet points."""
    
    def __init__(self):
        """Initialize the action verb enhancer with verb databases."""
        self.nlp = spacy.load('en_core_web_sm')
        
        # Define verb categories and their impact levels
        self.action_verbs = {
            'leadership': {
                'strong': {
                    'led', 'spearheaded', 'directed', 'orchestrated', 'championed',
                    'mentored', 'managed', 'guided', 'initiated', 'established'
                },
                'weak': {
                    'helped', 'assisted', 'participated', 'supported', 'worked on',
                    'was responsible for', 'handled', 'dealt with'
                }
            },
            'achievement': {
                'strong': {
                    'achieved', 'delivered', 'exceeded', 'outperformed', 'generated',
                    'increased', 'improved', 'reduced', 'accelerated', 'maximized'
                },
                'weak': {
                    'completed', 'finished', 'did', 'made', 'met goals',
                    'worked toward', 'tried to', 'attempted'
                }
            },
            'technical': {
                'strong': {
                    'engineered', 'architected', 'designed', 'developed', 'implemented',
                    'optimized', 'refactored', 'streamlined', 'integrated', 'automated'
                },
                'weak': {
                    'coded', 'programmed', 'wrote', 'typed', 'entered',
                    'used', 'utilized', 'employed'
                }
            },
            'communication': {
                'strong': {
                    'presented', 'negotiated', 'influenced', 'persuaded', 'mediated',
                    'collaborated', 'partnered', 'facilitated', 'trained', 'educated'
                },
                'weak': {
                    'talked', 'spoke', 'told', 'said', 'attended',
                    'met with', 'participated in', 'was involved in'
                }
            },
            'analytical': {
                'strong': {
                    'analyzed', 'assessed', 'evaluated', 'researched', 'investigated',
                    'identified', 'formulated', 'calculated', 'measured', 'forecasted'
                },
                'weak': {
                    'looked at', 'reviewed', 'thought about', 'considered',
                    'checked', 'watched', 'observed', 'noticed'
                }
            }
        }
        
        # Create mapping of weak to strong verbs
        self.verb_improvements = {}
        for category, verbs in self.action_verbs.items():
            for weak in verbs['weak']:
                # For each weak verb, suggest top 3 strong verbs from same category
                self.verb_improvements[weak] = list(verbs['strong'])[:3]
    
    def identify_bullet_points(self, text: str) -> List[str]:
        """
        Extract bullet points from text.
        
        Args:
            text: Resume text to analyze
            
        Returns:
            List of bullet point text strings
        """
        bullet_points: List[str] = []

        if not text:
            return bullet_points

        # Line-based extraction is simpler and less error-prone than trying
        # multiple overlapping regexes. Detect common bullet markers and
        # normalized numbered/lettered lists.
        # broaden the set of recognized bullet characters (common bullets and a few rarer variants)
        bullet_re = re.compile(r'^\s*[\u2022\u2023\u2043\u00B7\u2E21\-\*\u25CB\u25AA\u25E6\u2192]\s+(.*)$')
        numbered_re = re.compile(r'^\s*(\d+)[\.)]\s+(.*)$')
        letter_re = re.compile(r'^\s*([a-zA-Z])\)\s+(.*)$')

        seen = set()
        for raw_line in text.splitlines():
            line = raw_line.rstrip()
            if not line.strip():
                continue

            m = bullet_re.match(line)
            if m:
                candidate = m.group(1).strip()
            else:
                m = numbered_re.match(line)
                if m:
                    candidate = m.group(2).strip()
                else:
                    m = letter_re.match(line)
                    if m:
                        candidate = m.group(2).strip()
                    else:
                        # fallback: if the line looks like a bullet because it
                        # starts with a dash/asterisk or contains a leading bullet char
                        stripped = line.strip()
                        if stripped.startswith(('-', '*')):
                            candidate = stripped.lstrip('-*').strip()
                        else:
                            # last-resort: match any non-alphanumeric single char bullet
                            m2 = re.match(r'^\s*([^A-Za-z0-9\s])\s+(.*)$', line)
                            if m2:
                                candidate = m2.group(2).strip()
                            else:
                                # not a bullet-like line
                                continue

            if candidate and candidate not in seen:
                bullet_points.append(candidate)
                seen.add(candidate)

        return bullet_points
    
    def extract_leading_verb(self, text: str) -> Tuple[str, int, int]:
        """
        Extract the leading verb from a bullet point.
        
        Args:
            text: Bullet point text
            
        Returns:
            Tuple of (verb, start_index, end_index) or (None, -1, -1) if no verb found
        """
        doc = self.nlp(text)
        
        # Look for multi-word weak verbs first
        for weak_verb in [v for verbs in self.action_verbs.values() for v in verbs['weak']]:
            if ' ' in weak_verb and weak_verb.lower() in text.lower():
                start = text.lower().index(weak_verb.lower())
                return (text[start:start + len(weak_verb)], start, start + len(weak_verb))
        
        # Then look for the first verb token
        for token in doc:
            if token.pos_ == 'VERB' or (token.pos_ == 'AUX' and token.dep_ == 'ROOT'):
                # Get any auxiliary or particle if present
                verb_phrase = token.text
                next_token = token.i + 1 if token.i + 1 < len(doc) else None
                
                if next_token:
                    if doc[next_token].dep_ in ['prt', 'aux', 'prep'] and len(text) > token.idx + len(verb_phrase):
                        verb_phrase = text[token.idx:doc[next_token].idx + len(doc[next_token].text)]
                
                return (verb_phrase, token.idx, token.idx + len(verb_phrase))
        
        return (None, -1, -1)
    
    def categorize_verb(self, verb: str) -> List[Tuple[str, str]]:
        """
        Categorize a verb and determine its strength.
        
        Args:
            verb: Verb to analyze
            
        Returns:
            List of (category, strength) tuples
        """
        if not verb:
            return []
        
        verb_lower = verb.lower()
        categories = []
        
        for category, verbs in self.action_verbs.items():
            if verb_lower in verbs['strong']:
                categories.append((category, 'strong'))
            elif verb_lower in verbs['weak']:
                categories.append((category, 'weak'))
            # Also check if verb is part of a multi-word phrase
            else:
                for strong_verb in verbs['strong']:
                    if verb_lower in strong_verb or strong_verb in verb_lower:
                        categories.append((category, 'strong'))
                        break
                for weak_verb in verbs['weak']:
                    if verb_lower in weak_verb or weak_verb in verb_lower:
                        categories.append((category, 'weak'))
                        break
        
        return categories
    
    def suggest_stronger_verbs(self, verb: str) -> List[str]:
        """
        Suggest stronger alternatives for a weak verb.
        
        Args:
            verb: Verb to find alternatives for
            
        Returns:
            List of suggested stronger verbs
        """
        verb_lower = verb.lower()
        
        # Direct lookup in improvements dictionary
        if verb_lower in self.verb_improvements:
            return self.verb_improvements[verb_lower]
        
        # Look for partial matches
        suggestions = []
        for weak_verb, improvements in self.verb_improvements.items():
            if verb_lower in weak_verb or weak_verb in verb_lower:
                suggestions.extend(improvements)
        
        return list(set(suggestions))  # Remove duplicates
    
    def enhance_bullet_point(self, bullet: str) -> Dict[str, any]:
        """
        Analyze and enhance a single bullet point.
        
        Args:
            bullet: Text of the bullet point
            
        Returns:
            Dictionary containing analysis and suggestions
        """
        # Extract the leading verb
        verb, start, end = self.extract_leading_verb(bullet)
        if not verb:
            return {
                'original': bullet,
                'has_verb': False,
                'suggestion': 'Start with a strong action verb'
            }
        
        # Analyze the verb
        categories = self.categorize_verb(verb)
        
        # If no categories found, verb might be uncategorized
        if not categories:
            return {
                'original': bullet,
                'has_verb': True,
                'verb': verb,
                'strength': 'unknown',
                'categories': [],
                'suggestions': self.suggest_stronger_verbs(verb)
            }
        
        # Check if any category considers this a weak verb
        is_weak = any(strength == 'weak' for _, strength in categories)
        
        result = {
            'original': bullet,
            'has_verb': True,
            'verb': verb,
            'verb_position': (start, end),
            'categories': [cat for cat, _ in categories],
            'strength': 'weak' if is_weak else 'strong'
        }
        
        # Add suggestions if the verb is weak
        if is_weak:
            suggestions = self.suggest_stronger_verbs(verb)
            if suggestions:
                result['suggestions'] = suggestions
                
                # Create example replacements
                examples = []
                verb_with_space = bullet[start:end + 1]  # Include following space
                for suggestion in suggestions[:2]:  # Limit to top 2 suggestions
                    new_bullet = bullet[:start] + suggestion + bullet[end:]
                    examples.append(new_bullet)
                
                if examples:
                    result['examples'] = examples
        
        return result
    
    def enhance_bullet_points(self, text: str) -> List[Dict[str, any]]:
        """
        Analyze and enhance all bullet points in text.
        
        Args:
            text: Resume text containing bullet points
            
        Returns:
            List of enhancement suggestions for each bullet point
        """
        bullet_points = self.identify_bullet_points(text)
        return [self.enhance_bullet_point(bullet) for bullet in bullet_points]
    
    def summarize_enhancements(self, enhancements: List[Dict[str, any]]) -> Dict[str, any]:
        """
        Generate a summary of enhancement suggestions.
        
        Args:
            enhancements: List of enhancement results
            
        Returns:
            Dictionary with summary statistics and key suggestions
        """
        total_points = len(enhancements)
        if total_points == 0:
            return {
                'status': 'No bullet points found',
                'suggestions': ['Add bullet points to describe your experience']
            }
        
        # Count verbs by strength
        verb_counts = {
            'missing': len([e for e in enhancements if not e['has_verb']]),
            'weak': len([e for e in enhancements if e.get('strength') == 'weak']),
            'strong': len([e for e in enhancements if e.get('strength') == 'strong']),
            'unknown': len([e for e in enhancements if e.get('strength') == 'unknown'])
        }
        
        # Generate overall suggestions
        suggestions = []
        
        if verb_counts['missing'] > 0:
            suggestions.append(
                f"Add action verbs to {verb_counts['missing']} bullet point(s)"
            )
        
        if verb_counts['weak'] > 0:
            suggestions.append(
                f"Replace weak verbs in {verb_counts['weak']} bullet point(s) with stronger alternatives"
            )
        
        if verb_counts['unknown'] > 0:
            suggestions.append(
                f"Consider using recognized action verbs in {verb_counts['unknown']} bullet point(s)"
            )
        
        # Calculate statistics
        has_verbs = total_points - verb_counts['missing']
        strong_ratio = verb_counts['strong'] / total_points if total_points > 0 else 0
        
        return {
            'stats': {
                'total_points': total_points,
                'verb_usage': verb_counts,
                'strong_verb_ratio': strong_ratio
            },
            'status': 'good' if strong_ratio >= 0.7 else 'needs_improvement',
            'suggestions': suggestions
        }