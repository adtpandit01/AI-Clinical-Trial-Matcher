# 🧬 AI Clinical Trial Matcher

An AI-powered system that matches patient descriptions with relevant clinical trials using semantic search and LLM reasoning.

This project demonstrates a **production-style Generative AI pipeline** including:

- Vector Search
- LLM reasoning
- Secure authentication
- API + Frontend architecture

---

# 🚀 Features

### 🔐 Authentication System
- User registration
- Login with JWT authentication
- Password reset
- Protected API endpoints

### 🧠 AI Patient Matching
Users enter a free-text patient description such as:60 year old male with stage IV lung cancer


The system:

1. Converts the patient text into embeddings
2. Searches a vector database of clinical trials
3. Retrieves the most relevant trials
4. Uses an LLM to explain why the trial matches

### 🔎 Semantic Trial Search
Clinical trials are stored in **ChromaDB** with embeddings of eligibility criteria.

Similarity search finds the most relevant trials.

### 🤖 AI Explanation Engine
An LLM generates a human-readable explanation describing why a trial matches the patient profile.

---

# 🏗️ System Architecture
Streamlit UI
↓
FastAPI Backend
↓
Patient Text → Embedding Model
↓
Vector Search (ChromaDB)
↓
Top Matching Trials
↓
LLM Explanation (Groq)

# 📂 Project Structure

clinical-matcher/
│
├── app/
│ ├── auth/
│ │ ├── auth_routes.py
│ │ └── auth_service.py
│ │
│ ├── db/
│ │ └── database.py
│ │
│ ├── services/
│ │ ├── embedding_service.py
│ │ ├── vector_store.py
│ │ ├── trials_api_service.py
│ │ ├── explanation_service.py
│ │ └── patient_extraction_service.py
│ │
│ └── main.py
│
├── frontend/
│ └── streamlit_app.py
│
├── requirements.txt
└── README.md


---

# ⚙️ Installation

### 1️⃣ Clone Repository

```
bash
git clone https://github.com/adtpandit01/clinical-trial-matcher.git
cd clinical-trial-matcher

'''
###2️⃣ Create Virtual Environment
python -m venv venv

###Activate environment:

Windows

venv\Scripts\activate

Mac/Linux

source venv/bin/activate
###3️⃣ Install Dependencies
pip install -r requirements.txt
🔑 Environment Variables

Create a .env file in the root folder:

GROQ_API_KEY=your_api_key
HF_TOKEN=your_huggingface_token
JWT_SECRET_KEY=your_secret_key
▶️ Running the Application
Start Backend
uvicorn app.main:app --reload

Backend will run at:

http://127.0.0.1:8000
Start Frontend
streamlit run frontend/streamlit_app.py

Frontend will run at:

http://localhost:8501
📊 Example Output

Input:

60 year old male with stage IV lung cancer

Output:

🏆 Best Match
Phase II Trial of Almonertinib Plus Lastet for EGFR+ NSCLC

Similarity Score: 0.53

Explanation:
This trial may match the patient because it targets stage IV
non-small cell lung cancer patients.
🧪 API Endpoints
Endpoint	Description
POST /register	Register user
POST /login	Login user
POST /reset-password	Reset password
GET /search-trials	Fetch clinical trials
POST /match-patient	Match patient to trials
🛠️ Tech Stack

Backend

FastAPI

Python

AI

Sentence Transformers

ChromaDB

Groq LLM

Frontend

Streamlit

Database

SQLite

📌 Future Improvements

LangGraph reasoning agent

Eligibility criteria parsing

Trial ranking optimization

Public deployment

---

# 3️⃣ How to Push to GitHub

Run:

```bash
git init
git add .
git commit -m "Initial commit - AI Clinical Trial Matcher"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/clinical-matcher.git
git push -u origin main



👨‍💻 Author

Adarsh Tiwari
AI Engineer

