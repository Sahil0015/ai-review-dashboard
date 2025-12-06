from pymongo import MongoClient, DESCENDING
from datetime import datetime
from typing import List, Dict
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

# ============================================
# MONGODB CONNECTION
# ============================================

MONGODB_URI = os.getenv("MONGODB_URI")

client = MongoClient(MONGODB_URI)
db = client["yelp_review_system"]  # Database name

# Collections
submissions_collection = db["submissions"]
evaluations_collection = db["evaluations"]

print(f"✅ Connected to MongoDB: {db.name}")


# ============================================
# SUBMISSION OPERATIONS
# ============================================

def save_submission(data: Dict) -> str:
    """Save a new submission to MongoDB and return submission ID"""
    submission_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()
    
    document = {
        '_id': submission_id,  # Use submission_id as MongoDB _id
        'submission_id': submission_id,
        'timestamp': timestamp,
        'user_rating': data['user_rating'],
        'review_text': data['review_text'],
        'ai_predicted_rating': data['ai_predicted_rating'],
        'ai_explanation': data['ai_explanation'],
        'ai_summary': data['ai_summary'],
        'recommended_actions': data['recommended_actions'],
        'sentiment': data['sentiment'],
        'user_response': data.get('user_response', '')
    }
    
    submissions_collection.insert_one(document)
    return submission_id


def get_all_submissions() -> List[Dict]:
    """Get all submissions from MongoDB (sorted by newest first)"""
    submissions = list(
        submissions_collection.find({}, {'_id': 0})  # Exclude MongoDB _id from results
        .sort('timestamp', DESCENDING)
    )
    
    # Add rating_match field
    for sub in submissions:
        sub['rating_match'] = sub['user_rating'] == sub['ai_predicted_rating']
    
    return submissions


def get_analytics() -> Dict:
    """Calculate analytics from MongoDB data"""
    submissions = list(submissions_collection.find({}))
    
    if len(submissions) == 0:
        return {
            'total_submissions': 0,
            'average_user_rating': 0,
            'average_predicted_rating': 0,
            'accuracy': 0,
            'sentiment_distribution': {},
            'rating_distribution': {}
        }
    
    total = len(submissions)
    user_ratings = [s['user_rating'] for s in submissions]
    predicted_ratings = [s['ai_predicted_rating'] for s in submissions]
    sentiments = [s['sentiment'] for s in submissions]
    
    # Calculate accuracy
    matches = sum(1 for s in submissions if s['user_rating'] == s['ai_predicted_rating'])
    accuracy = (matches / total * 100) if total > 0 else 0
    
    # Sentiment distribution
    sentiment_dist = {}
    for sentiment in sentiments:
        sentiment_dist[sentiment] = sentiment_dist.get(sentiment, 0) + 1
    
    # Rating distribution
    rating_dist = {}
    for rating in user_ratings:
        rating_dist[rating] = rating_dist.get(rating, 0) + 1
    
    return {
        'total_submissions': total,
        'average_user_rating': round(sum(user_ratings) / total, 2),
        'average_predicted_rating': round(sum(predicted_ratings) / total, 2),
        'accuracy': round(accuracy, 2),
        'sentiment_distribution': sentiment_dist,
        'rating_distribution': rating_dist
    }


# ============================================
# EVALUATION OPERATIONS
# ============================================

def save_evaluation_metrics(metrics: Dict):
    """Save evaluation metrics to MongoDB"""
    metrics['timestamp'] = datetime.now().isoformat()
    evaluations_collection.insert_one(metrics)


def get_evaluation_metrics() -> List[Dict]:
    """Get all evaluation metrics from MongoDB"""
    evaluations = list(
        evaluations_collection.find({}, {'_id': 0})
        .sort('timestamp', DESCENDING)
    )
    return evaluations


# ============================================
# UTILITY FUNCTIONS
# ============================================

def clear_all_submissions():
    """Clear all submissions (use with caution!)"""
    result = submissions_collection.delete_many({})
    return result.deleted_count


def get_submission_by_id(submission_id: str) -> Dict:
    """Get a specific submission by ID"""
    submission = submissions_collection.find_one({'submission_id': submission_id}, {'_id': 0})
    return submission if submission else {}
