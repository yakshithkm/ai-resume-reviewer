import sys, os, re
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.resume_parser.parser import ResumeParser

text = '''
Education

University of Technology
Master of Computer Science
• Specialized in Machine Learning
• Research assistant in NLP lab
• Published 2 conference papers

Tech College
Bachelor of Engineering
- Dean's List all semesters
- Led student coding club
- Completed capstone project
'''

parser = ResumeParser()
parser.text = text
# Reuse the same logic from parse_resume to inspect the 'education' block processing
lines = parser.text.split('\n')
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
for line in lines:
    stripped = line.strip()
    if not stripped:
        continue
    lowered = stripped.lower()
    matched = False
    matched_kw = None
    for sec, keywords in header_keywords.items():
        for kw in keywords:
            kw = kw.lower()
            if re.search(r"\b" + re.escape(kw) + r"\b", lowered):
                current = sec
                matched = True
                matched_kw = kw
                break
        if matched:
            break
    if matched:
        if matched_kw and stripped.lower() != matched_kw:
            buffers[current].append(line)
    else:
        if '@' in lowered or 'email' in lowered or 'linkedin.com' in lowered or 'github.com' in lowered or 'phone' in lowered:
            current = 'contact'
        buffers[current].append(line)

original_lines = buffers['education']
print('ORIGINAL LINES FOR EDUCATION:')
for ln in original_lines:
    print(repr(ln))

# compute included_lines like parser
raw_lines = original_lines
bullet_char_re = re.compile(r'^\s*[\u2022\u00B7\-\*\u25CB\u25AA\u25E6\u2192]\s+')
numbered_re = re.compile(r'^\s*[\d]+[\.\)]\s+')
letter_re = re.compile(r'^\s*[a-zA-Z]\)\s+')

blocks = []
cur = []
for l in raw_lines:
    if not l.strip():
        if cur:
            blocks.append(cur)
            cur = []
        continue
    cur.append(l)
if cur:
    blocks.append(cur)

print('\nBLOCKS:')
for b in blocks:
    print('BLOCK:')
    for ln in b:
        print('  ', repr(ln))

included_lines = []
for block in blocks:
    found_idx = None
    for i, l in enumerate(block):
        s = l.strip()
        if not s:
            continue
        if s.endswith(':') or bullet_char_re.match(s) or numbered_re.match(s) or letter_re.match(s):
            found_idx = i
            break
    print('found_idx for block:', found_idx)
    if found_idx is not None:
        included_lines.extend(block[found_idx:])

text_block = '\n'.join(included_lines) if included_lines else '\n'.join(original_lines)
print('\nTEXT_BLOCK PASSED TO EXTRACTOR:')
print(text_block)

from src.resume_parser.bullet_extractor import BulletPointExtractor
be = BulletPointExtractor()
print('\nEXTRACTOR OUTPUT:')
print(be.extract_bullet_points(text_block))
