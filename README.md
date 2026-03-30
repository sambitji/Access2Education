# Access2Education
AI-powered education platform designed to improve learning outcomes and accessibility by combining personalized instruction, data-driven performance analysis, and human–AI collaboration to support social and economic development.
<div align="center">

# 🎓 EduPlatform
### AI-Powered Personalized Learning System

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://mongodb.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)

> **Student ka aptitude test lo → ML model learning style detect kare → Personalized content recommend karo**

[Features](#-features) • [Architecture](#-architecture) • [Setup](#-setup) • [API Docs](#-api-documentation) • [ML Pipeline](#-ml-pipeline) • [Screenshots](#-screenshots)

---

![EduPlatform Banner](https://via.placeholder.com/900x300/0f172a/6366f1?text=EduPlatform+%7C+AI+Powered+Learning)

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **Aptitude Test** | 25 questions, 5 sections, 30 minutes — logical, verbal, numerical, memory, attention |
| 🤖 **ML Clustering** | Voting Ensemble (GB + SVM + LR) — **93.3% CV accuracy** — 4 learning styles |
| 🎯 **Personalized Recommendations** | Style ke hisaab se content score karta hai (0-100) |
| 💬 **AI Chatbot** | DeepSeek-powered lecture summarizer + Q&A |
| 📊 **Progress Tracking** | Subject-wise completion aur visual charts |
| 🔐 **JWT Auth** | Dual token (access 30min + refresh 7 days) + OTP password reset |

---

## 🏗️ Architecture

```
edu-platform/
│
├── 🤖 ml/                          # Machine Learning Pipeline
│   ├── notebooks/
│   │   ├── 01_data_exploration.ipynb
│   │   ├── 02_clustering.ipynb
│   │   └── 03_recommendation.ipynb
│   ├── models/                     # Trained model files (.pkl)
│   ├── train_model.py              # Ensemble model train karo
│   ├── predict_cluster.py          # Prediction engine (3-tier fallback)
│   └── recommender.py              # Content recommendation engine
│
├── ⚙️ backend/                     # FastAPI Server
│   ├── routes/
│   │   ├── auth.py                 # Login, Register, JWT, OTP
│   │   ├── test.py                 # Aptitude test + ML prediction
│   │   └── content.py              # Recommendations + Progress
│   ├── models/
│   │   ├── user.py
│   │   ├── result.py
│   │   └── content.py
│   ├── database/db.py              # MongoDB + Indexes
│   ├── config.py                   # Centralized settings
│   └── main.py                     # FastAPI entry point
│
├── 🎨 frontend/                    # React + Vite + Tailwind
│   └── src/
│       ├── pages/                  # Home, Login, Register, Test, Dashboard, Learn, Progress
│       ├── components/
│       │   ├── AptitudeTest/       # Test UI + QuestionCard
│       │   ├── Dashboard/          # StudentDashboard + ProgressChart
│       │   ├── Chatbot/            # ChatWindow + MessageBubble
│       │   └── Lecture/            # LecturePlayer + SummaryPanel
│       ├── store/authStore.js      # Zustand global state
│       └── services/api.js         # Axios + auto token refresh
│
└── 📦 data/
    ├── student_aptitude_dataset.csv  # 10,000 student records
    └── content_metadata.json         # 44 content items
```

---

## 🤖 ML Pipeline

### Learning Styles (4 Clusters)

| Style | Emoji | Dominant Feature | Best Content |
|---|---|---|---|
| Visual Learner | 👁️ | High Verbal + Memory | Videos, Infographics |
| Conceptual Thinker | 🧠 | High Logical | Articles, Case Studies |
| Practice-Based | ⚙️ | High Numerical + Attention | Exercises, Projects |
| Step-by-Step | 📋 | High Memory | Notes, Tutorials |

### Model Performance

```
Model Comparison (5-fold CV):
──────────────────────────────────────────────
Voting Ensemble (GB+SVM+LR)  : 93.3% ± 0.6%  ✅ USED
SVM (rbf)                    : 93.4% ± 0.3%
Gradient Boosting            : 93.2% ± 0.3%
Logistic Regression          : 93.1% ± 0.3%
KMeans (unsupervised)        : 92.0%
──────────────────────────────────────────────

Feature Importance:
  numerical  : 30.1%  ████████████████
  logical    : 21.1%  ██████████
  verbal     : 20.1%  ██████████
  memory     : 18.3%  █████████
  attention  : 10.4%  █████
```

### Prediction Fallback Chain
```
Ensemble Classifier (93.3%)
        ↓ (if model not found)
KMeans Clustering (92.0%)
        ↓ (if no models at all)
Rule-Based (dominant feature)
```

---

## 🚀 Setup

### Prerequisites

```bash
Node.js >= 18.0
Python >= 3.11
MongoDB >= 7.0
```

### Step 1 — Clone karo

```bash
git clone https://github.com/YOUR_USERNAME/edu-platform.git
cd edu-platform
```

### Step 2 — ML Models Train Karo *(pehle ye karo)*

```bash
cd ml
pip install -r requirements.txt
python train_model.py
```

Output:
```
✅ Dataset loaded: data/student_aptitude_dataset.csv
   Rows: 10000
CV Accuracy: 0.9330 ± 0.0062
✅ classifier.pkl
✅ scaler.pkl
✅ label_encoder.pkl
✅ kmeans_model.pkl
✅ cluster_map.pkl
🎉 Training Complete! CV Accuracy: 0.9330
```

### Step 3 — Backend Setup

```bash
cd backend

# Virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Environment variables setup
cp .env.example .env
# .env mein apni values bharo (neeche dekho)
```

**`backend/.env`:**
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=edu_platform
SECRET_KEY=<run: python -c "import secrets; print(secrets.token_hex(32))">
REFRESH_SECRET_KEY=<run again for different key>
DEEPSEEK_API_KEY=your-deepseek-api-key
```

```bash
# MongoDB start karo (local)
mongod

# Server start karo
uvicorn main:app --reload --port 8000
```

✅ API: `http://localhost:8000`
✅ Swagger Docs: `http://localhost:8000/docs`

### Step 4 — Frontend Setup

```bash
cd frontend
npm install

# Environment setup
cp .env.example .env
# .env mein: VITE_API_URL=http://localhost:8000

npm run dev
```

✅ App: `http://localhost:5173`

---

## 📡 API Documentation

### Auth Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | New account banao |
| `POST` | `/auth/login` | Login — JWT tokens milenge |
| `POST` | `/auth/refresh` | Access token refresh karo |
| `POST` | `/auth/logout` | Logout — token invalidate |
| `GET` | `/auth/me` | Apna profile dekho |
| `PUT` | `/auth/me` | Profile update karo |
| `POST` | `/auth/forgot-password` | OTP email pe bhejo |
| `POST` | `/auth/reset-password` | OTP se password reset |

### Test Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/test/questions` | 25 questions fetch karo |
| `POST` | `/test/submit` | Answers submit → ML predict |
| `GET` | `/test/result` | Latest result dekho |
| `GET` | `/test/history` | Saare attempts ki history |
| `POST` | `/test/retake` | 30 din baad retake |
| `GET` | `/test/model-info` | ML model ki info |

### Content Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/content/recommendations` | Personalized recommendations |
| `GET` | `/content/all` | Saara content (filters) |
| `GET` | `/content/search?q=` | Search karo |
| `GET` | `/content/subjects` | Subjects list |
| `GET` | `/content/progress` | Learning progress |
| `POST` | `/content/complete/{id}` | Content complete mark karo |
| `POST` | `/content/rate/{id}` | Rating do |

---

## 🔐 API Keys Ko Safe Rakhna

### Step 1 — `.env` files kabhi push mat karo

`.gitignore` mein ye lines hain:
```
backend/.env
frontend/.env
.env.local
*.secret
```

### Step 2 — Keys already push ho gayi hain?

```bash
# History se hata do
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch backend/.env' \
  --prune-empty --tag-name-filter cat -- --all

# Force push
git push origin --force --all
```

### Step 3 — `.env.example` files commit karo *(without real values)*

```bash
git add backend/.env.example
git add frontend/.env.example
git commit -m "Add env examples"
```

### Step 4 — Keys rotate karo *(if they were exposed)*

```bash
# Naya SECRET_KEY generate karo
python -c "import secrets; print(secrets.token_hex(32))"

# DeepSeek: platform.deepseek.com → API Keys → Regenerate
# MongoDB Atlas: Security → Database Access → Edit → Update Password
```

---

## 🗂️ Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Required | Description |
|---|---|---|
| `MONGODB_URL` | ✅ | MongoDB connection string |
| `DATABASE_NAME` | ✅ | Database ka naam |
| `SECRET_KEY` | ✅ | JWT signing key (min 32 chars) |
| `REFRESH_SECRET_KEY` | ✅ | Refresh token key (different from above) |
| `DEEPSEEK_API_KEY` | ✅ | DeepSeek chatbot ke liye |
| `DEBUG` | ❌ | `True` dev mein, `False` production mein |
| `ML_MODELS_PATH` | ❌ | Default: `../ml/models` |
| `RETEST_COOLDOWN_DAYS` | ❌ | Default: `30` |
| `EMAIL_ENABLED` | ❌ | `False` (OTP console pe print hoga) |

### Frontend (`frontend/.env`)

| Variable | Required | Description |
|---|---|---|
| `VITE_API_URL` | ✅ | Backend URL — `http://localhost:8000` |

---

## 🛠️ Tech Stack

### ML
- **scikit-learn** — VotingClassifier, KMeans, StandardScaler
- **pandas / numpy** — Data processing
- **matplotlib / seaborn** — Visualization

### Backend
- **FastAPI** — Async REST API
- **Motor** — Async MongoDB driver
- **python-jose** — JWT authentication
- **passlib[bcrypt]** — Password hashing
- **httpx** — DeepSeek API calls
- **pydantic-settings** — Config management

### Frontend
- **React 18** + **Vite** — Fast build tool
- **Tailwind CSS** — Utility-first styling
- **Zustand** — Lightweight state management
- **Axios** — HTTP client + auto token refresh
- **Recharts** — Charts aur graphs
- **React Router v6** — Client-side routing
- **react-markdown** — Chatbot response rendering
- **react-hot-toast** — Notifications

### Database
- **MongoDB** — Flexible document storage
- **Collections**: `users`, `test_results`, `progress`, `refresh_tokens`, `otps`

---

## 📊 Database Schema

```
users {
  _id, name, email, password_hash, role,
  learning_style, cluster_id,           ← Set after aptitude test
  total_completed, last_test_date,
  needs_recluster, joined_at, last_login
}

test_results {
  user_id, attempt_number,
  scores: { logical, verbal, numerical, memory, attention, total },
  cluster_id, learning_style, confidence,
  correct_answers, total_marks,
  per_question: [...], submitted_at
}

progress {
  user_id, content_id, subject,
  completed, completed_at,
  time_spent_min, notes,
  rating, comment, rated_at
}
```

---

## 🗺️ User Flow

```
Register
   │
   ▼
Aptitude Test (25 questions)
   │
   ▼
ML Model Predicts Learning Style
(Voting Ensemble — 93.3% accuracy)
   │
   ├──► visual_learner     → Videos + Infographics
   ├──► conceptual_thinker → Articles + Case Studies
   ├──► practice_based     → Exercises + Projects
   └──► step_by_step       → Notes + Tutorials
         │
         ▼
    Personalized Dashboard
         │
         ▼
    Learn Content
         │
    AI Chatbot (DeepSeek) → Summary + Q&A
         │
         ▼
    Mark Complete + Rate
         │
         ▼
    Progress Tracking
         │
         ▼
    Re-Test after 30 days → Re-clustering
```

---

## 🤝 Contributing

```bash
# Fork karo aur clone karo
git clone https://github.com/YOUR_USERNAME/edu-platform.git

# Branch banao
git checkout -b feature/your-feature-name

# Changes karo aur commit karo
git add .
git commit -m "feat: add your feature"

# Push karo
git push origin feature/your-feature-name

# Pull Request create karo
```

---

## 📄 License

MIT License — freely use, modify, and distribute.

---

<div align="center">

Made with ❤️ | React + FastAPI + scikit-learn + MongoDB

⭐ Star karo agar helpful laga!

</div>
