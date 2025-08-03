"""
Script to analyze a user's stance on the Israeli-Palestinian conflict.
"""

import json
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional
from webApp.bluesky_scraper import BlueskyScraper
from webApp.stance_analyzer import StanceAnalyzer
from webApp.config import (
    PROCESSED_DATA_DIR,
    VISUALIZATIONS_DIR,
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_FILE
)

# Set up logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def analyze_user(username: str) -> Optional[Dict]:
    """Analyze a user's stance based on their posts."""
    logger.info(f"Starting analysis for user: {username}")
    
    # Initialize components
    scraper = BlueskyScraper()
    analyzer = StanceAnalyzer()
    
    # Get user info
    user_info = scraper.get_user_info(username)
    if not user_info:
        logger.error(f"Could not find user {username}")
        return None
    
    logger.info(f"Found user: {user_info['display_name']} (@{username})")
    logger.info(f"Followers: {user_info['followers_count']}, Following: {user_info['following_count']}")
    
    # Fetch user's posts
    logger.info("Fetching user's posts...")
    posts = scraper.get_user_posts(username)
    
    if not posts:
        logger.error(f"No posts found for user {username}")
        return None
    
    logger.info(f"Retrieved {len(posts)} posts")
    
    # Save raw posts
    scraper.save_posts(posts, username)
    
    # Prepare features for analysis
    posts_features = []
    for post in posts:
        features = {
            'text': post.get('text', ''),
            'entities': post.get('entities', {}),
            'metrics': post.get('metrics', {}),
            'text_length': len(post.get('text', ''))
        }
        posts_features.append(features)
    
    # Analyze user's stance
    logger.info("Analyzing posts...")
    analysis = analyzer.analyze_user(posts_features)
    
    if not analysis:
        logger.error("Could not analyze user's stance")
        return None
    
    # Save results
    results = {username: analysis}
    output_file = PROCESSED_DATA_DIR / 'stance_analysis.json'
    
    # Load existing results if any
    if output_file.exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_results = json.load(f)
        existing_results.update(results)
        results = existing_results
    
    # Save updated results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
    
    # Generate visualization
    viz_file = VISUALIZATIONS_DIR / f'{username.replace(".", "_")}_analysis.png'
    analyzer.visualize_results(analysis, str(viz_file))
    
    # Print results
    print(f"\nNumber of posts analyzed: {len(posts)}")
    print("\nAnalysis Results:")
    print(f"Overall Stance: {analysis['stance']}")
    print(f"Confidence: {analysis['confidence']:.2f}")
    print(f"Average Score: {analysis['average_score']:.2f}")
    print("\nStance Distribution:")
    for stance, percentage in analysis['stance_distribution'].items():
        print(f"{stance}: {percentage:.1%}")
    
    return analysis

def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze_user.py <username>")
        print("Example: python analyze_user.py user.bsky.social")
        sys.exit(1)
    
    username = sys.argv[1]
    analyze_user(username)

if __name__ == "__main__":
    main() 