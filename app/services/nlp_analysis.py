import nltk
# Dynamically download the missing punctuation data on startup
nltk.download('punkt_tab')

from textblob import TextBlob

def analyze_text(text: str) -> dict:
    """
    A lightweight NLP analyzer using TextBlob to keep the server memory low.
    """
    if not text.strip():
        return {
            "word_count": 0,
            "sentence_count": 0,
            "sentiment_polarity": 0.0,
            "sentiment_subjectivity": 0.0
        }

    blob = TextBlob(text)
    sentences = blob.sentences
    words = blob.words

    return {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "sentiment_polarity": round(blob.sentiment.polarity, 2),
        "sentiment_subjectivity": round(blob.sentiment.subjectivity, 2)
    }
