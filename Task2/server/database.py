from pymongo import MongoClient, DESCENDING
from datetime import datetime
from typing import List, Dict
import os
from dotenv import load_dotenv
import uuid
import sys

load_dotenv()

# ============================================
# MONGODB CONNECTION WITH ERROR HANDLING
# ============================================

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    print("❌ ERROR: MONGODB_URI environment variable not set!")
    sys.exit(1)

print(f"Attempting MongoDB connection...")
print(f"Connection string starts with: {MONGODB_URI[:20]}...")

try:
    # Add timeout settings for production
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=5000,  # 5 second timeout
        connectTimeoutMS=10000,
        socketTimeoutMS=10000
    )
    
    # Test connection
    client.admin.command('ping')
    print(f"✅ Connected to MongoDB successfully")
    
    db = client["yelp_review_system"]
    submissions_collection = db["submissions"]
    evaluations_collection = db["evaluations"]
    
    print(f"✅ Database: {db.name}")
    print(f"✅ Collections ready")

except Exception as e:
    print(f"❌ MongoDB connection failed: {str(e)}")
    print(f"Connection URI: {MONGODB_URI[:30]}...")
    sys.exit(1)


# ============================================
# SUBMISSION OPERATIONS WITH ERROR HANDLING
# ============================================

def save_submission(data: Dict) -> str:
    """Save a new submission to MongoDB"""
    try:
        submission_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        document = {
            '_id': submission_id,
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
        print(f"✅ Saved submission: {submission_id}")
        return submission_id
        
    except Exception as e:
        print(f"❌ Error saving submission: {str(e)}")
        raise


def get_all_submissions() -> List[Dict]:
    """Get all submissions from MongoDB"""
    try:
        submissions = list(
            submissions_collection.find({}, {'_id': 0})
            .sort('timestamp', DESCENDING)
        )
        
        for sub in submissions:
            sub['rating_match'] = sub['user_rating'] == sub['ai_predicted_rating']
        
        print(f"✅ Retrieved {len(submissions)} submissions")
        return submissions
        
    except Exception as e:
        print(f"❌ Error fetching submissions: {str(e)}")
        raise


def get_analytics() -> Dict:
    """Calculate analytics from MongoDB data"""
    try:
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
        
        matches = sum(1 for s in submissions if s['user_rating'] == s['ai_predicted_rating'])
        accuracy = (matches / total * 100) if total > 0 else 0
        
        sentiment_dist = {}
        for sentiment in sentiments:
            sentiment_dist[sentiment] = sentiment_dist.get(sentiment, 0) + 1
        
        rating_dist = {}
        for rating in user_ratings:
            rating_dist[rating] = rating_dist.get(rating, 0) + 1
        
        print(f"✅ Calculated analytics for {total} submissions")
        
        return {
            'total_submissions': total,
            'average_user_rating': round(sum(user_ratings) / total, 2),
            'average_predicted_rating': round(sum(predicted_ratings) / total, 2),
            'accuracy': round(accuracy, 2),
            'sentiment_distribution': sentiment_dist,
            'rating_distribution': rating_dist
        }
        
    except Exception as e:
        print(f"❌ Error calculating analytics: {str(e)}")
        raise


def save_evaluation_metrics(metrics: Dict):
    """Save evaluation metrics"""
    try:
        metrics['timestamp'] = datetime.now().isoformat()
        evaluations_collection.insert_one(metrics)
        print(f"✅ Saved evaluation metrics")
    except Exception as e:
        print(f"❌ Error saving metrics: {str(e)}")
        raise


def get_evaluation_metrics() -> List[Dict]:
    """Get all evaluation metrics"""
    try:
        evaluations = list(
            evaluations_collection.find({}, {'_id': 0})
            .sort('timestamp', DESCENDING)
        )
        print(f"✅ Retrieved {len(evaluations)} evaluations")
        return evaluations
    except Exception as e:
        print(f"❌ Error fetching evaluations: {str(e)}")
        raise
