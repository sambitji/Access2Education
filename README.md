# Access2Education

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)


## Table of contents
- [Features](#features)
- [Architecture](#architecture)
- [Setup](#setup)
- [API Docs](#api-docs)
- [ML Pipeline](#ml-pipeline)

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **Aptitude Test** | 25 questions, 5 sections, ~30 minutes — auto-scored cognitive assessment |
| 🧩 **ML Clustering** | Voting ensemble (GB + SVM + LR) for student profiling and learning-style detection |
| 🎯 **Personalized Recommendations** | Content scoring (0–100) and progression-aware suggestions |
| 🤖 **AI Chatbot** | Lecture summarizer + Q&A assistant integration |
| 📊 **Progress Dashboard** | Subject-wise charts and completion tracking |
| 🔒 **Secure Auth** | JWT dual-token scheme with OTP-based password reset |

## Architecture

Client (React/Vite) ⇄ Backend (FastAPI) ⇄ ML modules

- API entry: `Backend/main.py` and `Backend/routes/`
- Database: MySQL (replace earlier MongoDB references) — connection code and migration scripts located under `Backend/database/`
- ML: `ML/` and `Backend/ML/` for training and inference

## Setup

1. Backend (Windows example)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r Backend/requirements_backend.txt
cd Backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. Frontend

```bash
cd Frontend
npm install
npm run dev -- --host 0.0.0.0
```

3. Environment
- Set a MySQL connection string (example): `DATABASE_URL=mysql+pymysql://user:pass@host:3306/dbname`

## API Docs

- See `Backend/routes/` for endpoints. Run the backend and visit `/docs` for interactive OpenAPI UI.

## ML Pipeline

- Training and clustering scripts: `ML/train_cluster.py`, predictions: `ML/predict_cluster.py`.

## Project layout

```
Access2Education/
├── Backend/            # FastAPI server and DB integration (MySQL)
├── Frontend/           # React/Vite application
├── ML/                 # Model training & inference
├── data/               # Datasets and metadata
└── vercel.json
```

## License

MIT — see LICENSE

## Author

Sambit — https://github.com/sambitji

---

## System Architecture & Workflow

The following diagram illustrates the interaction between the Frontend, Backend, ML Engine, and Database.

```mermaid
flowchart TD
	subgraph Client ["Frontend (React/Vite)"]
		F_Entry["App.jsx"] --> F_Admin["Dashboard.jsx"]
		F_Admin --> F_Test["AptitudeTest.jsx"]
		F_Admin --> F_Chat["Chatbot.jsx"]
		F_Admin --> F_SR["SpacedRepetition.jsx"]
	end

	subgraph Server ["Backend (FastAPI)"]
		B_Main["main.py"] --> B_Auth["routes/auth.py"]
		B_Main --> B_Test["routes/test.py"]
		B_Main --> B_Chat["routes/chatbot.py"]
		B_Main --> B_SR["routes/sr_routes.py"]
		B_Main --> B_Cont["routes/content.py"]
        
		B_Main --> B_DB["database/db.py"]
		B_Main --> B_Cfg["config.py"]
	end

	subgraph Intelligence ["ML & AI Logic"]
		B_Test --> ML_Pred["ML/predict_cluster.py"]
		B_Chat --> AI_Handler["AI Agent (DeepSeek)"]
		B_SR --> ML_SR["ML/spaced_repetition.py"]
		B_Cont --> ML_Rec["ML/recommender.py"]
        
		ML_Pred --> ML_Model["ML/models/ensemble.pkl"]
		ML_Train["ML/train_cluster.py"] --> ML_Model
	end

	B_DB --> DB_Cloud[("MySQL")]
    
	F_Entry <-->|REST API| B_Main
```

---

## Key Features

### Adaptive Learning DNA (ML Clustering)
Students take an aptitude test; a clustering pipeline profiles learning styles using ensemble models (K-Means / voting ensemble) across multiple cognitive dimensions.

### Smart Revision (SM-2 Spaced Repetition)
The SM-2 algorithm powers spaced repetition scheduling for optimized retention and revision reminders.

### AI Tutor (Chatbot)
An integrated AI assistant provides Q&A, lecture summarization, and context-aware help.

## Technology Stack

- **Frontend**: React (Vite), Tailwind CSS
- **Backend**: FastAPI (Python), Pydantic
- **Machine Learning**: scikit-learn, numpy, joblib
- **Database**: MySQL (connection code under `Backend/database/`)
- **Deployment**: Vercel / containerized options (Dockerfiles included)

## Deployment notes

- Configure environment variables such as `DATABASE_URL` (MySQL) and `SECRET_KEY`.
- For API docs, run the backend and visit `/docs` for OpenAPI UI.

## Project structure

```
Access2Education/
├── Backend/            # FastAPI Server, Routes, and DB logic (MySQL)
├── Frontend/           # React/Vite Application
├── ML/                 # Training scripts and Pickled Models (.pkl)
├── data/               # Metadata and datasets
├── Dockerfile.backend  # Self-hosting Docker config
└── vercel.json         # Vercel Monorepo Router
```

---

If you want I can further reformat sections, add back untranslated Hindi/notes, or include the original longer narrative — tell me which parts to prioritise.

