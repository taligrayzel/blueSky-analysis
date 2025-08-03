"""
Configuration settings for the stance analysis project.
"""

import os
from pathlib import Path

# Project directories
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
VISUALIZATIONS_DIR = DATA_DIR / 'visualizations'
MODEL_DIR = PROJECT_ROOT / 'models'
TESTS_DIR = PROJECT_ROOT / 'tests'

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, VISUALIZATIONS_DIR, MODEL_DIR, TESTS_DIR]:
    directory.mkdir(exist_ok=True)

# Data collection settings
POSTS_PER_USER = 100
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30  # seconds

# Reference users for stance analysis
PRO_ISRAEL_USERS = [
    'noatishby.bsky.social',      # Noa Tishby
    'emilyintelaviv.bsky.social', 
    'demmaj4israel.bsky.social'   # Emily Schrader
]

PRO_PALESTINE_USERS = [
    'monahijazi.bsky.social',     # Mona Hijazi
    'eyeonpalestine.bsky.social', # Eye on Palestine
]

# File paths
RAW_DATA_FILE = RAW_DATA_DIR / 'collected_posts.json'
PROCESSED_DATA_FILE = PROCESSED_DATA_DIR / 'processed_posts.json'
STANCE_ANALYSIS_FILE = PROCESSED_DATA_DIR / 'stance_analysis.json'

# Classification settings
TRAIN_TEST_SPLIT = 0.8
RANDOM_STATE = 42

# Feature extraction settings
MAX_FEATURES = 1000  # Maximum number of features for text vectorization
MIN_DF = 2          # Minimum document frequency for features
MAX_DF = 0.95       # Maximum document frequency for features

# Stance analysis weights
STANCE_WEIGHTS = {
    'keyword_ratio': 0.7,        # Weight for keyword usage
    'sentiment': 0.3, 
    'hashtag_usage': 0,        # Weight for hashtag patterns
    'engagement':0,           # Weight for engagement metrics
    'mention_patterns': 0,     # Weight for user mention patterns
    'content_length': 0       # Weight for content length
}

# Visualization settings
PLOT_STYLE = 'seaborn'
FIGURE_SIZE = (12, 8)
DPI = 300
COLOR_PALETTE = {
    'pro_israeli': '#1f77b4',    # Blue
    'pro_palestinian': '#ff7f0e', # Orange
    'neutral': '#2ca02c',         # Green
    'neutral_unclear': '#2ca02c'  # Also Green for neutral/unclear
}

# Logging settings
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = PROJECT_ROOT / 'stance_analysis.log' 