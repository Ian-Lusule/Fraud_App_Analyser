import pandas as pd
from textblob import TextBlob
from datetime import datetime
from typing import List, Dict # Import List and Dict from typing

# Define a list of words that should explicitly flag sentiment as negative
NEGATIVE_KEYWORDS = [
    "scam", "scum", "useless", "fraud", "fake", "deceptive", "ripoff",
    "unresponsive", "broken", "glitch", "buggy", "crash", "malware",
    "phishing", "steal", "stolen", "lie", "lying", "cheat", "cheating",
    "misleading", "unreliable", "waste of time", "terrible", "horrible",
    "worst", "bad experience", "do not install", "uninstall", "delete",
    "warning", "beware", "deceitful", "untrustworthy"
]

def analyze_sentiment(text: str) -> float:
    """
    Analyzes the sentiment polarity of a given text.
    Includes a check for explicit negative keywords to ensure strong negative flagging.

    Args:
        text (str): The input text.

    Returns:
        float: The sentiment polarity, ranging from -1.0 (negative) to 1.0 (positive).
               Returns 0 if the input is not a string.
    """
    if not isinstance(text, str):
        return 0

    lower_text = text.lower()
    for keyword in NEGATIVE_KEYWORDS:
        if keyword in lower_text:
            # If a negative keyword is found, force a strong negative polarity
            return -0.8 # A strong negative value, but not necessarily -1.0 to allow for nuance if other words are present

    # If no explicit negative keywords, proceed with TextBlob analysis
    return TextBlob(text).sentiment.polarity

def analyze_sentiment_batch(texts: List[str]) -> List[float]: # Changed list to List
    """
    Analyzes sentiment polarity for a batch of texts.

    Args:
        texts (List[str]): A list of text strings. # Changed list to List
    Returns:
        List[float]: A list of sentiment polarities corresponding to the input texts. # Changed list to List
    """
    return [analyze_sentiment(text) for text in texts]

def process_reviews(df: pd.DataFrame, pos_threshold: float, neg_threshold: float, progress_bar=None) -> pd.DataFrame:
    """
    Processes a DataFrame of reviews to add sentiment polarity and classification.

    Args:
        df (pd.DataFrame): DataFrame containing 'content' and 'at' (timestamp) columns.
        pos_threshold (float): Polarity threshold for positive sentiment.
        neg_threshold (float): Polarity threshold for negative sentiment.
        progress_bar (streamlit.DeltaGenerator, optional): A Streamlit progress bar to update.

    Returns:
        pd.DataFrame: The DataFrame with 'polarity', 'sentiment', and 'datetime' columns added.
    """
    if 'content' not in df.columns or 'at' not in df.columns:
        raise ValueError("DataFrame must contain 'content' and 'at' columns.")

    batch_size = 100
    polarities = []
    total_reviews = len(df)

    for i in range(0, total_reviews, batch_size):
        batch = df['content'][i:i + batch_size].tolist()
        polarities.extend(analyze_sentiment_batch(batch))
        if progress_bar:
            progress = 0.2 + (i + batch_size) / total_reviews * 0.6
            progress_bar.progress(min(progress, 0.8))

    df['polarity'] = polarities
    df['sentiment'] = df['polarity'].apply(
        lambda p: 'Positive' if p > pos_threshold else ('Negative' if p < neg_threshold else 'Neutral')
    )
    df['datetime'] = pd.to_datetime(df['at'])

    return df

def calculate_sentiment_metrics(filtered_df: pd.DataFrame, app_details: Dict) -> tuple: # Changed dict to Dict
    """
    Calculates various sentiment-related metrics for an app.

    Args:
        filtered_df (pd.DataFrame): DataFrame of filtered reviews with 'sentiment' column.
        app_details (Dict): Dictionary containing app details, including 'score'. # Changed dict to Dict

    Returns:
        tuple: (sentiment_counts, positive_pct, negative_pct, neutral_pct, app_rating_score, playstore_score)
    """
    sentiment_counts = filtered_df['sentiment'].value_counts()
    total_reviews = len(filtered_df)

    positive_pct = (sentiment_counts.get('Positive', 0) / total_reviews) * 100 if total_reviews > 0 else 0
    negative_pct = (sentiment_counts.get('Negative', 0) / total_reviews) * 100 if total_reviews > 0 else 0
    neutral_pct = (sentiment_counts.get('Neutral', 0) / total_reviews) * 100 if total_reviews > 0 else 0

    # Play Store score is usually out of 5, convert to percentage out of 100
    playstore_score = (app_details.get('score', 0.0)) * 20 if app_details and app_details.get('score') is not None else 0

    # Calculate app rating score based on sentiment distribution
    total_sentiment_reviews = sentiment_counts.get('Positive', 0) + sentiment_counts.get('Negative', 0) + sentiment_counts.get('Neutral', 0)
    if total_sentiment_reviews > 0:
        # A weighted average, giving more weight to positive, and some credit for neutral
        # This formula tries to approximate a score out of 100
        pos_score_calc = positive_pct + (neutral_pct * (positive_pct / (positive_pct + negative_pct)) if (positive_pct + negative_pct) > 0 else 0)
        app_rating_score = min(100, pos_score_calc)
    else:
        app_rating_score = 0 # No reviews to calculate score

    return sentiment_counts, positive_pct, negative_pct, neutral_pct, app_rating_score, playstore_score

def get_score_color(score: float, scale: float = 100) -> str:
    """
    Returns a hexadecimal color string based on the score value (VirusTotal style).

    Args:
        score (float): The score value.
        scale (float): The maximum possible score value.

    Returns:
        str: Hexadecimal color string (Green, Amber, or Red).
    """
    score_pct = (score / scale) * 100 if scale != 0 else 0
    if score_pct >= 75:
        return "#27ae60"  # Green
    elif score_pct >= 40:
        return "#f39c12"  # Amber/Yellow
    else:
        return "#e74c3c"  # Red

