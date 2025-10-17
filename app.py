# app.py

import os
import json  
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
import pandas as pd
import nltk
from utils.data_preprocessing import preprocess_data, GAME_TITLE_COLUMN
from utils.sentiment_analysis import analyze_sentiment
from utils.visualization import generate_sentiment_distribution

# Load environment variables from .env file
load_dotenv()

# --- NLTK DATA DOWNLOAD ---
nltk.download('stopwords')
nltk.download('wordnet')
# -------------------------

app = Flask(__name__)

# Ensure the static/plots directory exists
os.makedirs('static/plots', exist_ok=True)
os.makedirs('data', exist_ok=True)

# Get the API key from environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def get_ai_analysis(sentiment_counts, game_data, avg_polarity):
    """
    Calls the OpenRouter API to get an AI analysis of the sentiment data.
    """
    if not OPENROUTER_API_KEY:
        return "Error: OpenRouter API key is not configured."

    # Prepare the data for the prompt
    total_reviews = sum(sentiment_counts.values())
    positive_reviews = sentiment_counts.get('positive', 0)
    negative_reviews = sentiment_counts.get('negative', 0)
    neutral_reviews = sentiment_counts.get('neutral', 0)
    
    # Find the game with the most positive and most negative reviews
    most_positive_game = max(game_data['positive'], key=game_data['positive'].get) if game_data and 'positive' in game_data else 'N/A'
    most_negative_game = max(game_data['negative'], key=game_data['negative'].get) if game_data and 'negative' in game_data else 'N/A'

    prompt = f"""
    You are an expert data analyst specializing in player satisfaction for video games. 
    Based on the following sentiment analysis results from game reviews, please provide a comprehensive overview and analysis.

    **Instructions:**
    - Format your entire response using Markdown.
    - Use headings (`##`), bold text (`**text**`), and bullet points (`*`) to structure the analysis clearly.
    - Create a Markdown table to summarize the key sentiment metrics.

    Overall Sentiment Data:
    - Total Reviews Analyzed: {total_reviews}
    - Average Polarity: {avg_polarity:.2f} (Ranges from -1.0 (very negative) to 1.0 (very positive))
    - Positive Reviews: {positive_reviews} ({(positive_reviews/total_reviews)*100:.1f}%)
    - Negative Reviews: {negative_reviews} ({(negative_reviews/total_reviews)*100:.1f}%)
    - Neutral Reviews: {neutral_reviews} ({(neutral_reviews/total_reviews)*100:.1f}%)

    Game-Specific Insights:
    - Game with the highest proportion of positive reviews: {most_positive_game}
    - Game with the highest proportion of negative reviews: {most_negative_game}

    Please provide a detailed analysis covering:
    1.  **Overall Summary:** A brief overview of player satisfaction.
    2.  **Key Metrics Table:** A Markdown table summarizing the sentiment data.
    3.  **Key Takeaways:** Bullet points on the most important findings.
    4.  **Recommendations:** A numbered list of actionable recommendations for developers.
    """

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "x-ai/grok-4-fast", # You can change the model
                "messages": [{"role": "user", "content": prompt}],
            })
        )
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        return f"Error calling OpenRouter API: {e}"
    except (KeyError, IndexError) as e:
        return f"Error parsing API response: {e}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'overview_file' not in request.files or 'reviews_file' not in request.files:
        return jsonify({'error': 'Both overview and review files are required.'}), 400
    
    overview_file = request.files['overview_file']
    reviews_file = request.files['reviews_file']

    if overview_file.filename == '' or reviews_file.filename == '':
        return jsonify({'error': 'No selected file for one of the inputs.'}), 400
    
    try:
        # Save the files
        overview_path = os.path.join('data', overview_file.filename)
        reviews_path = os.path.join('data', reviews_file.filename)
        overview_file.save(overview_path)
        reviews_file.save(reviews_path)
        
        # Load the data from both files
        df_overview = pd.read_excel(overview_path)
        df_reviews = pd.read_excel(reviews_path)
        
        # Merge the two dataframes on the 'title' column
        # We use a left merge to ensure we keep all reviews, even if an overview is missing
        df_merged = pd.merge(df_reviews, df_overview, on='title', how='left')
        
        # Process the merged data
        df_processed = preprocess_data(df_merged)
        df_processed = analyze_sentiment(df_processed)
        
        # Generate visualizations
        plot_paths = generate_sentiment_distribution(df_processed, game_title_column=GAME_TITLE_COLUMN)
        
        # Prepare data for frontend
        sentiment_counts = df_processed['sentiment'].value_counts().to_dict()
        avg_polarity = df_processed['polarity'].mean()
        avg_subjectivity = df_processed['subjectivity'].mean()
        
        # Prepare game-specific data
        game_sentiment = df_processed.groupby(GAME_TITLE_COLUMN)['sentiment'].value_counts(normalize=True).unstack(fill_value=0)
        game_data = game_sentiment.to_dict()
        
        return jsonify({
            'success': True,
            'sentiment_counts': sentiment_counts,
            'avg_polarity': avg_polarity,
            'avg_subjectivity': avg_subjectivity,
            'plot_paths': plot_paths,
            'game_data': game_data,
            'total_reviews': len(df_processed)
        })

    except Exception as e:
        # Return a more detailed error message for debugging
        return jsonify({'error': f'An error occurred during processing: {str(e)}'}), 500

@app.route('/get_ai_analysis', methods=['POST'])
def get_ai_analysis_route():
    # Get the data from the request
    data = request.json
    sentiment_counts = data.get('sentiment_counts')
    game_data = data.get('game_data')
    avg_polarity = data.get('avg_polarity')

    if not all([sentiment_counts, game_data, avg_polarity is not None]):
        return jsonify({'error': 'Missing data for AI analysis.'}), 400

    # Get the AI analysis
    analysis = get_ai_analysis(sentiment_counts, game_data, avg_polarity)

    return jsonify({'analysis': analysis})


if __name__ == '__main__':
    app.run(debug=True)