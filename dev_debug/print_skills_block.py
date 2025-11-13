import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.resume_parser.parser import ResumeParser

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

p = ResumeParser()
p.text = text
sections = p.parse_resume()
import json
print(json.dumps(sections, indent=2))
print('\nSECTION DETAILS:\n')
print(json.dumps(p.section_details, indent=2))
