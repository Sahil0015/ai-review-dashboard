import pandas as pd
import json
import os
from datetime import datetime
from typing import List, Dict
import uuid

DATA_DIR = "data"
SUBMISSIONS_FILE = os.path.join(DATA_DIR, "submissions.csv")
EVALUATIONS_FILE = os.path.join(DATA_DIR, "evaluations.csv")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize files if they don't exist
if not os.path.exists(SUBMISSIONS_FILE):
    pd.DataFrame(columns=[
        'submission_id', 'timestamp', 'user_rating', 'review_text',
        'ai_predicted_rating', 'ai_explanation', 'ai_summary',
        'recommended_actions', 'sentiment', 'user_response'
    ]).to_csv(SUBMISSIONS_FILE, index=False)

if not os.path.exists(EVALUATIONS_FILE):
    pd.DataFrame(columns=[
        'prompt_version', 'accuracy', 'mae', 'validity_rate',
        'exact_matches', 'off_by_1', 'off_by_2_plus', 'total_samples', 'timestamp'
    ]).to_csv(EVALUATIONS_FILE, index=False)


def save_submission(data: Dict) -> str:
    """Save a new submission and return submission ID"""
    submission_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()
    
    new_row = {
        'submission_id': submission_id,
        'timestamp': timestamp,
        'user_rating': data['user_rating'],
        'review_text': data['review_text'],
        'ai_predicted_rating': data['ai_predicted_rating'],
        'ai_explanation': data['ai_explanation'],
        'ai_summary': data['ai_summary'],
        'recommended_actions': json.dumps(data['recommended_actions']),
        'sentiment': data['sentiment'],
        'user_response': data.get('user_response', '')
    }
    
    df = pd.read_csv(SUBMISSIONS_FILE)
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(SUBMISSIONS_FILE, index=False)
    
    return submission_id


def get_all_submissions() -> List[Dict]:
    """Get all submissions for admin dashboard"""
    df = pd.read_csv(SUBMISSIONS_FILE)
    
    submissions = []
    for _, row in df.iterrows():
        submissions.append({
            'submission_id': row['submission_id'],
            'timestamp': row['timestamp'],
            'user_rating': int(row['user_rating']),
            'review_text': row['review_text'],
            'ai_predicted_rating': int(row['ai_predicted_rating']),
            'ai_summary': row['ai_summary'],
            'recommended_actions': json.loads(row['recommended_actions']) if pd.notna(row['recommended_actions']) else [],
            'sentiment': row['sentiment'],
            'rating_match': int(row['user_rating']) == int(row['ai_predicted_rating'])
        })
    
    return sorted(submissions, key=lambda x: x['timestamp'], reverse=True)


def get_analytics() -> Dict:
    """Calculate analytics for admin dashboard"""
    df = pd.read_csv(SUBMISSIONS_FILE)
    
    if len(df) == 0:
        return {
            'total_submissions': 0,
            'average_user_rating': 0,
            'average_predicted_rating': 0,
            'accuracy': 0,
            'sentiment_distribution': {},
            'rating_distribution': {}
        }
    
    return {
        'total_submissions': len(df),
        'average_user_rating': round(df['user_rating'].mean(), 2),
        'average_predicted_rating': round(df['ai_predicted_rating'].mean(), 2),
        'accuracy': round((df['user_rating'] == df['ai_predicted_rating']).sum() / len(df) * 100, 2),
        'sentiment_distribution': df['sentiment'].value_counts().to_dict(),
        'rating_distribution': df['user_rating'].value_counts().sort_index().to_dict()
    }


def save_evaluation_metrics(metrics: Dict):
    """Save evaluation metrics"""
    df = pd.read_csv(EVALUATIONS_FILE)
    metrics['timestamp'] = datetime.now().isoformat()
    df = pd.concat([df, pd.DataFrame([metrics])], ignore_index=True)
    df.to_csv(EVALUATIONS_FILE, index=False)


def get_evaluation_metrics() -> List[Dict]:
    """Get all evaluation metrics"""
    df = pd.read_csv(EVALUATIONS_FILE)
    return df.to_dict('records')
