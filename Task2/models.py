from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime

class ReviewSubmission(BaseModel):
    """User review submission model"""
    rating: int = Field(..., ge=1, le=5, description="User's star rating (1-5)")
    review_text: str = Field(..., min_length=10, max_length=1000, description="Review content")
    
    @validator('review_text')
    def clean_review(cls, v):
        return v.strip()

class AIResponse(BaseModel):
    """AI-generated response model"""
    predicted_stars: int = Field(..., ge=1, le=5)
    explanation: str
    ai_summary: str
    recommended_actions: list[str]
    sentiment: str
    submission_id: str
    timestamp: str

class PredictionRequest(BaseModel):
    """Request for rating prediction"""
    review_text: str = Field(..., min_length=10, max_length=1000)
    prompt_version: Literal["v1", "v2", "v3"] = "v2"

class PredictionResponse(BaseModel):
    """Response from rating prediction"""
    predicted_stars: int
    explanation: str
    confidence: Optional[str] = None
    prompt_version: str

class AdminSubmission(BaseModel):
    """Admin view of a submission"""
    submission_id: str
    timestamp: str
    user_rating: int
    review_text: str
    ai_predicted_rating: int
    ai_summary: str
    recommended_actions: list[str]
    sentiment: str
    rating_match: bool

class EvaluationMetrics(BaseModel):
    """Evaluation metrics for prompt versions"""
    prompt_version: str
    accuracy: float
    mae: float
    validity_rate: float
    exact_matches: int
    off_by_1: int
    off_by_2_plus: int
    total_samples: int
