import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
import streamlit as st # Used for st.secrets

# --- Disclaimer Constants for Email ---
DISCLAIMER_TEXT_EMAIL = "The 'Fraud App Detector' provides an analysis based on publicly available app review sentiment and does not definitively label an app as fraudulent. This tool is for informational purposes only and should not be used as the sole basis for legal or financial decisions. Always conduct thorough due diligence."
DISCLAIMER_LINK_EMAIL = "https://support.google.com/googleplay/android-developer/answer/138230" # Placeholder: User should replace with actual legal reference

def send_analysis_email(
    user_name: str,
    user_email: str,
    app_details: dict,
    app_id: str,
    filtered_df: pd.DataFrame,
    sentiment_counts: dict,
    positive_pct: float,
    negative_pct: float,
    neutral_pct: float,
    app_rating_score: float,
    playstore_score: float,
    fraud_threshold: int,
    csv_data: bytes,
    pdf_data: bytes,
    sender_email: str,
    sender_password: str,
    smtp_server: str,
    smtp_port: int
):
    """
    Sends an email with the app analysis summary and attached CSV/PDF reports.

    Args:
        user_name (str): The name of the recipient.
        user_email (str): The email address of the recipient.
        app_details (dict): Dictionary containing app details.
        app_id (str): The ID of the analyzed app.
        filtered_df (pd.DataFrame): DataFrame of filtered reviews.
        sentiment_counts (dict): Counts of positive, neutral, negative reviews.
        positive_pct (float): Percentage of positive reviews.
        negative_pct (float): Percentage of negative reviews.
        neutral_pct (float): Percentage of neutral reviews.
        app_rating_score (float): Calculated app rating score.
        playstore_score (float): Play Store's official score.
        fraud_threshold (int): The configured fraud alert threshold.
        csv_data (bytes): The content of the CSV report as bytes.
        pdf_data (bytes): The content of the PDF report as bytes.
        sender_email (str): The sender's email address.
        sender_password (str): The sender's email password (app-specific password recommended).
        smtp_server (str): The SMTP server address.
        smtp_port (int): The SMTP server port.
    """
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = user_email
    msg['Subject'] = f"📊 Fraud App Analysis Report - {app_details['title'] if app_details else 'Unknown App'} ({datetime.now().strftime('%Y-%m-%d %H:%M')})"

    body = f"""
    <html>
        <body>
            <h3>Dear {user_name},</h3>

            <p>Thank you for choosing <strong>Fraud App Analyzer</strong>. We are pleased to provide you with a detailed analysis of the app <strong>{app_details['title'] if app_details else 'Unknown App'}</strong> (App ID: <strong>{app_id if app_id else 'Unknown'}</strong>).</p>

            <h3>📊 Summary of Findings:</h3>
            <ul>
                <li><strong>Total Reviews Analyzed:</strong> <span style="color:#3498db;"><strong>{len(filtered_df)}</strong></span></li>
                <li><strong>Positive Reviews:</strong> <span style="color:#27ae60;"><strong>{sentiment_counts.get('Positive', 0)} ({positive_pct:.1f}%)</strong></span></li>
                <li><strong>Neutral Reviews:</strong> <span style="color:#f39c12;"><strong>{sentiment_counts.get('Neutral', 0)} ({neutral_pct:.1f}%)</strong></span></li>
                <li><strong>Negative Reviews:</strong> <span style="color:#e74c3c;"><strong>{sentiment_counts.get('Negative', 0)} ({negative_pct:.1f}%)</strong></span></li>
                <li><strong>App Rating Score:</strong> <span style="color:#3498db;"><strong>{app_rating_score:.1f}%</strong></span></li>
                <li><strong>Play Store Score:</strong> <span style="color:#3498db;"><strong>{playstore_score:.1f}%</strong></span></li>
            </ul>

            <p><strong>🚨 Fraud Alert:</strong><br>
            {('A high number of negative reviews was detected. <strong style="color:#e74c3c;">This app may be fraudulent.</strong>' if negative_pct > fraud_threshold else 'No significant fraud indicators were found.')}</p>

            <p>Please find attached the detailed CSV and PDF reports for your reference.</p>

            <p>---</p>
            <p style="font-size:0.8em; color:#7f8c8d;"><b>Disclaimer:</b> {DISCLAIMER_TEXT_EMAIL}</p>
            <p style="font-size:0.8em; color:#7f8c8d;">Reference: <a href="{DISCLAIMER_LINK_EMAIL}" target="_blank" style="color:#85c1e9; text-decoration:none;">{DISCLAIMER_LINK_EMAIL}</a></p>
            <p>---</p>

            <p>Warm regards,<br>
            <strong>The Fraud App Analyzer Team</strong></p>
        </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))

    # Attach CSV
    csv_part = MIMEApplication(csv_data, Name=f"{app_id}_review_analysis.csv")
    csv_part['Content-Disposition'] = f'attachment; filename="{app_id}_review_analysis.csv"'
    msg.attach(csv_part)

    # Attach PDF
    pdf_part = MIMEApplication(pdf_data, Name=f"{app_id}_full_app_summary.pdf")
    pdf_part['Content-Disposition'] = f'attachment; filename="{app_id}_full_app_summary.pdf"'
    msg.attach(pdf_part)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)
        server.send_message(msg)

