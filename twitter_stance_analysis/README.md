# Bluesky Stance Analysis Tool

A comprehensive web application for analyzing social media users' stance on the Israeli-Palestinian conflict using Bluesky posts. This tool combines natural language processing, sentiment analysis, and keyword detection to provide detailed insights into user perspectives.

## 🌟 Features

- **Real-time Analysis**: Analyze any Bluesky user's stance instantly
- **Multi-factor Analysis**: Combines keyword detection, sentiment analysis, and engagement metrics
- **Interactive Web Interface**: Clean, modern UI with real-time results
- **Detailed Visualizations**: Pie charts showing stance distribution
- **Post-by-Post Breakdown**: Individual analysis of each post with highlighted keywords
- **Confidence Scoring**: Measures the reliability of stance predictions
- **Data Export**: Saves analysis results and raw data for further study

## 🏗️ Architecture

The project consists of several key components:

### Core Modules

- **`bluesky_scraper.py`**: Handles API authentication and data collection from Bluesky
- **`stance_analyzer.py`**: Performs stance analysis using NLP and machine learning techniques
- **`analyze_user.py`**: Orchestrates the analysis pipeline
- **`app.py`**: Flask web application server

### Data Flow

1. **Authentication**: Uses stored credentials or guest access to Bluesky API
2. **Data Collection**: Fetches up to 100 recent posts from the target user
3. **Feature Extraction**: Extracts text, entities, and engagement metrics
4. **Stance Analysis**: Applies keyword detection and sentiment analysis
5. **Visualization**: Generates charts and saves results
6. **Web Display**: Presents results through the Flask interface

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Bluesky account (optional, for better rate limits)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd twitter_stance_analysis
   ```

2. **Install dependencies**:
   ```bash
   cd webApp
   pip install -r requirements.txt
   ```

3. **Set up credentials** (optional):
   Create a `tokenskeys.env` file in the `webApp` directory:
   ```json
   {
     "bluesky_handle": "your_handle.bsky.social",
     "bluesky_app_password": "your_app_password"
   }
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the web interface**:
   Open your browser and go to `http://127.0.0.1:5000`

### Usage

1. Enter a Bluesky handle (e.g., `user.bsky.social`)
2. Click "Analyze" to start the analysis
3. View results including:
   - Overall stance classification
   - Confidence score
   - Stance distribution chart
   - Individual post analysis with highlighted keywords

## 🔧 Configuration

### Key Settings (`config.py`)

- **`POSTS_PER_USER`**: Number of posts to analyze (default: 100)
- **`STANCE_WEIGHTS`**: Weights for different analysis factors
- **`COLOR_PALETTE`**: Colors for stance visualization
- **`LOG_LEVEL`**: Logging verbosity

### Analysis Parameters

The stance analyzer uses multiple factors:

- **Keyword Detection** (70% weight): Identifies pro-Israeli and pro-Palestinian terms
- **Sentiment Analysis** (30% weight): Analyzes emotional tone and context
- **Confidence Scoring**: Based on post consistency and stance clarity

## 📊 Analysis Methodology

### Stance Classification

The system classifies posts into three categories:

- **Pro-Israeli**: Posts supporting Israel's position
- **Pro-Palestinian**: Posts supporting Palestine's position  
- **Neutral/Unclear**: Posts without clear stance or mixed signals

### Keyword Detection

#### Pro-Israeli Keywords
- General: `israel`, `israeli`, `zionist`, `jewish state`
- Support: `stand with israel`, `support israel`, `defend israel`
- Military: `idf`, `israel defense forces`, `iron dome`
- Historical: `holocaust`, `october 7`, `simchat torah massacre`
- Religious: `jewish`, `judaism`, `jerusalem`

#### Pro-Palestinian Keywords
- General: `palestine`, `palestinian`, `gaza`, `west bank`
- Support: `free palestine`, `support palestine`, `palestine will be free`
- Political: `hamas`, `resistance`, `end the occupation`
- Human Rights: `occupation`, `apartheid`, `genocide`, `humanitarian crisis`
- Historical: `nakba`, `palestinian history`

### Confidence Scoring

Confidence is calculated using:
- **Signal Strength**: Average absolute stance scores
- **Consistency**: Percentage of posts with clear stance
- **Variance**: Standard deviation of stance scores

## 📁 Project Structure

```
twitter_stance_analysis/
├── webApp/                          # Main application directory
│   ├── app.py                      # Flask web server
│   ├── analyze_user.py             # Analysis orchestration
│   ├── bluesky_scraper.py          # Bluesky API integration
│   ├── stance_analyzer.py          # Core analysis engine
│   ├── config.py                   # Configuration settings
│   ├── requirements.txt            # Python dependencies
│   ├── templates/
│   │   └── index.html             # Web interface template
│   └── static/
│       ├── styles.css             # Custom CSS styles
│       └── visualizations/        # Generated charts
├── data/                           # Data storage
│   ├── raw/                       # Raw Bluesky posts
│   ├── processed/                 # Analysis results
│   └── visualizations/            # Generated charts
├── tests/                         # Test files
└── README.md                      # This file
```

## 🔍 Example Analysis

### Sample Results

For user `@noatishby.bsky.social`:
- **Overall Stance**: Pro-Israeli
- **Confidence**: 43.3%
- **Average Score**: 0.303 (30.3% pro-Israeli)
- **Stance Distribution**:
  - Pro-Israeli: 63.2%
  - Neutral/Unclear: 31.6%
  - Pro-Palestinian: 5.3%

### Post Analysis Features

Each post is analyzed with:
- **Stance Classification**: Individual stance determination
- **Score**: Numerical stance strength (-1 to +1)
- **Keyword Highlighting**: Color-coded stance-related terms
- **Component Scores**: Breakdown of keyword and sentiment factors

## 🛠️ Development

### Adding New Features

1. **New Analysis Factors**: Modify `stance_analyzer.py` to add new scoring methods
2. **Additional Keywords**: Update keyword lists in `stance_analyzer.py`
3. **UI Enhancements**: Modify `templates/index.html` and `static/styles.css`
4. **API Integration**: Extend `bluesky_scraper.py` for additional data sources


## 📝 License

This project is for educational and research purposes. Please use responsibly and respect user privacy.

## 🆘 Troubleshooting

### Common Issues

1. **Authentication Errors**: Check your `tokenskeys.env` file format
2. **Rate Limiting**: The app automatically handles rate limits with retries
3. **User Not Found**: Ensure the Bluesky handle is correct and public
4. **No Posts**: Some users may have no public posts or very few posts

### Logs

Check `stance_analysis.log` for detailed error information and debugging.



**Note**: This tool is designed for educational and research purposes. Always respect user privacy and platform terms of service when collecting and analyzing social media data.
