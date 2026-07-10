# todo-api-devops

Application fil rouge de la formation **DevOps Avancé** — BeOpen IT · Dakar 2026

---

## 🚀 Pipeline CI/CD

La pipeline couvre les modules 2 à 5 de la formation :

```
git push
    │
    ├── [M3] lint          → flake8 (analyse statique)
    │         ↓ si OK
    ├── [M4] quality-gate  → pytest + coverage ≥ 80% + bandit
    │         ↓ si OK (main ou develop uniquement)
    ├── [M3] build         → docker build + push Docker Hub
    │         ↓ si OK (main uniquement)
    └── [M5] deploy        → kubectl set image → Rolling Update sur K8s
```

---

## 🔐 Secrets GitHub à configurer

**Settings → Secrets and variables → Actions**

| Secret | Description |
|--------|-------------|
| `DOCKERHUB_USERNAME` | Votre username Docker Hub |
| `DOCKERHUB_TOKEN` | Token Docker Hub (Account Settings → Security) |
| `KUBECONFIG_B64` | Kubeconfig en base64 : `cat kubeconfig.yml \| base64 -w 0` |
| `K8S_NAMESPACE` | Votre namespace Kubernetes (fourni par le formateur) |

---

## 📋 Déclencheurs de la pipeline

| Branche | Lint | Tests | Build | Deploy |
|---------|------|-------|-------|--------|
| `feature/*` | ✅ | ✅ | ❌ | ❌ |
| `develop` | ✅ | ✅ | ✅ | ❌ |
| `main` | ✅ | ✅ | ✅ | ✅ |
| PR vers main/develop | ✅ | ✅ | ❌ | ❌ |

---

## 🗂️ Structure

```
todo-api-devops/
├── app.py                          ← Application Flask
├── test_app.py                     ← Tests unitaires + intégration
├── requirements.txt
├── Dockerfile
├── setup.cfg                       ← Config pytest, flake8, coverage
├── CHANGELOG.md
├── .gitignore
├── .dockerignore
├── k8s/
│   ├── deployment.yml
│   ├── service.yml
│   └── configmap.yml
└── .github/
    ├── pull_request_template.md
    └── workflows/
        └── pipeline.yml            ← Pipeline complète modules 2-5
```

---

## 🔧 Lancer localement

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer les tests
pytest test_app.py -v

# Lancer l'application
python app.py

# Tester l'API
curl http://localhost:5000/health
curl http://localhost:5000/todos
curl -X POST http://localhost:5000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Mon premier todo"}'
```

---

## 📅 Modules de la formation couverts

| Module | Concept | Ce que fait la pipeline |
|--------|---------|------------------------|
| 2 | GitFlow, branches, PRs | Triggers selon la branche, template PR |
| 3 | CI/CD GitHub Actions | Jobs lint + build + push Docker Hub |
| 4 | Quality Gate | pytest + coverage 80% + bandit |
| 5 | Déploiement K8s | kubectl + Rolling Update sur cluster distant |
