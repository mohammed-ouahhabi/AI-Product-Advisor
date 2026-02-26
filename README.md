# AI Product Advisor

Application web full-stack pour centraliser des avis produits, analyser automatiquement leur sentiment et proposer des recommandations d'amélioration.

## Stack
- Frontend: React + Vite + Tailwind + Axios + Recharts
- Backend: Flask + SQLAlchemy + Flask-CORS + Flask-JWT-Extended
- DB: SQLite (local)
- IA: Hugging Face Transformers (sentiment analysis)

## Prérequis
- Python 3.11+
- Node.js 20+
- npm 10+

## Installation

### 1) Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```
API disponible sur `http://localhost:5000`.

### 2) Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
UI disponible sur `http://localhost:5173`.

## Authentification
- L'application nécessite une connexion via écran de login/inscription.
- Endpoints:
  - `POST /api/auth/register`
  - `POST /api/auth/login`
  - `GET /api/auth/me`
- Le frontend stocke le JWT dans `localStorage` (`auth_token`) puis l’envoie dans `Authorization: Bearer <token>`.

## Données et export SQL
- Schéma SQL fourni dans `backend/sql_dump.sql`.
- Les tables sont créées automatiquement au démarrage backend.

## API REST (extraits)
- `GET /api/products`
- `POST /api/products`
- `DELETE /api/products/{id}`
- `GET /api/products/{id}/reviews`
- `POST /api/products/{id}/reviews`
- `DELETE /api/reviews/{id}`
- `GET /api/products/{id}/stats`
- `GET /api/products/{id}/recommendations`

## Vérification multi-navigateur
Testé sur Chromium (Playwright). Firefox/WebKit à valider dans un environnement de recette.

## Livrables inclus
- Code source complet (`frontend/` + `backend/`)
- Export SQL (`backend/sql_dump.sql`)
- Fichiers de configuration (`.env.example`, configs Vite/Tailwind)
- Mini rapport (`docs/mini-rapport.md`)
