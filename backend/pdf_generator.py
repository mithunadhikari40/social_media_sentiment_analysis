import os
import pandas as pd
import base64
import io
import math
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, 
    Table, TableStyle, PageBreak, ListFlowable, ListItem
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
import pandas as pand
from transformers import pipeline

sentiment_pipeline = pipeline("sentiment-analysis")
# --- PDF Generation ---
heading_style = ParagraphStyle(name='Heading1', fontSize=16, alignment=TA_LEFT, spaceAfter=10, spaceBefore=10)



# --- Function to calculate sentiment ---
def calculate_sentiment(text):
    """Calculate sentiment of a single tweet using Hugging Face pipeline."""


    if pand.isna(text):
        return "neutral"
    result = sentiment_pipeline(str(text)[:512])[0]  # Limit text to 512 tokens
    return result['label'].lower()

def calculate_sentiment_with_confidence(text):
    """Calculate sentiment and confidence score of a single tweet using Hugging Face pipeline."""
    if pand.isna(text) or not str(text).strip():
        return 0.0

    # Hugging Face returns something like: [{'label': 'NEGATIVE', 'score': 0.998}]
    result = sentiment_pipeline(str(text)[:512])[0]  # truncate text if too long
    confidence = float(result['score'])

    return confidence

def get_dominant_sentiment(sentiment_dist):
    """Return capitalized dominant sentiment or 'N/A' if not available.
       Accepts either:
         - dict: {'negative': 10, 'positive': 5}  (values can be counts or percentages)
         - list of dicts: [{'sentiment':'negative','count':10,'percentage':66.67}, ...]
    """
    if not sentiment_dist:
        return 'N/A'

    # Case 1: dict mapping sentiment -> value
    if isinstance(sentiment_dist, dict):
        # pick the sentiment with the largest value
        return max(sentiment_dist.items(), key=lambda x: x[1])[0].capitalize()

    # Case 2: list of dicts as in your example
    if isinstance(sentiment_dist, list):
        # choose by 'count' first, fallback to 'percentage'
        best = max(sentiment_dist, key=lambda d: d.get('count', d.get('percentage', 0)))
        return best.get('sentiment', 'N/A').capitalize()

    # fallback
    return 'N/A'


def color_to_hex_nopound(c):
    """
    Return a hex color string WITHOUT the leading '#' (e.g. 'ffc107'),
    accepts:
      - reportlab.lib.colors.Color objects (has .red/.green/.blue floats 0..1)
      - tuples/lists of floats (r,g,b) in 0..1
      - hex strings ('#ffc107' or 'ffc107') or color names (will return as-is sans '#')
    """
    # If it's already a string (hex or name) -> strip leading '#'
    if isinstance(c, str):
        return c.lstrip('#')

    # reportlab Color may have hexval() — prefer that if available
    hv = getattr(c, 'hexval', None)
    if callable(hv):
        return hv().lstrip('#')

    # Try .red/.green/.blue attributes (reportlab Color)
    r = getattr(c, 'red', None)
    if r is not None:
        g = getattr(c, 'green')
        b = getattr(c, 'blue')
    else:
        # maybe a tuple/list of floats
        try:
            r, g, b = c[0], c[1], c[2]
        except Exception:
            raise ValueError("Unsupported color object; can't derive RGB")

    return '{:02x}{:02x}{:02x}'.format(int(r * 255), int(g * 255), int(b * 255))




def create_pdf_report(df: pd.DataFrame, wordcloud_paths: dict, output_path: str):
    """
    Generates a PDF report summarizing the sentiment analysis results.
    """
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))

    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(name='Title', fontSize=24, alignment=TA_CENTER, spaceAfter=20)
    body_style = styles['BodyText']

    story = []

    # --- Title ---
    story.append(Paragraph("Sentiment Analysis Report", title_style))
    story.append(Spacer(1, 24))

    # --- Summary ---
    story.append(Paragraph("Analysis Summary", heading_style))
    num_tweets = len(df)
    summary_text = f"This report summarizes the sentiment analysis performed on {num_tweets} text entries. The analysis was conducted using three different models: Naive Bayes, SVM, and BERT."
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 12))

    # --- Sentiment Distribution Tables ---
    story.append(Paragraph("Sentiment Distribution by Model", heading_style))
    
    for model_name in ['nb_sentiment', 'svm_sentiment', 'bert_sentiment']:
        model_title = model_name.split('_')[0].upper()
        story.append(Paragraph(f"<b>{model_title} Model:</b>", body_style))
        
        sentiment_counts = df[model_name].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        
        table_data = [sentiment_counts.columns.tolist()] + sentiment_counts.values.tolist()
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 24))

    # --- Word Clouds ---
    story.append(Paragraph("Word Clouds by Sentiment (BERT)", heading_style))
    
    for sentiment, path in wordcloud_paths.items():
        if path and os.path.exists(path):
            story.append(Paragraph(f"<b>{sentiment.capitalize()} Sentiment:</b>", body_style))
            img = Image(path, width=400, height=200)
            story.append(img)
            story.append(Spacer(1, 12))

    # --- Build PDF ---
    doc.build(story)

def create_base64_image(base64_string: str, width: float = 5*inch, height: float = 3*inch):
    """
    Convert base64 string to ReportLab Image object.
    """
    try:
        # Remove data URL prefix if present
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        
        image_data = base64.b64decode(base64_string)
        image_buffer = io.BytesIO(image_data)
        img = Image(image_buffer, width=width, height=height)
        return img
    except Exception as e:
        print(f"Error creating image from base64: {e}")
        return None

def create_analysis_pdf_report(analysis_data: dict, output_path: str):
    """
    Generates a comprehensive PDF report from analysis response data.
    
    Args:
        analysis_data: Dictionary containing analysis results
        output_path: Path where the PDF will be saved
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    
    # Initialize document with metadata
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        title="Social Media Sentiment Analysis Report",
        author="Sentiment Analysis System",
        leftMargin=1*cm,
        rightMargin=1*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'Title', 
        parent=styles['Heading1'],
        fontSize=20,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor('#2c3e50')
    )
    
    heading1_style = ParagraphStyle(
        'Heading1',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=20,
        textColor=colors.HexColor('#3498db'),
        borderBottomWidth=1,
        borderColor=colors.HexColor('#bdc3c7'),
        borderPadding=5
    )
    
    heading2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading3'],
        fontSize=14,
        spaceBefore=15,
        textColor=colors.HexColor('#2c3e50'),
        leftIndent=10
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    highlight_style = ParagraphStyle(
        'Highlight',
        parent=body_style,
        backColor=colors.HexColor('#f8f9fa'),
        borderWidth=1,
        borderColor=colors.HexColor('#e9ecef'),
        borderPadding=10,
        spaceBefore=10,
        spaceAfter=10
    )
    
    footer_style = ParagraphStyle(
        'Footer',
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#7f8c8d'),
        spaceBefore=20
    )

    story = []

    # --- Title Page ---
    story.append(Paragraph("Social Media Sentiment Analysis Report", title_style))
    story.append(Paragraph("Comprehensive Analysis Report", ParagraphStyle('Subtitle', parent=title_style, fontSize=14)))
    story.append(Spacer(1, 40))

    print(f"Analysis data: {analysis_data}")
    
    # Add metadata table
    metadata = [
        ["Analysis Date", analysis_data.get('createdAt', 'N/A')],
        ["Search Query", analysis_data.get('query', 'N/A')],
        ["Total Documents", len(analysis_data.get('rawData', []))],
        ["Analysis Duration", analysis_data.get('analysisDuration', 'N/A')],
        ["Language", analysis_data.get('language', 'English')],
    ]
    
    metadata_table = Table(metadata, colWidths=[150, 350])
    metadata_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e9ecef')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#495057')),
        ('FONTWEIGHT', (0, 0), (0, -1), 'BOLD'),
    ]))
    
    story.append(metadata_table)
    story.append(PageBreak())

    # --- Sentiment Distribution ---
    story.append(Paragraph("1. Sentiment Analysis Overview", heading_style))
    sentiment_dist = analysis_data.get('sentimentDistribution', [])
    print(f"sentiment dist: {sentiment_dist}")

    
    if sentiment_dist:
        # Sort by count descending
        sorted_dist = sorted(
            sentiment_dist, 
            key=lambda x: x.get('count', 0), 
            reverse=True
        )
        
        # Calculate total count for percentages
        print(f"sorted_dist is {sorted_dist}")
        total_count = sum(item.get('count', 0) for item in sorted_dist)
        
        # Create detailed table with visualization
        table_data = [
            ['Sentiment', 'Count', 'Percentage', 'Distribution']
        ]
        
        # Find max count for visual scaling
        max_count = max(item.get('count', 0) for item in sorted_dist) or 1
        
        for item in sorted_dist:
            print(f"item is {item}")

            count = item.get('count', 0)
            percentage = (count / total_count * 100) if total_count > 0 else 0
            sentiment = item.get('sentiment', 'Unknown').capitalize()
            
            # Create visual bar representation
            bar_width = int((count / max_count) * 30)  # 30 chars max width
            visual_bar = f"{'█' * bar_width} {count} ({percentage:.1f}%)"
            
            table_data.append([
                sentiment,
                str(count),
                f"{percentage:.1f}%",
                visual_bar
            ])
        
        # Create and style the table
        table = Table(table_data, colWidths=[100, 70, 80, 200], repeatRows=1)
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e9ecef')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (2, -1), 'CENTER'),
            ('FONTNAME', (3, 1), (3, -1), 'Courier'),  # Monospace for the bar
            ('FONTSIZE', (3, 1), (3, -1), 8),
        ]))
        
        # Add color coding to sentiment cells
        for i, item in enumerate(sorted_dist, 1):
            sentiment = item.get('sentiment', '').lower()
            if sentiment == 'positive':
                color = colors.HexColor('#d4edda')  # Light green
            elif sentiment == 'negative':
                color = colors.HexColor('#f8d7da')  # Light red
            else:
                color = colors.HexColor('#fff3cd')  # Light yellow
                
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, i), (0, i), color),
            ]))
        
        story.append(table)
        
        # Add summary insights
        dominant_sentiment = sorted_dist[0].get('sentiment', 'N/A').capitalize()
        dominant_percent = (sorted_dist[0].get('count', 0) / total_count * 100) if total_count > 0 else 0
        
        insights = [
            f"• Dominant sentiment is <b>{dominant_sentiment}</b> ({dominant_percent:.1f}% of total)",
            f"• Analyzed a total of <b>{total_count}</b> documents",
        ]
        
        if len(sorted_dist) > 1:
            sentiment_ratio = (sorted_dist[0].get('count', 0) / sorted_dist[1].get('count', 1)) if sorted_dist[1].get('count', 0) > 0 else 0
            insights.append(
                f"• <b>{dominant_sentiment}</b> sentiment is {sentiment_ratio:.1f}x more common than {sorted_dist[1].get('sentiment', 'the next').capitalize()}"
            )
        
        story.append(Spacer(1, 12))
        story.append(Paragraph("Key Insights:", ParagraphStyle('Heading2', parent=heading2_style, spaceBefore=10)))
        
        for insight in insights:
            story.append(Paragraph(insight, body_style))
        
        story.append(Spacer(1, 24))

    # --- Model Comparison ---
    story.append(Paragraph("2. Model Performance Analysis", heading_style))
    
    # Add introductory text
    story.append(Paragraph(
        "The following section compares the performance of different machine learning models "
        "used in the sentiment analysis. Each model was evaluated using standard metrics "
        "to ensure reliable and accurate sentiment classification.", 
        body_style
    ))
    story.append(Spacer(1, 12))
    
    model_metrics = analysis_data.get('modelMetrics', {})
    model_comparison = analysis_data.get('modelComparison', {})
    
    if model_metrics or model_comparison:
        # Create detailed metrics table
        table_data = [
            ['Model', 'Accuracy', 'Precision', 'Recall', 'F1-Score', 'Support']
        ]
        
        # Get metrics for each model
        for model_name, metrics in model_metrics.items():
            print(f"Model: {model_name} and metrics: {metrics}")
            table_data.append([
                model_name.upper(),
                f"{metrics.get('accuracy', 0):.3f}",
                f"{metrics.get('precision', 0):.3f}",
                f"{metrics.get('recall',  0):.3f}",
                f"{metrics.get('f1_score', 0):.3f}",
                str(metrics.get('support', 0))
            ])
        
        # If we have comparison data but no detailed metrics
        if not model_metrics and model_comparison:
            for model_name, accuracy in model_comparison.items():
                table_data.append([
                    model_name.upper(),
                    f"{accuracy:.3f}",
                    'N/A', 'N/A', 'N/A', 'N/A'
                ])
        
        # Create and style the table
        col_widths = [100, 70, 70, 70, 70, 70]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Define conditional formatting
        def get_highlight_color(value: float) -> colors.Color:
            if value >= 0.8:
                return colors.HexColor('#d4edda')  # Green
            elif value >= 0.6:
                return colors.HexColor('#fff3cd')  # Yellow
            return colors.HexColor('#f8d7da')  # Red
        
        # Apply styles
        style = [
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e9ecef')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]
        
        # Add conditional formatting for metric values
        for row in range(1, len(table_data)):
            for col in range(1, 5):  # Only for metric columns
                try:
                    value = float(table_data[row][col])
                    bg_color = get_highlight_color(value)
                    style.append(('BACKGROUND', (col, row), (col, row), bg_color))
                except (ValueError, IndexError):
                    pass
        
        table.setStyle(TableStyle(style))
        story.append(table)
        
        # Add model comparison insights
        if len(table_data) > 1:  # If we have model data
            # Find best performing model
            models = []
            for row in table_data[1:]:
                try:
                    models.append({
                        'name': row[0],
                        'accuracy': float(row[1]),
                        'f1': float(row[4])
                    })
                except (ValueError, IndexError):
                    continue
            
            if models:
                best_model = max(models, key=lambda x: (x['accuracy'], x['f1']))
                worst_model = min(models, key=lambda x: (x['accuracy'], x['f1']))
                
                insights = [
                    f"• <b>{best_model['name']}</b> achieved the highest accuracy ({best_model['accuracy']:.3f}) "
                    f"and F1-score ({best_model['f1']:.3f}) among all models.",
                    f"• The performance gap between the best and worst model is "
                    f"{(best_model['accuracy'] - worst_model['accuracy']):.3f} in accuracy."
                ]
                
                # Add specific insights based on model types
                if any('BERT' in m['name'] for m in models) and len(models) > 1:
                    bert_model = next((m for m in models if 'BERT' in m['name']), None)
                    if bert_model and bert_model['accuracy'] > 0.8:
                        insights.append(
                            "• The BERT-based model shows strong performance, likely due to its "
                            "ability to understand context and nuances in text."
                        )
                
                story.append(Spacer(1, 12))
                story.append(Paragraph("Key Insights:", ParagraphStyle(
                    'Heading2', 
                    parent=heading2_style, 
                    spaceBefore=10
                )))
                
                for insight in insights:
                    story.append(Paragraph(insight, body_style))
        
        story.append(Spacer(1, 24))

    # --- Key Insights & Recommendations ---
    story.append(Paragraph("3. Insights & Recommendations", heading_style))
    
    # Get all available data for analysis
    sentiment_dist = analysis_data.get('sentimentDistribution', [])
    model_metrics = analysis_data.get('modelMetrics', {})
    raw_data = analysis_data.get('rawData', [])
    
    # Calculate basic statistics
    total_posts = len(raw_data)
    positive_count = next((item.get('count', 0) for item in sentiment_dist 
                         if item.get('sentiment', '').lower() == 'positive'), 0)
    negative_count = next((item.get('count', 0) for item in sentiment_dist 
                         if item.get('sentiment', '').lower() == 'negative'), 0)
    neutral_count = total_posts - positive_count - negative_count

    print(f"positive_count: {positive_count}")
    print(f"negative_count: {neutral_count}")
    print(f"neutral_count: {neutral_count}")

    # Generate insights
    insights = []
    
    # Sentiment insights
    if sentiment_dist:
        print(f"sentiment_dist2: {sentiment_dist}")

        dominant_sentiment = max(sentiment_dist, key=lambda x: x.get('count', 0))
        dominant_percent = (dominant_sentiment.get('count', 0) / total_posts * 100) if total_posts > 0 else 0
        
        sentiment_insight = (
            f"The overall sentiment is predominantly <b>{dominant_sentiment.get('sentiment', 'neutral').capitalize()}</b> "
            f"({dominant_percent:.1f}% of all posts)."
        )
        insights.append(sentiment_insight)
        
        if dominant_sentiment['sentiment'].lower() == 'positive':
            insights.append(
                "The positive sentiment suggests that the general perception is favorable. "
                "This could indicate successful engagement or positive reception."
            )
        elif dominant_sentiment['sentiment'].lower() == 'negative':
            insights.append(
                "The negative sentiment highlights areas of concern that may require attention. "
                "Consider analyzing the negative posts for common themes or issues."
            )
    
    # Model performance insights
    if model_metrics:
        best_model = max(model_metrics.items(), 
                        key=lambda x: x[1].get('accuracy', 0))
        
        if best_model[1].get('accuracy', 0) > 0.8:
            model_insight = (
                f"The <b>{best_model[0].upper()}</b> model performed exceptionally well with an accuracy of "
                f"{best_model[1].get('accuracy', 0):.1%}. This high level of accuracy ensures reliable "
                "sentiment classification."
            )
        else:
            model_insight = (
                f"The <b>{best_model[0].upper()}</b> model showed the best performance with an accuracy of "
                f"{best_model[1].get('accuracy', 0):.1%}. Consider reviewing the model training data "
                "or exploring more advanced models if higher accuracy is required."
            )
        insights.append(model_insight)
    
    # Add any custom insights from the analysis
    custom_insights = analysis_data.get('insights', {})
    for key, value in custom_insights.items():
        if isinstance(value, (str, int, float)):
            insights.append(f"<b>{key.replace('_', ' ').title()}:</b> {value}")
    
    # Add recommendations
    recommendations = [
        "<b>Recommendations:</b>",
        "• Monitor sentiment trends over time to identify any significant shifts.",
        "• Investigate the context of neutral posts, as they may contain valuable qualitative feedback.",
        "• Consider implementing automated alerts for sudden changes in sentiment patterns.",
        "• Regularly update and retrain models with new data to maintain accuracy."
    ]
    
    # Add all insights to the document
    if insights:
        story.append(Paragraph("Key Findings:", heading2_style))
        for insight in insights:
            story.append(Paragraph(f"• {insight}", body_style))
        story.append(Spacer(1, 12))
    
    # Add recommendations
    story.append(Paragraph("Strategic Recommendations:", heading2_style))
    for rec in recommendations:
        story.append(Paragraph(rec, body_style))
    
    story.append(Spacer(1, 24))

    # --- Detailed Model Performance ---
    model_metrics = analysis_data.get('modelMetrics', {})
    print(f"[DEBUG] model_metrics type: {type(model_metrics)}")
    print(f"[DEBUG] model_metrics content: {model_metrics}")
    
    if model_metrics and isinstance(model_metrics, dict):
        story.append(Paragraph("4. Detailed Model Performance", heading_style))
        
        for model_name, metrics in model_metrics.items():
            print(f"[DEBUG] Processing model: {model_name}")
            print(f"[DEBUG] metrics type: {type(metrics)}")
            print(f"[DEBUG] metrics content: {metrics}")
            
            if not isinstance(metrics, dict):
                print(f"Warning: Metrics for {model_name} is not a dictionary, skipping...")
                continue
                
            # Model header
            story.append(Paragraph(f"{model_name.upper()} Model", heading2_style))
            
            # Safely get metric values with proper type checking
            def safe_get_metric(metrics_dict, key, subkey=None):
                try:
                    print(f"[DEBUG] safe_get_metric - key: {key}, subkey: {subkey}")
                    print(f"[DEBUG] metrics_dict type: {type(metrics_dict)}")
                    print(f"[DEBUG] metrics_dict: {metrics_dict}")
                    
                    if not isinstance(metrics_dict, dict):
                        print(f"[ERROR] metrics_dict is not a dictionary: {metrics_dict}")
                        return 0
                        
                    if subkey is not None:
                        print(f"[DEBUG] Getting subkey {subkey} from {key}")
                        if not isinstance(metrics_dict.get(key, {}), dict):
                            print(f"[WARNING] {key} is not a dictionary: {metrics_dict.get(key, {})}")
                            return 0
                        value = metrics_dict[key].get(subkey, 0)
                        print(f"[DEBUG] Got value: {value} (type: {type(value)})")
                        return value
                        
                    value = metrics_dict.get(key, 0)
                    print(f"[DEBUG] Got simple value: {value} (type: {type(value)})")
                    return value
                    
                except Exception as e:
                    print(f"[ERROR] Error in safe_get_metric: {str(e)}")
                    print(f"[ERROR] key: {key}, subkey: {subkey}")
                    print(f"[ERROR] metrics_dict: {metrics_dict}")
                    return 0
            
            # Overall metrics with safe value extraction
            print("[DEBUG] Extracting metrics...")
            try:
                accuracy = safe_get_metric(metrics, 'accuracy')
                precision = safe_get_metric(metrics, 'precision', 'weighted')
                recall = safe_get_metric(metrics, 'recall', 'weighted')
                f1_weighted = safe_get_metric(metrics, 'f1_score', 'weighted')
                f1_macro = safe_get_metric(metrics, 'f1_score', 'macro')
                support = safe_get_metric(metrics, 'support')
                
                print(f"[DEBUG] Extracted values - accuracy: {accuracy}, precision: {precision}, recall: {recall}, "
                      f"f1_weighted: {f1_weighted}, f1_macro: {f1_macro}, support: {support}")
                
                overall_metrics = [
                    ['Metric', 'Score'],
                    ['Accuracy', f"{float(accuracy):.3f}" if isinstance(accuracy, (int, float)) else 'N/A'],
                    ['Weighted Precision', f"{float(precision):.3f}" if isinstance(precision, (int, float)) else 'N/A'],
                    ['Weighted Recall', f"{float(recall):.3f}" if isinstance(recall, (int, float)) else 'N/A'],
                    ['Weighted F1-Score', f"{float(f1_weighted):.3f}" if isinstance(f1_weighted, (int, float)) else 'N/A'],
                    ['Macro F1-Score', f"{float(f1_macro):.3f}" if isinstance(f1_macro, (int, float)) else 'N/A'],
                    ['Support', str(int(support)) if isinstance(support, (int, float)) else 'N/A']
                ]
                print("[DEBUG] Successfully created overall_metrics")
            except Exception as e:
                print(f"[ERROR] Error creating overall_metrics: {str(e)}")
                print(f"[ERROR] Metrics content: {metrics}")
                # Fallback to empty metrics
                overall_metrics = [
                    ['Metric', 'Score'],
                    ['Error', 'Could not extract metrics'],
                    ['Details', 'Please check the logs for more information']
                ]
            
            # Create overall metrics table
            overall_table = Table(overall_metrics, colWidths=[150, 100])
            overall_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e9ecef')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ]))
            print(f"overall metric is {overall_metrics}")
            # Add conditional formatting for metric values
            for i in range(1, len(overall_metrics)):
                try:
                    value = float(overall_metrics[i][1])
                    if value >= 0.8:
                        color = colors.HexColor('#d4edda')  # Green
                    elif value >= 0.6:
                        color = colors.HexColor('#fff3cd')  # Yellow
                    else:
                        color = colors.HexColor('#f8d7da')  # Red
                    
                    overall_table.setStyle(TableStyle([
                        ('BACKGROUND', (1, i), (1, i), color),
                    ]))
                except (ValueError, IndexError):
                    pass
            
            story.append(overall_table)
            print(f"we got here line 661")
            print(f"we got here line metrics {metrics}")

            # Add per-class metrics if available
            # Show overall metrics table
            story.append(Spacer(1, 12))
            story.append(Paragraph("Evaluation Metrics:", ParagraphStyle(
                'Heading3',
                parent=heading2_style,
                fontSize=12,
                spaceBefore=10,
                spaceAfter=6
            )))

            # Build table from metrics dict
            metrics_table_data = [["Metric", "Value"]]

            for key, value in metrics.items():
                # Skip confusion_matrix here (can render separately if needed)
                if key == "confusion_matrix":
                    continue
                # Format numeric values to 3 decimals
                if isinstance(value, (int, float)):
                    value = f"{value:.3f}"
                metrics_table_data.append([key.capitalize(), str(value)])

            # Create and style metrics table
            metrics_table = Table(metrics_table_data, colWidths=[150, 150], repeatRows=1)
            metrics_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e9ecef')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ]))

            story.append(metrics_table)

            print("we got here line 704")

            
            # Add model-specific insights
            model_insights = []
            accuracy = metrics.get('accuracy', 0)
            print("We are here got here too")
            
            if accuracy > 0.85:
                model_insights.append(
                    "This model shows excellent performance with high accuracy across all classes. "
                    "It's well-suited for production use."
                )
            elif accuracy > 0.7:
                model_insights.append(
                    "The model shows good performance but has room for improvement. "
                    "Consider reviewing misclassified examples to identify patterns."
                )
            else:
                model_insights.append(
                    "The model's performance could be improved. Consider reviewing the training data, "
                    "feature engineering, or trying alternative model architectures."
                )

            print("we got here line 742")

            
            # Add any class-specific insights
            if 'f1_score' in metrics:
                f1_scores = metrics['f1_score']
                if isinstance(f1_scores, dict) and 'negative' in f1_scores and 'positive' in f1_scores:
                    if f1_scores['negative'] < 0.6 and f1_scores['positive'] > 0.8:
                        model_insights.append(
                            "The model performs significantly better on positive sentiment than negative. "
                            "This could indicate class imbalance or differences in how negative sentiment is expressed."
                        )
            
            if model_insights:
                story.append(Spacer(1, 10))
                story.append(Paragraph("Analysis:", ParagraphStyle(
                    'Heading3', 
                    parent=heading2_style,
                    fontSize=12,
                    spaceBefore=10,
                    spaceAfter=6
                )))
                
                for insight in model_insights:
                    story.append(Paragraph(f"• {insight}", body_style))
            
            story.append(Spacer(1, 24))
            print("We are here got here too2")


    # --- Model Confusion Analysis ---
    confusion_matrices = analysis_data.get('confusionMatrices', {})
    if confusion_matrices:
        story.append(Paragraph("5. Model Confusion Analysis", heading_style))
        
        # Add explanatory text
        story.append(Paragraph(
            "Confusion matrices provide detailed insight into model performance by showing the count of "
            "correct and incorrect predictions for each class. The diagonal elements represent correct "
            "predictions, while off-diagonal elements show misclassifications.",
            body_style
        ))
        print("We are here got here too21")

        story.append(Spacer(1, 12))
        print(f"model name and matrix data are {confusion_matrices.items()}")
        print(f"model data are {model_metrics}")

        for model_name, matrix_data in confusion_matrices.items():
            # Model header with performance summary if available
            model_metrics1 = model_metrics.get(model_name, {})
            accuracy = model_metrics1.get('accuracy', 0)

            header_text = f"{model_name.upper().replace('_', ' ')} Model"
            if accuracy > 0:
                header_text += f" (Accuracy: {accuracy:.1%})"

            story.append(Paragraph(header_text, heading2_style))
            print("We are here got here too22")

            # Convert matrix to table if it's a list
            if isinstance(matrix_data, list) and len(matrix_data) > 0:
                num_classes = len(matrix_data)

                # Choose labels dynamically
                if num_classes == 2:
                    sentiment_labels = ["Negative", "Positive"]
                elif num_classes == 3:
                    sentiment_labels = ["Negative", "Neutral", "Positive"]
                else:
                    sentiment_labels = [f"Class {i + 1}" for i in range(num_classes)]

                # Prepare table headers
                headers = ['Actual\\Predicted'] + sentiment_labels + ['Total', 'Accuracy']
                table_data = [headers]

                # Populate table data with values, row totals, and accuracies
                for i, row in enumerate(matrix_data):
                    label = sentiment_labels[i] if i < len(sentiment_labels) else f"Class {i + 1}"

                    row_total = sum(row)
                    class_accuracy = row[i] / row_total if row_total > 0 else 0

                    # Format row
                    formatted_row = [label]
                    for val in row:
                        pct = f" ({val / row_total:.0%})" if row_total > 0 else ""
                        formatted_row.append(f"{val}{pct}")
                    formatted_row.append(str(row_total))
                    formatted_row.append(f"{class_accuracy:.1%}")
                    table_data.append(formatted_row)

                # Add column totals
                col_totals = [sum(x) for x in zip(*matrix_data)]
                total = sum(col_totals)
                overall_accuracy = (
                    sum(matrix_data[i][i] for i in range(min(num_classes, len(col_totals)))) / total
                    if total > 0 else 0
                )
                table_data.append(['Total'] + [str(x) for x in col_totals] + [str(total), f"{overall_accuracy:.1%}"])

                # Create and style the table
                col_widths = [80] + [60] * num_classes + [60, 60]  # Adjust column widths
                table = Table(table_data, colWidths=col_widths, repeatRows=1)
                print("We are here got here too25")

                # Define styles
                style = [
                    # Header and first column styling
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),  # Header background
                    ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#2c3e50')),  # First column background
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text
                    ('TEXTCOLOR', (0, 1), (0, -1), colors.whitesmoke),  # First column text
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # First column font
                    ('FONTSIZE', (0, 0), (-1, -1), 8),  # Smaller font
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#e9ecef')),
                    ('LINEBELOW', (0, -1), (-1, -1), 1, colors.HexColor('#2c3e50')),
                    ('LINEAFTER', (0, 0), (0, -1), 1, colors.HexColor('#2c3e50')),
                    ('LINEAFTER', (-2, 0), (-2, -1), 1, colors.HexColor('#2c3e50')),
                ]

                # Alternating row colors
                for i in range(1, len(table_data) - 1):  # Skip header and total row
                    bg_color = colors.HexColor('#f8f9fa') if i % 2 == 0 else colors.whitesmoke
                    style.append(('BACKGROUND', (1, i), (-1, i), bg_color))

                # Color diagonal (correct predictions)
                for i in range(1, num_classes + 1):
                    style.append(('BACKGROUND', (i, i), (i, i), colors.HexColor('#d4edda')))

                # Highlight total row
                style.extend([
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e9ecef')),
                ])

                table.setStyle(TableStyle(style))

                story.append(table)
                story.append(Spacer(1, 12))

    # --- Data Insights & Examples ---

    print("We are here got here too3")

    raw_data = analysis_data.get('rawData', [])
    if raw_data and len(raw_data) > 0:
        story.append(PageBreak())
        story.append(Paragraph("6. Data Insights & Examples", heading_style))
        
        # Add explanatory text
        story.append(Paragraph(
            "This section provides a curated sample of analyzed posts to illustrate the model's predictions "
            "and the sentiment distribution in the dataset. Each example includes the original text and the "
            "assigned sentiment label.",
            body_style
        ))
        story.append(Spacer(1, 12))
        
        # Add summary statistics if available
        if 'statistics' in analysis_data:
            stats = analysis_data['statistics']
            stats_text = [
                f"• Total posts analyzed: {stats.get('total_posts', len(raw_data))}",
                f"• Average post length: {stats.get('avg_post_length', 0):.1f} characters",
                f"• Date range: {stats.get('start_date', 'N/A')} to {stats.get('end_date', 'N/A')}",
                f"• Most common words: {', '.join(stats.get('top_words', [])[:5])}"
            ]
            
            story.append(Paragraph("<b>Dataset Overview:</b>", body_style))
            for stat in stats_text:
                story.append(Paragraph(stat, body_style))
            story.append(Spacer(1, 12))
        
        # Add a note about the sample
        story.append(Paragraph(
            "<i>Note: The following is a representative sample of analyzed posts showing the diversity "
            "of sentiment in the dataset. Each post includes the predicted sentiment and confidence score.</i>",
            ParagraphStyle(
                'Italic',
                parent=body_style,
                fontSize=9,
                textColor=colors.HexColor('#6c757d'),
                spaceAfter=12
            )
        ))
        
        # Prepare sample data table
        sample_size = min(10, len(raw_data))  # Show up to 10 samples
        sample_data = raw_data[:sample_size]
        
        # Create a table for the sample data
        sample_headers = ['#', 'Sentiment', 'Confidence', 'Text Preview']
        sample_table_data = [sample_headers]
        
        for idx, post in enumerate(sample_data, 1):
            sentiment = str(post.get('sentiment', 'N/A')).capitalize()
            confidence = float(post.get('confidence', 0))
            text = str(post.get('text', ''))[:100] + ('...' if len(str(post.get('text', ''))) > 100 else '')
            
            # Determine sentiment color
            if sentiment == 'Positive':
                sent_color = colors.HexColor('#28a745')  # Green
            elif sentiment == 'Negative':
                sent_color = colors.HexColor('#dc3545')  # Red
            else:
                sent_color = colors.HexColor('#ffc107')  # Yellow
            
            # Format confidence with color coding
            print(f"the color object is this one {sent_color}")
            conf_style = colors.black
            if confidence > 0.8:
                conf_style = colors.HexColor('#28a745')  # Green
            elif confidence > 0.6:
                conf_style = colors.HexColor('#ffc107')  # Yellow
            elif confidence > 0:
                conf_style = colors.HexColor('#dc3545')  # Red

            # usage in your code:
            sent_hex = color_to_hex_nopound(sent_color)
            conf_hex = color_to_hex_nopound(conf_style)
            from xml.sax.saxutils import escape

            sample_table_data.append([
                str(idx),
                f'{calculate_sentiment(text)}',
                f'{calculate_sentiment_with_confidence(text):.1%}',
                escape(text)  # escape text to avoid breaking XML-like tags in Paragraph
            ])
        
        # Create and style the sample table
        col_widths = [30, 80, 70, 380]  # Adjusted column widths
        sample_table = Table(sample_table_data, colWidths=col_widths, repeatRows=1)
        
        # Define table styles
        sample_table_style = [
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            
            # Table borders and alignment
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Center align index column
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e9ecef')),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            
            # Cell padding
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]
        
        sample_table.setStyle(TableStyle(sample_table_style))
        story.append(sample_table)
        story.append(Spacer(1, 12))
        
        # Add a note about the full dataset
        if len(raw_data) > sample_size:
            story.append(Paragraph(
                f"<i>Showing {sample_size} of {len(raw_data)} analyzed posts. "
                "The full dataset contains more examples with diverse sentiment patterns.</i>",
                ParagraphStyle(
                    'Italic',
                    parent=body_style,
                    fontSize=8,
                    textColor=colors.HexColor('#6c757d'),
                    spaceBefore=6
                )
            ))
        
        # Add a final section with key observations if available
        if 'insights' in analysis_data and analysis_data['insights']:
            story.append(Spacer(1, 12))
            story.append(Paragraph("<b>Key Observations:</b>", body_style))
            for insight in analysis_data['insights']:
                story.append(Paragraph(f"• {insight}", body_style))
        
        # Show first 3 posts as examples
        for i, post in enumerate(raw_data[:3]):
            story.append(Paragraph(f"<b>Post {i+1}:</b>", body_style))
            text = post.get('text', 'N/A')[:150] + "..." if len(post.get('text', '')) > 150 else post.get('text', 'N/A')
            story.append(Paragraph(f"<i>Text:</i> {text}", body_style))
            
            # Show sentiment predictions from different models
            nb_sentiment = post.get('nb_sentiment', 'N/A')
            svm_sentiment = post.get('svm_sentiment', 'N/A')
            bert_sentiment = post.get('bert_sentiment', 'N/A')
            
            story.append(Paragraph(f"<i>Predictions:</i> NB: {nb_sentiment}, SVM: {svm_sentiment}, BERT: {bert_sentiment}", body_style))
            story.append(Spacer(1, 10))
        
        story.append(Spacer(1, 24))

    # --- Methodology & Technical Details ---
    story.append(PageBreak())
    story.append(Paragraph("8. Methodology & Technical Details", heading_style))
    print("We are here got here too4")

    # Add methodology sections with better formatting
    sections = [
        ("Data Collection",
         "Social media data was collected using the following parameters:\n"
         "• Query: {query}\n"
         "• Date Range: {start_date} to {end_date}\n"
         "• Source: {source}\n"
         "• Total Posts: {total_posts}".format(
             query=analysis_data.get('query', 'N/A'),
             start_date=analysis_data.get('startDate', 'N/A'),
             end_date=analysis_data.get('endDate', 'N/A'),
             source=analysis_data.get('source', 'Multiple social media platforms'),
             total_posts=len(raw_data) if raw_data else 0
         )),
         
        ("Text Preprocessing",
         "The following preprocessing steps were applied to the raw text data:\n"
         "• Lowercasing and punctuation removal\n"
         "• Tokenization and stopword removal\n"
         "• Lemmatization and stemming\n"
         "• Emoji and emoticon handling\n"
         "• URL and mention removal"),
         
        ("Machine Learning Models",
         "<b>1. Naive Bayes Classifier</b>\n"
         "A probabilistic classifier based on Bayes' theorem with strong independence assumptions between features.\n\n"
         "<b>2. Support Vector Machine (SVM)</b>\n"
         "A powerful classifier that finds the optimal hyperplane for separating different sentiment classes using an RBF kernel.\n\n"
         "<b>3. BERT (Bidirectional Encoder Representations from Transformers)</b>\n"
         "A state-of-the-art transformer-based model fine-tuned for sentiment analysis tasks."),
         
        ("Evaluation Metrics",
         "Model performance was evaluated using the following metrics:\n"
         "• <b>Accuracy</b>: Overall correctness of the model\n"
         "• <b>Precision</b>: True positives / (True positives + False positives)\n"
         "• <b>Recall</b>: True positives / (True positives + False negatives)\n"
         "• <b>F1-Score</b>: Harmonic mean of precision and recall\n"
         "• <b>Confusion Matrix</b>: Detailed breakdown of predictions vs actuals"),
         
        ("Sentiment Classification",
         "Posts were classified into three sentiment categories:\n"
         "• <b>Positive</b>: Expressing favorable opinions or emotions\n"
         "• <b>Neutral</b>: Objective statements or no clear sentiment\n"
         "• <b>Negative</b>: Expressing unfavorable opinions or emotions")
    ]
    print("We are here got here too on line 1113")

    
    # Add methodology sections to the document
    for i, (title, content) in enumerate(sections, 1):
        story.append(Paragraph(f"<b>{i}. {title}</b>", heading2_style))
        story.append(Paragraph(content.replace('\n', '<br/>'), body_style))
        story.append(Spacer(1, 12))
    
    # --- Conclusion & Recommendations ---
    story.append(PageBreak())
    story.append(Paragraph("9. Conclusion & Recommendations", heading_style))

    # Add summary of key findings
    sentiment_dist = analysis_data.get('sentimentDistribution', {})
    print(f"dominant sentiment is {sentiment_dist}")
    dominant_sentiment = get_dominant_sentiment(sentiment_dist)
    print("We are here got here too5")

    # Get best performing model
    best_model = None
    best_accuracy = 0
    print(f"The model name and metric is {model_metrics}")
    for model_name, metrics in model_metrics.items():
        if metrics.get('accuracy', 0) > best_accuracy:
            best_accuracy = metrics['accuracy']
            best_model = model_name.upper()
    
    # Create summary points
    summary = [
        f"The analysis of {len(raw_data)} social media posts revealed a dominant sentiment of <b>{dominant_sentiment}</b>.",
        f"The <b>{best_model}</b> model demonstrated the highest accuracy of <b>{best_accuracy:.1%}</b> in sentiment classification.",
        "The sentiment distribution shows a diverse range of opinions and perspectives on the analyzed topic."
    ]
    
    # Add summary to document
    story.append(Paragraph("<b>Key Findings:</b>", heading2_style))
    for point in summary:
        story.append(Paragraph(f"• {point}", body_style))
    
    # Add recommendations
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Strategic Recommendations:</b>", heading2_style))
    
    recommendations = [
        "<b>1. Sentiment Monitoring:</b> Implement continuous sentiment tracking to identify trends and shifts in public opinion.",
        "<b>2. Issue Resolution:</b> Address common themes in negative sentiment to improve overall perception.",
        "<b>3. Engagement Strategy:</b> Leverage positive sentiment to strengthen community engagement and brand advocacy.",
        "<b>4. Model Improvement:</b> Regularly update training data and fine-tune models for better accuracy.",
        "<b>5. Actionable Insights:</b> Use these findings to inform content strategy and communication approaches."
    ]
    
    for rec in recommendations:
        story.append(Paragraph(rec, body_style))
    
    # Add report metadata
    story.append(Spacer(1, 24))
    story.append(Paragraph("<b>Report Metadata</b>", heading2_style))
    print("We are here got here too6")

    metadata = [
        ("Report Generated", datetime.now().strftime("%Y-%m-%d %H:%M")),
        ("Analysis ID", analysis_data.get('analysisId', 'N/A')),
        ("Query", analysis_data.get('query', 'N/A')),
        ("Total Posts", len(raw_data) if raw_data else 0),
        ("Analysis Duration", analysis_data.get('analysisDuration', 'N/A')),
        ("Language", analysis_data.get('language', 'English')),
        ("Report Version", "1.0")
    ]
    
    # Create metadata table
    meta_table = Table([["Field", "Value"]] + metadata, colWidths=[150, 350])
    meta_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e9ecef')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ]))
    
    story.append(meta_table)
    
    # Add final notes
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<i>Note: This report is based on automated sentiment analysis and should be interpreted in the context of the data and time period analyzed. "
        "For more detailed analysis or specific questions, please contact the analytics team.</i>",
        ParagraphStyle(
            'Italic',
            parent=body_style,
            fontSize=8,
            textColor=colors.HexColor('#6c757d')
        )
    ))
    print("We are here got here too7")

    # --- Footer ---
    story.append(Spacer(1, 20))
    footer_text = (
        f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} | "
        f"Analysis ID: {analysis_data.get('analysisId', 'N/A')} | "
        f"© {datetime.now().year} Social Media Analysis Platform"
    )
    footer_style = ParagraphStyle(
        name='Footer',
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#6c757d'),
        spaceBefore=20
    )
    story.append(Paragraph(footer_text, footer_style))

    # --- Build PDF ---
    doc.build(story)
