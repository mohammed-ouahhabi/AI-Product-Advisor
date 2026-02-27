from collections import Counter
from functools import lru_cache
from typing import Iterable

from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline

from .config import settings

POSITIVE_WORDS = {'excellent', 'super', 'good', 'great', 'parfait', 'top'}
NEGATIVE_WORDS = {'nul', 'bad', 'poor', 'terrible', 'mauvais', 'déçu', 'probleme'}


@lru_cache(maxsize=1)
def get_sentiment_pipeline():
    return pipeline(task=settings.HF_TASK, model=settings.HF_MODEL_NAME)


@lru_cache(maxsize=1)
def get_text2text_pipeline():
    return pipeline('text2text-generation', model=settings.HF_TEXT2TEXT_MODEL)


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


def extract_weak_points(negative_texts: list[str], max_topics: int = 5) -> list[str]:
    docs = [text.strip() for text in negative_texts if text and text.strip()]
    if len(docs) < 2:
        return ['retours clients négatifs'] if docs else []

    try:
        vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            max_features=300,
            min_df=1,
            stop_words=[
                'le', 'la', 'les', 'de', 'des', 'du', 'et', 'en', 'un', 'une', 'pour', 'avec',
                'this', 'that', 'the', 'and', 'for', 'very', 'too', 'mais', 'pas', 'est', 'sur',
            ],
        )
        tfidf = vectorizer.fit_transform(docs)
        n_components = max(1, min(max_topics, tfidf.shape[0], tfidf.shape[1]))

        model = NMF(n_components=n_components, random_state=42, init='nndsvda', max_iter=500)
        model.fit(tfidf)

        feature_names = vectorizer.get_feature_names_out()
        weak_points: list[str] = []
        for topic in model.components_:
            top_idx = topic.argsort()[-3:][::-1]
            terms = [feature_names[i] for i in top_idx if topic[i] > 0]
            if terms:
                weak_points.append(', '.join(terms))

        # remove duplicates preserving order
        unique = []
        seen = set()
        for item in weak_points:
            if item not in seen:
                seen.add(item)
                unique.append(item)
        return unique[:max_topics] or ['retours clients négatifs']
    except Exception:
        return ['retours clients négatifs']


def generate_ai_recommendations(negative_texts: list[str], weak_points: list[str]) -> list[str]:
    if not negative_texts:
        return ['Continuer le suivi qualité et collecter davantage de feedback.']

    prompt = (
        'Tu es un expert produit e-commerce. '
        'À partir des avis négatifs suivants, propose exactement 4 recommandations actionnables en français. '
        'Une recommandation par ligne, sans numérotation.\n\n'
        f'Points faibles détectés: {", ".join(weak_points) if weak_points else "N/A"}\n\n'
        'Avis:\n- ' + '\n- '.join(negative_texts[:12])
    )

    try:
        generator = get_text2text_pipeline()
        output = generator(prompt, max_new_tokens=220, do_sample=False)[0]['generated_text']
        lines = [line.strip('-• ').strip() for line in output.splitlines() if line.strip()]
        cleaned = [line for line in lines if len(line) > 10]
        if cleaned:
            return cleaned[:5]
    except Exception:
        pass

    base = weak_points[:4] if weak_points else ['problèmes récurrents remontés par les clients']
    return [f'Améliorer en priorité : {item}.' for item in base]


def build_recommendations(negative_texts: list[str]):
    if not negative_texts:
        return {
            'negative_summary': 'Aucun retour négatif récurrent détecté.',
            'weak_points': [],
            'recommendations': ['Continuer le suivi qualité et collecter davantage de feedback.'],
        }

    weak_points = extract_weak_points(negative_texts)
    recommendations = generate_ai_recommendations(negative_texts, weak_points)
    summary = (
        'Synthèse IA des points faibles récurrents : '
        + '; '.join(weak_points[:5])
        + '.'
    )

    return {
        'negative_summary': summary,
        'weak_points': weak_points[:5],
        'recommendations': recommendations[:5],
    }
