import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.resume_parser.parser import ResumeParser

text = '''
Work Experience

Senior Software Engineer at TechCorp
• Led development of cloud-based platform
• Implemented CI/CD pipeline
• Mentored junior developers

Software Engineer at StartupCo
- Developed RESTful APIs
- Improved test coverage by 40%
- Optimized database queries
'''

p = ResumeParser()
p.text = text
sections = p.parse_resume()
import json
print(json.dumps(sections, indent=2))
print('\nSECTION DETAILS:\n')
print(json.dumps(p.section_details, indent=2))
