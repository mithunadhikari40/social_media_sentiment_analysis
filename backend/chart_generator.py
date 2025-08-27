import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from wordcloud import WordCloud
import io
import base64
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.dates as mdates
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style for better looking charts
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def create_sentiment_distribution_chart(sentiment_data):
    """Create pie chart for sentiment distribution"""
    if not sentiment_data:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    labels = [item['sentiment'].capitalize() for item in sentiment_data]
    sizes = [item['count'] for item in sentiment_data]
    colors = ['#2ecc71', '#e74c3c', '#95a5a6']  # Green, Red, Gray
    
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                     startangle=90, textprops={'fontsize': 12})
    
    # Enhance the appearance
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    ax.set_title('Sentiment Distribution', fontsize=16, fontweight='bold', pad=20)
    
    # Save to bytes
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer

def create_model_accuracy_chart(model_comparison):
    """Create bar chart for model accuracy comparison"""
    if not model_comparison:
        return None
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    models = [model.upper().replace('_', ' ') for model in model_comparison.keys()]
    accuracies = list(model_comparison.values())
    
    colors = ['#3498db', '#e74c3c', '#f39c12']
    bars = ax.bar(models, accuracies, color=colors, alpha=0.8, edgecolor='black', linewidth=1.2)
    
    # Add value labels on bars
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{acc:.3f}', ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    ax.set_ylabel('Accuracy Score', fontsize=14, fontweight='bold')
    ax.set_title('Model Accuracy Comparison', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylim(0, max(accuracies) * 1.2)
    ax.grid(axis='y', alpha=0.3)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer

def create_sentiment_by_model_chart(sentiment_counts):
    """Create grouped bar chart for sentiment counts by model"""
    if not sentiment_counts:
        return None
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Prepare data
    models = list(sentiment_counts.keys())
    sentiments = ['positive', 'negative', 'neutral']
    
    x = np.arange(len(models))
    width = 0.25
    
    colors = {'positive': '#2ecc71', 'negative': '#e74c3c', 'neutral': '#95a5a6'}
    
    for i, sentiment in enumerate(sentiments):
        counts = []
        for model in models:
            model_data = sentiment_counts[model]
            count = next((item['count'] for item in model_data if item['sentiment'] == sentiment), 0)
            counts.append(count)
        
        ax.bar(x + i * width, counts, width, label=sentiment.capitalize(), 
               color=colors[sentiment], alpha=0.8, edgecolor='black', linewidth=0.8)
    
    ax.set_xlabel('Models', fontsize=14, fontweight='bold')
    ax.set_ylabel('Count', fontsize=14, fontweight='bold')
    ax.set_title('Sentiment Count by Model', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x + width)
    ax.set_xticklabels([model.upper().replace('_', ' ') for model in models])
    ax.legend(fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer

def create_time_series_chart(time_series_data):
    """Create line chart for sentiment trends over time"""
    if not time_series_data:
        return None
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Prepare data
    dates = []
    positive_counts = []
    negative_counts = []
    neutral_counts = []
    
    for day_data in time_series_data:
        try:
            date_str = day_data.get('date', '')
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            dates.append(date_obj)
        except:
            continue
            
        positive_counts.append(day_data.get('positive', 0))
        negative_counts.append(day_data.get('negative', 0))
        neutral_counts.append(day_data.get('neutral', 0))
    
    if not dates:
        return None
    
    # Plot lines
    ax.plot(dates, positive_counts, marker='o', linewidth=2.5, label='Positive', color='#2ecc71', markersize=6)
    ax.plot(dates, negative_counts, marker='s', linewidth=2.5, label='Negative', color='#e74c3c', markersize=6)
    ax.plot(dates, neutral_counts, marker='^', linewidth=2.5, label='Neutral', color='#95a5a6', markersize=6)
    
    ax.set_xlabel('Date', fontsize=14, fontweight='bold')
    ax.set_ylabel('Number of Posts', fontsize=14, fontweight='bold')
    ax.set_title('Sentiment Trends Over Time', fontsize=16, fontweight='bold', pad=20)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer

def create_wordcloud_image(words_list, sentiment_type):
    """Create word cloud image from list of words"""
    if not words_list:
        return None
    
    # Join words or use the list directly
    if isinstance(words_list, list):
        text = ' '.join(words_list)
    else:
        text = str(words_list)
    
    if not text.strip():
        return None
    
    # Color schemes for different sentiments
    color_schemes = {
        'positive': ['#2ecc71', '#27ae60', '#58d68d', '#82e0aa'],
        'negative': ['#e74c3c', '#c0392b', '#ec7063', '#f1948a'],
        'neutral': ['#95a5a6', '#7f8c8d', '#bdc3c7', '#d5dbdb']
    }
    
    colors = color_schemes.get(sentiment_type.lower(), color_schemes['neutral'])
    
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        colormap=plt.cm.Set2,
        max_words=50,
        relative_scaling=0.5,
        random_state=42
    ).generate(text)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(f'{sentiment_type.capitalize()} Sentiment Word Cloud', 
                fontsize=16, fontweight='bold', pad=20)
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer

def create_confusion_matrix_chart(confusion_matrix, model_name):
    """Create heatmap for confusion matrix"""
    if not confusion_matrix:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Convert to numpy array if needed
    if isinstance(confusion_matrix, list):
        cm = np.array(confusion_matrix)
    else:
        cm = confusion_matrix
    
    # Labels
    labels = ['Negative', 'Neutral', 'Positive']
    
    # Create heatmap
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=labels, yticklabels=labels,
                cbar_kws={'label': 'Count'}, ax=ax,
                annot_kws={'size': 14, 'weight': 'bold'})
    
    ax.set_xlabel('Predicted Label', fontsize=14, fontweight='bold')
    ax.set_ylabel('True Label', fontsize=14, fontweight='bold')
    ax.set_title(f'{model_name.upper().replace("_", " ")} Confusion Matrix', 
                fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer

def create_model_metrics_chart(model_metrics):
    """Create grouped bar chart for detailed model metrics"""
    if not model_metrics:
        return None
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    models = list(model_metrics.keys())
    metrics = ['accuracy', 'precision', 'recall', 'f1_score']
    metric_labels = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
    
    x = np.arange(len(models))
    width = 0.2
    
    colors = ['#3498db', '#e74c3c', '#f39c12', '#9b59b6']
    
    for i, (metric, label) in enumerate(zip(metrics, metric_labels)):
        values = []
        for model in models:
            value = model_metrics[model].get(metric, 0)
            values.append(value)
        
        bars = ax.bar(x + i * width, values, width, label=label, 
                     color=colors[i], alpha=0.8, edgecolor='black', linewidth=0.8)
        
        # Add value labels on bars
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{val:.3f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    ax.set_xlabel('Models', fontsize=14, fontweight='bold')
    ax.set_ylabel('Score', fontsize=14, fontweight='bold')
    ax.set_title('Detailed Model Performance Metrics', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels([model.upper().replace('_', ' ') for model in models])
    ax.legend(fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 1.1)
    
    plt.tight_layout()
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer
