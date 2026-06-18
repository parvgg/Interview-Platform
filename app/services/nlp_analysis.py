import spacy
from textblob import TextBlob

# Load once at startup
nlp = spacy.load("en_core_web_sm")

def analyze_text(transcript: str) -> dict:
    """
    Analyze transcript for sentiment, vocabulary richness, and coherence.
    """
    if not transcript or len(transcript.strip()) == 0:
        return {
            "sentiment_score": 0.0,
            "vocabulary_richness": 0.0,
            "coherence_score": 0.0,
            "word_count": 0,
            "sentence_count": 0
        }

    doc = nlp(transcript)
    blob = TextBlob(transcript)

    # --- Sentiment (-1 to 1) ---
    sentiment_score = round(blob.sentiment.polarity, 3)

    # --- Vocabulary richness (type-token ratio) ---
    words = [token.text.lower() for token in doc if token.is_alpha]
    unique_words = set(words)
    vocabulary_richness = round(len(unique_words) / len(words), 3) if words else 0.0

    # --- Coherence (based on sentence transition + structure) ---
    sentences = list(doc.sents)
    sentence_count = len(sentences)

    # Simple coherence heuristic: average sentence length consistency
    # + ratio of connector words (because, therefore, however, etc.)
    connectors = {"because", "therefore", "however", "moreover", "additionally",
                  "furthermore", "thus", "consequently", "since", "although"}
    connector_count = sum(1 for token in doc if token.text.lower() in connectors)
    connector_ratio = connector_count / sentence_count if sentence_count > 0 else 0

    # Normalize: more connectors (up to a point) = better structured answer
    coherence_score = round(min(1.0, 0.5 + connector_ratio * 2), 3)

    return {
        "sentiment_score": sentiment_score,
        "vocabulary_richness": vocabulary_richness,
        "coherence_score": coherence_score,
        "word_count": len(words),
        "sentence_count": sentence_count
    }