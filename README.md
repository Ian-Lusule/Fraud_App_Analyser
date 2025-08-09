# 📱 Fraud App Analyzer

## Project Overview
The **Fraud App Analyzer** is a Streamlit-based web application designed to help users identify potentially fraudulent applications on the Google Play Store by analyzing public user reviews.  
It leverages sentiment analysis to gauge public opinion and provides detailed reports, comparison features, and email functionalities to share insights.  

This project aims to provide an **informational tool** for users to perform initial due diligence on mobile applications.

---

## Features

### 🔍 App Search & Selection
- Search for Google Play Store apps by name or direct Play Store URL.

### 📊 Sentiment Analysis
- Analyze user reviews to determine sentiment (**Positive**, **Neutral**, **Negative**) using **TextBlob**.

### ⚙️ Customizable Thresholds
- Adjust sentiment thresholds and a **"fraud alert"** percentage to fine-tune analysis.

### 📈 Interactive Data Visualization
- Display sentiment distribution with clear metrics.
- Visualize sentiment trends over time.
- Generate word clouds to identify common keywords in reviews.

### 🔄 App Comparison
- Compare two apps side-by-side based on sentiment and rating metrics.

### 📝 Comprehensive Reporting
- Download CSV reports of analyzed reviews.
- Generate PDF summary reports for single apps or comparisons (with charts & metrics).

### 📧 Email Integration
- Send analysis reports directly via email.

### 📱 Responsive UI
- Works seamlessly across desktop and mobile devices.

### ⚠️ Legal Disclaimer
- Prominent disclaimer in UI, PDF reports, and emails stating analysis is **for informational purposes only**.

---

## Project Structure
```
.
└── Fraud_App_Analyser
    ├── fraud_app_analyzer3.py        # Main app file
    ├── requirements.txt              # Dependencies
    ├── venv                          # Virtual environment
    ├── .streamlit                    # Streamlit config (secrets.toml)
    └── modules
        ├── __init__.py
        ├── ui_components.py
        ├── data_fetcher.py
        ├── sentiment_analyzer.py
        ├── report_generator.py
        └── email_sender.py
```

---

## Module Breakdown

### `fraud_app_analyzer3.py`
Main Streamlit app:
- Manages UI flow & session state.
- Calls data fetching, sentiment analysis, and reporting functions.

### `modules/ui_components.py`
- UI rendering & custom CSS for dark theme.
- Responsive design adjustments.

### `modules/data_fetcher.py`
- Uses `google_play_scraper` to fetch app details & reviews.
- Utilizes Streamlit caching.

### `modules/sentiment_analyzer.py`
- Sentiment analysis using **TextBlob**.
- Flags reviews with **negative keywords** like `"scam"`, `"fraud"`.

### `modules/report_generator.py`
- Generates PDF reports (single & comparison).
- Includes charts & disclaimer text.

### `modules/email_sender.py`
- Sends analysis reports via email.
- Uses credentials stored securely in Streamlit secrets.

---

## Setup Instructions

### **Prerequisites**
- Python 3.8+
- `pip` package manager

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Ian-Lusule/Fraud_App_Analyser.git
cd Fraud_App_Analyser
```

### 2️⃣ Create a Virtual Environment
```bash
python3 -m venv venv
```
Activate it:

**macOS/Linux**
```bash
source venv/bin/activate
```
**Windows (Command Prompt)**
```bash
.\venv\Scripts\activate.bat
```
**Windows (PowerShell)**
```powershell
.\venv\Scripts\Activate.ps1
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

**requirements.txt**
```
streamlit
google-play-scraper
textblob
pandas
numpy
matplotlib
scikit-learn
reportlab
wordcloud
```

### 4️⃣ Configure Streamlit Secrets (Email Feature)
```bash
mkdir -p .streamlit
```
Create `.streamlit/secrets.toml`:
```toml
EMAIL_SENDER = "your_email@example.com"
EMAIL_PASSWORD = "APP_SPECIFIC_PASSWORD"
SMTP_SERVER = "smtp.server.com"
SMTP_PORT = 587
```

---

## Usage

Run the app:
```bash
streamlit run fraud_app_analyzer3.py
```

Access via browser: [http://localhost:8501](http://localhost:8501)

### How to Use:
1. **Search** — Enter app name or Play Store URL.  
2. **Select App** — Analyze a single app or choose two for comparison.  
3. **Adjust Settings** — Set max reviews, sentiment thresholds, and fraud alert percentage.  
4. **Review Analysis** — View summaries, charts, and keywords.  
5. **Export/Email Reports** — Download CSV/PDF or send via email.  
6. **Compare Apps** — See side-by-side metrics.

---

## Important Disclaimer
The Fraud App Analyzer is an **analytical tool** using public app review sentiment.  
It **does not** definitively label any app as fraudulent.  
Use it **for informational purposes only** and perform independent due diligence.

---

## Contributing
Pull requests and issues are welcome:  
[GitHub Repository](https://github.com/Ian-Lusule/Fraud_App_Analyser)

---

## License
This project is licensed under the **MIT License**.
