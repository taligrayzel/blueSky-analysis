"""
Stance analysis classifier for social media posts.
"""

import json
import logging
from collections import Counter
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from textblob import TextBlob
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend suitable for server environments
import matplotlib.pyplot as plt
import seaborn as sns
import statistics
from pathlib import Path
import re
from markupsafe import Markup
from transformers import pipeline
from config import (
    STANCE_WEIGHTS,
    COLOR_PALETTE,
    PLOT_STYLE,
    FIGURE_SIZE,
    DPI,
    PROCESSED_DATA_DIR,
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

class StanceAnalyzer:
    """Analyzes stance in social media posts using multiple features."""
    
    def __init__(self):
        """Initialize the stance analyzer with parameters and weights."""
        self.weights = STANCE_WEIGHTS
        
        # Pro-Israel keywords and phrases
        self.pro_israeli_keywords = {
            # General terms
            'israel', 'israeli', 'zionist', 'zionism', 'jewish state', 'jewish people',
            'israel deserves to live', 'israel is under attack', 'am yisrael chai', 'homeland', 'unity',
            
            # Support terms
            'stand with israel', 'support israel', 'defend israel', 'standwithisrael', 'pray for israel',
            'bring them home', 'bringthemhome', 'jewish lives matter', 'never again', 'israelunderattack',

            # Military terms
            'idf', 'israel defense forces', 'mossad', 'israeli army', 'iron dome',
            'war on terror', 'eliminate hamas', 'defend ourselves', 'security', 'survival',

            # Political terms
            'netanyahu', 'bibi', 'benjamin netanyahu', 'israeli government', 'israeli pm',
            'judicial terror', 'strong leadership',

            # Historical terms
            'holocaust', 'shoah', 'jewish history', 'simchat torah massacre', 'october 7',

            # Religious terms
            'jewish', 'judaism', 'torah', 'jerusalem', 'temple mount',

            # Symbols
            '🇮🇱', '✡️', '🕎',

            # Emotional / additional terms
            'hostages', 'israeli hostages', 'terrorist', 'terrorism', 'hezbollah', 'rape is not resistance',
            'horror of terror attacks', 'hamas is isis'
        }

        # Pro-Palestine keywords and phrases
        self.pro_palestinian_keywords = {
            # General terms
            'palestine', 'palestinian', 'gaza', 'west bank', 'occupied territories',
            'palestinian lives matter', 'justice for palestine', 'from the river to the sea',

            # Support terms
            'free palestine', 'support palestine', 'palestine will be free', 'freepalestine',
            'stand with palestine', 'save gaza', 'coexist', 'decolonize',

            # Political terms
            'hamas', 'fatah', 'plo', 'palestinian authority', 'resistance', 'right to resist',
            'zionism is terrorism', 'end the occupation', 'settler colonialism', 'intifada',

            # Historical terms
            'nakba', 'palestinian history', 'arab history', 'palestinian people',

            # Human rights terms
            'occupation', 'settlements', 'apartheid', 'human rights', 'genocide',
            'ethnic cleansing', 'war crimes', 'humanitarian crisis', 'mass grave',
            'displaced civilians', 'bombing civilians', 'children suffering', 'open air prison',

            # Religious terms
            'muslim', 'islam', 'arab', 'al-aqsa', 'palestinian muslims',

            # Symbols
            '🇵🇸', '☪️', '🕌', '🍉', '💧', '🔑', '💔',

            # Additional terms
            'ceasefire', 'ceasefire now', 'stop the war', 'gaza genocide',
            'gaza war', 'gaza crisis', 'gaza children', 'gaza civilians',
            'not antisemitic', 'silence is violence'
        }



        # Set plot style
        # plt.style.use('default')

    def compute_confidence(self, scores: List[float]) -> float:
        if len(scores) == 0:
            return 0.0
        if len(scores) == 1:
            return 1.0

        abs_mean = np.mean([abs(s) for s in scores])                  # Stronger = clearer stance
        high_conf_ratio = sum(1 for s in scores if abs(s) > 0.4) / len(scores)  # Clear stance % posts
        score_std = statistics.stdev(scores)

        # Weighted sum: tune weights as needed
        confidence = (
            0.5 * abs_mean +         # strong signals
            0.3 * high_conf_ratio +  # many confident posts
            0.2 * (1 - score_std)    # low variance is more confident
        )
        return round(min(max(confidence, 0.0), 1.0), 3)
        
    def calculate_keyword_score(self, features: Dict) -> float:
        text = features.get('text', '').lower()
        pro_israeli_found = [keyword for keyword in self.pro_israeli_keywords if keyword.lower() in text]
        pro_palestinian_found = [keyword for keyword in self.pro_palestinian_keywords if keyword.lower() in text]
        pro_israeli_count = len(pro_israeli_found)
        pro_palestinian_count = len(pro_palestinian_found)
        total = pro_israeli_count + pro_palestinian_count

        if total > 0:
            print(f"\n[Keyword Detection]")
            print(f"Text: {text}")
            if pro_israeli_found:
                print(f"  Pro-Israeli keywords detected: {pro_israeli_found}")
            if pro_palestinian_found:
                print(f"  Pro-Palestinian keywords detected: {pro_palestinian_found}")

        if total == 0:
            return 0.0

        score = (pro_israeli_count - pro_palestinian_count) / total
        return max(-1.0, min(1.0, score))


    def calculate_sentiment_score(self, features: Dict) -> float:
        text = features.get('text', '').lower().strip()
        if not text:
            return 0.0

        raw_sentiment = TextBlob(text).sentiment.polarity
        scaled_sentiment = np.tanh(2.5 * raw_sentiment)  # Nonlinear
        print(f"  Raw sentiment: {raw_sentiment:.3f} → Scaled: {scaled_sentiment:.3f}")

        # Keyword counts
        pro_israeli_count = sum(1 for kw in self.pro_israeli_keywords if kw in text)
        pro_palestinian_count = sum(1 for kw in self.pro_palestinian_keywords if kw in text)
        total_count = pro_israeli_count + pro_palestinian_count

        # Emojis and emotional triggers
        symbol_keywords = {"🕎", "🇮🇱", "🇵🇸", "✡️", "💔", "🙏🏼", "🕯️"}
        emotion_keywords = {"terrorist", "hostage", "massacre", "slaughter", "freedom", "genocide"}

        has_symbol = any(sym in text for sym in symbol_keywords)
        has_emotion = any(emo in text for emo in emotion_keywords)

        symbol_boost = 0.15 if has_symbol else 0.0
        emotion_boost = 0.25 if has_emotion else 0.0

        # No stance-related keywords, just return minimal effect from emotion/symbol if present
        if total_count == 0:
            # Treat it as neutral
            return 0.0

        # Contextual direction
        context_balance = (pro_israeli_count - pro_palestinian_count) / total_count

        # Adjusted score with boosts
        base_score = context_balance * (scaled_sentiment + symbol_boost + emotion_boost)

        # If sentiment is very close to zero, use fallback strength
        if abs(scaled_sentiment) < 0.1 and abs(base_score) < 0.2:
            base_score += context_balance * 0.25  # Inject directional bias from keyword ratio

        return max(-1.0, min(1.0, base_score))
            

    def analyze_stance(self, features: Dict) -> Tuple[str, float, Dict[str, float]]:
        """Analyze stance using keyword, sentiment classification."""

        # Individual scores
        keyword_score = self.calculate_keyword_score(features)
        sentiment_score = self.calculate_sentiment_score(features)

        # Combine all scores
        scores = {
            'keyword_ratio': keyword_score,
            'sentiment': sentiment_score
        }

        weights = self.weights
        raw_score = sum(scores[k] * weights.get(k, 0.0) for k in scores)
        final_score = max(-1.0, min(1.0, raw_score))

        # Label assignment
        if final_score > 0.2:
            stance = 'pro-Israeli'
        elif final_score < -0.2:
            stance = 'pro-Palestinian'
        else:
            stance = 'neutral/unclear'

        return stance, final_score, scores

    def analyze_user(self, posts_features: List[Dict]) -> Dict:
        """Analyze a user's overall stance based on multiple posts."""
        post_analyses = []
        stance_counts = Counter()

        for features in posts_features:
            stance, score, component_scores = self.analyze_stance(features)
            raw_text = features.get("text", "")
            highlighted = self.highlight_keywords(raw_text)

            post_analyses.append({
                'stance': stance,
                'score': score,
                'component_scores': component_scores,
                'text': raw_text,
                'highlighted_text': highlighted
            })
            stance_counts[stance] += 1

        total_posts = len(post_analyses)
        if total_posts == 0:
            return {
                'stance': 'unknown',
                'confidence': 0.0,
                'average_score': 0.0,
                'stance_distribution': {},
                'post_analyses': []
            }

        stance_distribution = {
            stance: round(count / total_posts, 3)
            for stance, count in stance_counts.items()
        }

        scores = [a['score'] for a in post_analyses]
        average_score = round(np.mean(scores), 3)

        confidence = self.compute_confidence(scores)

        if stance_counts['pro-Israeli'] > stance_counts['pro-Palestinian']:
            overall_stance = 'pro-Israeli'
        elif stance_counts['pro-Palestinian'] > stance_counts['pro-Israeli']:
            overall_stance = 'pro-Palestinian'
        else:
            overall_stance = 'neutral/unclear'

        return {
            'stance': overall_stance,
            'confidence': round(confidence, 3),
            'average_score': average_score,
            'stance_distribution': stance_distribution,
            'post_analyses': post_analyses
        }
        
    def highlight_keywords(self, text: str) -> str:
        """Highlight pro-Israeli and pro-Palestinian keywords in the post text."""
        def wrap_keywords(keywords, color):
            for kw in sorted(keywords, key=lambda x: -len(x)):  # longer first
                pattern = re.escape(kw)
                text_pattern = re.compile(rf"(?i)\b({pattern})\b")
                nonlocal text
                text = text_pattern.sub(
                    rf"<span style='color:{color}; font-weight:bold;'>\1</span>",
                    text
                )

        text = text.replace("\n", " ")
        wrap_keywords(self.pro_israeli_keywords, "#1f77b4")     # Blue
        wrap_keywords(self.pro_palestinian_keywords, "#ff7f0e")  # Orange
        return Markup(text)

    def visualize_results(self, results: Dict, output_file: Optional[str] = None) -> None:
        """Generate a pie chart of stance distribution only."""
        try:
            stance_dist = results.get('stance_distribution', {})
            if not stance_dist:
                logger.warning("No stance distribution available to visualize.")
                return

            # Prepare labels and values
            labels = list(stance_dist.keys())
            values = [v * 100 for v in stance_dist.values()]  # convert to percentage
            colors = [
                COLOR_PALETTE.get(label.lower().replace('/', '_').replace('-', '_'), '#999999')
                for label in labels
            ]

            # Create the pie chart
            plt.figure(figsize=(6, 6))
            plt.pie(
                values,
                labels=labels,
                colors=colors,
                autopct='%1.1f%%',
                startangle=140
            )
            plt.title("Stance Distribution")
            plt.axis('equal')  # Equal aspect ratio ensures the pie is a circle.

            # Save or display
            if output_file:
                Path(output_file).parent.mkdir(parents=True, exist_ok=True)
                plt.savefig(output_file, dpi=DPI, bbox_inches='tight')
                logger.info(f"Visualization saved to {output_file}")
            else:
                plt.show()

            plt.close()

        except Exception as e:
            logger.error(f"Error generating visualization: {str(e)}")
            raise


    def analyze_post(self, text: str) -> dict:
        """Analyze a single post (raw text) and return stance, confidence, and details."""
        features = {
            'text': text,
            'entities': {'hashtags': [], 'mentions': [], 'links': []},
            'metrics': {},
            'text_length': len(text)
        }
        stance, score, details = self.analyze_stance(features)
        # Confidence is 1 for a single post (no variance)
        return {
            'stance': stance,
            'confidence': 1.0,
            'score': score,
            'details': details
        }

if __name__ == "__main__":
    # Example usage
    analyzer = StanceAnalyzer()
    # Add example analysis code here if needed 