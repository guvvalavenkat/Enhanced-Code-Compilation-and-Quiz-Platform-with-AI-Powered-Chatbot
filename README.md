# Enhanced Code Compilation and Quiz Platform with AI-Powered Chatbot

**Live Demo:** [https://enhanced-code-compilation-and-quiz-4gk1.onrender.com/](https://enhanced-code-compilation-and-quiz-4gk1.onrender.com/)

---

## 📌 Project Overview

Enhanced Code Compilation and Quiz Platform with AI-Powered Chatbot is a full-stack web application built with **Flask** that integrates an online code editor, automated assessments, instructor-led quizzes, and an AI tutoring assistant. The platform supports role-based access (**student, faculty, admin**) using **Flask-Login** and **bcrypt**. Faculty can author coding problems with multiple test cases, create quizzes, and monitor student performance. Code execution is powered by the **Judge0 API** (via RapidAPI), and an AI assistant (Google Gemini API) provides on-demand hints and explanations. Real-time chat and notifications use **Flask-SocketIO**. Production data is stored in **PostgreSQL** (hosted on Railway), and the app is deployed to **Render** with `render.yaml` and served using **Gunicorn**.

---

## 🚀 Features

* Secure **role-based authentication** (student, faculty, admin)
* Real-time **code execution** across multiple languages (Judge0 integration)
* **Automated quizzes** and test-case based evaluation
* Integrated **AI chatbot** for coding assistance (Gemini)
* **Real-time chat** and live notifications (Flask-SocketIO)
* Role-specific dashboards and performance tracking
* Deployed on **Render**, database hosted on **Railway**

---

## 🛠️ Tech Stack

* **Backend:** Flask, Flask-SocketIO, SQLAlchemy, Alembic/Flask-Migrate
* **Frontend:** HTML, CSS, JS, Bootstrap, ACE Editor
* **Database:** PostgreSQL (Railway)
* **APIs:** Judge0 (code execution), Google Gemini (AI assistant)
* **Deployment:** Render, Gunicorn

---

## ⚙️ Installation (local)

> Assumes Python 3.10+ and PostgreSQL (or use a local sqlite for quick tests)

```bash
# clone
git clone <repo-url>
cd <project-folder>

# create venv and install
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
pip install -r requirements.txt

# set environment variables (example)
# export FLASK_APP=app.py
# export FLASK_ENV=development
# export DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# run migrations and start
flask db upgrade
flask run
```

---

## 🔐 Required Environment Variables

Create a `.env` (or set in your hosting provider) with at least:

```
FLASK_APP=app.py
FLASK_ENV=production
DATABASE_URL=<your-postgres-connection-url>
SECRET_KEY=<your-secret-key>
JUDGE0_API_URL=<judge0-endpoint>
JUDGE0_API_KEY=<judge0-api-key>
GEMINI_API_KEY=<google-gemini-api-key>
RAILWAY_DB_URL=<if using Railway DB URL>
```

> **Important:** Never commit API keys/credentials to version control. Use environment variables or your platform's secret manager.

---

## 📦 Deployment (Render + Railway)

1. Push repository to GitHub.
2. Create a new Web Service on **Render** and connect the GitHub repo. Use `render.yaml` if present for automatic configuration.
3. On Render, set environment variables (DATABASE\_URL, SECRET\_KEY, JUDGE0\_API\_KEY, GEMINI\_API\_KEY, etc.).
4. Railway or another managed PostgreSQL service should provide the production database URL; set it as `DATABASE_URL` on Render.
5. Render will build and start the service (Gunicorn recommended in `Procfile` or `render.yaml`).

---

## 🧭 Usage

* Visit the live demo: [https://enhanced-code-compilation-and-quiz-4gk1.onrender.com/](https://enhanced-code-compilation-and-quiz-4gk1.onrender.com/)
* Sign up as student/faculty/admin (or use seeded accounts if provided)
* Faculty: create problems/quizzes and add test cases
* Student: submit code, view compile/run outputs and quiz results
* Use the AI chat for hints and explanations during practice

---

## ✅ Production Notes & Recommendations

* Move all secrets to environment variables or your hosting secrets manager.
* Offload long-running compilation jobs to a background worker (e.g., Celery + Redis) to avoid blocking web workers.
* Add rate limiting and input sanitization to prevent abuse.
* Harden logging, monitoring (e.g., Sentry, Prometheus) and set up automated backups for the database.
