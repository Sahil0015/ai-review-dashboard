from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import uvicorn

from models import (
    ReviewSubmission, AIResponse, PredictionRequest, PredictionResponse,
    AdminSubmission, EvaluationMetrics
)
from llm_service import (
    predict_rating, generate_summary_and_actions, generate_user_response
)
from database import (
    save_submission, get_all_submissions, get_analytics,
    save_evaluation_metrics, get_evaluation_metrics
)

# ============================================
# FASTAPI APP INITIALIZATION
# ============================================

app = FastAPI(
    title="Yelp Review AI System",
    description="AI-powered review rating prediction and feedback system for Fynd Assessment",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# HEALTH CHECK
# ============================================

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Yelp Review AI System",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "components": {
            "api": "operational",
            "llm_service": "operational",
            "database": "operational"
        }
    }

# ============================================
# USER ENDPOINTS
# ============================================

@app.post("/api/user/submit", response_model=AIResponse, tags=["User"])
async def submit_review(submission: ReviewSubmission):
    """
    User submits a review with rating.
    Returns AI analysis and personalized response.
    """
    try:
        # 1. Predict rating using V2 (best performing)
        prediction = predict_rating(submission.review_text, prompt_version="v3")
        
        # 2. Generate summary and recommendations
        summary, actions, sentiment = generate_summary_and_actions(
            submission.review_text,
            submission.rating,
            prediction['predicted_stars']
        )
        
        # 3. Generate user-facing response
        user_response = generate_user_response(submission.review_text, submission.rating)
        
        # 4. Save to database
        submission_id = save_submission({
            'user_rating': submission.rating,
            'review_text': submission.review_text,
            'ai_predicted_rating': prediction['predicted_stars'],
            'ai_explanation': prediction['explanation'],
            'ai_summary': summary,
            'recommended_actions': actions,
            'sentiment': sentiment,
            'user_response': user_response
        })
        
        return AIResponse(
            predicted_stars=prediction['predicted_stars'],
            explanation=prediction['explanation'],
            ai_summary=summary,
            recommended_actions=actions,
            sentiment=sentiment,
            submission_id=submission_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing submission: {str(e)}"
        )

# ============================================
# PREDICTION ENDPOINTS (For Testing)
# ============================================

@app.post("/api/predict/v1", response_model=PredictionResponse, tags=["Prediction"])
async def predict_v1(request: PredictionRequest):
    """Predict rating using V1 (Simple) prompt"""
    try:
        result = predict_rating(request.review_text, prompt_version="v1")
        return PredictionResponse(
            predicted_stars=result['predicted_stars'],
            explanation=result['explanation'],
            prompt_version="v1"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict/v2", response_model=PredictionResponse, tags=["Prediction"])
async def predict_v2(request: PredictionRequest):
    """Predict rating using V2 (Criteria-based) prompt"""
    try:
        result = predict_rating(request.review_text, prompt_version="v2")
        return PredictionResponse(
            predicted_stars=result['predicted_stars'],
            explanation=result['explanation'],
            prompt_version="v2"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict/v3", response_model=PredictionResponse, tags=["Prediction"])
async def predict_v3(request: PredictionRequest):
    """Predict rating using V3 (Chain-of-thought) prompt"""
    try:
        result = predict_rating(request.review_text, prompt_version="v3")
        return PredictionResponse(
            predicted_stars=result['predicted_stars'],
            explanation=result['explanation'],
            prompt_version="v3"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict_any(request: PredictionRequest):
    """Predict rating using any prompt version (v1/v2/v3)"""
    try:
        result = predict_rating(request.review_text, prompt_version=request.prompt_version)
        return PredictionResponse(
            predicted_stars=result['predicted_stars'],
            explanation=result['explanation'],
            prompt_version=request.prompt_version
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# ADMIN ENDPOINTS
# ============================================

@app.get("/api/admin/submissions", response_model=list[AdminSubmission], tags=["Admin"])
async def get_submissions():
    """Get all review submissions for admin dashboard"""
    try:
        submissions = get_all_submissions()
        return submissions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/analytics", tags=["Admin"])
async def get_dashboard_analytics():
    """Get analytics for admin dashboard"""
    try:
        analytics = get_analytics()
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/evaluations", response_model=list[EvaluationMetrics], tags=["Admin"])
async def get_evaluations():
    """Get evaluation metrics for all prompt versions"""
    try:
        evaluations = get_evaluation_metrics()
        return evaluations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/evaluate", tags=["Admin"])
async def save_evaluation(metrics: EvaluationMetrics):
    """Save evaluation metrics (called after running notebook evaluation)"""
    try:
        save_evaluation_metrics(metrics.dict())
        return {"message": "Evaluation metrics saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# RUN SERVER
# ============================================

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
