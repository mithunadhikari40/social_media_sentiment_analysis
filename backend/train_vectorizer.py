import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os

# Ensure the models directory exists
os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'models'), exist_ok=True)

# Load the sample tweets data
df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'sample_tweets.csv'))

# Initialize and fit the TF-IDF vectorizer
tfidf_vectorizer = TfidfVectorizer(
    max_features=5000,  # Limit the number of features to keep the model size manageable
    stop_words='english',
    ngram_range=(1, 2)  # Consider both unigrams and bigrams
)

# Fit the vectorizer on the text data
tfidf_vectorizer.fit(df['Text'].astype(str))

# Save the vectorizer
vectorizer_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'tfidf_vectorizer.pkl')
joblib.dump(tfidf_vectorizer, vectorizer_path)

print(f"TF-IDF vectorizer trained and saved to: {vectorizer_path}")
