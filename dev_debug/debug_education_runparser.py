import sys, os
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
sections = parser.parse_resume()
print('SECTIONS KEYS:', list(sections.keys()))
print('\nEDUCATION TEXT (repr lines):')
for ln in sections['education']['text'].split('\n'):
    print(repr(ln))

print('\nEDUCATION BULLETS:')
for b in sections['education']['bullet_points']:
    print(repr(b))
