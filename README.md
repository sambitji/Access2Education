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
[⚙️ Setup](#️-setup) &nbsp;·&nbsp;
[📡 API Docs](#-api-documentation) &nbsp;·&nbsp;
[🗺️ User Flow](#️-user-flow)

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
│   ├── notebooks/
│   │   ├── 01_data_exploration.ipynb    # EDA + distributions + outlier detection
│   │   ├── 02_clustering.ipynb          # K-Means + PCA visualization + elbow method
│   │   └── 03_recommendation.ipynb      # Scoring engine + heatmaps + end-to-end test
│   ├── models/                          # Trained .pkl files (git-ignored)
│   ├── train_model.py                   # Voting Ensemble training script
│   ├── predict_cluster.py               # 3-tier prediction (Ensemble → KMeans → Rules)
│   └── recommender.py                   # Content recommendation engine class
│
├── ⚙️ backend/
│   ├── routes/
│   │   ├── auth.py                      # Register, Login, JWT, OTP password reset
│   │   ├── test.py                      # Aptitude test + ML cluster prediction
│   │   └── content.py                   # Recommendations, progress, ratings
│   ├── models/
│   │   ├── user.py                      # Pydantic user schemas + validators
│   │   ├── result.py                    # Test result schemas
│   │   └── content.py                   # Content + progress schemas
│   ├── database/db.py                   # MongoDB connection + indexes
│   ├── config.py                        # Pydantic-settings centralized config
│   └── main.py                          # FastAPI app + CORS + lifespan
│
├── 🎨 frontend/src/
│   ├── pages/
│   │   ├── Home.jsx                     # Landing page
│   │   ├── Login.jsx / Register.jsx     # Auth forms
│   │   ├── TestPage.jsx                 # Aptitude test flow
│   │   ├── TestResult.jsx               # Results + radar chart + confidence
│   │   ├── Dashboard.jsx                # Personalized student dashboard
│   │   ├── LearnPage.jsx                # Content library + detail view
│   │   └── Progress.jsx                 # Progress tracking
│   ├── components/
│   │   ├── AptitudeTest/                # Test UI + QuestionCard
│   │   ├── Dashboard/                   # StudentDashboard + ProgressChart (Recharts)
│   │   ├── Chatbot/                     # ChatWindow + MessageBubble (react-markdown)
│   │   └── Lecture/                     # LecturePlayer + SummaryPanel
│   ├── store/authStore.js               # Zustand global state
│   └── services/api.js                  # Axios + automatic JWT refresh
│
└── 📦 data/
    ├── student_aptitude_dataset.csv      # 10,000 synthetic student records
    └── content_metadata.json            # 44 content items (6 subjects × 7 types)
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

### Dataset

| Property | Value |
|---|---|
| Total records | 10,000 students |
| Features | logical, verbal, numerical, memory, attention (0–100) |
| Class distribution | 26% Visual · 22% Conceptual · 28% Practice · 24% Step-by-Step |
| Generated via | Controlled Gaussian distributions per learning style |

### Model Selection

```
Classifier              CV Accuracy    Notes
─────────────────────────────────────────────────────
Voting Ensemble ✅      93.3% ± 0.6%  GB + SVM + LR  ← USED
SVM (rbf, C=10)         93.4% ± 0.3%  Best single model
Gradient Boosting        93.2% ± 0.3%  150 estimators
Logistic Regression      93.1% ± 0.3%  Stable baseline
KNN (k=5)               92.2% ± 0.5%
KMeans (unsupervised)    92.0%         No label info used
─────────────────────────────────────────────────────
```

> **Why Voting Ensemble?** Single best model (SVM) aur Voting Ensemble ki accuracy almost same hai,
> but ensemble zyada **robust** hai — kisi ek model ke edge cases dusra model cover kar leta hai.
> Production mein stability > marginal accuracy gain.

### Feature Importance

```
numerical   30.1%  ████████████████
logical     21.1%  ██████████
verbal      20.1%  ██████████
memory      18.3%  █████████
attention   10.4%  █████
```

### Prediction Fallback Chain

```
1️⃣  Voting Ensemble Classifier  (93.3% accuracy)
         ↓ if model files not found
2️⃣  KMeans Clustering          (92.0% accuracy)
         ↓ if no models at all
3️⃣  Rule-Based (dominant feature → style mapping)
```

### Recommendation Scoring (0–100 points)

```
Content Type Match (preferred)  →  50 pts
Tag Boost Match (per tag, max 3) →  30 pts
Difficulty Progression          →  20 pts
Already Completed               →   0 pts  (skip)
```

Difficulty progression adapts automatically:
- 0 completions → prefer difficulty 1
- 3–7 completions → prefer difficulty 2
- 8+ completions → prefer difficulty 3–4

---

## 🗺️ User Flow

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Register / Login                                          │
│         │                                                   │
│         ▼                                                   │
│   Aptitude Test  ──────────────────────────────────────┐   │
│   25 questions · 5 sections · 30 min timer             │   │
│         │                                               │   │
│         ▼                                               │   │
│   ML Prediction (Voting Ensemble — 93.3% accuracy)     │   │
│         │                                               │   │
│    ┌────┴─────────────────────────┐                     │   │
│    │                              │                     │   │
│   👁️ Visual Learner         🧠 Conceptual             │   │
│   → Videos, Infographics     → Articles, Theory        │   │
│                                                         │   │
│   ⚙️ Practice-Based         📋 Step-by-Step            │   │
│   → Exercises, Projects     → Notes, Tutorials         │   │
│    └─────────────────────────────┘                     │   │
│         │                                               │   │
│         ▼                                               │   │
│   Personalized Dashboard                                │   │
│         │                                               │   │
│    ┌────▼─────────────┐                                 │   │
│    │  Learn Content   │ ◄── AI Chatbot (DeepSeek)       │   │
│    │  Mark Complete   │     Summary + Q&A               │   │
│    │  Rate (1-5 ⭐)   │                                  │   │
│    └────┬─────────────┘                                 │   │
│         │                                               │   │
│         ▼                                               │   │
│   Progress Tracking                                     │   │
│   Subject-wise charts                                   │   │
│         │                                               │   │
│         ▼                                               │   │
│   Re-Test after 30 days ────────────────────────────────┘   │
│   (Re-clustering — style may change with progress)          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Database Schema

```
users
├── _id, name, email, password_hash (bcrypt)
├── role: "student" | "teacher"
├── learning_style, cluster_id        ← Set after aptitude test
├── total_completed, last_test_date
└── needs_recluster, joined_at, last_login

test_results
├── user_id, attempt_number
├── scores: { logical, verbal, numerical, memory, attention, total }
├── cluster_id, learning_style, confidence
├── correct_answers (out of 25), total_marks (out of 500)
└── per_question: [...], submitted_at, ml_mode

progress
├── user_id, content_id
├── subject, content_type, difficulty
├── completed, completed_at, time_spent_min, notes
└── rating (1–5), comment, rated_at

refresh_tokens   →  user_id, token, expires_at (TTL index: 7 days)
otps             →  email, otp, expires_at (TTL index: 10 min), used
```

---

## ⚙️ Setup

### Prerequisites

```
Python  ≥ 3.11
Node.js ≥ 18.0
MongoDB ≥ 7.0
```

### 1. Clone

```bash
git clone https://github.com/YOUR_USERNAME/edu-platform.git
cd edu-platform
```

### 2. Train ML Models *(do this first)*

```bash
cd ml
pip install -r requirements.txt
python train_model.py
```

Expected output:
```
✅ Dataset loaded: data/student_aptitude_dataset.csv (10,000 rows)
CV Accuracy: 0.9330 ± 0.0062
✅ classifier.pkl · scaler.pkl · label_encoder.pkl · kmeans_model.pkl
🎉 Training Complete!
```

### 3. Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # Fill in your values
mongod                      # Start MongoDB
uvicorn main:app --reload
```

API → `http://localhost:8000`
Swagger → `http://localhost:8000/docs`

### 4. Frontend

```bash
cd frontend
npm install
cp .env.example .env        # VITE_API_URL=http://localhost:8000
npm run dev
```

App → `http://localhost:5173`

---

## 📡 API Documentation

### Auth

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register — JWT tokens milenge |
| `POST` | `/auth/login` | Login — access + refresh token |
| `POST` | `/auth/refresh` | Access token refresh (30 min) |
| `POST` | `/auth/logout` | Logout — token revoke |
| `GET` | `/auth/me` | Profile dekho |
| `PUT` | `/auth/me` | Profile update |
| `POST` | `/auth/forgot-password` | OTP email pe bhejo |
| `POST` | `/auth/reset-password` | OTP se password reset |

### Test

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/test/questions` | 25 questions (correct answers hidden) |
| `POST` | `/test/submit` | Submit → ML predict → style assign |
| `GET` | `/test/result` | Latest result + confidence score |
| `GET` | `/test/history` | Saare attempts |
| `POST` | `/test/retake` | 30-day cooldown ke baad |
| `GET` | `/test/model-info` | ML model version + accuracy |

### Content

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/content/recommendations` | Personalized list (filtered + scored) |
| `GET` | `/content/all` | Full library (subject/type/difficulty filter) |
| `GET` | `/content/search?q=` | Full-text search |
| `GET` | `/content/subjects` | Subject list + counts |
| `GET` | `/content/progress` | Learning progress + subject breakdown |
| `POST` | `/content/complete/{id}` | Mark complete + time tracking |
| `POST` | `/content/rate/{id}` | 1–5 star rating |

---

## 🛠️ Tech Stack

### ML
`scikit-learn` · `pandas` · `numpy` · `scipy` · `matplotlib` · `seaborn`

### Backend
`FastAPI` · `Motor (async MongoDB)` · `python-jose (JWT)` · `passlib[bcrypt]` · `pydantic-settings` · `httpx`

### Frontend
`React 18` · `Vite` · `Tailwind CSS` · `Zustand` · `Axios` · `Recharts` · `React Router v6` · `react-markdown` · `react-hot-toast` · `framer-motion`

### Database
`MongoDB 7.0` — Collections: `users` · `test_results` · `progress` · `refresh_tokens` · `otps`

---

## 🤝 Contributing

```bash
git checkout -b feature/your-feature
git commit -m "feat: add your feature"
git push origin feature/your-feature
# Open Pull Request
```

---

## 📄 License

[MIT](LICENSE) — freely use, modify, and distribute.

---

<div align="center">
<br/>

Built with ❤️ using **React · FastAPI · scikit-learn · MongoDB**

⭐ **Star karo agar helpful laga!**

</div>
