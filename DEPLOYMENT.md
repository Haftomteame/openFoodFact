# Déployer Pur Beurre — accessible partout

Stack recommandée (gratuite) :

| Composant | Service | URL publique |
|-----------|---------|--------------|
| Base de données | MongoDB Atlas | déjà configuré |
| Backend API | [Render](https://render.com) | `https://pur-beurre-api.onrender.com` |
| Frontend | [Vercel](https://vercel.com) | `https://votre-app.vercel.app` |

---

## Prérequis

1. Code poussé sur **GitHub** (Render et Vercel se connectent au repo).
2. **MongoDB Atlas** opérationnel :
   - **Network Access** → `0.0.0.0/0` (accès depuis n'importe où, requis pour Render/Vercel).
   - URI dans `backend/.env` en local (ne jamais committer `.env`).

3. Seed de la base (une fois, depuis votre PC) :

```powershell
cd backend
.\.venv\Scripts\activate
python scripts\seed_data.py
```

---

## Étape 1 — Backend sur Render

1. [render.com](https://render.com) → **New** → **Blueprint** (ou **Web Service**).
2. Connectez le repo GitHub.
3. Si Blueprint : Render lit `render.yaml` à la racine.
4. Sinon, configurez manuellement :
   - **Root Directory** : `backend`
   - **Build** : `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start** : `gunicorn pur_beurre.wsgi --bind 0.0.0.0:$PORT --log-file -`
   - **Health Check Path** : `/api/health/`

5. Variables d'environnement (Environment) :

| Variable | Valeur |
|----------|--------|
| `MONGODB_URI` | `mongodb+srv://...@cluster0....mongodb.net/pur_beurre?retryWrites=true&w=majority` |
| `MONGODB_DB` | `pur_beurre` |
| `DEBUG` | `False` |
| `SECRET_KEY` | chaîne aléatoire longue |
| `JWT_SECRET_KEY` | autre chaîne aléatoire |
| `ALLOWED_HOSTS` | `pur-beurre-api.onrender.com` (votre URL Render) |
| `CORS_ALLOWED_ORIGINS` | URL Vercel du frontend (étape 2) |

6. Déployez. Testez : `https://VOTRE-API.onrender.com/api/health/` → `{"status":"ok"}`.

> **Note** : le plan gratuit Render met l'API en veille après ~15 min d'inactivité ; le premier appel peut prendre 30–60 s.

---

## Étape 2 — Frontend sur Vercel

1. [vercel.com](https://vercel.com) → **Add New Project** → importez le repo GitHub.
2. **Root Directory** : `frontend`
3. Framework : **Vite** (détecté automatiquement).
4. Variable d'environnement **au build** :

| Variable | Valeur |
|----------|--------|
| `VITE_API_URL` | `https://VOTRE-API.onrender.com/api` |

5. Déployez. Vous obtenez une URL du type `https://pur-beurre.vercel.app`.

6. Retournez sur **Render** et mettez à jour :

```
CORS_ALLOWED_ORIGINS=https://pur-beurre.vercel.app
```

Redéployez le backend si nécessaire.

---

## Étape 3 — Vérification

- [ ] `https://VOTRE-API.onrender.com/api/health/` répond OK
- [ ] `https://VOTRE-APP.vercel.app` s'ouvre
- [ ] Inscription / connexion fonctionnent
- [ ] Recherche produit et substituts OK

---

## Alternative — Heroku (backend)

```bash
cd backend
heroku create pur-beurre-api
heroku config:set DEBUG=False MONGODB_URI=... ALLOWED_HOSTS=.herokuapp.com
heroku config:set CORS_ALLOWED_ORIGINS=https://votre-app.vercel.app
git subtree push --prefix backend heroku main
```

Le `Procfile` utilise déjà Gunicorn avec `$PORT`.

---

## Sécurité

- Ne commitez jamais `.env` ni les mots de passe MongoDB.
- Si des identifiants ont été exposés, changez le mot de passe dans Atlas → **Database Access**.
- En production : `DEBUG=False` et clés `SECRET_KEY` / `JWT_SECRET_KEY` uniques.
