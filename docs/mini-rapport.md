# Mini rapport — AI Product Advisor

## 1) Architecture
- **Frontend**: React + Vite + Tailwind CSS, interface redesign (thème sombre, cartes, hiérarchie visuelle renforcée).
- **Backend**: Flask REST API (Blueprint `/api`) + SQLAlchemy.
- **Authentification**: JWT avec endpoints inscription/connexion/profil (`Flask-JWT-Extended`).
- **Base de données**: SQLite en local.
- **Intégration IA**:
  - Sentiment automatique à l'ajout d'avis.
  - Recommandations V2 full IA (extraction de thèmes via TF-IDF + NMF, puis génération des recommandations via modèle text2text).

## 2) Modèles IA choisis
- Sentiment: `distilbert-base-uncased-finetuned-sst-2-english` (Hugging Face Transformers).
- Génération de recommandations: `google/flan-t5-base` (text2text).
- Fallback prévu si indisponibilité réseau/modèle.

## 3) Limites
- Le modèle de sentiment par défaut est anglophone.
- Les performances de génération dépendent des ressources machine (CPU/RAM).
- RBAC non implémenté (un seul rôle utilisateur côté API).

## 4) Pistes d'amélioration
- Passer à un modèle de sentiment francophone par défaut.
- Ajouter évaluation qualité des recommandations (métriques + feedback humain).
- Introduire PostgreSQL + migrations Alembic.
- Ajouter conformité RGAA avancée (navigation clavier et audit automatisé).
