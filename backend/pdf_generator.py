import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors

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
