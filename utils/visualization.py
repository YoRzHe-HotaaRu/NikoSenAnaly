# utils/visualization.py
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

def generate_sentiment_distribution(df, game_title_column='title', output_path='static/plots/'):
    """
    Generates and saves sentiment distribution plots.
    
    Args:
        df (pd.DataFrame): The processed dataframe with sentiment analysis.
        game_title_column (str): The name of the column containing game titles.
        output_path (str): The directory to save the generated plots.
    
    Returns:
        dict: A dictionary with the paths to the generated plot files.
    """
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
    
    # Sentiment by Game
    plt.figure(figsize=(12, 8))
    # Use the game_title_column variable here
    game_sentiment = df.groupby(game_title_column)['sentiment'].value_counts(normalize=True).unstack(fill_value=0)
    game_sentiment.plot(kind='bar', stacked=True, figsize=(12, 8))
    plt.title('Sentiment by Game')
    plt.ylabel('Proportion')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, 'sentiment_by_game.png'))
    plt.close()
    
    return {
        'sentiment_distribution': os.path.join(output_path, 'sentiment_distribution.png'),
        'polarity_distribution': os.path.join(output_path, 'polarity_distribution.png'),
        'sentiment_by_game': os.path.join(output_path, 'sentiment_by_game.png')
    }