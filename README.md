# Access2Education
AI-powered education platform designed to improve learning outcomes and accessibility by combining personalized instruction, data-driven performance analysis, and human–AI collaboration to support social and economic development.

<div align="center">

<br/>

# 🎓 EduPlatform

### AI-Powered Personalized Learning System

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://mongodb.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

<br/>

> **"Har student alag hota hai — toh content bhi alag hona chahiye."**
>
> EduPlatform ek AI-powered education system hai jo pehle har student ka aptitude test leta hai,
> phir Machine Learning se uski **learning style detect** karta hai,
> aur uske hisaab se **personalized content recommend** karta hai.

<br/>

[🚀 Features](#-features) &nbsp;·&nbsp;
[🏗️ Architecture](#️-architecture) &nbsp;·&nbsp;
[🤖 ML Pipeline](#-ml-pipeline) &nbsp;·&nbsp;
[🚀 Quick Start](#-quick-start) &nbsp;·&nbsp;
[⚙️ Setup](#️-setup) &nbsp;·&nbsp;
[📡 API Docs](#-api-documentation)

<br/>

</div>

---

## 🎯 Problem Statement

Traditional education ka ek bada problem hai — **ek hi teaching style sabke liye kaam nahi karti.** Koi student diagram se jaldi samajhta hai, koi theory padhke, koi practice karke. EduPlatform is problem ko solve karta hai by:

1. **Measure** karna — 25-question aptitude test se student ki cognitive strengths pata karna
2. **Classify** karna — Machine Learning se 4 learning styles mein cluster karna
3. **Personalize** karna — Har student ke liye different content types recommend karna
4. **Assist** karna — AI chatbot se lecture summarize aur doubts clear karna

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **Aptitude Test** | 25 questions · 5 cognitive sections · 30 min timer · Auto-scored |
| 🤖 **ML Clustering** | Voting Ensemble (GB + SVM + LR) — **93.3% CV Accuracy** |
| 🎯 **Smart Recommendations** | 0–100 scoring engine — type + tags + difficulty progression |
| 💬 **AI Chatbot** | DeepSeek-powered lecture summarizer + Q&A assistant |
| 📊 **Progress Dashboard** | Subject-wise charts, completion tracking, recent activity |
| 🔐 **Secure Auth** | JWT dual-token system + OTP-based password reset |
| 🚀 **Demo Mode** | Offline/Frontend-only mode for quick testing and static deployments |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         EduPlatform                             │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────────────┐ │
│  │   Frontend   │    │   Backend    │    │   ML Pipeline     │ │
│  │  React + Vite│◄──►│   FastAPI    │◄──►│  scikit-learn     │ │
│  │  Tailwind CSS│    │   Motor      │    │  Voting Ensemble  │ │
│  │  Zustand     │    │   PyJWT      │    │  KMeans fallback  │ │
│  └──────────────┘    └──────┬───────┘    └───────────────────┘ │
│                             │                                   │
│                      ┌──────▼───────┐                          │
│                      │   MongoDB    │                          │
│                      │  5 collections│                          │
│                      └──────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

### Project Structure

```
edu-platform/
│
├── 🤖 ml/
│   ├── notebooks/                       # EDA + Model Exploration
│   ├── models/                          # Trained .pkl files (git-ignored)
│   ├── train_model.py                   # Voting Ensemble training script
│   ├── predict_cluster.py               # 3-tier prediction (Ensemble → KMeans → Rules)
│   └── recommender.py                   # Content recommendation engine class
│
├── ⚙️ backend/
│   ├── routes/                          # FastAPI endpoints (Auth, Test, Content, SR, Chatbot)
│   │   ├── sr_routes.py                 # Spaced Repetition Logic (Renamed for clarity)
│   │   ├── chatbot.py                   # DeepSeek AI assistant routes
│   │   ├── cluster.py                   # Learning Style prediction routes
│   │   └── ...                          # Auth, Test, Content routers
│   ├── models/                          # Pydantic schemas
│   ├── database/db.py                   # MongoDB configuration
│   └── main.py                          # FastAPI entry point (All routers registered)
│
├── 🎨 frontend/src/
│   ├── pages/                           # Home, Dashboard, Test, Learn
│   ├── components/                      # Chatbot, Charts, UI elements
│   ├── store/authStore.js               # Zustand state management
│   ├── services/api.js                  # Axios instance with Demo Support
│   └── services/demoApi.js              # Mock backend for Frontend-only mode
│
├── 🚀 bootstrap.py                      # One-click environment setup script
└── 📦 data/                             # Dataset and metadata
```

---

## 🤖 ML Pipeline

### Learning Style Clusters

| Cluster | Style | Key Traits | Recommended Content |
|---|---|---|---|
| 0 | 👁️ Visual Learner | High verbal + memory | Videos, Infographics |
| 1 | 🧠 Conceptual Thinker | High logical | Articles, Case Studies |
| 2 | ⚙️ Practice-Based | High numerical + attention | Exercises, Projects |
| 3 | 📋 Step-by-Step | High memory | Notes, Tutorials |

### Dataset & Model Selection

- **Dataset**: 10,000 synthetic student records with Gaussian distributions.
- **Top Performer**: Voting Ensemble (GB + SVM + LR) reaching **93.3% accuracy**.
- **Robust Fallback**: Prediction chain handles missing model files gracefully.

---

## 🚀 Quick Start (Automated Setup)

Instead of manual installation, use the provided bootstrap script:

```bash
python bootstrap.py
```

This will initialize backend `.env`, install frontend dependencies, and retrain ML models automatically.

---

## ⚙️ Setup (Manual)

### 1. Train ML Models
```bash
cd ML
pip install -r requirments_ml.txt
python train_cluster.py
```

### 2. Backend
```bash
cd Backend
pip install -r requirements_backend.txt
uvicorn main:app --reload
```

### 3. Frontend
```bash
cd Frontend
npm install
npm run dev
```

---

## 📡 API Documentation

### Auth & Test Endpoints
Full Swagger docs available at `http://localhost:8000/docs` when the backend is running.

---

## 🛠️ Developer & Debugging Support

To make development easier, we've implemented a **Direct Execution** pattern for all backend route files. 

You can now run individual route files directly for testing or debugging without manual `PYTHONPATH` configuration:
```bash
python Backend/routes/auth.py
python Backend/routes/sr_routes.py
```
This automatically handles imports from the parent `Backend` and `ML` packages.

---

## 🛠️ Tech Stack

**ML**: scikit-learn, pandas, numpy  
**Backend**: FastAPI, Motor (MongoDB), JWT  
**Frontend**: React 18, Vite, Tailwind CSS, Zustand, Recharts, Framer Motion

---

## 🤝 Contributing
Feel free to fork and submit Pull Requests!

---

## 📄 License
[MIT](LICENSE) — Built with ❤️ for educational accessibility.

<div align="center">
<br/>
⭐ Star this repo if you find it helpful!
</div>

