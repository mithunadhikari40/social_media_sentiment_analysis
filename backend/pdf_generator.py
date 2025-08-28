import os
import pandas as pd
import base64
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
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
    Generate a comprehensive PDF report from analysis response data.
    Includes metadata, summaries, model comparisons, detailed metrics,
    confusion matrices, per-model sentiment tables, key insights, top words,
    sample records, and methodology. Images/diagrams are intentionally avoided.
    """
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))

    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(name='Title', fontSize=24, alignment=TA_CENTER, spaceAfter=20)
    heading_style = ParagraphStyle(name='Heading1', fontSize=16, alignment=TA_LEFT, spaceAfter=10, spaceBefore=10)
    subheading_style = ParagraphStyle(name='Heading2', fontSize=13, alignment=TA_LEFT, spaceAfter=6, spaceBefore=6, textColor=colors.darkblue)
    body_style = styles['BodyText']
    small_style = ParagraphStyle(name='Small', fontSize=9, alignment=TA_LEFT, spaceAfter=4)

    story = []

    # --- Title / Cover ---
    story.append(Paragraph("Social Media Sentiment Analysis Report", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Report Metadata", heading_style))
    created_at = analysis_data.get('createdAt', 'N/A')
    analysis_id = analysis_data.get('id', 'N/A')
    query_text = analysis_data.get('query', 'N/A')
    metrics = analysis_data.get('metrics', {}) or {}
    total_tweets = metrics.get('totalTweets') if isinstance(metrics, dict) else None
    overall_sentiment = metrics.get('overallSentiment') if isinstance(metrics, dict) else None
    confidence_score = metrics.get('confidenceScore') if isinstance(metrics, dict) else None

    meta_rows = [
        ["Analysis ID", str(analysis_id)],
        ["Query", str(query_text)],
        ["Created At", str(created_at)],
        ["Total Posts Analyzed", str(total_tweets if total_tweets is not None else 'N/A')],
        ["Overall Sentiment", str(overall_sentiment if overall_sentiment is not None else 'N/A')],
        ["Confidence Score", f"{confidence_score:.2f}%" if isinstance(confidence_score, (int, float)) else 'N/A'],
    ]
    meta_table = Table([["Field", "Value"]] + meta_rows, colWidths=[2.2*inch, 4.8*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f3f4f6')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 18))

    # Executive summary
    story.append(Paragraph("Executive Summary", heading_style))
    summary_lines = []
    if isinstance(metrics, dict):
        pos = metrics.get('positivePercentage')
        neg = metrics.get('negativePercentage')
        neu = metrics.get('neutralPercentage')
        if all(isinstance(x, (int, float)) for x in [pos, neg, neu]):
            summary_lines.append(f"Positive {pos:.1f}%, Negative {neg:.1f}%, Neutral {neu:.1f}%.")
    if overall_sentiment:
        summary_lines.append(f"Overall sentiment is <b>{overall_sentiment.title()}</b> with confidence {confidence_score:.1f}%" if isinstance(confidence_score, (int, float)) else f"Overall sentiment is <b>{overall_sentiment.title()}</b>.")
    if not summary_lines:
        summary_lines.append("This report summarizes sentiment distribution, model performance, and key insights.")
    story.append(Paragraph(" ".join(summary_lines), body_style))
    story.append(Spacer(1, 12))

    # --- Sentiment Distribution (BERT) ---
    story.append(Paragraph("Sentiment Distribution (BERT)", heading_style))
    sentiment_dist = analysis_data.get('sentimentDistribution', [])
    if sentiment_dist:
        table_data = [['Sentiment', 'Count', 'Percentage']]
        for item in sentiment_dist:
            table_data.append([
                item.get('sentiment', ''),
                str(item.get('count', 0)),
                f"{item.get('percentage', 0):.1f}%"
            ])
        
        table = Table(table_data, colWidths=[2*inch, 1.5*inch, 2*inch])
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

    # --- Per-Model Sentiment Counts ---
    sentiment_counts = analysis_data.get('sentimentCounts', {}) or {}
    if isinstance(sentiment_counts, dict) and len(sentiment_counts) > 0:
        story.append(Paragraph("Per-Model Sentiment Breakdown", heading_style))
        # Build a table with rows as sentiments and columns as models
        models = list(sentiment_counts.keys())
        sentiments = ['negative', 'neutral', 'positive']
        header = ['Sentiment'] + models
        rows = [header]
        for s in sentiments:
            row = [s.title()]
            for m in models:
                values = sentiment_counts.get(m, [])
                val = next((v for v in values if isinstance(v, dict) and v.get('sentiment') == s), None)
                if val:
                    row.append(f"{val.get('count', 0)} ({val.get('percentage', 0):.1f}%)")
                else:
                    row.append("0 (0.0%)")
            rows.append(row)
        model_table = Table(rows)
        model_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#374151')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(model_table)
        story.append(Spacer(1, 18))

    # --- Model Comparison ---
    story.append(Paragraph("Model Performance Comparison", heading_style))
    model_comparison = analysis_data.get('modelComparison', {})
    if model_comparison:
        table_data = [['Model', 'Accuracy']]
        for model, accuracy in model_comparison.items():
            table_data.append([model.upper(), f"{accuracy:.3f}"])
        
        table = Table(table_data, colWidths=[3*inch, 3*inch])
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
    if isinstance(insights, dict) and len(insights) > 0:
        story.append(Paragraph("Key Insights", heading_style))
        # Known insight keys with richer formatting
        sentiment_balance = insights.get('sentimentBalance') or insights.get('SentimentBalance')
        if isinstance(sentiment_balance, dict) and len(sentiment_balance) > 0:
            story.append(Paragraph("Sentiment Balance", subheading_style))
            sb_table = Table([
                ['Positive', 'Negative', 'Neutral'],
                [
                    f"{sentiment_balance.get('positive', 0):.1f}%",
                    f"{sentiment_balance.get('negative', 0):.1f}%",
                    f"{sentiment_balance.get('neutral', 0):.1f}%",
                ]
            ])
            sb_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            story.append(sb_table)
            story.append(Spacer(1, 8))

        best_model = insights.get('bestModel') or insights.get('BestModel')
        if isinstance(best_model, dict) and len(best_model) > 0:
            story.append(Paragraph("Best Performing Model", subheading_style))
            bm_table = Table([
                ['Model', 'Accuracy'],
                [str(best_model.get('name', 'N/A')), f"{best_model.get('accuracy', 0):.3f}"]
            ], colWidths=[3*inch, 3*inch])
            bm_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            story.append(bm_table)
            story.append(Spacer(1, 8))

        model_behavior = insights.get('modelBehavior') or insights.get('ModelBehavior')
        if model_behavior:
            story.append(Paragraph("Model Behavior", subheading_style))
            story.append(Paragraph(str(model_behavior), body_style))
            story.append(Spacer(1, 8))

        # Any remaining insight keys
        for key, value in insights.items():
            if key in ['sentimentBalance', 'SentimentBalance', 'bestModel', 'BestModel', 'modelBehavior', 'ModelBehavior']:
                continue
            story.append(Paragraph(key.replace('_', ' ').title(), subheading_style))
            story.append(Paragraph(str(value), body_style))
            story.append(Spacer(1, 6))
        story.append(Spacer(1, 12))

    # --- Model Metrics ---
    model_metrics = analysis_data.get('modelMetrics', {})
    if isinstance(model_metrics, dict) and len(model_metrics) > 0:
        story.append(Paragraph("Detailed Model Metrics", heading_style))
        mm_table_rows = [['Model', 'Accuracy', 'Precision', 'Recall', 'F1-Score']]
        for model_name, metrics_obj in model_metrics.items():
            mm_table_rows.append([
                model_name.upper(),
                f"{(metrics_obj.get('accuracy', 0)):.3f}",
                f"{(metrics_obj.get('precision', 0)):.3f}",
                f"{(metrics_obj.get('recall', 0)):.3f}",
                f"{(metrics_obj.get('f1_score', 0)):.3f}",
            ])
        mm_table = Table(mm_table_rows)
        mm_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(mm_table)
        story.append(Spacer(1, 24))

    # --- Confusion Matrices ---
    confusion_matrices = analysis_data.get('confusionMatrices', {})
    if isinstance(confusion_matrices, dict) and len(confusion_matrices) > 0:
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

    # --- Top Words by Sentiment ---
    word_cloud_data = analysis_data.get('wordCloudData', {}) or {}
    if isinstance(word_cloud_data, dict) and len(word_cloud_data) > 0:
        story.append(Paragraph("Top Words by Sentiment", heading_style))
        for sentiment in ['positive', 'negative', 'neutral']:
            words = word_cloud_data.get(sentiment)
            if words and isinstance(words, list) and len(words) > 0:
                story.append(Paragraph(sentiment.title(), subheading_style))
                # Show as comma-separated, truncated for readability
                preview = ", ".join([str(w) for w in words[:50]])
                if len(words) > 50:
                    preview += ", ..."
                story.append(Paragraph(preview, small_style))
                story.append(Spacer(1, 6))
        story.append(Spacer(1, 12))

    # Page break before appendix-like content
    story.append(PageBreak())

    # --- Sample Data Analysis ---
    raw_data = analysis_data.get('rawData', [])
    if raw_data and len(raw_data) > 0:
        story.append(Paragraph("Sample Data Analysis", heading_style))
        story.append(Paragraph("Representative sample of analyzed posts:", body_style))
        story.append(Spacer(1, 12))
        
        # Show up to first 5 posts as examples
        for i, post in enumerate(raw_data[:5]):
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

    # --- Time Series Summary (textual) ---
    ts = analysis_data.get('timeSeriesData', [])
    if isinstance(ts, list) and len(ts) > 0:
        story.append(Paragraph("Temporal Sentiment Summary", heading_style))
        try:
            first_date = ts[0].get('date')
            last_date = ts[-1].get('date')
            sum_pos = sum(int(day.get('positive', 0)) for day in ts)
            sum_neg = sum(int(day.get('negative', 0)) for day in ts)
            sum_neu = sum(int(day.get('neutral', 0)) for day in ts)
            total = max(1, sum_pos + sum_neg + sum_neu)
            story.append(Paragraph(
                f"Window {first_date} → {last_date}. Totals: Positive {sum_pos} ({(sum_pos/total*100):.1f}%), "
                f"Negative {sum_neg} ({(sum_neg/total*100):.1f}%), Neutral {sum_neu} ({(sum_neu/total*100):.1f}%).",
                body_style
            ))
        except Exception:
            pass
        story.append(Spacer(1, 12))

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
