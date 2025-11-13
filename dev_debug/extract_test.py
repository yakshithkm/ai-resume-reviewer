import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.resume_parser.bullet_extractor import BulletPointExtractor

text_block = '''Programming Languages:
• Python (Expert)
• Java (Advanced)
• JavaScript (Intermediate)

Tools and Technologies:
- Git
- Docker
- Kubernetes
'''
print('TEXT BLOCK:\n', text_block)
be = BulletPointExtractor()
print('EXTRACTED:\n', be.extract_bullet_points(text_block))
