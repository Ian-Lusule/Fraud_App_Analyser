import io
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from wordcloud import WordCloud
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import green, red, yellow, black, grey, white, blue, HexColor
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER # Import TA_CENTER for text alignment
import numpy as np
from typing import Dict # Import Dict from typing

# Import for consistent color logic
from modules.sentiment_analyzer import get_score_color

# --- Disclaimer Constants for Reports ---
DISCLAIMER_TEXT = "The 'Fraud App Detector' provides an analysis based solely on publicly available app review sentiment and does not involve deep technical analysis of the app's code or official investigative findings. This tool is for informational purposes only and should not be used as the sole basis for legal, financial, or investment decisions. Always conduct thorough due diligence."
DISCLAIMER_LINK = "https://support.google.com/googleplay/android-developer/answer/138230"

# New constants for risk messaging
RISK_WARNING_SHORT = "Strong indicators of potential risk identified"
RISK_ADVICE_UI = "Exercise caution and conduct further independent research before downloading, using, or trusting this app. Consider reporting the app directly to the Google Play Store or relevant authorities if you have concerns. Look for red flags such as unclear developer history, excessive permissions, or consistent scam reports elsewhere."


def create_sentiment_trend_chart(trend_df: pd.DataFrame, for_pdf: bool = True) -> plt.Figure:
    """
    Generates a matplotlib figure for sentiment trend over time.

    Args:
        trend_df (pd.DataFrame): DataFrame with sentiment counts indexed by date.
        for_pdf (bool): If True, optimizes for PDF embedding (smaller, no interactive elements).

    Returns:
        matplotlib.figure.Figure: The generated matplotlib figure.
    """
    fig, ax = plt.subplots(figsize=(8, 4) if for_pdf else (10, 6))
    if not trend_df.empty:
        trend_df.plot(ax=ax, grid=True, legend=True)
        ax.set_title("Sentiment Trend Over Time", fontsize=10 if for_pdf else 14, pad=5)
        ax.set_xlabel("Date", fontsize=8 if for_pdf else 12)
        ax.set_ylabel("Number of Reviews", fontsize=8 if for_pdf else 12)
        ax.tick_params(axis='x', labelsize=7 if for_pdf else 10)
        ax.tick_params(axis='y', labelsize=7 if for_pdf else 10)
        ax.legend(title='Sentiment', fontsize=7 if for_pdf else 10)
        ax.grid(True, linestyle='-', alpha=0.7)
    else:
        ax.text(0.5, 0.5, "No data for sentiment trend.", horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=10 if for_pdf else 12, color='gray')
        ax.set_title("Sentiment Trend Over Time (No Data)", fontsize=10 if for_pdf else 14, pad=5)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.tight_layout()
    return fig

def create_word_cloud_image(all_text: str, for_pdf: bool = True) -> plt.Figure:
    """
    Generates a matplotlib figure for a word cloud.

    Args:
        all_text (str): The concatenated text for the word cloud.
        for_pdf (bool): If True, optimizes for PDF embedding.

    Returns:
        matplotlib.figure.Figure: The generated matplotlib figure.
    """
    from wordcloud import WordCloud # Import here to avoid circular dependency if WordCloud is not used elsewhere
    fig, ax = plt.subplots(figsize=(8, 4) if for_pdf else (10, 5))
    if all_text.strip():
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(all_text)
        ax.imshow(wordcloud, interpolation="bilinear")
    else:
        ax.text(0.5, 0.5, "No review text available for keyword analysis.", horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=10 if for_pdf else 12, color='gray')
    ax.axis("off")
    fig.tight_layout()
    return fig

def create_comparison_barchart(app1_metrics: Dict, app2_metrics: Dict, app1_details: Dict, app2_details: Dict) -> io.BytesIO:
    """
    Generates a grouped bar chart for app comparison and returns it as a BytesIO buffer.
    """
    labels = ['Positive %', 'Negative %', 'Neutral %', 'App Rating']
    app1_vals = [app1_metrics['positive_pct'], app1_metrics['negative_pct'], app1_metrics['neutral_pct'], app1_metrics['app_rating_score']]
    app2_vals = [app2_metrics['positive_pct'], app2_metrics['negative_pct'], app2_metrics['neutral_pct'], app2_metrics['app_rating_score']]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, app1_vals, width, label=app1_details.get('title', 'App 1'), color='#3498db') # Blue
    rects2 = ax.bar(x + width/2, app2_vals, width, label=app2_details.get('title', 'App 2'), color='#e67e22') # Orange

    ax.set_ylabel('Scores (%)', fontsize=12)
    ax.set_title('App Comparison by Sentiment and Rating', fontsize=14, pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=0, ha='center', fontsize=10)
    ax.legend(fontsize=10)
    ax.set_ylim(0, 100)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    for rect in rects1 + rects2:
        height = rect.get_height()
        ax.annotate(f'{height:.1f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)

    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plt.close(fig)
    return buf


def generate_single_app_pdf_report(
    app_id: str,
    app_details: Dict,
    filtered_df: pd.DataFrame,
    sentiment_counts: pd.Series,
    positive_pct: float,
    negative_pct: float,
    neutral_pct: float,
    app_rating_score: float,
    playstore_score: float,
    fraud_threshold: int,
    trend_df: pd.DataFrame,
    all_text_for_wordcloud: str,
    report_df: pd.DataFrame = pd.DataFrame()
) -> io.BytesIO:
    """
    Generates a comprehensive PDF report for a single app analysis.

    Returns:
        io.BytesIO: A BytesIO buffer containing the PDF report.
    """
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='TableText', parent=styles['Normal'], wordWrap='CJK', fontSize=9))
    styles.add(ParagraphStyle(name='DisclaimerStyle', parent=styles['Normal'], fontSize=9, textColor=HexColor('#e74c3c')))
    styles.add(ParagraphStyle(name='DisclaimerLinkStyle', parent=styles['Normal'], fontSize=9, textColor=HexColor('#85c1e9')))
    styles.add(ParagraphStyle(name='RiskInfoStyle', parent=styles['Normal'], fontSize=10, textColor=HexColor('#555555'))) # New style for risk info
    styles.add(ParagraphStyle(name='CenteredH2', parent=styles['h2'], alignment=TA_CENTER)) # New style for centered H2
    styles.add(ParagraphStyle(name='CaptionText', parent=styles['Normal'], fontSize=8, textColor=HexColor('#555555')))

    story = []

    # Header and Title
    story.append(Paragraph("<b>App Analysis Summary Report</b>", styles['h1']))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Paragraph(f"App Name: {app_details['title'] if app_details else 'Unknown App'}", styles['Normal']))
    story.append(Paragraph(f"App ID: {app_id if app_id else 'Unknown'}", styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))

    # App Details Table
    story.append(Paragraph("<b>App Details</b>", styles['h2']))
    app_details_data = [
        ['Metric', 'Value'],
        ['Developer', app_details.get('developer', 'N/A')],
        ['Category', app_details.get('genre', 'N/A')],
        ['Installs', app_details.get('installs', 'N/A')],
        ['Released', app_details.get('released', 'N/A')],
        ['Play Store Score', f"{app_details.get('score', 0.0):.2f}"],
    ]
    app_details_table = Table(app_details_data, colWidths=[2.5*inch, 4*inch])
    app_details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), white),
        ('GRID', (0, 0), (-1, -1), 1, black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(app_details_table)
    story.append(Spacer(1, 0.2 * inch))


    # Review Summary (Metrics Table)
    story.append(Paragraph("<b>Review Summary</b>", styles['h2']))
    summary_data_table = [
        ['Total Reviews', 'Positive', 'Neutral', 'Negative'],
        [
            str(len(filtered_df)),
            f"{sentiment_counts.get('Positive', 0)} ({positive_pct:.1f}%)",
            f"{sentiment_counts.get('Neutral', 0)} ({neutral_pct:.1f}%)",
            f"{sentiment_counts.get('Negative', 0)} ({negative_pct:.1f}%)"
        ]
    ]
    summary_table = Table(summary_data_table, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), white),
        ('GRID', (0, 0), (-1, -1), 1, black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("<b>Summary of Findings</b>", styles['h2']))

    pdf_colors = {
        "Positive": green,
        "Neutral": yellow,
        "Negative": red,
    }

    summary_findings_data = [
        ['Metric', 'Value (%)', 'Status'],
        [Paragraph('Positive', styles['TableText']), f"{positive_pct:.1f}%", ''],
        [Paragraph('Neutral', styles['TableText']), f"{neutral_pct:.1f}%", ''],
        [Paragraph('Negative', styles['TableText']), f"{negative_pct:.1f}%", ''],
        [Paragraph('App Rating', styles['TableText']), f"{app_rating_score:.1f}%", ''],
        [Paragraph('PlayStore Score', styles['TableText']), f"{playstore_score:.1f}%", ''],
    ]

    summary_findings_table = Table(summary_findings_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
    summary_findings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), white),
        ('GRID', (0, 0), (-1, -1), 1, black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),

        ('TEXTCOLOR', (0, 1), (1, 1), pdf_colors['Positive']),
        ('TEXTCOLOR', (0, 2), (1, 2), pdf_colors['Neutral']),
        ('TEXTCOLOR', (0, 3), (1, 3), pdf_colors['Negative']),
        ('TEXTCOLOR', (0, 4), (1, 4), HexColor(get_score_color(app_rating_score))),
        ('TEXTCOLOR', (0, 5), (1, 5), HexColor(get_score_color(playstore_score))),
    ]))
    story.append(summary_findings_table)
    story.append(Spacer(1, 0.2 * inch))

    # Risk Alert (Updated messaging for PDF)
    if negative_pct > fraud_threshold:
        story.append(Paragraph(f"<font color='red'><b>🚨 {RISK_WARNING_SHORT} based on a high percentage of negative reviews ({negative_pct:.1f}%, exceeding your threshold of {fraud_threshold}%).</b></font>", styles['h3']))
        story.append(Paragraph(f"<font color='black'>Our analysis is based solely on public user review sentiment and does not involve deep technical analysis of the app's code or official investigative findings.</font>", styles['RiskInfoStyle']))
        story.append(Paragraph(f"<font color='black'>We strongly recommend conducting further independent research and due diligence before downloading, using, or trusting this app with personal information or financial data. If you have concerns, consider reporting the app directly to the Google Play Store or relevant authorities. Look for red flags such as unclear developer history, excessive permissions, or consistent scam reports elsewhere.</font>", styles['RiskInfoStyle']))
    else:
        story.append(Paragraph("<b>✅ No significant risk indicators found based on current analysis settings.</b>", styles['h3']))
    story.append(Spacer(1, 0.2 * inch))

    # Common Keywords in Reviews (Image)
    story.append(Paragraph("<b>Common Keywords in Reviews</b>", styles['CenteredH2']))
    keyword_img_fig = create_word_cloud_image(all_text_for_wordcloud, for_pdf=True)
    keyword_img_buf = io.BytesIO()
    keyword_img_fig.savefig(keyword_img_buf, format="png", bbox_inches="tight", dpi=100)
    keyword_img_buf.seek(0)
    plt.close(keyword_img_fig)
    img_keywords = ReportLabImage(keyword_img_buf)
    img_keywords.drawHeight = 2.5 * inch
    img_keywords.drawWidth = 5 * inch
    story.append(img_keywords)
    story.append(Spacer(1, 0.2 * inch))

    # Sentiment Trend Over Time (Image)
    story.append(Paragraph("<b>Sentiment Trend Over Time</b>", styles['CenteredH2']))
    trend_img_fig = create_sentiment_trend_chart(trend_df, for_pdf=True)
    trend_img_buf = io.BytesIO()
    trend_img_fig.savefig(trend_img_buf, format="png", bbox_inches="tight", dpi=100)
    trend_img_buf.seek(0)
    plt.close(trend_img_fig)
    img_trend = ReportLabImage(trend_img_buf)
    img_trend.drawHeight = 2.5 * inch
    img_trend.drawWidth = 5 * inch
    story.append(img_trend)
    story.append(Spacer(1, 0.2 * inch))

    # Detailed Reviews Table (First 10)
    story.append(Paragraph("<b>Sample Reviews</b>", styles['h2']))
    if not filtered_df.empty:
        review_table_data = [['Date/Time', 'Content', 'Sentiment']]
        for _, row in filtered_df[['datetime', 'content', 'sentiment']].head(10).iterrows():
            review_table_data.append([
                Paragraph(row['datetime'].strftime('%Y-%m-%d %H:%M'), styles['TableText']),
                Paragraph(row['content'], styles['TableText']),
                Paragraph(row['sentiment'], styles['TableText'])
            ])

        review_table = Table(review_table_data, colWidths=[1.2*inch, 4.3*inch, 1*inch])
        review_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), white),
            ('GRID', (0, 0), (-1, -1), 1, black),
            ('VALIGN', (0,0), (-1,-1), 'TOP')
        ]))
        story.append(review_table)
    else:
        story.append(Paragraph("No filtered reviews to display.", styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))

    # Model Training Report (Table)
    if not report_df.empty:
        story.append(Paragraph("<b>Sentiment Classifier Performance</b>", styles['CenteredH2']))
        story.append(Paragraph(
            "Metrics Description: <br/>- Precision: Proportion of correct positive predictions. <br/>- Recall: Proportion of actual positives correctly identified. <br/>- F1-score: Harmonic mean of precision and recall. <br/>- Support: Number of samples per class.",
            styles['CaptionText']
        ))
        story.append(Spacer(1, 0.1 * inch))
        # Modify model_report_data to include a new 'Class/Metric' column
        report_df_with_index = report_df.reset_index()
        report_df_with_index.rename(columns={'index': 'Class/Metric'}, inplace=True)
        model_report_data = [report_df_with_index.columns.tolist()] + report_df_with_index.values.tolist()

        model_table = Table(model_report_data)
        model_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), white),
            ('GRID', (0, 0), (-1, -1), 1, black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        story.append(model_table)
        story.append(Spacer(1, 0.2 * inch))

    # --- Disclaimer Section in PDF ---
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("---", styles['Normal']))
    story.append(Paragraph("<b>Disclaimer:</b>", styles['DisclaimerStyle']))
    story.append(Paragraph(DISCLAIMER_TEXT, styles['DisclaimerStyle']))
    story.append(Paragraph(f"Reference: <link href='{DISCLAIMER_LINK}'>{DISCLAIMER_LINK}</link>", styles['DisclaimerLinkStyle']))
    story.append(Spacer(1, 0.2 * inch))


    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer

def generate_comparison_pdf_report(
    app1_details: Dict,
    app2_details: Dict,
    app1_metrics: Dict,
    app2_metrics: Dict
) -> io.BytesIO:
    """
    Generates a PDF report comparing two apps.

    Returns:
        io.BytesIO: A BytesIO buffer containing the comparison PDF report.
    """
    pdf_buffer_comp = io.BytesIO()
    doc_comp = SimpleDocTemplate(pdf_buffer_comp, pagesize=letter)
    styles_comp = getSampleStyleSheet()
    styles_comp.add(ParagraphStyle(name='DisclaimerStyle', parent=styles_comp['Normal'], fontSize=9, textColor=HexColor('#e74c3c')))
    styles_comp.add(ParagraphStyle(name='DisclaimerLinkStyle', parent=styles_comp['Normal'], fontSize=9, textColor=HexColor('#85c1e9')))
    styles_comp.add(ParagraphStyle(name='CenteredH2', parent=styles_comp['h2'], alignment=TA_CENTER))

    story_comp = []

    # Header
    story_comp.append(Paragraph("<b>App Comparison Report</b>", styles_comp['h1']))
    story_comp.append(Spacer(1, 0.2 * inch))
    story_comp.append(Paragraph(f"<b>Comparing:</b> {app1_details['title']} vs. {app2_details['title']}", styles_comp['h2']))
    story_comp.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles_comp['Normal']))
    story_comp.append(Spacer(1, 0.2 * inch))

    # Details Table
    story_comp.append(Paragraph("<b>App Details</b>", styles_comp['h2']))
    details_data = [
        ['Metric', app1_details.get('title', 'App 1'), app2_details.get('title', 'App 2')],
        ['Developer', app1_details.get('developer', 'N/A'), app2_details.get('developer', 'N/A')],
        ['Category', app1_details.get('genre', 'N/A'), app2_details.get('genre', 'N/A')],
        ['Installs', app1_details.get('installs', 'N/A'), app2_details.get('installs', 'N/A')],
        ['Released', app1_details.get('released', 'N/A'), app2_details.get('released', 'N/A')],
    ]
    details_table = Table(details_data, colWidths=[1.5*inch, 2.75*inch, 2.75*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), grey), ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12), ('BACKGROUND', (0, 1), (-1, -1), white),
        ('GRID', (0, 0), (-1, -1), 1, black), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story_comp.append(details_table)
    story_comp.append(Spacer(1, 0.2 * inch))

    # Comparison Chart Image
    story_comp.append(Paragraph("<b>Comparison Chart</b>", styles_comp['CenteredH2']))
    chart_buf = create_comparison_barchart(app1_metrics, app2_metrics, app1_details, app2_details)
    img_chart = ReportLabImage(chart_buf)
    img_chart.drawHeight = 3 * inch
    img_chart.drawWidth = 6 * inch
    story_comp.append(img_chart)
    story_comp.append(Spacer(1, 0.2 * inch))

    # Metrics Table
    story_comp.append(Paragraph("<b>Comparison Metrics</b>", styles_comp['h2']))
    metrics_data = [
        ['Metric', app1_details.get('title', 'App 1'), app2_details.get('title', 'App 2')],
        ['Play Store Score (out of 5)', f"{app1_details.get('score', 0.0):.2f}", f"{app2_details.get('score', 0.0):.2f}"],
        ['App Rating Score (%)', f"{app1_metrics['app_rating_score']:.1f}%", f"{app2_metrics['app_rating_score']:.1f}%"],
        ['Positive Sentiment', f"{app1_metrics['positive_pct']:.1f}%", f"{app2_metrics['positive_pct']:.1f}%"],
        ['Negative Sentiment', f"{app1_metrics['negative_pct']:.1f}%", f"{app2_metrics['negative_pct']:.1f}%"],
        ['Neutral Sentiment', f"{app1_metrics['neutral_pct']:.1f}%", f"{app2_metrics['neutral_pct']:.1f}%"],
        ['Total Reviews Analyzed', str(app1_metrics['total']), str(app2_metrics['total'])],
    ]
    metrics_table = Table(metrics_data, colWidths=[2*inch, 2.5*inch, 2.5*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), grey), ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12), ('BACKGROUND', (0, 1), (-1, -1), white),
        ('GRID', (0, 0), (-1, -1), 1, black), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story_comp.append(metrics_table)
    story_comp.append(Spacer(1, 0.2 * inch))

    # --- Disclaimer Section in PDF ---
    story_comp.append(Spacer(1, 0.3 * inch))
    story_comp.append(Paragraph("---", styles_comp['Normal']))
    story_comp.append(Paragraph("<b>Disclaimer:</b>", styles_comp['DisclaimerStyle']))
    story_comp.append(Paragraph(DISCLAIMER_TEXT, styles_comp['DisclaimerStyle']))
    story_comp.append(Paragraph(f"Reference: <link href='{DISCLAIMER_LINK}'>{DISCLAIMER_LINK}</link>", styles_comp['DisclaimerLinkStyle']))
    story_comp.append(Spacer(1, 0.2 * inch))

    doc_comp.build(story_comp)
    pdf_buffer_comp.seek(0)
    return pdf_buffer_comp

