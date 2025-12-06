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


import logging
import sys

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Reduce noise from third-party libraries
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


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


# Test database connection on startup
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting Yelp Review AI System...")
    try:
        from database import client
        client.admin.command('ping')
        logger.info("✅ MongoDB connection successful")
        logger.info(f"📡 Server ready at http://0.0.0.0:8000")
        logger.info(f"📚 API docs available at http://0.0.0.0:8000/docs")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        logger.exception("Full traceback:")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Shutting down Yelp Review AI System...")


# ============================================
# HEALTH CHECK
# ============================================

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    logger.debug("Health check requested")
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
    logger.info(f"📝 New review submission received | Rating: {submission.rating} | Text length: {len(submission.review_text)} chars")
    logger.debug(f"Review text preview: {submission.review_text[:100]}...")
    
    try:
        # 1. Predict rating using V3 (best performing)
        logger.info("🔮 Step 1/4: Predicting rating using V3 prompt...")
        prediction = predict_rating(submission.review_text, prompt_version="v3")
        logger.info(f"✓ Prediction complete | Predicted: {prediction['predicted_stars']} stars | Actual: {submission.rating} stars")
        
        # 2. Generate summary and recommendations
        logger.info("📊 Step 2/4: Generating summary and recommendations...")
        summary, actions, sentiment = generate_summary_and_actions(
            submission.review_text,
            submission.rating,
            prediction['predicted_stars']
        )
        logger.info(f"✓ Analysis complete | Sentiment: {sentiment} | Actions: {len(actions)}")
        
        # 3. Generate user-facing response
        logger.info("💬 Step 3/4: Generating user response...")
        user_response = generate_user_response(submission.review_text, submission.rating)
        logger.info(f"✓ Response generated | Length: {len(user_response)} chars")
        
        # 4. Save to database
        logger.info("💾 Step 4/4: Saving to database...")
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
        logger.info(f"✅ Submission saved successfully | ID: {submission_id}")
        
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
        logger.error(f"❌ Error processing submission: {str(e)}")
        logger.exception("Full traceback:")
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
    logger.info(f"🔮 Prediction request (V1) | Text length: {len(request.review_text)} chars")
    try:
        result = predict_rating(request.review_text, prompt_version="v1")
        logger.info(f"✓ V1 Prediction: {result['predicted_stars']} stars")
        return PredictionResponse(
            predicted_stars=result['predicted_stars'],
            explanation=result['explanation'],
            prompt_version="v1"
        )
    except Exception as e:
        logger.error(f"❌ V1 Prediction failed: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict/v2", response_model=PredictionResponse, tags=["Prediction"])
async def predict_v2(request: PredictionRequest):
    """Predict rating using V2 (Criteria-based) prompt"""
    logger.info(f"🔮 Prediction request (V2) | Text length: {len(request.review_text)} chars")
    try:
        result = predict_rating(request.review_text, prompt_version="v2")
        logger.info(f"✓ V2 Prediction: {result['predicted_stars']} stars")
        return PredictionResponse(
            predicted_stars=result['predicted_stars'],
            explanation=result['explanation'],
            prompt_version="v2"
        )
    except Exception as e:
        logger.error(f"❌ V2 Prediction failed: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict/v3", response_model=PredictionResponse, tags=["Prediction"])
async def predict_v3(request: PredictionRequest):
    """Predict rating using V3 (Chain-of-thought) prompt"""
    logger.info(f"🔮 Prediction request (V3) | Text length: {len(request.review_text)} chars")
    try:
        result = predict_rating(request.review_text, prompt_version="v3")
        logger.info(f"✓ V3 Prediction: {result['predicted_stars']} stars")
        return PredictionResponse(
            predicted_stars=result['predicted_stars'],
            explanation=result['explanation'],
            prompt_version="v3"
        )
    except Exception as e:
        logger.error(f"❌ V3 Prediction failed: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict_any(request: PredictionRequest):
    """Predict rating using any prompt version (v1/v2/v3)"""
    logger.info(f"🔮 Prediction request ({request.prompt_version}) | Text length: {len(request.review_text)} chars")
    try:
        result = predict_rating(request.review_text, prompt_version=request.prompt_version)
        logger.info(f"✓ {request.prompt_version.upper()} Prediction: {result['predicted_stars']} stars")
        return PredictionResponse(
            predicted_stars=result['predicted_stars'],
            explanation=result['explanation'],
            prompt_version=request.prompt_version
        )
    except Exception as e:
        logger.error(f"❌ {request.prompt_version.upper()} Prediction failed: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# ADMIN ENDPOINTS
# ============================================

@app.get("/api/admin/submissions", response_model=list[AdminSubmission], tags=["Admin"])
async def get_submissions():
    """Get all review submissions for admin dashboard"""
    logger.info("📋 Admin request: Fetching all submissions...")
    try:
        submissions = get_all_submissions()
        logger.info(f"✓ Retrieved {len(submissions)} submissions")
        return submissions
    except Exception as e:
        logger.error(f"❌ Failed to fetch submissions: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/analytics", tags=["Admin"])
async def get_dashboard_analytics():
    """Get analytics for admin dashboard"""
    logger.info("📈 Admin request: Fetching analytics...")
    try:
        analytics = get_analytics()
        logger.info(f"✓ Analytics retrieved | Total submissions: {analytics.get('total_submissions', 'N/A')}")
        return analytics
    except Exception as e:
        logger.error(f"❌ Failed to fetch analytics: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/evaluations", response_model=list[EvaluationMetrics], tags=["Admin"])
async def get_evaluations():
    """Get evaluation metrics for all prompt versions"""
    logger.info("📊 Admin request: Fetching evaluation metrics...")
    try:
        evaluations = get_evaluation_metrics()
        logger.info(f"✓ Retrieved {len(evaluations)} evaluation records")
        return evaluations
    except Exception as e:
        logger.error(f"❌ Failed to fetch evaluations: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/evaluate", tags=["Admin"])
async def save_evaluation(metrics: EvaluationMetrics):
    """Save evaluation metrics (called after running notebook evaluation)"""
    logger.info(f"💾 Admin request: Saving evaluation metrics for {metrics.prompt_version}...")
    logger.debug(f"Metrics: Accuracy={metrics.accuracy}, MAE={metrics.mae}, RMSE={metrics.rmse}")
    try:
        save_evaluation_metrics(metrics.dict())
        logger.info(f"✅ Evaluation metrics saved for {metrics.prompt_version}")
        return {"message": "Evaluation metrics saved successfully"}
    except Exception as e:
        logger.error(f"❌ Failed to save evaluation metrics: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# RUN SERVER
# ============================================

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
