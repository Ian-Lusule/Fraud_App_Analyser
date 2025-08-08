import streamlit as st
from google_play_scraper import app, reviews, Sort, search # Ensure search is imported if used directly in main app

@st.cache_data
def fetch_app_details(app_id: str, country: str):
    """
    Fetches details for a given app ID from Google Play Store.

    Args:
        app_id (str): The ID of the app (e.g., 'com.example.app').
        country (str): The country code for the Play Store (e.g., 'us', 'ke').

    Returns:
        dict: A dictionary containing app details, or None if an error occurs.
    """
    try:
        return app(app_id, lang='en', country=country)
    except Exception as e:
        st.error(f"Error fetching app details for {app_id}: {str(e)}")
        return None

@st.cache_data
def fetch_reviews(app_id: str, country: str, max_reviews: int):
    """
    Fetches a specified maximum number of reviews for a given app ID.

    Args:
        app_id (str): The ID of the app.
        country (str): The country code for the Play Store.
        max_reviews (int): The maximum number of reviews to fetch.

    Returns:
        list: A list of review dictionaries.
    """
    try:
        all_reviews = []
        continuation_token = None
        # Fetch reviews in batches until max_reviews is reached or no more reviews
        while len(all_reviews) < max_reviews:
            count_to_fetch = min(200, max_reviews - len(all_reviews)) # Fetch up to 200 reviews per call
            if count_to_fetch <= 0:
                break

            result, new_token = reviews(
                app_id,
                lang='en',
                country=country,
                count=count_to_fetch,
                sort=Sort.NEWEST, # Sort by newest reviews
                continuation_token=continuation_token
            )
            all_reviews.extend(result)
            if not new_token or len(result) < count_to_fetch: # Stop if no more token or fewer reviews than requested
                break
            continuation_token = new_token
        return all_reviews[:max_reviews] # Return exactly max_reviews or fewer if not available
    except Exception as e:
        st.error(f"Error fetching reviews for {app_id}: {str(e)}")
        return []
