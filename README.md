# FoodFacts Hub

WebApp Django + React pour trouver des **substituts alimentaires plus sains** grâce à l'API [Open Food Facts](https://world.openfoodfacts.org).

Projet réalisé dans le cadre du module Open Data (IPSSI).

## Fonctionnalités

- Création de compte et connexion (JWT)
- Parcours par **catégorie** → sélection d'un produit → proposition de substitut
- Recherche par **code-barres** (ex. Nutella : `8000500310427`)
- Affichage : description, Nutri-Score, magasins, lien Open Food Facts
- Enregistrement dans **« Mes aliments substitués »** (MongoDB)

## Architecture

```
backend/
  api/services/
    off_client.py      → Téléchargement API Open Food Facts
    data_cleaner.py    → Nettoyage des données
    repository.py      → Persistance et recherches MongoDB
    substitute_finder.py → Logique de recommandation
frontend/              → Interface React (Vite)
```

**Collections MongoDB :**
| Collection | Rôle |
|---|---|
| `users` | Comptes utilisateurs |
| `categories` | Catégories d'aliments |
| `products_cache` | Produits nettoyés (cache local) |
| `substitutions` | Substituts enregistrés par utilisateur |

## Prérequis

- Python 3.11+
- Node.js 18+
- MongoDB : [MongoDB Atlas](https://www.mongodb.com/atlas) (recommandé) ou Docker local

## Lancer l'app en une seule commande

**Première fois** (installation) :

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Éditez .env : MONGODB_URI Atlas (voir section ci-dessous) ou local
cd ..
npm run install:all
npm run seed
```

**Ensuite, à chaque session** :

```powershell
npm run dev
```

Ou :

```powershell
.\start-dev.ps1
```

- Frontend : http://localhost:5173  
- Backend : http://127.0.0.1:8080/api/ (port 8080 : le 8000 est souvent bloqué sous Windows)

MongoDB : **Atlas** (recommandé, voir ci-dessous) ou local (`docker compose up -d`).

---

## Installation rapide (détaillée)

### 1. MongoDB

**Option A — MongoDB Atlas (recommandé)**

Voir la section [Configuration MongoDB Atlas](#configuration-mongodb-atlas) ci-dessous.

**Option B — MongoDB local (Docker)**

```bash
docker compose up -d
```

Puis dans `backend/.env` :

```
MONGODB_URI=mongodb://localhost:27017/pur_beurre
MONGODB_DB=pur_beurre
```

### 2. Backend Django

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Éditez .env avec votre MONGODB_URI (Atlas ou local)

python manage.py check
python scripts/seed_data.py
python manage.py runserver
```

API disponible sur : http://127.0.0.1:8080/api/

### 3. Frontend React

```bash
cd frontend
npm install
npm run dev
```

Interface sur : http://localhost:5173

## Configuration MongoDB Atlas

### 1. Créer le cluster

1. Connectez-vous sur [MongoDB Atlas](https://cloud.mongodb.com).
2. Créez un cluster (gratuit M0 suffit pour le développement).
3. Créez la base `pur_beurre` (ou laissez-la se créer automatiquement au premier seed).

### 2. Utilisateur de base de données

Dans **Database Access** → **Add New Database User** :

- Créez un utilisateur avec mot de passe (notez-le).
- Rôle recommandé en dev : **Read and write to any database**.

Pour le travail en équipe, vous pouvez inviter vos collègues avec des rôles différenciés :

| Rôle Atlas | Usage |
|---|---|
| **Owner** | Administrateur du projet |
| **Read Only** | Consultation uniquement |
| **Read and write to any database** | Développement |

### 3. Accès réseau

Dans **Network Access** → **Add IP Address** :

- **Add Current IP Address** pour le développement local.
- **Allow Access from Anywhere** (`0.0.0.0/0`) si vous déployez sur Render/Vercel (voir [DEPLOYMENT.md](./DEPLOYMENT.md)).

### 4. URI de connexion

Dans **Database** → **Connect** → **Drivers** → **Python**, copiez l'URI :

```
mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
```

Remplacez `<user>` et `<password>` par vos identifiants. Si le mot de passe contient des caractères spéciaux (`@`, `#`, `%`…), encodez-les en URL (ex. `@` → `%40`).

### 5. Fichier `backend/.env`

Éditez `backend/.env` (ne jamais le committer) :

```env
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/pur_beurre?retryWrites=true&w=majority
MONGODB_DB=pur_beurre
```

Le nom de base `pur_beurre` doit figurer dans l'URI (avant le `?`).

### 6. Peupler la base (seed)

Atlas est vide au départ. Depuis `backend/` avec le venv activé :

```powershell
python manage.py check
python scripts/seed_data.py
```

Cela crée les collections : `users`, `categories`, `products_cache`, `substitutions`.

Vérifiez dans Atlas → **Browse Collections** que la base `pur_beurre` contient bien les données.

### 7. Lancer l'application

```powershell
npm run dev
```

Plus besoin de Docker MongoDB si vous utilisez Atlas. En cas d'erreur de connexion, vérifiez l'IP autorisée, l'utilisateur/mot de passe et l'encodage du mot de passe dans l'URI.

## Endpoints API

| Méthode | Route | Description |
|---|---|---|
| POST | `/api/auth/register/` | Inscription |
| POST | `/api/auth/login/` | Connexion |
| GET | `/api/categories/` | Liste des catégories |
| GET | `/api/categories/products/?category_tag=...` | Produits par catégorie |
| GET | `/api/products/<barcode>/` | Produit par code-barres |
| POST | `/api/substitute/` | Trouver un substitut |
| POST | `/api/substitutions/save/` | Enregistrer un substitut |
| GET | `/api/substitutions/` | Mes substituts |
| DELETE | `/api/substitutions/<id>/` | Supprimer un substitut |

## Déploiement (accessible partout)

Guide pas à pas : **[DEPLOYMENT.md](./DEPLOYMENT.md)**

Résumé : **MongoDB Atlas** (base) + **Render** (API Django) + **Vercel** (frontend React).

1. Atlas : Network Access `0.0.0.0/0`, puis `python scripts/seed_data.py` en local.
2. Render : service web dans `backend/`, variables `MONGODB_URI`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`.
3. Vercel : projet dans `frontend/`, variable `VITE_API_URL=https://votre-api.onrender.com/api`.

## Gestion de projet Agile

- **Trello** : [Ajoutez ici le lien vers votre board Trello](https://trello.com)
- **Présentation** : [Ajoutez ici le lien Google Slides](https://docs.google.com/presentation)

## Équipe & rôles suggérés

| Membre | Rôle | Tâches |
|---|---|---|
| Dev Backend | API Django, services OFF, MongoDB | Fait |
| Dev Frontend | React, parcours utilisateur | Fait |
| DevOps | Atlas, déploiement Heroku | À faire |
| Chef de projet | Trello, présentation | En cours |

## Licence

Projet académique — données © [Open Food Facts](https://world.openfoodfacts.org) (ODbL).
