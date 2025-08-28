import tweepy
import pandas as pd
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from typing import List, Dict, Any
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Download required NLTK data
try:
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('punkt', quiet=True)
except Exception as e:
    print(f"Warning: Could not download NLTK data: {e}")

logger = logging.getLogger(__name__)

class TwitterClient:
    def __init__(self):
        """Initialize Twitter API client with Bearer Token"""
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        if not self.bearer_token:
            raise ValueError("TWITTER_BEARER_TOKEN not found in environment variables")
        
        # Initialize Tweepy client with Bearer Token
        self.client = tweepy.Client(bearer_token=self.bearer_token)
        
        # Initialize text preprocessing tools
        self.lemmatizer = WordNetLemmatizer()
        try:
            self.stop_words = set(stopwords.words('english'))
        except Exception as e:
            print(f"Warning: Could not load stopwords, using basic set: {e}")
            # Basic stopwords if NLTK fails
            self.stop_words = {
                'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
                'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
                'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
                'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
                'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
                'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
                'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after',
                'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
                'further', 'then', 'once'
            }
    
    def search_tweets(self, query: str, max_results: int = 100) -> pd.DataFrame:
        """
        Search for tweets based on a query and return as DataFrame
        
        Args:
            query: Search query for tweets
            max_results: Maximum number of tweets to fetch (10-100)
            
        Returns:
            DataFrame with columns: text, created_at, author_id, public_metrics
        """
        try:
            # Ensure max_results is within Twitter API limits
            max_results = min(max(max_results, 10), 100)
            
            # Search for tweets
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'lang'],
                expansions=['author_id'],
                user_fields=['username', 'name']
            )
            
            if not tweets.data:
                logger.warning(f"No tweets found for query: {query}")
                return pd.DataFrame(columns=['text', 'created_at', 'author_id', 'username'])
            
            # Convert tweets to list of dictionaries
            tweet_data = []
            users_dict = {}
            
            # Create users dictionary if users data is available
            if tweets.includes and 'users' in tweets.includes:
                users_dict = {user.id: user.username for user in tweets.includes['users']}
            
            for tweet in tweets.data:
                # Skip non-English tweets to improve analysis quality
                if hasattr(tweet, 'lang') and tweet.lang != 'en':
                    continue
                    
                tweet_info = {
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'author_id': tweet.author_id,
                    'username': users_dict.get(tweet.author_id, 'unknown'),
                    'retweet_count': tweet.public_metrics['retweet_count'] if tweet.public_metrics else 0,
                    'like_count': tweet.public_metrics['like_count'] if tweet.public_metrics else 0,
                    'reply_count': tweet.public_metrics['reply_count'] if tweet.public_metrics else 0
                }
                tweet_data.append(tweet_info)
            
            if not tweet_data:
                logger.warning(f"No English tweets found for query: {query}")
                return pd.DataFrame(columns=['text', 'created_at', 'author_id', 'username'])
            
            df = pd.DataFrame(tweet_data)
            logger.info(f"Successfully fetched {len(df)} tweets for query: {query}")
            return df
            
        except tweepy.TooManyRequests:
            logger.error("Twitter API rate limit exceeded")
            raise Exception("Twitter API rate limit exceeded. Please try again later.")
        except tweepy.Unauthorized:
            logger.error("Twitter API unauthorized - check bearer token")
            raise Exception("Twitter API authentication failed. Please check your bearer token.")
        except tweepy.NotFound:
            logger.error("Twitter API endpoint not found")
            raise Exception("Twitter API endpoint not found.")
        except Exception as e:
            logger.error(f"Error fetching tweets: {str(e)}")
            raise Exception(f"Failed to fetch tweets from Twitter API: {str(e)}")
    
    def clean_tweet_text(self, text: str) -> str:
        """
        Clean tweet text by removing URLs, mentions, hashtags, and stop words for better analysis
        
        Args:
            text: Raw tweet text
            
        Returns:
            Cleaned and processed tweet text
        """
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove user mentions
        text = re.sub(r'@\w+', '', text)
        
        # Remove hashtags (keep the text, remove the #)
        text = re.sub(r'#(\w+)', r'\1', text)
        
        # Remove non-alphabetic characters except spaces
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Split into words
        words = text.split()
        
        # Remove stop words and lemmatize
        try:
            processed_words = []
            for word in words:
                if word not in self.stop_words and len(word) > 2:  # Also filter very short words
                    lemmatized_word = self.lemmatizer.lemmatize(word)
                    processed_words.append(lemmatized_word)
            
            # Join processed words
            cleaned_text = ' '.join(processed_words)
        except Exception as e:
            print(f"Warning: Error in text processing, using basic cleaning: {e}")
            # Fallback to basic cleaning if lemmatization fails
            cleaned_text = ' '.join([word for word in words if word not in self.stop_words and len(word) > 2])
        
        return cleaned_text.strip()
    
    def preprocess_tweets_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess tweets DataFrame for sentiment analysis
        
        Args:
            df: DataFrame with tweet data
            
        Returns:
            Preprocessed DataFrame with cleaned text
        """
        if df.empty:
            return df
        
        # Clean tweet text
        df['original_text'] = df['text'].copy()
        df['text'] = df['text'].apply(self.clean_tweet_text)
        
        # Remove empty tweets after cleaning
        df = df[df['text'].str.strip() != ''].copy()
        
        # Add timestamp column if not present
        if 'timestamp' not in df.columns and 'created_at' in df.columns:
            df['timestamp'] = df['created_at']
        
        return df.reset_index(drop=True)

def get_twitter_client() -> TwitterClient:
    """Factory function to get Twitter client instance"""
    return TwitterClient()
