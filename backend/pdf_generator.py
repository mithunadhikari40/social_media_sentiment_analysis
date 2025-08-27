import os
import pandas as pd
import base64
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import inch

# --- PDF Generation ---

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
    heading_style = ParagraphStyle(name='Heading1', fontSize=16, alignment=TA_LEFT, spaceAfter=10, spaceBefore=10)
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
    Generates a basic PDF report from analysis response data.
    """
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))

    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(name='Title', fontSize=24, alignment=TA_CENTER, spaceAfter=20)
    heading_style = ParagraphStyle(name='Heading1', fontSize=16, alignment=TA_LEFT, spaceAfter=10, spaceBefore=10)
    body_style = styles['BodyText']

    story = []

    # --- Title ---
    story.append(Paragraph("Social Media Sentiment Analysis Report", title_style))
    story.append(Spacer(1, 24))

    # --- Query Information ---
    story.append(Paragraph("Analysis Details", heading_style))
    query_text = f"<b>Search Query:</b> {analysis_data.get('query', 'N/A')}"
    story.append(Paragraph(query_text, body_style))
    created_at = analysis_data.get('createdAt', 'N/A')
    date_text = f"<b>Analysis Date:</b> {created_at}"
    story.append(Paragraph(date_text, body_style))
    story.append(Spacer(1, 12))

    # --- Sentiment Distribution ---
    story.append(Paragraph("Sentiment Distribution", heading_style))
    sentiment_dist = analysis_data.get('sentimentDistribution', [])
    if sentiment_dist:
        table_data = [['Sentiment', 'Count', 'Percentage']]
        for item in sentiment_dist:
            table_data.append([
                item.get('sentiment', ''),
                str(item.get('count', 0)),
                f"{item.get('percentage', 0):.1f}%"
            ])
        
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

    # --- Model Comparison ---
    story.append(Paragraph("Model Performance Comparison", heading_style))
    model_comparison = analysis_data.get('modelComparison', {})
    if model_comparison:
        table_data = [['Model', 'Accuracy']]
        for model, accuracy in model_comparison.items():
            table_data.append([model.upper(), f"{accuracy:.3f}"])
        
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

    # --- Key Insights ---
    insights = analysis_data.get('insights', {})
    if insights:
        story.append(Paragraph("Key Insights", heading_style))
        for key, value in insights.items():
            insight_text = f"<b>{key.replace('_', ' ').title()}:</b> {str(value)}"
            story.append(Paragraph(insight_text, body_style))
        story.append(Spacer(1, 12))

    # --- Model Metrics ---
    model_metrics = analysis_data.get('modelMetrics', {})
    if model_metrics:
        story.append(Paragraph("Detailed Model Metrics", heading_style))
        for model_name, metrics in model_metrics.items():
            story.append(Paragraph(f"<b>{model_name.upper()} Model:</b>", body_style))
            metrics_text = f"Accuracy: {metrics.get('accuracy', 0):.3f}, Precision: {metrics.get('precision', 0):.3f}, Recall: {metrics.get('recall', 0):.3f}, F1-Score: {metrics.get('f1_score', 0):.3f}"
            story.append(Paragraph(metrics_text, body_style))
            story.append(Spacer(1, 6))
        story.append(Spacer(1, 24))

    # --- Confusion Matrices ---
    confusion_matrices = analysis_data.get('confusionMatrices', {})
    if confusion_matrices:
        story.append(Paragraph("Confusion Matrices", heading_style))
        for model_name, matrix_data in confusion_matrices.items():
            story.append(Paragraph(f"<b>{model_name.upper().replace('_', ' ')} Model:</b>", body_style))
            
            # Convert matrix to table if it's a list
            if isinstance(matrix_data, list) and len(matrix_data) > 0:
                headers = ['Actual\\Predicted', 'Negative', 'Neutral', 'Positive']
                table_data = [headers]
                
                sentiment_labels = ['Negative', 'Neutral', 'Positive']
                for i, row in enumerate(matrix_data):
                    if i < len(sentiment_labels):
                        table_row = [sentiment_labels[i]] + [str(val) for val in row]
                        table_data.append(table_row)
                
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (1, 1), (-1, -1), colors.beige),
                ]))
                
                story.append(table)
                story.append(Spacer(1, 12))

    # --- Sample Data Analysis ---
    raw_data = analysis_data.get('rawData', [])
    if raw_data and len(raw_data) > 0:
        story.append(Paragraph("Sample Data Analysis", heading_style))
        story.append(Paragraph("Representative sample of analyzed posts:", body_style))
        story.append(Spacer(1, 12))
        
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

    # --- Methodology ---
    story.append(Paragraph("Methodology & Technical Details", heading_style))
    methodology_text = """
    <b>Data Collection:</b> Social media posts were collected and preprocessed for sentiment analysis.<br/><br/>
    <b>Text Preprocessing:</b> Data cleaning, tokenization, and feature extraction were performed to prepare the text for analysis.<br/><br/>
    <b>Machine Learning Models:</b><br/>
    • <b>Naive Bayes:</b> Probabilistic classifier using Bayes' theorem with strong independence assumptions<br/>
    • <b>SVM:</b> Support Vector Machine with RBF kernel for non-linear classification<br/>
    • <b>BERT:</b> Pre-trained transformer model fine-tuned for sentiment analysis<br/><br/>
    <b>Evaluation Metrics:</b> Models were evaluated using accuracy, precision, recall, and F1-score to ensure comprehensive performance assessment.<br/><br/>
    <b>Sentiment Categories:</b> Posts were classified into three categories: Positive, Negative, and Neutral sentiments.
    """
    story.append(Paragraph(methodology_text, body_style))
    
    # --- Footer ---
    story.append(Spacer(1, 30))
    total_posts = len(raw_data) if raw_data else 0
    footer_text = f"Report generated on {analysis_data.get('createdAt', 'N/A')} | Total posts analyzed: {total_posts}"
    footer_style = ParagraphStyle(name='Footer', fontSize=10, alignment=TA_CENTER, textColor=colors.grey)
    story.append(Paragraph(footer_text, footer_style))

    # --- Build PDF ---
    doc.build(story)
