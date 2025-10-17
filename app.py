# app.py
from flask import Flask, render_template, request, jsonify
import pandas as pd
from utils.data_preprocessing import preprocess_data
from utils.sentiment_analysis import analyze_sentiment
from utils.visualization import generate_sentiment_distribution
import os

app = Flask(__name__)

# Ensure the static/plots directory exists
os.makedirs('static/plots', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        # Save the file
        file_path = os.path.join('data', file.filename)
        os.makedirs('data', exist_ok=True)
        file.save(file_path)
        
        # Process the data
        df = preprocess_data(file_path)
        df = analyze_sentiment(df)
        
        # Generate visualizations
        plot_paths = generate_sentiment_distribution(df)
        
        # Prepare data for frontend
        sentiment_counts = df['sentiment'].value_counts().to_dict()
        avg_polarity = df['polarity'].mean()
        avg_subjectivity = df['subjectivity'].mean()
        
        # If you have game titles, prepare game-specific data
        game_data = None
        if 'game_title' in df.columns:
            game_sentiment = df.groupby('game_title')['sentiment'].value_counts(normalize=True).unstack()
            game_data = game_sentiment.to_dict()
        
        return jsonify({
            'success': True,
            'sentiment_counts': sentiment_counts,
            'avg_polarity': avg_polarity,
            'avg_subjectivity': avg_subjectivity,
            'plot_paths': plot_paths,
            'game_data': game_data,
            'total_reviews': len(df)
        })

if __name__ == '__main__':
    app.run(debug=True)