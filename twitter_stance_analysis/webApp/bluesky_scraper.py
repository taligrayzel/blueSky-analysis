"""
Bluesky social media scraper for collecting posts and user data.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
import atproto
from atproto import Client
from config import (
    RAW_DATA_DIR, 
    POSTS_PER_USER, 
    MAX_RETRIES, 
    REQUEST_TIMEOUT,
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

class BlueskyScraper:
    """Scraper for collecting data from Bluesky social media platform."""
    
    def __init__(self):
        """Initialize the Bluesky scraper with API client."""
        self.client = Client()
        self._authenticate()
        
    def _authenticate(self) -> None:
        """Authenticate with Bluesky API."""
        try:
            # Try to authenticate with stored credentials
            if self._load_credentials():
                return
                
            # If no stored credentials, use guest authentication
            logger.info("Using guest authentication")
            self.client.login()
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise
            
    def _load_credentials(self) -> bool:
        """Load stored API credentials if available."""
        try:
            creds_file = Path('tokenskeys.env')
            if not creds_file.exists():
                return False
                
            with open(creds_file, 'r') as f:
                credentials = json.load(f)
                
            if 'bluesky_handle' in credentials and 'bluesky_app_password' in credentials:
                self.client.login(
                    credentials['bluesky_handle'],
                    credentials['bluesky_app_password']
                )
                logger.info("Successfully authenticated with stored credentials")
                return True
                
            return False
            
        except Exception as e:
            logger.warning(f"Error loading credentials: {str(e)}")
            return False
            
    def _extract_entities(self, record) -> Dict[str, List[str]]:
        """Extract entities (mentions, links, hashtags) from a post."""
        entities = {
            'mentions': [],
            'links': [],
            'hashtags': []
        }
        
        try:
            if not hasattr(record, 'facets') or record.facets is None:
                return entities
                
            for facet in record.facets:
                if not hasattr(facet, 'features') or facet.features is None:
                    continue
                    
                for feature in facet.features:
                    try:
                        if hasattr(feature, 'did'):  # Mention
                            entities['mentions'].append(feature.did)
                        elif hasattr(feature, 'uri'):  # Link
                            entities['links'].append(feature.uri)
                        elif hasattr(feature, 'tag'):  # Hashtag
                            entities['hashtags'].append(feature.tag)
                    except Exception as e:
                        logger.debug(f"Error processing entity feature: {str(e)}")
                        continue
        except Exception as e:
            logger.debug(f"Error extracting entities: {str(e)}")
        
        return entities
        
    def get_user_posts(self, handle: str, max_posts: int = POSTS_PER_USER) -> List[Dict]:
        """Get posts from a specific user."""
        try:
            logger.info(f"Fetching up to {max_posts} posts from @{handle}")
            posts = []
            seen_ids = set()  # Track unique post IDs
            
            # Get user profile first
            profile = self.client.get_profile(actor=handle)
            if not profile:
                logger.error(f"Could not find user @{handle}")
                return []

            # Get user's posts
            cursor = None
            retry_count = 0
            
            while len(posts) < max_posts and retry_count < MAX_RETRIES:
                try:
                    response = self.client.get_author_feed(
                        actor=handle,
                        limit=min(100, max_posts - len(posts)),
                        cursor=cursor
                    )
                    
                    if not response or not hasattr(response, 'feed'):
                        logger.error("Invalid response from API")
                        break
                        
                    if not response.feed:
                        break
                        
                    for feed_view in response.feed:
                        if not hasattr(feed_view, 'post'):
                            continue
                            
                        post = feed_view.post
                        if not hasattr(post, 'record'):
                            continue
                            
                        # Skip if we've already seen this post
                        if post.uri in seen_ids:
                            logger.debug(f"Skipping duplicate post {post.uri}")
                            continue
                            
                        try:
                            # Get basic post data
                            post_data = {
                                'id': post.uri,
                                'text': post.record.text,
                                'created_at': post.record.created_at,
                                'metrics': {
                                    'repost_count': getattr(post, 'repost_count', 0),
                                    'like_count': getattr(post, 'like_count', 0),
                                    'reply_count': getattr(post, 'reply_count', 0)
                                }
                            }
                            
                            # Add entities if available
                            if hasattr(post.record, 'facets'):
                                post_data['entities'] = self._extract_entities(post.record)
                            else:
                                post_data['entities'] = {'mentions': [], 'links': [], 'hashtags': []}
                                
                            posts.append(post_data)
                            seen_ids.add(post.uri)
                            logger.debug(f"Successfully processed post {post.uri}")
                            
                        except Exception as e:
                            logger.warning(f"Error processing post {post.uri}: {str(e)}")
                            continue
                    
                    if not response.cursor:
                        break
                    cursor = response.cursor
                    
                    # Reset retry count on successful request
                    retry_count = 0
                    
                except Exception as e:
                    retry_count += 1
                    logger.warning(f"Error fetching posts (attempt {retry_count}/{MAX_RETRIES}): {str(e)}")
                    time.sleep(REQUEST_TIMEOUT)  # Wait before retrying
                    
            logger.info(f"Retrieved {len(posts)} unique posts from @{handle}")
            return posts

        except Exception as e:
            logger.error(f"Error fetching posts: {str(e)}")
            return []
            
    def save_posts(self, posts: List[Dict], handle: str) -> None:
        """Save collected posts to a JSON file."""
        try:
            output_file = RAW_DATA_DIR / f'{handle.replace(".", "_")}_posts.json'
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Saved {len(posts)} posts to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving posts: {str(e)}")
            
    def get_user_info(self, handle: str) -> Optional[Dict]:
        """Get basic information about a user."""
        try:
            profile = self.client.get_profile(actor=handle)
            if not profile:
                return None
                
            return {
                'handle': handle,
                'display_name': getattr(profile, 'display_name', ''),
                'description': getattr(profile, 'description', ''),
                'followers_count': getattr(profile, 'followers_count', 0),
                'following_count': getattr(profile, 'following_count', 0),
                'posts_count': getattr(profile, 'posts_count', 0)
            }
            
        except Exception as e:
            logger.error(f"Error fetching user info: {str(e)}")
            return None 