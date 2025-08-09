import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import io
from datetime import datetime
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Import from google_play_scraper directly for search functionality
from google_play_scraper import search, Sort

# Import modularized functions
from modules.ui_components import (
    set_page_config_and_styles,
    display_app_result_row,
    display_metric_card,
    circular_display,
    display_comparison_bar,
    display_disclaimer
)
from modules.data_fetcher import fetch_app_details, fetch_reviews
from modules.sentiment_analyzer import (
    analyze_sentiment,
    analyze_sentiment_batch,
    process_reviews,
    calculate_sentiment_metrics,
    get_score_color
)
from modules.report_generator import (
    create_sentiment_trend_chart,
    create_word_cloud_image,
    create_comparison_barchart,
    generate_single_app_pdf_report,
    generate_comparison_pdf_report,
    DISCLAIMER_TEXT, DISCLAIMER_LINK,
    RISK_WARNING_SHORT, RISK_ADVICE_UI
)
from modules.email_sender import RISK_WARNING_EMAIL, RISK_ADVICE_EMAIL, send_analysis_email

# ---------------------------- UI Configuration ----------------------------
set_page_config_and_styles()

st.markdown('<div class="header"><h1>📱 Fraud App Detector</h1></div>', unsafe_allow_html=True)
st.markdown("""
<div class="main">
    <p>Analyze Google Play Store apps for potential fraud using sentiment analysis of reviews. Search by app name or URL, customize settings, and compare apps.</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'selected_app' not in st.session_state:
    st.session_state.selected_app = None
if 'app1_id' not in st.session_state:
    st.session_state.app1_id = None
if 'app2_id' not in st.session_state:
    st.session_state.app2_id = None
if 'app1_details' not in st.session_state:
    st.session_state.app1_details = None
if 'app2_details' not in st.session_state:
    st.session_state.app2_details = None

# ----------------------- App Input & Settings ------------------------
st.markdown("### 🔍 Search for an App", unsafe_allow_html=True)
col1, col2 = st.columns([3, 1])
with col1:
    input_val = st.text_input("Enter App Name or Paste Play Store Link", placeholder="e.g., com.example.app or app name", key="search_input")
with col2:
    country = st.selectbox("Country", ["us", "gb", "in", "ke","tz", "ca", "de", "fr", "jp", "ng", "au"], index=3, key="country_select")

max_reviews = st.slider("Maximum Reviews to Analyze", 100, 10000, 500, 100, key="max_reviews_slider")

if input_val:
    try:
        match = re.search(r"id=([a-zA-Z0-9._]+)", input_val)
        if match:
            app_id_from_url = match.group(1)
            app_details_from_url = fetch_app_details(app_id_from_url, country)
            if app_details_from_url:
                display_app_result_row(app_details_from_url)
                if st.button(f"Analyze '{app_details_from_url['title']}'", key=f"analyze_direct_{app_id_from_url}"):
                    st.session_state.selected_app = app_id_from_url
                    st.rerun()
            else:
                st.warning(f"Could not find app details for '{app_id_from_url}'. Please check the ID.")
        else:
            app_name = input_val
            results = search(app_name, lang='en', country=country)
            if not results:
                st.warning(f"No apps found for the search term '{app_name}'. Please try a different name or use a Play Store URL.")
            else:
                st.markdown("### 🎯 Select App to Analyze or Compare", unsafe_allow_html=True)
                for i, app_result in enumerate(results[:10]):
                    app_id = app_result['appId']

                    cols = st.columns([0.1, 0.45, 0.1, 0.15, 0.15]) # Icon, Title, Rating, Analyze, Compare

                    with cols[0]:
                        st.image(app_result['icon'], width=40)
                    with cols[1]:
                        st.markdown(f"<b>{app_result['title']}</b>", unsafe_allow_html=True)
                    with cols[2]:
                        score = app_result.get('score')
                        formatted_score = f"{score:.2f}" if score is not None else "0.00"
                        st.write(f"{formatted_score} ⭐")
                    with cols[3]:
                        if st.button("Analyze", key=f"analyze_{app_id}_{i}"):
                            st.session_state.selected_app = app_id
                            # playstore_score is calculated in sentiment_analyzer now
                            st.rerun()
                    with cols[4]:
                        if st.button("Compare", key=f"compare_{app_id}_{i}", help="Add this app to comparison"):
                            if st.session_state.app1_id is None:
                                st.session_state.app1_id = app_id
                                st.session_state.app1_details = fetch_app_details(app_id, country)
                                st.success(f"'{app_result['title']}' added as App 1 for comparison.")
                            elif st.session_state.app2_id is None:
                                if app_id != st.session_state.app1_id:
                                    st.session_state.app2_id = app_id
                                    st.session_state.app2_details = fetch_app_details(app_id, country)
                                    st.success(f"'{app_result['title']}' added as App 2 for comparison.")
                                else:
                                    st.warning("Cannot compare an app to itself. Please select a different app for App 2.")
                            else:
                                st.warning("You can only compare two apps at a time. Click 'Clear Compared Apps' below to select new apps.")
                            st.rerun()
    except Exception as e:
        st.error(f"Error processing app input: {str(e)}")

# ----------------------- Sentiment Analysis Settings ------------------------
st.markdown("---")
st.markdown("### ⚙️ Analysis Settings", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    pos_threshold = st.slider("Positive Sentiment Threshold", 0.0, 1.0, 0.1, 0.05, key="pos_threshold")
with col2:
    neg_threshold = st.slider("Negative Sentiment Threshold", -1.0, 0.0, -0.1, 0.05, key="neg_threshold")
with col3:
    fraud_threshold = st.slider("Risk Alert Threshold (% Negative)", 10, 50, 30, 5, key="fraud_threshold")

# ----------------------- Sentiment Analysis ------------------------
if st.session_state.selected_app:
    st.markdown("---")
    st.markdown("## 🔍 Analyzing Reviews", unsafe_allow_html=True)
    progress_bar = st.progress(0.0)
    app_id = st.session_state.selected_app
    app_details = fetch_app_details(app_id, country)
    raw_reviews = fetch_reviews(app_id, country, max_reviews)
    progress_bar.progress(0.2)

    if not raw_reviews:
        st.error("No reviews found for this app or an error occurred during fetching. Please try a different app or adjust review limits.")
        st.session_state.selected_app = None
    else:
        df = pd.DataFrame(raw_reviews)
        if 'content' not in df.columns:
            st.error("No valid review content found in the fetched data.")
            st.session_state.selected_app = None
        else:
            # Process reviews and add sentiment
            df = process_reviews(df, pos_threshold, neg_threshold, progress_bar)
            progress_bar.progress(0.9)

            # --- START NEW SECTION: CURRENTLY ANALYZING APP ---
            st.markdown("---")
            st.markdown("### 🔍 Currently Analyzing", unsafe_allow_html=True)
            if app_details:
                app_title = app_details.get('title', 'Unknown App')
                app_icon = app_details.get('icon', 'https://www.gstatic.com/android/market_images/web/play_store_512.png')
                app_url = f"https://play.google.com/store/apps/details?id={st.session_state.selected_app}"

                st.markdown(f"""
                <div class="current-app-card">
                    <img src="{app_icon}" onerror="this.src='https://placehold.co/60x60/cccccc/000000?text=No+Img';">
                    <div>
                        <h4>{app_title}</h4>
                        <p><a href="{app_url}" target="_blank">View on Play Store</a></p>
                        <p><b>Category:</b> {app_details.get('genre', 'N/A')}</p>
                        <p><b>Installs:</b> {app_details.get('installs', 'N/A')}</p>
                        <p><b>Released:</b> {app_details.get('released', 'N/A')}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info(f"Analyzing App ID: **{st.session_state.selected_app}**. Details loading or not available.")
            # --- END NEW SECTION ---

            # ----------------------- Review Filtering ------------------------
            st.markdown("---")
            st.markdown("### 🔎 Filter Reviews", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                sentiment_filter = st.multiselect("Filter by Sentiment", ["Positive", "Neutral", "Negative"], default=["Positive", "Neutral", "Negative"], key="sentiment_filter")
            with col2:
                min_date = df['datetime'].min().date() if not df.empty else datetime.now().date()
                max_date = df['datetime'].max().date() if not df.empty else datetime.now().date()
                date_range = st.date_input("Select Date Range", [min_date, max_date], key="date_range")

            if len(date_range) == 2:
                filtered_df = df[
                    (df['sentiment'].isin(sentiment_filter)) &
                    (df['datetime'].dt.date >= date_range[0]) &
                    (df['datetime'].dt.date <= date_range[1])
                ]
            else:
                filtered_df = df[
                    (df['sentiment'].isin(sentiment_filter)) &
                    (df['datetime'].dt.date >= date_range[0])
                ]

            if filtered_df.empty:
                st.warning("No reviews match the selected filters. Try adjusting the date range or sentiment filter.")
            else:
                st.dataframe(filtered_df[['datetime', 'content', 'sentiment']].head(10), use_container_width=True)

                # ----------------------- Sentiment Trend Calculation ------------------------
                trend_df = filtered_df.groupby([filtered_df['datetime'].dt.date, 'sentiment']).size().unstack().fillna(0)

                # ----------------------- Visualizations (UI Display) ------------------------
                st.markdown("---")
                # Streamlit UI display for Sentiment Trend (controlled by checkbox)
                if st.checkbox("Show Sentiment Trend Over Time", key="show_trend_ui"):
                    st.markdown("### 📈 Sentiment Trend Over Time", unsafe_allow_html=True)
                    fig_trend_ui = create_sentiment_trend_chart(trend_df, for_pdf=False)
                    st.pyplot(fig_trend_ui)
                    plt.close(fig_trend_ui)

                # Streamlit UI display for Common Keywords (controlled by checkbox)
                if st.checkbox("Show Common Keywords in Reviews", key="show_keywords_ui"):
                    st.markdown("### 🔤 Common Keywords in Reviews", unsafe_allow_html=True)
                    all_text_ui = " ".join(filtered_df['content'].dropna())
                    if all_text_ui.strip():
                        fig_wordcloud_ui = create_word_cloud_image(all_text_ui, for_pdf=False)
                        st.pyplot(fig_wordcloud_ui)
                        plt.close(fig_wordcloud_ui)
                    else:
                        st.warning("No text available for keyword analysis.")


                # ----------------------- Metrics ------------------------
                st.markdown("---")
                st.markdown("### 🧮 Review Summary", unsafe_allow_html=True)
                sentiment_counts, positive_pct, negative_pct, neutral_pct, app_rating_score, playstore_score = \
                    calculate_sentiment_metrics(filtered_df, app_details)

                cols = st.columns(4)
                with cols[0]:
                    display_metric_card("Total Reviews", len(filtered_df))
                with cols[1]:
                    display_metric_card("Positive", sentiment_counts.get('Positive', 0))
                with cols[2]:
                    display_metric_card("Neutral", sentiment_counts.get('Neutral', 0))
                with cols[3]:
                    display_metric_card("Negative", sentiment_counts.get('Negative', 0))

                st.markdown("---")
                st.markdown("### 🧾 Summary of Findings", unsafe_allow_html=True)
                cols = st.columns(5)
                with cols[0]: circular_display("Positive", positive_pct)
                with cols[1]: circular_display("Neutral", neutral_pct)
                with cols[2]: circular_display("Negative", negative_pct)
                with cols[3]: circular_display("App Rating", app_rating_score)
                with cols[4]: circular_display("PlayStore Score", playstore_score)

                if negative_pct > fraud_threshold:
                    # Updated warning message on UI
                    st.error(f"🚨 {RISK_WARNING_SHORT} ({negative_pct:.1f}% negative reviews, based on your threshold of {fraud_threshold}%). {RISK_ADVICE_UI}")
                else:
                    st.success("✅ No significant risk indicators found based on current analysis settings.")

                # ----------------------- Model Training ------------------------
                st.markdown("---")
                st.markdown("### 🤖 Sentiment Classifier", unsafe_allow_html=True)
                label_map = {'Positive': 1, 'Negative': 0, 'Neutral': 2}
                if 'sentiment' in df.columns:
                    df['label'] = df['sentiment'].map(label_map)
                else:
                    df['label'] = 0

                if len(df['label'].unique()) > 1:
                    if len(df) > 1:
                        try:
                            # Using the original logic for model training, as it's self-contained
                            from sklearn.model_selection import train_test_split
                            from sklearn.ensemble import RandomForestClassifier
                            from sklearn.metrics import classification_report

                            X_train, X_test, y_train, y_test = train_test_split(
                                df[['polarity']], df['label'],
                                test_size=0.3, random_state=42,
                                stratify=df['label'] if len(df['label'].unique()) > 1 and df['label'].value_counts().min() >= 2 else None
                            )
                            clf = RandomForestClassifier(random_state=42)
                            clf.fit(X_train, y_train)
                            y_pred = clf.predict(X_test)
                            unique_labels = sorted(df['label'].unique())
                            target_names = [k for k, v in label_map.items() if v in unique_labels]

                            try:
                                report_dict = classification_report(y_test, y_pred, target_names=target_names, labels=unique_labels, output_dict=True, zero_division=0)
                                report_df = pd.DataFrame(report_dict).transpose().round(2)
                                st.table(report_df)
                            except ValueError as ve:
                                st.warning(f"Could not generate full classification report: {ve}. This might happen if a sentiment category is missing in the test set or has too few samples for evaluation after split.")
                        except ValueError as e:
                            st.warning(f"Could not split data for model training: {e}. This usually means not enough data points per class or overall for the chosen test size.")
                    else:
                        st.warning("Not enough reviews for effective model training and testing (need more than 1 review).")
                else:
                    st.warning("Not enough unique sentiment labels for model training (need at least two types of sentiment).")

                progress_bar.progress(1.0)

                # ----------------------- Export Options ------------------------
                st.markdown("---")
                st.markdown("### 💾 Export Results", unsafe_allow_html=True)
                csv = filtered_df[['datetime', 'content', 'sentiment', 'polarity']].to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download CSV Report", data=csv, file_name=f'{app_id}_review_analysis.csv', mime='text/csv', key="download_csv")

                st.markdown("### 🧾 Download Full Report", unsafe_allow_html=True)

                # Generate PDF report
                pdf_buffer = generate_single_app_pdf_report(
                    app_id, app_details, filtered_df, sentiment_counts,
                    positive_pct, negative_pct, neutral_pct, app_rating_score,
                    playstore_score, fraud_threshold, trend_df,
                    " ".join(filtered_df['content'].dropna()),
                    report_df if 'report_df' in locals() else pd.DataFrame() # Pass report_df if it exists
                )
                st.download_button("📥 Download Full PDF Report", data=pdf_buffer, file_name=f"{app_id}_full_app_summary.pdf", mime="application/pdf", key="download_pdf")

                # ----------------------- Email Report ------------------------
                st.markdown("---")
                st.markdown("### 📧 Email Report", unsafe_allow_html=True)
                user_name = st.text_input("Enter your name:", key="email_name")
                user_email = st.text_input("Enter your email address to receive the report:", key="email_address")

                # Using Streamlit secrets for sensitive information
                sender_email = st.secrets.get("EMAIL_SENDER", "info@lusule.com")
                sender_password = st.secrets.get("EMAIL_PASSWORD", "YOUR_EMAIL_PASSWORD_HERE") # IMPORTANT: Replace with your actual app-specific password or retrieve from secrets
                smtp_server = st.secrets.get("SMTP_SERVER", "mail.lusule.com")
                smtp_port = st.secrets.get("SMTP_PORT", 587)


                if st.button("Send Email Report", key="send_email_button"):
                    if not user_email or not user_name:
                        st.warning("Please enter your name and email address.")
                    else:
                        try:
                            send_analysis_email(
                                user_name, user_email, app_details, app_id, filtered_df,
                                sentiment_counts, positive_pct, negative_pct, neutral_pct,
                                app_rating_score, playstore_score, fraud_threshold,
                                csv, pdf_buffer.getvalue(),
                                sender_email, sender_password, smtp_server, smtp_port
                            )
                            st.success(f"Report successfully sent to {user_email}!")
                        except smtplib.SMTPAuthenticationError:
                            st.error("Email sending failed: Authentication error. Please check your sender email and password in Streamlit secrets.")
                        except smtplib.SMTPConnectError:
                            st.error("Email sending failed: Could not connect to the SMTP server. Please check the server address and port.")
                        except Exception as e:
                            st.error(f"Failed to send email: {e}. Please ensure your email settings are correct and try again.")

# ----------------------- App Comparison Section ------------------------
st.markdown("---")
st.markdown("## 🆚 Compare Apps", unsafe_allow_html=True)

if st.session_state.app1_id and st.session_state.app2_id:
    app1_details = st.session_state.app1_details
    app2_details = st.session_state.app2_details

    col_app1, col_clear, col_app2 = st.columns([1, 0.5, 1])

    with col_app1:
        if app1_details:
            st.markdown(f"""
            <div class="comparison-card">
                <img src="{app1_details['icon']}" onerror="this.src='https://placehold.co/40x40/cccccc/000000?text=No+Img';">
                <div class="details">
                    <b>App 1: {app1_details['title']}</b><br>
                    <span class="rating">Score: {app1_details.get('score', 0.0):.2f} ⭐</span>
                    <p style="font-size:0.9em; margin: 2px 0;"><b>Category:</b> {app1_details.get('genre', 'N/A')}</p>
                    <p style="font-size:0.9em; margin: 2px 0;"><b>Installs:</b> {app1_details.get('installs', 'N/A')}</p>
                    <p style="font-size:0.9em; margin: 2px 0;"><b>Released:</b> {app1_details.get('released', 'N/A')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    with col_clear:
        if st.button("Clear Compared Apps", key="clear_compare_apps"):
            st.session_state.app1_id = None
            st.session_state.app2_id = None
            st.session_state.app1_details = None
            st.session_state.app2_details = None
            st.rerun()
    with col_app2:
        if app2_details:
            st.markdown(f"""
            <div class="comparison-card">
                <img src="{app2_details['icon']}" onerror="this.src='https://placehold.co/40x40/cccccc/000000?text=No+Img';">
                <div class="details">
                    <b>App 2: {app2_details['title']}</b><br>
                    <span class="rating">Score: {app2_details.get('score', 0.0):.2f} ⭐</span>
                    <p style="font-size:0.9em; margin: 2px 0;"><b>Category:</b> {app2_details.get('genre', 'N/A')}</p>
                    <p style="font-size:0.9em; margin: 2px 0;"><b>Installs:</b> {app2_details.get('installs', 'N/A')}</p>
                    <p style="font-size:0.9em; margin: 2px 0;"><b>Released:</b> {app2_details.get('released', 'N/A')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    if app1_details and app2_details:
        st.markdown("### Comparison Metrics", unsafe_allow_html=True)

        # Fetch reviews and analyze sentiment for both apps
        @st.cache_data
        def get_sentiment_metrics_for_comparison(app_id_val, country_val, max_reviews_val, pos_thresh, neg_thresh):
            app_reviews = fetch_reviews(app_id_val, country_val, max_reviews_val)
            if not app_reviews:
                return {"total": 0, "positive_pct": 0, "negative_pct": 0, "neutral_pct": 0, "app_rating_score": 0}

            df_app = pd.DataFrame(app_reviews)
            if 'content' not in df_app.columns:
                return {"total": 0, "positive_pct": 0, "negative_pct": 0, "neutral_pct": 0, "app_rating_score": 0}

            # Use the modularized sentiment analysis functions
            df_app['polarity'] = df_app['content'].apply(analyze_sentiment)
            df_app['sentiment'] = df_app['polarity'].apply(
                lambda p: 'Positive' if p > pos_thresh else ('Negative' if p < neg_thresh else 'Neutral')
            )

            sentiment_counts_app, positive_pct_app, negative_pct_app, neutral_pct_app, app_rating_score_app, _ = \
                calculate_sentiment_metrics(df_app, None) # Pass None for app_details as it's not needed for playstore_score here

            return {
                "total": len(df_app),
                "positive_pct": positive_pct_app,
                "negative_pct": negative_pct_app,
                "neutral_pct": neutral_pct_app,
                "app_rating_score": app_rating_score_app
            }

        app1_metrics = get_sentiment_metrics_for_comparison(st.session_state.app1_id, country, max_reviews, pos_threshold, neg_threshold)
        app2_metrics = get_sentiment_metrics_for_comparison(st.session_state.app2_id, country, max_reviews, pos_threshold, neg_threshold)

        # Display comparison bars
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; font-weight: bold; color: #eee; margin-bottom: 10px;">
            <div style="flex: 1; text-align: center; padding-right: 5px;">{app1_details['title']}</div>
            <div style="flex: 1; text-align: center; padding-left: 5px;">{app2_details['title']}</div>
        </div>
        """, unsafe_allow_html=True)


        display_comparison_bar("Play Store Score", app1_details.get('score', 0.0), app2_details.get('score', 0.0), max_value=5.0,
                               app1_title=app1_details['title'], app2_title=app2_details['title'])
        display_comparison_bar("Total Reviews", app1_metrics["total"], app2_metrics["total"], max_value=max(1, app1_metrics["total"], app2_metrics["total"]),
                               app1_title=app1_details['title'], app2_title=app2_details['title'])
        display_comparison_bar("App Rating Score (%)", app1_metrics["app_rating_score"], app2_metrics["app_rating_score"], max_value=100.0,
                               app1_title=app1_details['title'], app2_title=app2_details['title'])
        display_comparison_bar("Positive Sentiment (%)", app1_metrics["positive_pct"], app2_metrics["positive_pct"], max_value=100.0,
                               app1_title=app1_details['title'], app2_title=app2_details['title'])
        display_comparison_bar("Negative Sentiment (%)", app1_metrics["negative_pct"], app2_metrics["negative_pct"], max_value=100.0,
                               app1_title=app1_details['title'], app2_title=app2_details['title'])
        display_comparison_bar("Neutral Sentiment (%)", app1_metrics["neutral_pct"], app2_metrics["neutral_pct"], max_value=100.0,
                               app1_title=app1_details['title'], app2_title=app2_details['title'])

        # --- Comparison PDF Export ---
        st.markdown("---")
        st.markdown("### 💾 Export Comparison Report", unsafe_allow_html=True)

        pdf_buffer_comp = generate_comparison_pdf_report(
            app1_details, app2_details, app1_metrics, app2_metrics
        )

        st.download_button(
            "📥 Download Comparison PDF Report",
            data=pdf_buffer_comp,
            file_name=f"comparison_{st.session_state.app1_id}_vs_{st.session_state.app2_id}.pdf",
            mime="application/pdf",
            key="download_comparison_pdf"
        )


elif st.session_state.app1_id is None and st.session_state.app2_id is None:
    st.info("Select two apps using the 'Compare' button above to see a detailed comparison.")
else:
    st.info("Select a second app to compare.")

# ----------------------- Disclaimer Section ------------------------
st.markdown("---")
display_disclaimer()
