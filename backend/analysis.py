import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

# Ensure NLTK data is available
nltk.download('stopwords')
nltk.download('wordnet')

# --- Paths to Pre-trained Models and Vectorizer ---
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
PLOTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'plots')

NB_MODEL_PATH = os.path.join(MODELS_DIR, 'naive_bayes_model.pkl')
SVM_MODEL_PATH = os.path.join(MODELS_DIR, 'svm_model.pkl')
BERT_MODEL_PATH = os.path.join(MODELS_DIR, 'bert_model.pth')
VECTORIZER_PATH = os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl')

# --- Load Models and Vectorizer ---
nb_model = joblib.load(NB_MODEL_PATH)
svm_model = joblib.load(SVM_MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

# Load BERT model and tokenizer
bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert_model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=3)
bert_model.load_state_dict(torch.load(BERT_MODEL_PATH, map_location=torch.device('cpu')))
bert_model.eval()

# --- Text Preprocessing ---
def clean_text(text):
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove non-alphabetic characters
    text = text.lower()  # Convert to lowercase
    words = text.split()
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    return ' '.join(words)

# --- Prediction Functions ---
def predict_sentiment_nb_svm(text, model):
    cleaned_text = clean_text(text)
    vectorized_text = vectorizer.transform([cleaned_text])
    prediction = model.predict(vectorized_text)
    return prediction[0]

def predict_sentiment_bert(text):
    cleaned_text = clean_text(text)
    inputs = bert_tokenizer(cleaned_text, return_tensors='pt', truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = bert_model(**inputs)
    prediction = torch.argmax(outputs.logits, dim=1).item()
    sentiment_map = {0: 'negative', 1: 'neutral', 2: 'positive'}
    return sentiment_map[prediction]

# --- Main Analysis Function ---
def run_analysis(df: pd.DataFrame):
    df['cleaned_text'] = df['text'].apply(clean_text)
    
    # Get predictions
    df['nb_sentiment'] = df['text'].apply(lambda x: predict_sentiment_nb_svm(x, nb_model))
    df['svm_sentiment'] = df['text'].apply(lambda x: predict_sentiment_nb_svm(x, svm_model))
    df['bert_sentiment'] = df['text'].apply(predict_sentiment_bert)
    
    return df

# --- Visualization Functions ---
def generate_wordcloud(df: pd.DataFrame, sentiment: str):
    if not os.path.exists(PLOTS_DIR):
        os.makedirs(PLOTS_DIR)

    text = ' '.join(df[df['bert_sentiment'] == sentiment]['cleaned_text'])
    if not text:
        return None

    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    
    file_path = os.path.join(PLOTS_DIR, f'wordcloud_{sentiment}.png')
    plt.savefig(file_path)
    plt.close()
    return file_path
