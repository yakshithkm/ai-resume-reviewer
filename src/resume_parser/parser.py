"""
Minimal ResumeParser implementation used by the application and tests.

This file provides a small, well-formed parser with the methods the
application expects. The real project may use spaCy and more advanced
logic; the tests in this repo monkeypatch most behaviors, so this
implementation focuses on stability and clear return shapes.
"""
import os
import re
import spacy
from typing import Dict, Any, List
from datetime import datetime
from dateutil.relativedelta import relativedelta
import docx
import io
from pdfminer.high_level import extract_text
from .bullet_extractor import BulletPointExtractor
from .cache import ResumeCache


class ResumeParser:
    """A lightweight resume parser with predictable outputs for tests."""

    # Class-level cached NLP objects to avoid reloading per request
    _NLP = None
    _MATCHER = None

    def __init__(self) -> None:
        self.text: str = ""
        self.sections: Dict[str, str] = {}  # Add sections attribute
        self.section_details: Dict[str, Dict[str, Any]] = {}
        self.bullet_extractor = BulletPointExtractor()
        self.cache = ResumeCache()
        
        # Load spaCy model once (singleton pattern)
        try:
            if ResumeParser._NLP is None:
                ResumeParser._NLP = spacy.load('en_core_web_sm')
            self.nlp = ResumeParser._NLP
            if ResumeParser._MATCHER is None and self.nlp:
                ResumeParser._MATCHER = spacy.matcher.PhraseMatcher(self.nlp.vocab, attr="LOWER")
                # Initialize patterns one time
                self.matcher = ResumeParser._MATCHER
                self._initialize_skill_patterns()
            else:
                self.matcher = ResumeParser._MATCHER
        except Exception as e:
            print(f"Warning: Could not initialize spaCy model: {e}")
            self.nlp = None
            self.matcher = None
    
    def _initialize_skill_patterns(self):
        """Initialize skill patterns for PhraseMatcher"""
        if not self.nlp:
            return
            
        programming_skills = [
            "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go",
            "Rust", "PHP", "Ruby", "Swift", "Kotlin", "SQL", "HTML", "CSS"
        ]
        
        frameworks = [
            "React", "Angular", "Vue.js", "Django", "Flask", "Spring", 
            "Node.js", "Express.js", "TensorFlow", "PyTorch", "Scikit-learn",
            "Pandas", "NumPy", "Docker", "Kubernetes"
        ]
        
        tools = [
            "Git", "AWS", "Azure", "GCP", "Linux", "Unix", "Jenkins",
            "CircleCI", "GitHub Actions", "Jira", "Confluence", 
            "Terraform", "Ansible"
        ]
        
        # Add patterns to matcher
        self.matcher.add("PROGRAMMING", [self.nlp(text) for text in programming_skills])
        self.matcher.add("FRAMEWORK", [self.nlp(text) for text in frameworks])
        self.matcher.add("TOOL", [self.nlp(text) for text in tools])
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file using pdfminer.six."""
        try:
            return extract_text(file_path) or ""
        except Exception:
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from a DOCX file using python-docx."""
        try:
            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text]
            return "\n".join(paragraphs)
        except Exception:
            return ""
    
    def parse_resume(self, file_path: str = None) -> Dict[str, Dict[str, Any]]:
        """Parse resume into sections with caching."""
        # Try cache first
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                cached_result = self.cache.get(file_path, content)
                if cached_result:
                    self.section_details = cached_result
                    # Important: set self.text from the cached result file content
                    self.text = content
                    return self.section_details
            except:
                pass
        
        # Extract text if needed
        if file_path:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.pdf':
                self.text = self.extract_text_from_pdf(file_path)
            elif ext == '.docx':
                self.text = self.extract_text_from_docx(file_path)
            else:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        self.text = f.read()
                except Exception:
                    self.text = ""
        
        # Define section headers
        headers = {
            'contact': ['contact', 'contact information', 'personal information'],
            'summary': ['summary', 'professional summary', 'profile', 'objective'],
            'experience': ['experience', 'work experience', 'employment history'],
            'education': ['education', 'academic background', 'qualifications'],
            'skills': ['skills', 'technical skills', 'technologies', 'expertise']
        }
        
        # Parse sections
        sections = []
        current_section = None
        current_content = []
        
        for line in (self.text or "").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            
            # Check for section headers
            lowered = stripped.lower()
            found_section = False
            
            for sec, variants in headers.items():
                if any(lowered == v or lowered.startswith(v + ' ') or 
                      lowered.startswith(v + ':') for v in variants):
                    if current_section:
                        sections.append((current_section, current_content))
                    current_section = sec
                    current_content = [stripped]
                    found_section = True
                    break
            
            if not found_section:
                if not current_section:
                    current_section = 'contact'
                current_content.append(stripped)
        
        # Add final section
        if current_section and current_content:
            sections.append((current_section, current_content))
        
        # Create section details
        details = {}
        for sec, content in sections:
            if not content:
                continue
            
            # Special handling for contact
            if sec == 'contact':
                text_block = '\n'.join(content)
            else:
                content_lines = content[1:] if len(content) > 1 else []
                text_block = '\n'.join(content_lines)
            
            text_block = text_block.strip()
            if not text_block:
                continue
            
            bullets = []
            if sec in ('experience', 'education', 'skills'):
                bullets = self.bullet_extractor.extract_bullet_points(text_block)
            
            details[sec] = {
                'text': text_block,
                'bullet_points': bullets
            }
        
        # Cache results
        self.section_details = details
        if file_path:
            try:
                self.cache.set(file_path, self.text, details)
            except:
                pass
        
        return self.section_details
    
    def get_skills(self) -> Dict[str, Dict[str, Any]]:
        """Extract skills using NLP and pattern matching."""
        skills = {}
        
        # Define skill recategorization rules
        cloud_tools = {'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'terraform', 'ansible'}
        
        # Get text from relevant sections
        combined_text = ""
        
        # Use sections from test input if available
        if hasattr(self, 'sections') and self.sections:
            for section in ['skills']:
                if section in self.sections:
                    combined_text += self.sections[section] + "\n"
        
        # Otherwise use parser.text if available
        if not combined_text and self.text:
            combined_text = self.text
        
        # First, try to extract category: skill format (e.g., "Programming: Python, Java")
        # Pattern 1: Category followed by comma-separated skills on the same line
        category_pattern = r'([A-Za-z\s]+):\s*([^:\n-]+?)(?:\n|$)'
        
        for match in re.finditer(category_pattern, combined_text):
            category = match.group(1).strip()
            skills_text = match.group(2).strip()
            
            # Skip if this looks like a heading with bullet points following
            if not skills_text or len(skills_text) < 3:
                continue
            
            # Split by commas to get individual skills
            individual_skills = [s.strip() for s in re.split(r',|;|/', skills_text)]
            for skill in individual_skills:
                if skill and len(skill) > 1 and not skill.startswith('-'):
                    # Auto-categorize cloud tools
                    if any(cloud_tool in skill.lower() for cloud_tool in cloud_tools):
                        skill_key = f"Cloud: {skill}"
                        final_category = "Cloud"
                    else:
                        skill_key = f"{category}: {skill}"
                        final_category = category
                    
                    if skill_key not in skills:
                        skills[skill_key] = {"count": 1, "category": final_category}
                    else:
                        skills[skill_key]["count"] += 1
        
        # Use spaCy for extraction (always try this for comprehensive results)
        if self.nlp and combined_text:
            doc = self.nlp(combined_text)
            
            # Use PhraseMatcher for skill detection
            if self.matcher:
                matches = self.matcher(doc)
                for match_id, start, end in matches:
                    skill = doc[start:end].text
                    category = self.nlp.vocab.strings[match_id]
                    skill_key = f"{category}: {skill}"
                    if skill_key not in skills:
                        skills[skill_key] = {"count": 1, "category": category}
                    else:
                        skills[skill_key]["count"] += 1
            
            # Extract technical terms and proper nouns
            for token in doc:
                if token.pos_ in ["NOUN", "PROPN"] and len(token.text) > 2:
                    if (token.is_title or token.is_upper) and not token.like_num:
                        skill = token.text
                        # Skip common words
                        if skill.lower() not in {'skills', 'technical', 'additional', 'experienced'}:
                            if skill not in skills:
                                skills[skill] = {"count": 1, "category": "OTHER"}
                            else:
                                skills[skill]["count"] += 1
        
        # Regex fallback - expand patterns to include more skills
        if not skills and combined_text:
            patterns = {
                "PROGRAMMING": r"\b(?:python|java|javascript|typescript|c\+\+|c#|go|rust)\b",
                "FRAMEWORK": r"\b(?:react|angular|vue|django|flask|spring|node\.js|tensorflow|pytorch)\b",
                "TOOL": r"\b(?:git|docker|kubernetes|aws|azure|jenkins|terraform)\b"
            }
            
            for category, pattern in patterns.items():
                matches = re.finditer(pattern, combined_text.lower())
                for match in matches:
                    skill = match.group().strip()
                    # Capitalize first letter
                    skill = skill.capitalize() if skill.lower() not in {'aws', 'git'} else skill.upper()
                    if skill not in skills:
                        skills[skill] = {"count": 1, "category": category}
                    else:
                        skills[skill]["count"] += 1
        
        return skills
    
    def get_contact_info(self) -> Dict[str, Any]:
        """Extract contact information."""
        info = {
            'name': None,
            'email': None,
            'phone': None,
            'location': None,
            'linkedin': None,
            'github': None
        }
        
        if 'contact' not in self.sections:
            return info
        
        text = self.sections['contact']
        
        # Extract email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            info['email'] = email_match.group()
        
        # Extract phone
        phone_pattern = r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            info['phone'] = phone_match.group()
        
        # Extract LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/[\w\-]+', text)
        if linkedin_match:
            info['linkedin'] = linkedin_match.group()
        
        # Extract GitHub
        github_match = re.search(r'github\.com/[\w\-]+', text)
        if github_match:
            info['github'] = github_match.group()
        
        # Extract location
        location_match = re.search(r'[A-Z][a-zA-Z\s-]+,\s*[A-Z]{2}(?:\s*\d{5})?', text)
        if location_match:
            info['location'] = location_match.group()
        
        # Extract name (first line)
        lines = text.split('\n')
        if lines:
            name = lines[0].strip()
            if len(name) > 3 and not any(x in name.lower() for x in 
                                       ['resume', 'cv', 'curriculum', 'vitae']):
                info['name'] = name
        
        return info
    
    def extract_bullet_points(self, section_name: str) -> List[str]:
        """Extract bullet points from a section."""
        section = self.section_details.get(section_name, {})
        section_text = section.get('text', '') if isinstance(section, dict) else ''
        return self.bullet_extractor.extract_bullet_points(section_text)
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse various date formats."""
        try:
            return datetime.strptime(date_str, '%B %Y')
        except ValueError:
            try:
                return datetime.strptime(date_str, '%b %Y')
            except ValueError:
                try:
                    return datetime.strptime(date_str, '%Y-%m')
                except ValueError:
                    try:
                        return datetime.strptime(date_str, '%m/%Y')
                    except ValueError:
                        if re.match(r'^\d{4}$', date_str):
                            return datetime.strptime(f"January {date_str}", '%B %Y')
                        raise
    
    def get_experience(self) -> List[Dict[str, Any]]:
        """Extract structured experience information."""
        experience = []
        
        if 'experience' not in self.section_details:
            return experience
        
        section = self.section_details['experience']
        text = section.get('text', '')
        
        title_patterns = [
            r'(?:senior|lead|principal|staff)?\s*(?:software|systems?|data)',
            r'(?:engineer|developer|architect|scientist|analyst)',
            r'(?:tech|engineering|development|product|program|project)',
            r'(?:lead|manager|director|head|chief|vp|supervisor)',
            r'(?:frontend|backend|full\s*stack|web|mobile)\s*developer'
        ]
        
        date_patterns = [
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',
            r'\d{4}-\d{2}',
            r'\d{2}/\d{4}'
        ]
        
        location_pattern = r'[A-Z][a-zA-Z\s-]+,\s*[A-Z]{2}(?:\s*\d{5})?'
        
        entries = []
        current_entry = []
        
        for line in text.splitlines():
            line = line.strip()
            if not line:
                if current_entry:
                    entries.append('\n'.join(current_entry))
                    current_entry = []
                continue
            
            if (re.search(r'(?:19|20)\d{2}', line) and
                (any(re.search(p, line, re.I) for p in title_patterns) or
                 re.search(r'(?:@|at|\bat\b)\s+[A-Z][a-zA-Z0-9\s&\.,]+', line, re.I))):
                if current_entry:
                    entries.append('\n'.join(current_entry))
                    current_entry = []
            
            current_entry.append(line)
        
        if current_entry:
            entries.append('\n'.join(current_entry))
        
        for entry in entries:
            if not entry.strip():
                continue
            
            job_info = {
                'company': None,
                'title': None,
                'start_date': None,
                'end_date': None,
                'duration': None,
                'location': None,
                'achievements': [],
                'technologies': [],
                'impact': []
            }
            
            lines = entry.split('\n')
            header = ' '.join(line.strip() for line in lines[:2])
            
            # Extract company
            company_match = re.search(
                r'(?:@|at|\bat\b)\s+([A-Z][a-zA-Z0-9\s&\.,]+)(?:,|\s|$)', 
                header, re.I)
            if company_match:
                company_name = company_match.group(1).strip()
                company_name = re.sub(r',\s*$', '', company_name)
                job_info['company'] = company_name
            
            # Extract title - try to extract the full title before 'at'
            title_part = re.split(r'\s+at\s+', header, flags=re.I)[0] if ' at ' in header.lower() else header
            title_match = re.search(r'((?:senior|lead|principal|staff)\s+)?(?:software|data)\s+engineer', title_part, re.I)
            if title_match:
                job_info['title'] = title_match.group(0).strip()
            else:
                # Fallback to pattern matching
                for pattern in title_patterns:
                    title_match = re.search(pattern, header, re.I)
                    if title_match:
                        job_info['title'] = title_match.group(0).strip().title()
                        break
            
            # Extract dates
            if re.search(r'present|current|now', header, re.I):
                dates = []
                for pattern in date_patterns:
                    dates.extend(re.findall(pattern, header))
                if dates:
                    job_info['start_date'] = dates[0]
                    job_info['end_date'] = 'Present'
            else:
                dates = []
                for pattern in date_patterns:
                    dates.extend(re.findall(pattern, header))
                if len(dates) >= 2:
                    job_info['start_date'] = dates[0]
                    job_info['end_date'] = dates[1]
                elif len(dates) == 1:
                    job_info['start_date'] = dates[0]
            
            # Calculate duration
            if job_info['start_date'] and job_info['end_date']:
                try:
                    start = self._parse_date(job_info['start_date'])
                    end = (datetime.now() if job_info['end_date'] == 'Present'
                          else self._parse_date(job_info['end_date']))
                    duration = relativedelta(end, start)
                    
                    if duration.years > 0 and duration.months > 0:
                        job_info['duration'] = f"{duration.years} years {duration.months} months"
                    elif duration.years > 0:
                        job_info['duration'] = f"{duration.years} years"
                    elif duration.months > 0:
                        job_info['duration'] = f"{duration.months} months"
                except (ValueError, TypeError):
                    pass
            
            # Extract location
            location_text = header + '\n' + '\n'.join(lines[:3])
            location_match = re.search(location_pattern, location_text)
            if location_match:
                job_info['location'] = location_match.group(0).strip()
            
            # Process bullet points
            content = '\n'.join(lines[2:])
            bullets = self.bullet_extractor.extract_bullet_points(content)
            
            if bullets:
                # Add all bullets to achievements
                job_info['achievements'] = bullets
                
                # Also categorize them
                for bullet in bullets:
                    # Look for technology mentions
                    if re.search(r'using|with|through|via|built\s+(?:with|using)', bullet, re.I):
                        job_info['technologies'].append(bullet)
                    # Look for impact statements
                    if re.search(r'increased|decreased|reduced|improved|achieved|won', bullet, re.I):
                        job_info['impact'].append(bullet)
            
            if job_info['company'] or job_info['title']:
                experience.append(job_info)
        
        return experience
    
    def get_education(self) -> List[Dict[str, str]]:
        """Extract structured education information."""
        degrees = []
        
        if 'education' not in self.section_details:
            return degrees
        
        degree_patterns = {
            'bachelors': [
                r"bachelor'?s?(?:\sof\s(?:science|arts|engineering|business))?",
                r"b\.?(?:s|a|e|b\.?a)",
                r"undergraduate degree",
            ],
            'masters': [
                r"master'?s?(?:\sof\s(?:science|arts|engineering|business))?",
                r"m\.?(?:s|a|e|b\.?a)",
                r"graduate degree",
            ],
            'phd': [
                r"ph\.?d",
                r"doctor(?:ate)?\sof\sphilosophy",
                r"doctoral degree",
            ]
        }
        
        major_patterns = [
            r"(?:in|of)\s+([A-Za-z\s]+?)(?:\s*,|\s+Expected|\s+\d{4}|$)",  # "... in Computer Science, 2024"
            r"([^,\.]+)\smajor",      # "Computer Science major"
        ]
        
        # Compile patterns
        degree_res = {
            level: re.compile('|'.join(patterns), re.IGNORECASE)
            for level, patterns in degree_patterns.items()
        }
        major_re = re.compile('|'.join(major_patterns), re.IGNORECASE)
        
        section = self.section_details['education']
        text = section.get('text', '')
        
        # Split into entries
        entries = []
        current_entry = []
        
        for line in text.splitlines():
            line = line.strip()
            if not line:
                if current_entry:
                    entries.append('\n'.join(current_entry))
                    current_entry = []
                continue
            
            if (len(line) > 5 and
                not re.search(r'(?:19|20)\d{2}|gpa|bachelor|master|phd|degree', line, re.I)):
                if current_entry:
                    entries.append('\n'.join(current_entry))
                    current_entry = []
            
            current_entry.append(line)
        
        if current_entry:
            entries.append('\n'.join(current_entry))
        
        for entry in entries:
            if not entry.strip():
                continue
            
            degree_info = {
                'degree': None,
                'major': None,
                'school': None,
                'graduation': None,
                'gpa': None
            }
            
            # Extract degree
            for level, pattern in degree_res.items():
                if pattern.search(entry):
                    degree_info['degree'] = level.title()
                    break
            
            # Extract major - try multiple patterns and pick the best match
            major_match = None
            # Try specific pattern first: "Bachelor of Science in Computer Science"
            specific_match = re.search(r'(?:bachelor|master|doctor).*?\s+in\s+([A-Za-z\s]+?)(?:\s*,|\s+Expected|\s+\d{4}|$)', entry, re.I)
            if specific_match:
                major = specific_match.group(1).strip()
                # Remove leading "Science in" or "Arts in" etc
                major = re.sub(r'^(?:Science|Arts|Engineering|Business)\s+in\s+', '', major, flags=re.I)
                degree_info['major'] = major
            else:
                # Fallback to general pattern
                major_match = major_re.search(entry)
                if major_match:
                    degree_info['major'] = major_match.group(1).strip()
            
            # Extract graduation
            grad_match = re.search(r'(?:expected|anticipated)?\s*(?:19|20)\d{2}', entry, re.I)
            if grad_match:
                degree_info['graduation'] = grad_match.group(0).strip()
            
            # Extract GPA
            gpa_match = re.search(r'(?:gpa|grade point average)[:\s]+([0-9.]+)', entry, re.I)
            if gpa_match:
                degree_info['gpa'] = gpa_match.group(1)
            
            # Extract school (first line)
            lines = entry.split('\n')
            if lines:
                first_line = lines[0].strip()
                if (len(first_line) > 5 and
                    not any(word in first_line.lower() for word in 
                           ['gpa', 'expected', 'bachelor', 'master', 'phd'])):
                    degree_info['school'] = first_line
            
            if degree_info['school'] or degree_info['degree']:
                degrees.append(degree_info)
        
        return degrees