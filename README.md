# Code Review Intelligence Engine

> An ML-powered system that reviews GitHub Pull Requests like a senior engineer — detecting bugs, security vulnerabilities, and complexity issues, posting inline comments automatically, and learning each developer's personal weak spots over time.

---

## What it does ?

When a developer opens a Pull Request on GitHub, this system:

1. Receives the PR automatically via GitHub webhook
2. Parses the code changes using an AST parser to understand structure
3. Runs an ensemble of CodeBERT + XGBoost to classify issues
4. Generates a SHAP-based explanation for every flag raised
5. Posts inline review comments directly on the PR within 60 seconds
6. Builds a personalised reviewer profile per developer over time
---

## Why this is different from existing tools

| Feature | SonarQube | DeepSource | This project |
|---|---|---|---|
| Inline PR comments | Yes | Yes | Yes |
| Bug detection | Partial | Yes | Yes |
| Security flags | Yes | Yes | Yes |
| Explains WHY flagged | No | No | Yes (SHAP) |
| Learns per developer | No | No | Yes |
| Open / self-trainable | Partial | No | Yes |

The key differentiator: **personalised reviewer profile**. After reviewing 10+ PRs from the same developer, the system learns their recurring weak spots and prioritises those checks first. No existing tool does this.

---

## Architecture

```
GitHub PR opened
      |
      v
GitHub Webhook
      |
      v
Flask API (/webhook)
      |
      v
Celery Task Queue (Redis)
      |
      v
  +---+---+
  |       |
  v       v
AST     CodeBERT
Parser  Fine-tuned
  |       |
  v       v
XGBoost  Issue
Features  Labels
  |       |
  +---+---+
      |
      v
SHAP Explainer
      |
      v
Developer Profile Store
      |
      v
GitHub API
      |
      v
Inline PR Comments posted
```

---

## Tech stack used :

**Machine Learning**
- `transformers` — CodeBERT fine-tuned on real GitHub PR review data
- `xgboost` — complexity and structural issue classifier using AST features
- `scikit-learn` — baseline models, ensemble logic, evaluation metrics
- `shap` — explainability layer, generates reason for every flag

**Code Understanding**
- `ast` — Python's built-in Abstract Syntax Tree parser
- `tree-sitter` — multi-language parser (extensible to JavaScript, Java, etc.)

**Backend & System**
- `flask` — REST API with `/review` and `/webhook` endpoints
- `celery` — async task queue so webhook never times out
- `redis` — message broker for Celery
- `PyGithub` — posts inline comments via GitHub API

---

## Project structure

```
code-review-intelligence/
├── data/                   # Raw and processed PR datasets
├── models/                 # Saved model files (gitignored — too large)
├── api/
│   └── app.py              # Flask API — webhook + review endpoints
├── notebooks/              # EDA, training, evaluation notebooks
├── tests/
│   └── test_parser.py      # Unit tests for AST parser and diff extractor
├── ast_features.py         # Extracts structural features from code
├── diff_parser.py          # Parses raw PR diffs into added lines
├── webhook_parser.py       # Extracts PR metadata from GitHub payload
├── requirements.txt
├── .env.example            # Environment variable template
└── README.md
```

---

## How to run locally :

**Step 1 — Clone the repo**
```bash
git clone https://github.com/Abdulkhaderk/code-review-intelligence.git
cd code-review-intelligence
```

**Step 2 — Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

**Step 3 — Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 4 — Set up environment variables**
```bash
cp .env.example .env
# Open .env and fill in your GitHub token and webhook secret
```

**Step 5 — Start Redis (required for Celery)**
```bash
# Mac
brew install redis && redis-server

# Windows — use WSL or Docker
docker run -p 6379:6379 redis
```

**Step 6 — Start the Flask API**
```bash
python api/app.py
```

**Step 7 — Test it's running**
```bash
curl http://localhost:5000/health
# Expected: {"status": "ok", "message": "Code review engine is running"}
```

---

## Environment variables

Copy `.env.example` to `.env` and fill in:

```
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_WEBHOOK_SECRET=your_webhook_secret
FLASK_ENV=development
REDIS_URL=redis://localhost:6379/0
```

Get your GitHub token at: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token → check `repo`

---

## Running tests

```bash
pytest tests/ -v
```

All 7 tests should pass covering: AST feature extraction, diff parsing, edge cases (malformed code, empty diffs).

---

## Model training

Training notebooks are in `notebooks/` and run in order:

```
01_eda.ipynb              — Dataset exploration and label distribution
02_baseline_model.ipynb   — TF-IDF + Logistic Regression baseline
03_xgboost_ast.ipynb      — XGBoost on AST structural features
04_codebert_finetune.ipynb — CodeBERT fine-tuning (run on Google Colab T4 GPU)
05_ensemble.ipynb         — Combined model + SHAP explainability
06_evaluation.ipynb       — Final evaluation, confusion matrix, SHAP plots
```

Training data: ~500+ labelled PR diffs scraped from public Python repos (Flask, Requests, FastAPI) using the GitHub API. Labels: `bug`, `security`, `style`, `complexity`, `none`.

---

## Personalised reviewer profile

After reviewing 10+ PRs from the same GitHub user, the system builds a profile tracking their most frequent issue types. From PR 11 onwards, the review comment includes:

```
Based on your last 8 PRs, focusing on input validation first
(flagged 4 times previously).
```

Profiles are stored per GitHub username in a local SQLite database.

---

## What I learned building this:


---

## Author

**Abdul Khader**
- GitHub: [@Abdulkhaderk](https://github.com/Abdulkhaderk)
- Built as a flagship portfolio project combining Data Science and Software Engineering

---

## License

MIT License — feel free to fork, extend, and build on this.
