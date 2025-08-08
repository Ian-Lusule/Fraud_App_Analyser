import streamlit as st
from modules.sentiment_analyzer import get_score_color # Import for consistent color logic
from modules.report_generator import DISCLAIMER_TEXT, DISCLAIMER_LINK # Import disclaimer constants

def set_page_config_and_styles():
    """
    Sets the Streamlit page configuration and applies custom CSS styles
    for a dark theme, responsiveness, and improved aesthetics.
    """
    st.set_page_config(page_title="Fraud App Analyzer", page_icon="📱", layout="wide")
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

        /* General body and background */
        body {
            font-family: 'Inter', sans-serif;
            color: #E0E0E0; /* Slightly brighter light text for dark background */
            background-color: #121212; /* Even darker background for body */
        }

        /* Streamlit main container adjustments for responsiveness */
        .stApp {
            max-width: 1200px; /* Max width for desktop */
            margin: auto; /* Center content */
            padding: 20px;
        }

        /* Header styling */
        .header {
            background-color: #1F2E3D; /* Dark blue/gray for header */
            color: white;
            padding: 15px 25px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .header h1 {
            color: white !important;
            margin: 0;
            font-size: 2.5em; /* Larger font for header */
            font-weight: 700;
        }

        /* Main content area */
        .main {
            background-color: #1A1A1A; /* Slightly lighter dark for main content */
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            margin-bottom: 20px;
            color: #E0E0E0; /* Ensure text is light */
        }
        .main p {
            color: #E0E0E0 !important;
            line-height: 1.6;
        }

        /* Input fields and select boxes */
        div[data-testid="stTextInput"] > div > input,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] {
            background-color: #2C2C2C; /* Distinct darker background for inputs */
            color: #F0F0F0; /* Very light text */
            border: 1px solid #555;
            border-radius: 8px; /* More rounded corners */
            padding: 8px 12px;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);
        }
        div[data-testid="stTextInput"] > label,
        div[data-testid="stSelectbox"] label {
            color: #D0D0D0; /* Label color */
            font-weight: 600;
            margin-bottom: 5px;
        }
        /* Options in dropdown */
        div[data-baseweb="popover"] div[role="listbox"] {
            background-color: #2C2C2C; /* Match input background */
            color: #F0F0F0; /* Match input text */
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }
        div[data-baseweb="popover"] div[role="option"] {
            color: #F0F0F0;
            padding: 10px 15px;
        }
        div[data-baseweb="popover"] div[role="option"]:hover {
            background-color: #444;
        }

        /* App search result rows */
        .app-result-row {
            display: flex;
            align-items: center;
            background-color: #252525; /* Slightly lighter dark background for results */
            padding: 12px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            margin: 10px 0;
            color: #E0E0E0;
            transition: transform 0.2s ease-in-out;
        }
        .app-result-row:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        .app-result-row img {
            max-width: 50px; /* Slightly larger icon */
            max-height: 50px;
            margin-right: 15px;
            border-radius: 10px;
            object-fit: cover;
        }
        .app-result-row .details {
            flex-grow: 1;
            font-size: 17px; /* Slightly larger text */
            font-weight: bold;
            color: #E0E0E0;
        }
        .app-result-row .rating {
            font-size: 16px;
            color: #B0B0B0; /* Slightly subdued color for rating */
            margin-left: 10px;
            white-space: nowrap; /* Prevent wrapping for rating */
        }

        /* Metric Cards */
        .metric-card {
            background-color: #252525; /* Darker card background */
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            color: #E0E0E0;
            text-align: center;
            margin: 10px 0;
            border: 1px solid #3A3A3A;
        }
        .metric-card b {
            font-size: 1.1em;
            color: #85C1E9; /* Light blue for labels */
        }
        .metric-card span {
            font-size: 1.6em;
            font-weight: bold;
            display: block;
            margin-top: 5px;
        }

        /* Streamlit Buttons */
        .stButton > button {
            background-color: #3498db; /* Blue */
            color: white;
            border: none;
            padding: 10px 18px;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease-in-out;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            margin: 5px; /* Add margin for spacing */
        }
        .stButton > button:hover {
            background-color: #2980b9; /* Darker blue on hover */
            transform: translateY(-2px);
            box-shadow: 0 6px 10px rgba(0,0,0,0.3);
        }
        /* Specific styling for 'Compare' button */
        .stButton > button[key*="compare_"] {
            background-color: #2ecc71; /* Green for compare */
        }
        .stButton > button[key*="compare_"]:hover {
            background-color: #27ae60;
        }
        /* Clear Compared Apps button */
        .stButton > button[key="clear_compare_apps"] {
            background-color: #e74c3c; /* Red */
        }
        .stButton > button[key="clear_compare_apps"]:hover {
            background-color: #c0392b;
        }

        /* Adjust button width/alignment for app search results */
        /* This targets the container of the buttons within the app result columns */
        div[data-testid^="stColumn"] > div > div > div > div > div.stButton {
            display: flex;
            justify-content: flex-end; /* Align buttons to the right */
            gap: 8px; /* Space between buttons */
            flex-wrap: nowrap; /* Prevent wrapping on desktop */
        }

        /* Ensure buttons within app result rows are compact on mobile */
        @media (max-width: 768px) {
            /* Target the specific column that holds the Analyze/Compare buttons */
            div[data-testid^="stColumn"]:nth-of-type(4), /* Analyze button column */
            div[data-testid^="stColumn"]:nth-of-type(5) { /* Compare button column */
                flex-basis: auto !important; /* Allow content to dictate width */
                width: auto !important; /* Override fixed widths if any */
                max-width: unset !important; /* Remove max-width constraints */
            }

            div[data-testid^="stColumn"] > div > div > div > div > div.stButton {
                flex-direction: row; /* Keep buttons in a row */
                justify-content: center; /* Center buttons horizontally */
                flex-wrap: wrap; /* Allow wrapping if space is very limited */
                gap: 5px; /* Smaller gap on mobile */
            }
            div[data-testid^="stColumn"] > div > div > div > div > div.stButton button {
                width: auto; /* Allow buttons to size based on content */
                min-width: 80px; /* Ensure minimum size */
                padding: 8px 12px; /* Slightly smaller padding */
                font-size: 14px; /* Smaller font size */
                flex-grow: 1; /* Allow buttons to grow to fill space */
            }
        }


        /* Compare Apps Section Container */
        div[data-testid="stVerticalBlock"] > div > div:nth-child(2) > div:nth-child(3) {
            background-color: #1F2E3D; /* Darker blue/gray for the compare section */
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 6px 15px rgba(0,0,0,0.4);
            margin-top: 30px;
            border: 1px solid #34495e;
        }

        /* Individual Comparison Cards */
        .comparison-card {
            display: flex;
            align-items: center;
            background-color: #2C3E50; /* Slightly lighter dark for individual cards */
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            margin: 8px 0;
            min-height: 70px; /* Ensure consistent height */
            color: #E0E0E0;
            border: 1px solid #4A647A;
        }
        .comparison-card img {
            max-width: 50px;
            max-height: 50px;
            margin-right: 15px;
            border-radius: 10px;
            object-fit: cover;
        }
        .comparison-card .details {
            flex-grow: 1;
            font-size: 17px;
            font-weight: bold;
            color: #E0E0E0;
        }
        .comparison-card .rating {
            color: #B0B0B0;
            font-size: 15px;
        }

        /* Current App Analyzing Card */
        .current-app-card {
            display: flex;
            align-items: center;
            gap: 15px;
            background-color: #252525;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #444;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }
        .current-app-card img {
            width: 60px;
            height: 60px;
            border-radius: 12px;
            object-fit: cover;
        }
        .current-app-card h4 {
            margin: 0;
            color: #85C1E9 !important; /* Light blue for app title */
            font-size: 1.4em;
        }
        .current-app-card p {
            margin: 0;
            font-size: 0.9em;
        }
        .current-app-card a {
            color: #BBCCEE !important;
            text-decoration: none;
            transition: color 0.2s;
        }
        .current-app-card a:hover {
            color: #99AACC !important;
            text-decoration: underline;
        }


        /* Text elements for better contrast */
        h1, h2, h3, h4, h5, h6, strong, p, span, li, table {
            color: #E0E0E0 !important; /* Ensure all text is light on dark background */
        }
        /* Streamlit specific text elements */
        .stMarkdown, .stText, .stAlert {
            color: #E0E0E0 !important;
        }
        .stMarkdown p, .stText p {
            color: #E0E0E0 !important;
        }
        /* Warning and Success messages */
        div[data-testid="stAlert"] div[role="alert"] {
            color: inherit !important;
        }
        div[data-testid="stAlert"] div[role="alert"] span {
            color: inherit !important;
        }

        /* Styles for the football-style comparison bars */
        .bar-container {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            width: 100%;
            flex-wrap: wrap; /* Allow wrapping on small screens */
            justify-content: center; /* Center items on small screens */
        }
        .bar-label-wrapper {
            width: 100%; /* Full width for label on small screens */
            text-align: center;
            font-weight: bold;
            color: #E0E0E0;
            margin-bottom: 5px;
            font-size: 1.1em;
        }
        .bar-values-wrapper {
            display: flex;
            align-items: center;
            width: 100%; /* Full width for values and bars */
            justify-content: space-between;
        }
        .bar-value {
            min-width: 50px; /* Space for the numeric value */
            text-align: center;
            font-weight: bold;
            color: #E0E0E0;
            font-size: 1em;
            padding: 0 5px;
        }
        .bars-wrapper {
            display: flex;
            flex-grow: 1;
            align-items: center;
            justify-content: space-between;
            margin: 0 10px;
        }
        .bar {
            height: 30px; /* Taller bars */
            border-radius: 5px; /* More rounded */
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            white-space: nowrap;
            overflow: hidden;
            position: relative;
            transition: width 0.3s ease-in-out; /* Smooth transition for width changes */
        }
        .bar.left {
            margin-right: 5px;
            justify-content: flex-end;
            padding-right: 8px;
        }
        .bar.right {
            margin-left: 5px;
            justify-content: flex-start;
            padding-left: 8px;
        }
        .bar-positive { background-color: #27ae60; } /* Green */
        .bar-negative { background-color: #e74c3c; } /* Red */
        .bar-neutral { background-color: #7f8c8d; } /* Blue-gray */
        .bar-score { background-color: #3498db; } /* Blue for general score */
        .bar-score.good { background-color: #27ae60; }
        .bar-score.bad { background-color: #e74c3c; }

        /* Circular Display Styling */
        .circular-metric-container {
            display: inline-block;
            margin: 10px;
            text-align: center;
            width: 120px; /* Fixed width for consistent layout */
        }
        .circular-metric-circle {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            border: 2px solid rgba(255,255,255,0.1); /* Subtle border */
        }
        .circular-metric-content {
            text-align: center;
            color:white;
            font-size:24px; /* Larger percentage */
            font-weight:bold;
        }
        .circular-metric-label {
            font-size:14px; /* Smaller label */
            font-weight: normal;
            display: block;
            margin-top: 5px;
            color: rgba(255,255,255,0.8);
        }

        /* Responsive adjustments */
        @media (max-width: 768px) {
            .stApp {
                padding: 10px;
            }
            .header h1 {
                font-size: 1.8em;
            }
            .main {
                padding: 15px;
            }
            .app-result-row {
                flex-direction: column;
                align-items: flex-start;
            }
            .app-result-row img {
                margin-bottom: 10px;
            }
            .app-result-row .details, .app-result-row .rating {
                width: 100%;
                text-align: left;
                margin-left: 0;
            }
            .stButton > button {
                width: 100%; /* Full width buttons on small screens */
                margin: 5px 0;
            }
            /* This was the problematic rule, removed as the new one above is more precise */
            /* .st-emotion-cache-1jmve3k {
                flex-direction: column;
                gap: 0;
            } */
            /* .st-emotion-cache-1jmve3k button {
                width: 100%;
            } */
            .bar-container {
                flex-direction: column;
                align-items: center;
            }
            .bar-label-wrapper {
                margin-bottom: 10px;
            }
            .bar-values-wrapper {
                flex-direction: column;
                align-items: center;
            }
            .bar-value {
                margin-bottom: 5px;
            }
            .bars-wrapper {
                flex-direction: row; /* Keep bars side-by-side */
                width: 100%;
                margin: 0;
            }
            .bar.left, .bar.right {
                width: 48% !important; /* Adjust width for smaller bars */
                flex-grow: 0; /* Prevent unwanted growth */
            }
            .circular-metric-container {
                width: 100px;
                height: 100px;
                margin: 5px;
            }
            .circular-metric-circle {
                width: 100px;
                height: 100px;
            }
            .circular-metric-content {
                font-size: 20px;
            }
            .circular-metric-label {
                font-size: 12px;
            }
        }

        @media (max-width: 480px) {
            .circular-metric-container {
                width: 80px;
                height: 80px;
            }
            .circular-metric-circle {
                width: 80px;
                height: 80px;
            }
            .circular-metric-content {
                font-size: 16px;
            }
            .circular-metric-label {
                font-size: 10px;
            }
        }

        /* Disclaimer Styling */
        .disclaimer-box {
            background-color: #1F2E3D; /* Dark blue/gray, matching header */
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #34495e;
            margin-top: 30px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }
        .disclaimer-box h3 {
            color: #E74C3C !important; /* Red for emphasis */
            margin-top: 0;
            font-weight: 700;
        }
        .disclaimer-box p {
            color: #E0E0E0 !important;
            line-height: 1.5;
            margin-bottom: 10px;
        }
        .disclaimer-box a {
            color: #85C1E9 !important; /* Light blue for link */
            text-decoration: none;
            font-weight: 600;
        }
        .disclaimer-box a:hover {
            text-decoration: underline;
        }

    </style>
    """, unsafe_allow_html=True)

def display_app_result_row(app_result):
    """
    Displays a single app search result row with icon, title, and rating.
    """
    app_id = app_result['appId']
    score = app_result.get('score')
    formatted_score = f"{score:.2f}" if score is not None else "0.00"
    st.markdown(f"""
    <div class="app-result-row">
        <img src="{app_result['icon']}" onerror="this.src='https://placehold.co/50x50/cccccc/000000?text=No+Img';">
        <div class="details">
            <b>{app_result['title']}</b>
        </div>
        <div class="rating">{formatted_score} ⭐</div>
    </div>
    """, unsafe_allow_html=True)

def display_metric_card(label, value):
    """
    Displays a stylized metric card.
    """
    st.markdown(f"<div class='metric-card'><b>{label}</b><br><span style='color: white;'>{value}</span></div>", unsafe_allow_html=True)

def circular_display(label, value, scale=100):
    """
    Displays a circular metric with a color based on score.
    """
    # Define colors based on the review summary screenshot:
    color_map = {
        "Positive": "#27ae60",  # Green
        "Neutral": "#f39c12",   # Amber/Yellow
        "Negative": "#e74c3c",  # Red
    }
    if "Rating" in label or "Score" in label:
        display_color = get_score_color(value, scale)
    else:
        display_color = color_map.get(label, "#3498db") # Default to blue if not found

    st.markdown(f"""
    <div class="circular-metric-container">
        <div class="circular-metric-circle" style="background:{display_color};">
            <div class="circular-metric-content">{value:.1f}%<span class="circular-metric-label">{label}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_comparison_bar(label, value1, value2, max_value=100, app1_title="", app2_title=""):
    """
    Displays a football-style comparison bar for two values.
    """
    val1_formatted = f"{value1:.1f}%" if "%)" in label else (f"{value1:.2f}" if "Score" in label else str(value1))
    val2_formatted = f"{value2:.1f}%" if "%)" in label else (f"{value2:.2f}" if "Score" in label else str(value2))

    # Calculate widths as percentages of the max_value
    # Ensure a minimum width for visibility if value is zero or very small
    min_bar_width_percent = 2 # Minimum percentage for bar visibility
    width1_raw = (value1 / max_value) * 100 if max_value > 0 and value1 is not None else 0
    width2_raw = (value2 / max_value) * 100 if max_value > 0 and value2 is not None else 0

    width1 = max(width1_raw, min_bar_width_percent if width1_raw > 0 else 0)
    width2 = max(width2_raw, min_bar_width_percent if width2_raw > 0 else 0)

    # Adjust colors based on metric type
    color1 = "#3498db" # Default blue
    color2 = "#3498db" # Default blue

    if "Positive" in label:
        color1, color2 = "#27ae60", "#27ae60" # Green
    elif "Negative" in label:
        color1, color2 = "#e74c3c", "#e74c3c" # Red
    elif "Neutral" in label:
        color1, color2 = "#7f8c8d", "#7f8c8d" # Blue-gray
    elif "Score" in label or "Rating" in label:
        color1 = get_score_color(value1, max_value)
        color2 = get_score_color(value2, max_value)


    st.markdown(f"""
    <div class="bar-container">
        <div class="bar-label-wrapper">{label}</div>
        <div class="bar-values-wrapper">
            <div class="bar-value">{val1_formatted}</div>
            <div class="bars-wrapper">
                <div class="bar left" style="width:{width1:.1f}%; background-color:{color1};"></div>
                <div class="bar right" style="width:{width2:.1f}%; background-color:{color2};"></div>
            </div>
            <div class="bar-value">{val2_formatted}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def display_disclaimer():
    """
    Displays the legal disclaimer on the Streamlit UI.
    """
    st.markdown(f"""
    <div class="disclaimer-box">
        <h3>Important Disclaimer</h3>
        <p><b>{DISCLAIMER_TEXT}</b></p>
        <p>For more information on the legal considerations of app analysis and data usage, please refer to: <a href="{DISCLAIMER_LINK}" target="_blank">{DISCLAIMER_LINK}</a></p>
    </div>
    """, unsafe_allow_html=True)
