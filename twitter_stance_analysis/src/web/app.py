"""
Web application for stance analysis visualization.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from flask import Flask, render_template, request, jsonify, send_file

# Add src directory to Python path
src_dir = Path(__file__).parent.parent
sys.path.append(str(src_dir))

from webApp.bluesky_scraper import BlueskyScraper
from webApp.stance_analyzer import StanceAnalyzer
from webApp.config import (
    PROCESSED_DATA_DIR,
    VISUALIZATIONS_DIR,
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_FILE
)

app = Flask(__name__)
scraper = BlueskyScraper()
analyzer = StanceAnalyzer()

def load_analysis_results() -> Dict:
    """Load existing analysis results."""
    results_file = PROCESSED_DATA_DIR / 'stance_analysis.json'
    if results_file.exists():
        with open(results_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_user():
    """Search for a Bluesky user and analyze their stance."""
    username = request.json.get('username')
    if not username:
        return jsonify({'error': 'No username provided'}), 400
        
    try:
        # Get user info
        user_info = scraper.get_user_info(username)
        if not user_info:
            return jsonify({'error': f'User {username} not found'}), 404
            
        # Get user's posts
        posts = scraper.get_user_posts(username)
        if not posts:
            return jsonify({'error': f'No posts found for {username}'}), 404
            
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
        
        # Analyze stance
        analysis = analyzer.analyze_user(posts_features)
        if not analysis:
            return jsonify({'error': 'Could not analyze user\'s stance'}), 500
            
        # Save results
        results = load_analysis_results()
        results[username] = analysis
        
        with open(PROCESSED_DATA_DIR / 'stance_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4)
            
        # Generate visualization
        viz_file = VISUALIZATIONS_DIR / f'{username.replace(".", "_")}_analysis.png'
        analyzer.visualize_results(analysis, str(viz_file))
        
        return jsonify({
            'user_info': user_info,
            'analysis': analysis,
            'visualization': f'/visualization/{username}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/visualization/<username>')
def get_visualization(username: str):
    """Serve the visualization image for a user."""
    viz_file = VISUALIZATIONS_DIR / f'{username.replace(".", "_")}_analysis.png'
    if not viz_file.exists():
        return jsonify({'error': 'Visualization not found'}), 404
    return send_file(str(viz_file))

@app.route('/compare', methods=['POST'])
def compare_users():
    """Compare stance analysis of multiple users."""
    usernames = request.json.get('usernames', [])
    if not usernames:
        return jsonify({'error': 'No usernames provided'}), 400
        
    try:
        results = load_analysis_results()
        comparison = {}
        
        for username in usernames:
            if username in results:
                comparison[username] = results[username]
            else:
                # Analyze user if not in results
                user_info = scraper.get_user_info(username)
                if not user_info:
                    continue
                    
                posts = scraper.get_user_posts(username)
                if not posts:
                    continue
                    
                posts_features = []
                for post in posts:
                    features = {
                        'text': post.get('text', ''),
                        'entities': post.get('entities', {}),
                        'metrics': post.get('metrics', {}),
                        'text_length': len(post.get('text', ''))
                    }
                    posts_features.append(features)
                    
                analysis = analyzer.analyze_user(posts_features)
                if analysis:
                    comparison[username] = analysis
                    
        return jsonify(comparison)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def get_history():
    """Get analysis history for all users."""
    try:
        results = load_analysis_results()
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 