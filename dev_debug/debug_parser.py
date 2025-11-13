import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.resume_parser.parser import ResumeParser

p = ResumeParser()
text = """
Summary
Experienced software engineer with passion for clean code.

Contact
email@example.com
(123) 456-7890
"""

p.text = text
sections = p.parse_resume()
print('SECTIONS:')
for k,v in sections.items():
    print(k, '->', v)
    
print('\n-- RAW LINE-BASED BUFFERS DEBUG --')
lines = p.text.split('\n')
print('LINES:')
for i,l in enumerate(lines):
    print(i, repr(l))
print('---')
section_keywords = {
    'contact': ['contact'] + p.SECTION_KEYWORDS.get('contact', []),
    'summary': ['summary'] + p.SECTION_KEYWORDS.get('summary', []),
    'education': ['education'] + p.SECTION_KEYWORDS.get('education', []),
    'experience': ['experience'] + p.SECTION_KEYWORDS.get('experience', []),
    'skills': ['skills'] + p.SECTION_KEYWORDS.get('skills', [])
}
buffers = {k: [] for k in section_keywords.keys()}
buffers['unknown'] = []
current = 'unknown'
for line in lines:
    stripped = line.strip()
    if not stripped:
        continue
    lowered = stripped.lower()
    matched = False
    for sec, keywords in section_keywords.items():
        for kw in keywords:
            kw = kw.lower()
            if lowered == kw or lowered.startswith(kw) or f"{kw}:" in lowered:
                current = sec
                matched = True
                break
        if matched:
            break
    if not matched:
        buffers[current].append(line)

for k,v in buffers.items():
    print(k, '->', v)

print('\n-- SKILLS SAMPLE DEBUG --')
skills_text = """
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
lines = skills_text.split('\n')
buffers = {k: [] for k in section_keywords.keys()}
buffers['unknown'] = []
current = 'unknown'
for line in lines:
    stripped = line.strip()
    if not stripped:
        continue
    lowered = stripped.lower()
    matched = False
    for sec, keywords in section_keywords.items():
        for kw in keywords:
            kw = kw.lower()
            if lowered == kw or lowered.startswith(kw) or f"{kw}:" in lowered:
                current = sec
                matched = True
                break
        if matched:
            break
    if not matched:
        buffers[current].append(line)

print('buffers[skills] original lines ->', buffers['skills'])
import src.resume_parser.bullet_extractor as be
filtered = [ln for ln in buffers['skills'] if re.compile(r'^\s*[\u2022\u00B7\-\*\u25CB\u25AA\u25E6\u2192]\s+').match(ln) or re.compile(r'^\s*[\d]+[\.\)]\s+').match(ln) or re.compile(r'^\s*[a-zA-Z]\)\s+').match(ln) or ln.strip().endswith(':')]
print('filtered lines ->', filtered)
print('extractor ->', be.BulletPointExtractor.extract_bullet_points('\n'.join(filtered)))
