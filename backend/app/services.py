from collections import Counter
from functools import lru_cache
from typing import Iterable

from transformers import pipeline

from .config import settings

NEGATIVE_KEYWORD_RECO = {
    'batterie': 'Améliorer l\'autonomie et optimiser la gestion énergétique.',
    'livraison': 'Renforcer le suivi logistique et réduire les délais de livraison.',
    'qualité': 'Augmenter les contrôles qualité avant expédition.',
    'prix': 'Revoir le positionnement tarifaire ou ajouter plus de valeur perçue.',
    'son': 'Optimiser les composants audio et affiner les réglages acoustiques.',
    'application': 'Stabiliser l\'application compagnon et corriger les bugs critiques.',
    'confort': 'Repenser l\'ergonomie du produit et les matériaux de contact.',
    'sav': 'Renforcer la réactivité du support client et la clarté des procédures SAV.',
}

POSITIVE_WORDS = {'excellent', 'super', 'good', 'great', 'parfait', 'top'}
NEGATIVE_WORDS = {'nul', 'bad', 'poor', 'terrible', 'mauvais', 'déçu', 'probleme'}


@lru_cache(maxsize=1)
def get_sentiment_pipeline():
    return pipeline(task=settings.HF_TASK, model=settings.HF_MODEL_NAME)


def map_label(label: str) -> str:
    normalized = label.lower()
    if 'neg' in normalized or normalized in {'label_0', '1 star', '2 stars'}:
        return 'negative'
    if 'neu' in normalized or normalized == 'label_1' or normalized == '3 stars':
        return 'neutral'
    return 'positive'


def analyze_sentiment(text: str):
    try:
        classifier = get_sentiment_pipeline()
        result = classifier(text, truncation=True)[0]
        sentiment = map_label(result['label'])
        return sentiment, float(result['score'])
    except Exception:
        # Fallback lightweight approach when model download is unavailable.
        tokens = set(text.lower().split())
        if tokens & NEGATIVE_WORDS:
            return 'negative', 0.6
        if tokens & POSITIVE_WORDS:
            return 'positive', 0.6
        return 'neutral', 0.5


def aggregate_statistics(reviews: Iterable[dict]):
    reviews = list(reviews)
    total = len(reviews)
    if total == 0:
        return {
            'total_reviews': 0,
            'average_rating': 0,
            'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0},
        }
    avg = sum(item.rating for item in reviews) / total
    sentiments = Counter(item.sentiment for item in reviews)
    return {
        'total_reviews': total,
        'average_rating': round(avg, 2),
        'sentiment_distribution': {
            'positive': sentiments.get('positive', 0),
            'neutral': sentiments.get('neutral', 0),
            'negative': sentiments.get('negative', 0),
        },
    }


def build_recommendations(negative_texts: list[str]):
    if not negative_texts:
        return {
            'negative_summary': 'Aucun retour négatif récurrent détecté.',
            'weak_points': [],
            'recommendations': ['Continuer le suivi qualité et collecter davantage de feedback.'],
        }

    lowered = ' '.join(negative_texts).lower()
    matched = [kw for kw in NEGATIVE_KEYWORD_RECO if kw in lowered]
    if not matched:
        matched = ['qualité', 'sav']

    weak_points = matched[:5]
    recos = [NEGATIVE_KEYWORD_RECO[key] for key in weak_points][:5]
    summary = (
        'Les avis négatifs mentionnent principalement : '
        + ', '.join(weak_points)
        + '.'
    )
    return {
        'negative_summary': summary,
        'weak_points': weak_points,
        'recommendations': recos,
    }
