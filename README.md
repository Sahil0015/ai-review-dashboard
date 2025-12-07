# 🍽️ AI-Powered Yelp Review Analysis System

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29-red.svg)](https://streamlit.io)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-brightgreen.svg)](https://mongodb.com)
[![Groq](https://img.shields.io/badge/LLM-Groq%20LLaMA-purple.svg)](https://groq.com)

An intelligent review analysis system that uses LLMs to predict star ratings, generate summaries, and provide actionable business recommendations from Yelp reviews.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Project Structure](#-project-structure)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Task 1: Prompt Engineering & Evaluation](#-task-1-prompt-engineering--evaluation)
- [Task 2: Streamlit AI Dashboard](#-task-2-full-stack-ai-dashboard)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Author](#-author)

---

## 🎯 Overview

This project was developed as part of the **AI Intern Assessment**. It demonstrates:

1. **Prompt Engineering**: Designing, testing, and evaluating multiple prompt strategies for LLM-based review classification
2. **Full-Stack Development**: Building a production-ready AI-powered web application with real-time analytics

---

## 📁 Project Structure

```
Ai-intern-assessment/
├── Task1/                          # Prompt Engineering & Analysis
│   ├── task1.ipynb                 # Jupyter notebook with full analysis
│   ├── yelp.csv                    # Dataset (10,000 Yelp reviews)
│   ├── design.txt                  # Design workflow
│   └── prompt_evaluation_metrics.csv
│
├── Task2/                          # Full-Stack Application
│   ├── server/                     # FastAPI Backend
│   │   ├── app.py                  # Main API application
│   │   ├── config.py               # Groq/LLM configuration
│   │   ├── database.py             # MongoDB operations
│   │   ├── llm_service.py          # LLM prompts & calls
│   │   └── models.py               # Pydantic models
│   │
│   ├── client/                     # Streamlit Frontend
│   │   ├── user_app.py             # User review submission
│   │   └── admin_app.py            # Admin analytics dashboard
│   │
│   └── data/                       # Local data backup
│
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## ✨ Features

### 🔬 Task 1: Prompt Engineering
- **3 Prompt Versions** with different strategies:
  - **V1 (Simple)**: Baseline single-shot classification
  - **V2 (Criteria-Based)**: Detailed rating criteria with examples
  - **V3 (Chain-of-Thought)**: Step-by-step reasoning approach
- **Comprehensive Evaluation**: Accuracy, MAE, RMSE, Validity Rate
- **Reliability Testing**: Consistency across multiple runs
- **Detailed Visualizations**: Confusion matrices, error distributions

### 🖥️ Task 2: AI Dashboard

#### User Features
- ⭐ Submit reviews with 1-5 star ratings
- 🤖 Get AI-predicted ratings with explanations
- 📝 Receive AI-generated review summaries
- 💡 View business recommendations
- 🎭 Sentiment analysis (Positive/Negative/Mixed)

#### Admin Features
- 📊 Real-time analytics dashboard
- 🔄 Auto-refresh with configurable intervals
- 📈 Interactive charts (Rating & Sentiment distribution)
- 📋 View all submissions with details
- 📥 Export data to CSV
- 🆕 New submission indicators

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **LLM** | Groq API (LLaMA 3.1 8B Instant) |
| **Backend** | FastAPI + Uvicorn |
| **Frontend** | Streamlit |
| **Database** | MongoDB Atlas |
| **Data Validation** | Pydantic |
| **Visualization** | Plotly, Matplotlib, Seaborn |
| **ML/Data** | Pandas, NumPy, Scikit-learn |
| **Deployment** | Render (Backend), Streamlit Cloud (Frontend) |

---

## 🔬 Task 1: Prompt Engineering & Evaluation

### Workflow

```
Load Dataset (10,000 reviews)
        ↓
Sample 200 reviews (40 per star rating)
        ↓
Define 3 Prompt Versions
        ↓
Validate Input/Output with Pydantic
        ↓
Run LLM Predictions
        ↓
Calculate Metrics & Compare
        ↓
Reliability/Consistency Testing
        ↓
Final Analysis & Recommendations
```

### Prompt Strategies

| Version | Strategy | Description |
|---------|----------|-------------|
| **V1** | Simple | Direct classification prompt |
| **V2** | Criteria-Based | Explicit rating criteria (1-5★) with examples |
| **V3** | Chain-of-Thought | Systematic analysis of positives, negatives, tone |

### Evaluation Metrics

- **Accuracy**: Exact match percentage
- **MAE**: Mean Absolute Error
- **RMSE**: Root Mean Square Error
- **Validity Rate**: % of valid JSON responses
- **Off-by-1/2+ Analysis**: Error distribution

---

## 🖥️ Task 2: Full-Stack AI Dashboard

### Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User App      │────▶│   FastAPI       │────▶│   MongoDB       │
│  (Streamlit)    │     │   Backend       │     │   Atlas         │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
┌─────────────────┐              │
│   Admin App     │──────────────┘
│  (Streamlit)    │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│   Groq LLM      │
│   (LLaMA 3.1)   │
└─────────────────┘
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/health` | Detailed health status |
| `POST` | `/api/user/submit` | Submit review for AI analysis |
| `POST` | `/api/predict/v1` | Predict with V1 prompt |
| `POST` | `/api/predict/v2` | Predict with V2 prompt |
| `POST` | `/api/predict/v3` | Predict with V3 prompt |
| `GET` | `/api/admin/submissions` | Get all submissions |
| `GET` | `/api/admin/analytics` | Get dashboard analytics |
| `GET` | `/api/admin/evaluations` | Get evaluation metrics |

---

## 🚀 Installation

### Prerequisites

- Python 3.10+
- MongoDB Atlas account
- Groq API key

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sahil0015/ai-review-dashboard.git
   cd ai-review-dashboard
   ```

2. **Create virtual environment**
   ```bash
   python -m venv myenv
   
   # Windows
   myenv\Scripts\activate
   
   # Linux/Mac
   source myenv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## ⚙️ Configuration

Create a `.env` file in the root directory:

```env
# Groq API
GROQ_API_KEY=your_groq_api_key_here

# MongoDB Atlas
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

### MongoDB Atlas Setup

1. Create a free cluster at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a database user with read/write permissions
3. Whitelist your IP address (or `0.0.0.0/0` for development)
4. Get your connection string and add it to `.env`

---

## ▶️ Running the Application

### Task 1: Jupyter Notebook
```bash
cd Task1
jupyter notebook task1.ipynb
```

### Task 2: Full Application

**1. Start the FastAPI Backend**
```bash
cd Task2/server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**2. Start User Dashboard (new terminal)**
```bash
cd Task2/client
streamlit run user_app.py --server.port 8501
```

**3. Start Admin Dashboard (new terminal)**
```bash
cd Task2/client
streamlit run admin_app.py --server.port 8502
```

### Access Points

| Service | URL |
|---------|-----|
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| User Dashboard | http://localhost:8501 |
| Admin Dashboard | http://localhost:8502 |

---

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Example: Submit Review

```bash
curl -X POST "http://localhost:8000/api/user/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 4,
    "review_text": "Great food and excellent service! The pasta was amazing, though the wait was a bit long."
  }'
```

**Response:**
```json
{
  "predicted_stars": 4,
  "explanation": "Mostly positive with minor complaint about wait time",
  "ai_summary": "Customer enjoyed the food quality and service...",
  "recommended_actions": ["Optimize wait times during peak hours", "..."],
  "sentiment": "Positive",
  "submission_id": "abc12345",
  "timestamp": "2025-12-07T10:30:00"
}
```

---

## 🌐 Deployment

### Backend (Render)

1. Push code to GitHub
2. Create a new **Web Service** on [Render](https://render.com)
3. Connect your GitHub repository
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd Task2/server && uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (`GROQ_API_KEY`, `MONGODB_URI`)

### Frontend (Streamlit Cloud)

1. Deploy from GitHub at [Streamlit Cloud](https://streamlit.io/cloud)
2. Point to `Task2/client/user_app.py` or `admin_app.py`
3. Add secrets in Streamlit Cloud settings

### Live Demo

- **Backend API**: https://ai-review-dashboard.onrender.com
- **User App**: [Streamlit Cloud URL]
- **Admin App**: [Streamlit Cloud URL]

---

## 📊 Sample Results

### Prompt Comparison

| Metric | V1 (Simple) | V2 (Criteria) | V3 (CoT) |
|--------|-------------|---------------|----------|
| Accuracy | ~45% | ~52% | ~55% |
| MAE | ~0.85 | ~0.72 | ~0.68 |
| Validity | 98% | 99% | 99% |

*Results may vary based on sample selection and model behavior*

---

## 🧪 Testing

```bash
# Run API health check
curl http://localhost:8000/health

# Test prediction endpoint
curl -X POST "http://localhost:8000/api/predict/v3" \
  -H "Content-Type: application/json" \
  -d '{"review_text": "Absolutely loved this place! Best pizza in town."}'
```

---

## 📝 Logging

The application includes comprehensive logging:

- **Backend**: Structured logs with timestamps, levels, and function names
- **Database**: Connection status, operation success/failure logs
- **LLM Service**: API calls, retries, and error handling

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 👤 Author

**Sahil Aggarwal**

- 📧 Email: sahilaggarwal1532003@gmail.com
- 💼 LinkedIn: [sahil-codes](https://www.linkedin.com/in/sahil-codes/)
- 🐙 GitHub: [Sahil0015](https://github.com/Sahil0015)

---

## 📄 License

This project is licensed under the MIT License — feel free to use, modify, and share with attribution.

---

## 🙏 Acknowledgments

- [Fynd](https://www.fynd.com/) for the assessment opportunity
- [Groq](https://groq.com/) for the fast LLM inference API
- [MongoDB](https://mongodb.com/) for the database platform
- [Streamlit](https://streamlit.io/) for the easy-to-use frontend framework

---

<p align="center">
  Made with ❤️
</p>
