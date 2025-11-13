import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.verb_enhancer import ActionVerbEnhancer

def main():
    # Initialize the verb enhancer
    enhancer = ActionVerbEnhancer()
    
    # Read the sample resume
    with open('examples/sample_resume.txt', 'r') as f:
        resume_text = f.read()
    
    # Analyze all bullet points
    enhancements = enhancer.enhance_bullet_points(resume_text)
    
    # Get summary statistics
    summary = enhancer.summarize_enhancements(enhancements)
    
    # Print analysis results
    print("\nRESUME BULLET POINT ANALYSIS")
    print("=" * 30)
    
    if 'stats' in summary:
        print("\nSUMMARY STATISTICS")
        print("-" * 20)
        stats = summary['stats']
        print(f"Total bullet points: {stats['total_points']}")
        print(f"Verb usage:")
        for category, count in stats['verb_usage'].items():
            print(f"  - {category.title()}: {count}")
        print(f"Strong verb ratio: {stats['strong_verb_ratio']:.0%}")
    
    print("\nOVERALL STATUS")
    print("-" * 20)
    print(f"Status: {summary.get('status', 'Unknown').replace('_', ' ').title()}")
    
    if summary['suggestions']:
        print("\nSUGGESTED IMPROVEMENTS")
        print("-" * 20)
        for suggestion in summary['suggestions']:
            print(f"• {suggestion}")
    
    print("\nDETAILED ANALYSIS")
    print("-" * 20)
    for i, result in enumerate(enhancements, 1):
        print(f"\nBullet point #{i}:")
        print(f"Original: {result['original']}")
        
        if not result['has_verb']:
            print(f"Issue: {result['suggestion']}")
            continue
            
        print(f"Verb used: {result['verb']}")
        if 'categories' in result:
            print(f"Categories: {', '.join(result['categories'])}")
        print(f"Strength: {result['strength']}")
        
        if 'suggestions' in result:
            print("Suggested stronger verbs:")
            for verb in result['suggestions'][:3]:
                print(f"  - {verb}")
            
        if 'examples' in result:
            print("Example improvements:")
            for example in result['examples']:
                print(f"  - {example}")
        
        print("-" * 20)

if __name__ == "__main__":
    main()