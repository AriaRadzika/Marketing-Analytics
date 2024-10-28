import pandas as pd
from sqlalchemy import create_engine
import urllib
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download the VADER lexicon for sentiment analysis
nltk.download('vader_lexicon')

# Define the SQLAlchemy connection string
params = urllib.parse.quote_plus(
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=LAPTOP-U301BD8U\\SQLEXPRESS;"
    "Database=MarketingAnalytics;"
    "Trusted_Connection=yes;"
)

# Create the SQLAlchemy engine with the correct connection string
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

# Define the SQL query to fetch customer reviews data
query = "SELECT ReviewID, CustomerID, ProductID, ReviewDate, Rating, ReviewText FROM dbo.customer_reviews"

# Fetch the data into a DataFrame using SQLAlchemy
df = pd.read_sql(query, engine)
print("Data fetched successfully.")
print(df.head())  # Display the first few rows

# Clean extra spaces in 'ReviewText'
df['ReviewText'] = df['ReviewText'].str.replace('  ', ' ', regex=False)

# Initialize the VADER sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Define a function to calculate sentiment scores
def calculate_sentiment(review):
    sentiment = sia.polarity_scores(review)
    return sentiment['compound']

# Define a function to categorize sentiment using text and rating
def categorize_sentiment(score, rating):
    if score > 0.05:
        if rating >= 4:
            return 'Positive'
        elif rating == 3:
            return 'Mixed Positive'
        else:
            return 'Mixed Negative'
    elif score < -0.05:
        if rating <= 2:
            return 'Negative'
        elif rating == 3:
            return 'Mixed Negative'
        else:
            return 'Mixed Positive'
    else:
        if rating >= 4:
            return 'Positive'
        elif rating <= 2:
            return 'Negative'
        else:
            return 'Neutral'

# Define a function to bucket sentiment scores into ranges
def sentiment_bucket(score):
    if score >= 0.5:
        return '0.5 to 1.0'
    elif 0.0 <= score < 0.5:
        return '0.0 to 0.49'
    elif -0.5 <= score < 0.0:
        return '-0.49 to 0.0'
    else:
        return '-1.0 to -0.5'

# Apply sentiment analysis to calculate sentiment scores
df['SentimentScore'] = df['ReviewText'].apply(calculate_sentiment)

# Apply sentiment categorization using text and rating
df['SentimentCategory'] = df.apply(
    lambda row: categorize_sentiment(row['SentimentScore'], row['Rating']), axis=1
)

# Apply sentiment bucketing to categorize scores into defined ranges
df['SentimentBucket'] = df['SentimentScore'].apply(sentiment_bucket)

# Display the first few rows of the DataFrame with sentiment analysis results
print(df.head())

# Save the DataFrame with sentiment analysis to a new CSV file
df.to_csv('C:/Users/ariap/Documents/Project/Data Analyst Portofolio Projects/fact_customer_reviews_with_sentiment.csv', index=False)
print("Data saved to 'fact_customer_reviews_with_sentiment.csv'.")
