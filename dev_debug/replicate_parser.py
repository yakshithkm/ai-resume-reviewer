import sys, os, re
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.resume_parser.bullet_extractor import BulletPointExtractor

text = '''
Skills

Programming Languages:
• Python (Expert)
• Java (Advanced)
• JavaScript (Intermediate)

Tools and Technologies:
- Git
- Docker
- Kubernetes
'''

# header split
header_keywords = {
    'contact': ['contact', 'contact information'],
    'summary': ['summary', 'objective', 'profile', 'about'],
    'education': ['education', 'academic', 'qualifications', 'university', 'college'],
    'experience': ['experience', 'work', 'work experience', 'employment', 'job', 'position'],
    'skills': ['skills', 'technical skills', 'technologies']
}

buffers = {k: [] for k in header_keywords.keys()}
buffers['unknown'] = []

current = 'unknown'
for i,line in enumerate(text.splitlines()):
    stripped = line.strip()
    if not stripped:
        continue
    lowered = stripped.lower()
    matched = False
    for sec, keywords in header_keywords.items():
        for kw in keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", lowered):
                current = sec
                matched = True
                break
        if matched:
            break
    if not matched:
        if '@' in lowered or 'email' in lowered or 'linkedin.com' in lowered or 'github.com' in lowered or 'phone' in lowered:
            current = 'contact'
    buffers[current].append(line)

original_lines = buffers['skills']
print('ORIGINAL LINES:')
for ln in original_lines:
    print(repr(ln))

text_string = '\n'.join(original_lines)
print('\nTEXT STRING PASSED TO EXTRACTOR:\n', text_string)

be = BulletPointExtractor()
print('\nEXTRACTOR OUTPUT:\n', be.extract_bullet_points(text_string))
