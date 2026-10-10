# CodePilot

Mini projet inspiré de Replit : un environnement de projet avec API backend, sandbox Docker, et agent IA capable de lire/écrire des fichiers et d’exécuter des commandes.

## Prérequis

- Python 3.11+
- Docker
- Clé API OpenAI

## Structure

- `backend/` : API FastAPI + agent IA + sandbox
- `docker-compose.yml` : orchestration locale
- `LANCER.txt` : instructions de lancement

## Lancer localement

1. Construire le sandbox Docker :
   ```bash
   docker build -f backend/Dockerfile.sandbox -t codepilot-sandbox .
   ```

2. Créer le venv et installer les dépendances :
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Configurer la clé OpenAI :
   ```bash
   cp .env.example .env
   ```
   Puis remplir `OPENAI_API_KEY`.

4. Démarrer l’API :
   ```bash
   cd backend
   source .venv/bin/activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. Tester une création de projet :
   ```bash
   curl -X POST http://localhost:8000/projects \
     -H "Content-Type: application/json" \
     -d '{"name":"demoapp"}'
   ```

6. Tester le chat IA :
   ```bash
   curl -X POST http://localhost:8000/agent/chat \
     -H "Content-Type: application/json" \
     -d '{"project_name":"demoapp","message":"Crée un mini site HTML avec un bouton rouge et le texte Hello"}'
   ```

## Remarques

- Les projets sont stockés dans `/tmp/codepilot_projects`.
- Le sandbox Docker exécute les commandes dans un conteneur isolé.
- Le backend est prêt à être branché à un frontend (React/Next.js/Monaco/terminal).
