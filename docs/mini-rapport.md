# Mini rapport — AI Product Advisor

## 1) Architecture
- **Frontend**: React + Vite + Tailwind CSS, interface redesign (thème sombre, cartes, hiérarchie visuelle renforcée).
- **Backend**: Flask REST API (Blueprint `/api`) + SQLAlchemy.
- **Authentification**: JWT avec endpoints inscription/connexion/profil (`Flask-JWT-Extended`).
- **Base de données**: SQLite en local.
- **Intégration IA**: service backend de sentiment déclenché automatiquement à chaque création d'avis.

## 2) Modèle IA choisi
- Modèle par défaut: `distilbert-base-uncased-finetuned-sst-2-english` via Hugging Face Transformers.
- Mapping des labels du modèle vers les classes applicatives: `positive`, `neutral`, `negative`.
- Fallback prévu si indisponibilité réseau/modèle: heuristique lexicale légère.

## 3) Limites
- Modèle de sentiment par défaut anglophone.
- Recommandations basées sur règles/mots-clés.
- RBAC non implémenté (un seul rôle utilisateur côté API actuellement).

## 4) Pistes d'amélioration
- Ajouter rôles (admin/analyste) et permissions fines.
- Ajouter tests automatisés plus complets (auth + UI).
- Introduire PostgreSQL + migrations Alembic.
- Ajouter conformité RGAA avancée (navigation clavier et audit automatisé).
