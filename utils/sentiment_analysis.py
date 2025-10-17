# utils/sentiment_analysis.py
from textblob import TextBlob
import pandas as pd

def analyze_sentiment(df, method='textblob'):
    if method == 'textblob':
        df['polarity'] = df['cleaned_review'].apply(lambda x: TextBlob(x).sentiment.polarity)
        df['subjectivity'] = df['cleaned_review'].apply(lambda x: TextBlob(x).sentiment.subjectivity)
        
        # Categorize sentiment
        df['sentiment'] = df['polarity'].apply(lambda x: 'positive' if x > 0 else ('negative' if x < 0 else 'neutral'))
    
    # You could add BERT implementation here if needed
    
    return df