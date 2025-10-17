# utils/data_preprocessing.py
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# --- CONFIGURATION ---
# Set these to the exact names of the columns in your Excel files.
REVIEW_COLUMN_NAME = 'user_review'  # The column with the review text from reviews.xlsx
GAME_TITLE_COLUMN = 'title'         # The column with the game title (in both files)
# ---------------------

def preprocess_data(df):
    # The dataframe is already merged in app.py, so we just process it here.
    
    # Print the columns to the console for debugging
    print("Columns found after merge:", df.columns.tolist())
    
    # Check if the required columns exist
    if REVIEW_COLUMN_NAME not in df.columns:
        raise ValueError(f"Column '{REVIEW_COLUMN_NAME}' not found in the merged data.")
    if GAME_TITLE_COLUMN not in df.columns:
        raise ValueError(f"Column '{GAME_TITLE_COLUMN}' not found in the merged data.")
        
    # Basic preprocessing
    # Ensure all review text is string and handle missing values
    df['cleaned_review'] = df[REVIEW_COLUMN_NAME].fillna('').astype(str).apply(clean_text)
    
    return df

def clean_text(text):
    # Handle potential non-string data (though we've converted to string above)
    if not isinstance(text, str):
        text = str(text)
        
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs, mentions, hashtags
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'@\w+|#\w+', '', text)
    
    # Remove punctuation and numbers
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    
    # Tokenize and remove stopwords
    tokens = text.split()
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    
    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    
    return ' '.join(tokens)