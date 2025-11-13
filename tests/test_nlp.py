from resume_parser.parser import ResumeParser


def test_nlp_section_classification():
    """Test NLP-based section classification"""
    parser = ResumeParser()

    # Test text with clear section markers
    test_text = """
John Smith
Email: john@example.com

Professional Summary
Experienced software engineer specialized in AI/ML

Work Experience
Senior Developer at Tech Corp
- Led team of 5 developers
- Implemented ML pipeline

Education
MS in Computer Science
University of Technology

Technical Skills
Python, TensorFlow, AWS
"""

    parser.text = test_text
    parser.doc = parser.nlp(test_text)
    sections = parser.parse_resume(None)  # None because we set text directly

    # Check if major sections are identified
    assert any('summary' in section.lower() for section in sections)
    assert any('experience' in section.lower() for section in sections)
    assert any('education' in section.lower() for section in sections)
    assert any('skills' in section.lower() for section in sections)


def test_nlp_skill_extraction():
    """Test NLP-based skill extraction"""
    parser = ResumeParser()

    # Test text with various skill formats
    test_text = """
Technical Skills:
- Python programming
- TensorFlow and PyTorch
- AWS Cloud Services
- Git version control

Additional Skills:
Docker, Kubernetes, CI/CD
Experienced in Agile/Scrum
"""

    parser.text = test_text
    parser.doc = parser.nlp(test_text)
    skills = parser.get_skills()

    # Check if common skills are identified
    common_skills = ['Python', 'TensorFlow', 'PyTorch', 'AWS', 'Git', 'Docker', 'Kubernetes']
    for skill in common_skills:
        assert any(skill.lower() in s.lower() for s in skills)


def test_entity_recognition():
    """Test entity recognition in resume text"""
    parser = ResumeParser()

    test_text = """
Jane Smith
Email: jane.smith@email.com

Education
University of Technology
Master of Science in Computer Science
2018 - 2020

Experience
Software Engineer at Google Inc.
January 2020 - Present
"""

    parser.text = test_text
    doc = parser.nlp(test_text)

    # Check if key entities are recognized
    entities = [(ent.text, ent.label_) for ent in doc.ents]

    # Should find person name
    assert any(ent[1] == 'PERSON' for ent in entities)

    # Should find organizations
    assert any(ent[1] == 'ORG' for ent in entities)

    # Should find dates
    assert any(ent[1] == 'DATE' for ent in entities)