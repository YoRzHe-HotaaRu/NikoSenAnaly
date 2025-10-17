# utils/visualization.py
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

def generate_sentiment_distribution(df, output_path='static/plots/'):
    # Create directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    # Sentiment distribution
    plt.figure(figsize=(10, 6))
    sns.countplot(x='sentiment', data=df)
    plt.title('Sentiment Distribution')
    plt.savefig(os.path.join(output_path, 'sentiment_distribution.png'))
    plt.close()
    
    # Polarity distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df['polarity'], bins=30, kde=True)
    plt.title('Polarity Distribution')
    plt.savefig(os.path.join(output_path, 'polarity_distribution.png'))
    plt.close()
    
    # If you have game titles, you can create a game-specific analysis
    if 'game_title' in df.columns:
        game_sentiment = df.groupby('game_title')['sentiment'].value_counts(normalize=True).unstack()
        game_sentiment.plot(kind='bar', stacked=True, figsize=(12, 8))
        plt.title('Sentiment by Game')
        plt.savefig(os.path.join(output_path, 'sentiment_by_game.png'))
        plt.close()
    
    return {
        'sentiment_distribution': os.path.join(output_path, 'sentiment_distribution.png'),
        'polarity_distribution': os.path.join(output_path, 'polarity_distribution.png'),
        'sentiment_by_game': os.path.join(output_path, 'sentiment_by_game.png') if 'game_title' in df.columns else None
    }