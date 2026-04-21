# Access2Education — AI-Powered Personalized Learning Platform

Access2Education is a cutting-edge, full-stack educational platform designed to revolutionize the way students learn. By leveraging **Machine Learning (ML)** for learning-style clustering, the **SM-2 Spaced Repetition Algorithm** for long-term memory retention, and **AI Tutoring**, it adapts it's curriculum to every student's unique "Learning DNA."

---

## 🚀 System Architecture & Workflow

The following diagram illustrates the seamless interaction between the Frontend, Backend, ML Engine, and Database.

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

    B_DB --> DB_Cloud[("MongoDB Atlas")]
    
    F_Entry <-->|REST API| B_Main
```

---

## ✨ Key Features

### 🧠 Adaptive Learning DNA (ML Clustering)
The platform doesn't just teach—it learns about you. Upon entry, students take a multi-dimensional aptitude test. Our **K-Means Clustering model** analyzes results across Logical, Verbal, Numerical, Memory, and Attention scores to categorize the student into one of four distinct learning styles:
- **Visual Learner**: Prioritizes diagrams and video lectures.
- **Conceptual Thinker**: Focuses on deep theory and case studies.
- **Practice-Based**: emphasizes hands-on coding and projects.
- **Step-by-Step**: Follows structured, sequential notes.

### 📅 Smart Revision (SM-2 Spaced Repetition)
We use the **SuperMemo-2 (SM-2)** algorithm to optimize your memory. The system tracks your performance on every topic and calculates the exact date you need to revise it to prevent the "forgetting curve."

### 🤖 AI Tutor (DeepSeek Integration)
Integrated with the **DeepSeek-V3** model, our AI chatbot acts as a 24/7 personal tutor, answering complex questions, explaining code, and providing hints based on the student's current progress.

---

## 🛠️ Technology Stack

- **Frontend**: React (Vite), Tailwind CSS, Framer Motion, Lucide Icons.
- **Backend**: FastAPI (Python), Motor (Async MongoDB), Pydantic.
- **Machine Learning**: Scikit-learn, Numpy, Joblib (Ensemble Clustering).
- **Database**: MongoDB Atlas.
- **Deployment**: Vercel (Monorepo setup).

---

## 🌐 Deployment (Vercel)

This project is configured as a Vercel-ready monorepo.

### Configuration & Deployment
1. **Repository Linking**: Connect this repository to your **Vercel** account.
2. **Environment Setup**: In the Vercel Project Settings, add the required environment variables:
   - Database Connection Strings (`MONGODB_URL`).
   - Security Secrets (`SECRET_KEY`).
   - Third-party AI Integration keys.
3. **Trigger Build**: Vercel will use the `vercel.json` orchestration to deploy the full-stack application.

---

## 📁 Project Structure

```text
Access2Education/
├── Backend/            # FastAPI Server, Routes, and DB logic
├── Frontend/           # React/Vite Application
├── ML/                 # Training scripts and Pickled Models (.pkl)
├── data/               # Metadata and datasets
├── Dockerfile.backend  # Self-hosting Docker config
└── vercel.json         # Vercel Monorepo Router
```

---

## 👨‍💻 Author
**Sambit** — [GitHub](https://github.com/sambitji)

*"Accessing Quality Education for Everyone"*
