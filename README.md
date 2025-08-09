# 📱 Fraud App Analyzer

![License](https://img.shields.io/github/license/Ian-Lusule/Fraud_App_Analyser?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-ff4b4b?style=flat-square&logo=streamlit)
![Contributions welcome](https://img.shields.io/badge/Contributions-Welcome-brightgreen?style=flat-square)
![Issues](https://img.shields.io/github/issues/Ian-Lusule/Fraud_App_Analyser?style=flat-square)
![Stars](https://img.shields.io/github/stars/Ian-Lusule/Fraud_App_Analyser?style=flat-square)

---

## 📑 Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#-features)
3. [Technical Architecture & Libraries](#-technical-architecture--libraries)
4. [Weaknesses & Limitations](#-weaknesses--limitations)
5. [Advantages](#-advantages)
6. [Important Disclaimer](#-important-disclaimer)
7. [Future Improvements](#-future-improvements)
8. [Project Structure](#-project-structure)
9. [Module Breakdown](#-module-breakdown)
10. [Setup Instructions](#️-setup-instructions)
11. [Usage](#-usage)
12. [Contributing](#-contributing)
13. [License](#-license)

---

## 🎥 Demo Screenshot / GIF

![Fraud App Analyzer Demo](docs/demo.gif)

---

## Project Overview
The **Fraud App Analyzer** is a Streamlit-based web application meticulously designed to empower users in identifying potentially problematic or fraudulent applications on the Google Play Store.  
It performs **comprehensive sentiment analysis** on public user reviews, providing actionable insights through **detailed reports**, **side-by-side comparisons**, and **integrated email functionalities** for seamless sharing.

**Core Mission:**  
Serve as an informational and preliminary screening tool, enabling users to conduct initial due diligence on mobile applications before downloading or engaging with them.

---

## ✨ Features
### 🔍 App Search & Selection
- Search for Google Play Store apps by **name** or **URL**.
- Displays essential details (icon, title, Play Store rating).
- Analyze an app in-depth or add to a comparison list.

### 📊 Sentiment Analysis
- Uses **TextBlob** to classify reviews into **Positive**, **Neutral**, or **Negative**.
- Flags reviews containing **negative keywords** (e.g., "scam", "fraud", "useless").
- Ensures subtle negative feedback is captured.

### ⚙️ Customizable Thresholds
- Adjust positive/negative sentiment thresholds.
- Set a **risk alert percentage** to trigger warnings when negative sentiment exceeds your preference.

### 📈 Interactive Data Visualization
- **Sentiment Distribution** charts.
- **Sentiment Trends Over Time** with line graphs.
- **Word Cloud** for frequent review terms.
- Visuals embedded in both the UI and generated PDF reports.

### 🔄 App Comparison
- Compare **two apps side-by-side**:
  - Play Store score
  - Review count
  - Calculated sentiment percentages
  - Category, installs, and release date
- "Football-style" bar visuals for quick metric comparison.

### 📝 Comprehensive Reporting
- **CSV Reports** with detailed review data.
- **PDF Reports** with charts, key metrics, and disclaimers.
- Enhanced sentiment classifier performance table.

### 📧 Email Integration
- Send CSV/PDF reports directly via email.
- Secure handling of credentials with **Streamlit secrets**.
- Summary and disclaimer included in email body.

### 📱 Responsive UI
- Mobile-friendly, dark theme.
- Consistent look across devices.

### ⚠️ Legal Disclaimer
- Integrated throughout UI, PDF reports, and emails.
- States the tool is **for informational purposes only** and not definitive proof of fraud.

---

## 🛠 Technical Architecture & Libraries
- **Framework & UI:** `streamlit`
- **Data Fetching:** `google-play-scraper`, `pandas`
- **Sentiment Analysis:** `textblob`, custom keyword filtering, `wordcloud`
- **Machine Learning:** `scikit-learn`, `RandomForestClassifier`
- **Reporting & Email:** `reportlab`, `matplotlib`, `smtplib`, Python `email` libs

---

## ⚠️ Weaknesses & Limitations
- Relies solely on public reviews — cannot detect hidden malicious code.
- Sentiment analysis may misclassify sarcasm/jargon.
- Risk alert is **not legal proof**.
- Large-scale scraping may face rate limits.
- Small datasets can affect accuracy.
- Email security depends on safe credential handling.

---

## ✅ Advantages
- User-friendly and intuitive.
- Early warning system for suspicious apps.
- Transparent, explainable results.
- Customizable thresholds.
- Professional, shareable reports.
- Fully open-source and extensible.

---

## 📜 Important Disclaimer
The Fraud App Analyzer **does not label any app as fraudulent**.  
It highlights **risk indicators** from public reviews and user-defined thresholds.  
Always perform **independent verification** before installing or using an app.

---

## 🚀 Future Improvements
- BERT/RoBERTa-based NLP.
- Multi-language support.
- Aspect-based sentiment analysis.
- Developer reputation metrics.
- Permission analysis.
- Anomaly detection in reviews.
- Historical trend forecasting.
- Proxy rotation for large-scale scraping.
- Transactional email service integration.

---

## 📂 Project Structure
```

Fraud\_App\_Analyser/
├── fraud\_app\_analyzer3.py
├── requirements.txt
├── venv/
├── .streamlit/
└── modules/
├── **init**.py
├── ui\_components.py
├── data\_fetcher.py
├── sentiment\_analyzer.py
├── report\_generator.py
└── email\_sender.py

````

---

## 🧩 Module Breakdown
- **fraud_app_analyzer3.py** — Main UI & workflow.
- **ui_components.py** — Custom UI elements.
- **data_fetcher.py** — Fetches app info & reviews.
- **sentiment_analyzer.py** — Runs sentiment classification.
- **report_generator.py** — Builds PDF reports.
- **email_sender.py** — Sends emails.

---

## ⚙️ Setup Instructions
### 1️⃣ Clone Repository
```bash
git clone https://github.com/Ian-Lusule/Fraud_App_Analyser.git
cd Fraud_App_Analyser
````

### 2️⃣ Create Virtual Environment

```bash
python3 -m venv venv
```

Activate:

```bash
# macOS/Linux
source venv/bin/activate
# Windows (CMD)
.\venv\Scripts\activate.bat
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Email Secrets

```bash
mkdir -p .streamlit
nano .streamlit/secrets.toml
```

```toml
EMAIL_SENDER = "your_email@example.com"
EMAIL_PASSWORD = "APP_SPECIFIC_PASSWORD"
SMTP_SERVER = "smtp.your-email-provider.com"
SMTP_PORT = 587
```

---

## ▶️ Usage

```bash
streamlit run fraud_app_analyzer3.py
```

Open browser: [http://localhost:8501](http://localhost:8501)

---

## 🤝 Contributing

Contributions are welcome!
Fork, make changes, and submit a PR via [GitHub](https://github.com/Ian-Lusule/Fraud_App_Analyser).

---

## 📄 License

This project is licensed under the **MIT License**.


