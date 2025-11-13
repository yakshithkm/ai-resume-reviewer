from src.resume_parser.parser import ResumeParser


def test_parser_produces_bullet_enhancements():
    parser = ResumeParser()

    # Minimal resume-like text with an experience section and a couple of bullets
    parser.text = """
Experience
- helped the team improve performance by optimizing queries
• coded features and fixed bugs
"""

    sections = parser.parse_resume()
    assert 'experience' in sections

    # New contract: `sections` remains a mapping of section -> text (string).
    # Per-section bullet data and enhancements are available via `parser.section_details`.
    details = parser.section_details.get('experience', {})
    assert isinstance(details.get('bullet_points', []), list)

    # If the verb enhancer is available, ensure enhancements are present and aligned
    if details.get('bullet_enhancements'):
        enhancements = details['bullet_enhancements']
        assert isinstance(enhancements, list)
        assert len(enhancements) == len(details['bullet_points'])
        for e, orig in zip(enhancements, details['bullet_points']):
            assert e.get('original') == orig
    else:
        # If the enhancer isn't available in the environment, at least bullets were extracted
        assert len(details.get('bullet_points', [])) >= 1
