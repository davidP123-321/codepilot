# CodePilot

Mini projet inspiré de Replit.

## Prérequis
- Python 3.11+
- Docker
- clé OpenAI

## Lancer

### 1) Construire le sandbox
```bash
docker build -f backend/Dockerfile.sandbox -t codepilot-sandbox .
```

### 2) Installer les dépendances backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 3) Remplir la clé API
Ouvre `backend/.env` et mets :
```env
OPENAI_API_KEY=ta_cle_openai
```

### 4) Démarrer l’API
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5) Tester
```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{"name":"demoapp"}'
```

```bash
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"project_name":"demoapp","message":"Crée un mini site HTML simple"}'
```
