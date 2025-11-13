import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.resume_parser.bullet_extractor import BulletPointExtractor
text = """Experience:
• Led team of 5 developers on cloud migration project
• Implemented CI/CD pipeline using Jenkins
• Reduced deployment time by 60%"""

print('INPUT:')
print(text)

print('\nRAW EXTRACT:')
lines = text.split('\n')
for i,l in enumerate(lines):
    print(i, repr(l), [ord(c) for c in (l[:2])])

a = BulletPointExtractor.extract_bullet_points(text)
print('\nCLEAN EXTRACT:')
print(a)

# Also print internal behavior by mimicking function
from src.resume_parser import bullet_extractor as be

lines = text.split('\n')
bullet_points=[]
in_bullet_list=False
current_bullet=''
for i,line in enumerate(lines):
    line=line.strip()
    if not line:
        continue
    if be.BulletPointExtractor.BULLET_START_REGEX.search(line):
        in_bullet_list=True
        continue
    m=be.BulletPointExtractor.BULLET_REGEX.search(line)
    import re
    test = re.search(r'•\s+', line)
    print('LINE', i, repr(line), 'MATCH', bool(m), 'MATCH_SPAN', m.span() if m else None, 'SIMPLE_DOT_SEARCH', bool(test))
    if m:
        if current_bullet:
            bullet_points.append(current_bullet.strip())
        current_bullet=line[m.end():].strip()
        in_bullet_list=True
        continue
    elif in_bullet_list and line:
        if (i>0 and (line[0].islower() or line[0] in ',' or all(c in ' \t' for c in lines[i-1][:len(line)-len(line.lstrip())]))):
            if current_bullet:
                current_bullet += ' ' + line
            else:
                current_bullet=line
        else:
            if current_bullet:
                bullet_points.append(current_bullet.strip())
            current_bullet=line
if current_bullet:
    bullet_points.append(current_bullet.strip())

print('\nRAW LIST:')
print(bullet_points)
