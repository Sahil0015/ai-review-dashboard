from pymongo import MongoClient, DESCENDING
from datetime import datetime
from typing import List, Dict
import os
from dotenv import load_dotenv
import uuid
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# ============================================
# MONGODB CONNECTION
# ============================================

MONGODB_URI = os.getenv("MONGODB_URI")

try:
    client = MongoClient(MONGODB_URI)
    db = client["yelp_review_system"]  # Database name
    
    # Collections
    submissions_collection = db["submissions"]
    evaluations_collection = db["evaluations"]
    
    logger.info(f"✅ Connected to MongoDB: {db.name}")
except Exception as e:
    logger.error(f"❌ Failed to connect to MongoDB: {e}")
    raise


# ============================================
# SUBMISSION OPERATIONS
# ============================================

def save_submission(data: Dict) -> str:
    """Save a new submission to MongoDB and return submission ID"""
    logger.info("Saving new submission to database...")
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
    
    try:
        submissions_collection.insert_one(document)
        logger.info(f"✅ Submission saved successfully with ID: {submission_id}")
    except Exception as e:
        logger.error(f"❌ Failed to save submission: {e}")
        raise
    
    return submission_id


def get_all_submissions() -> List[Dict]:
    """Get all submissions from MongoDB (sorted by newest first)"""
    logger.info("Fetching all submissions from database...")
    try:
        submissions = list(
            submissions_collection.find({}, {'_id': 0})  # Exclude MongoDB _id from results
            .sort('timestamp', DESCENDING)
        )
        
        # Add rating_match field
        for sub in submissions:
            sub['rating_match'] = sub['user_rating'] == sub['ai_predicted_rating']
        
        logger.info(f"✅ Retrieved {len(submissions)} submissions")
        return submissions
    except Exception as e:
        logger.error(f"❌ Failed to fetch submissions: {e}")
        raise


def get_analytics() -> Dict:
    """Calculate analytics from MongoDB data"""
    logger.info("Calculating analytics from database...")
    try:
        submissions = list(submissions_collection.find({}))
        logger.info(f"✅ Fetched {len(submissions)} submissions for analytics")
    except Exception as e:
        logger.error(f"❌ Failed to fetch data for analytics: {e}")
        raise
    
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
    logger.info("Saving evaluation metrics to database...")
    metrics['timestamp'] = datetime.now().isoformat()
    try:
        evaluations_collection.insert_one(metrics)
        logger.info("✅ Evaluation metrics saved successfully")
    except Exception as e:
        logger.error(f"❌ Failed to save evaluation metrics: {e}")
        raise


def get_evaluation_metrics() -> List[Dict]:
    """Get all evaluation metrics from MongoDB"""
    logger.info("Fetching evaluation metrics from database...")
    try:
        evaluations = list(
            evaluations_collection.find({}, {'_id': 0})
            .sort('timestamp', DESCENDING)
        )
        logger.info(f"✅ Retrieved {len(evaluations)} evaluation records")
        return evaluations
    except Exception as e:
        logger.error(f"❌ Failed to fetch evaluation metrics: {e}")
        raise


# ============================================
# UTILITY FUNCTIONS
# ============================================

def clear_all_submissions():
    """Clear all submissions (use with caution!)"""
    logger.warning("⚠️ Clearing all submissions from database...")
    try:
        result = submissions_collection.delete_many({})
        logger.info(f"✅ Deleted {result.deleted_count} submissions")
        return result.deleted_count
    except Exception as e:
        logger.error(f"❌ Failed to clear submissions: {e}")
        raise


def get_submission_by_id(submission_id: str) -> Dict:
    """Get a specific submission by ID"""
    logger.info(f"Fetching submission with ID: {submission_id}")
    try:
        submission = submissions_collection.find_one({'submission_id': submission_id}, {'_id': 0})
        if submission:
            logger.info(f"✅ Found submission: {submission_id}")
        else:
            logger.warning(f"⚠️ Submission not found: {submission_id}")
        return submission if submission else {}
    except Exception as e:
        logger.error(f"❌ Failed to fetch submission {submission_id}: {e}")
        raise
