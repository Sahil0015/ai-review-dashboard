import json
import re
import os
import sys
from typing import Dict, Tuple
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))
from config import client, model

# ============================================
# PROMPT FUNCTIONS
# ============================================

def prompt_v1(review_text: str) -> str:
    """V1: Simple baseline prompt"""
    return f"""Classify this Yelp review on a scale of 1-5 stars.

Review: "{review_text}"

Respond with valid JSON only:
{{"predicted_stars": <1-5>, "explanation": "<brief reason>"}}"""


def prompt_v2(review_text: str) -> str:
    """V2: Criteria-based with examples"""
    
    return f"""
Rate this Yelp review (1–5):

1★ very negative; major failures; strong dissatisfaction
2★ mostly negative; significant issues; few positives
3★ mixed; clear positives + negatives; neutral tone
4★ mostly positive; minor issues only; satisfied
5★ very positive; enthusiastic praise; no real complaints

EXAMPLES:
1★ → "Food was cold, long wait, rude server." → {{"predicted_stars": 1, "explanation": "Severe complaints"}}
3★ → "Decent burger, soggy fries, friendly service." → {{"predicted_stars": 3, "explanation": "Mixed"}}
4★ → "Loved the pasta, slow check." → {{"predicted_stars": 4, "explanation": "Mostly positive"}}

Review: "{review_text}"

Respond with valid JSON only:
{{"predicted_stars": <1-5>, "explanation": "<brief reason>"}}"""


def prompt_v3(review_text: str) -> str:
    """V3: Chain-of-thought reasoning"""
    
    return f"""Rate this Yelp review (1-5 stars) by analyzing it systematically.

Review: "{review_text}"

Think through:
1. What specific positive aspects are mentioned?
2. What specific negative aspects are mentioned?
3. What's the overall emotional tone?
4. Are there any strong keywords (love, hate, terrible, amazing)?

Respond with valid JSON only:
{{"predicted_stars": <1-5>, "explanation": "<brief reason>"}}"""


PROMPT_FUNCTIONS = {
    "v1": prompt_v1,
    "v2": prompt_v2,
    "v3": prompt_v3
}


# ============================================
# LLM CALLING
# ============================================

def call_llm(review_text: str, prompt_func: callable, max_retries: int = 3) -> str:
    """Call Groq API with retry logic"""
    prompt = prompt_func(review_text)
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e).lower()
            
            if "rate" in error_msg or "429" in error_msg:
                import time
                wait_time = (2 ** attempt) * 2
                time.sleep(wait_time)
                continue
            
            if attempt < max_retries - 1:
                import time
                time.sleep(2)
                continue
            
            return f"ERROR: {str(e)}"
    
    return "ERROR: Max retries exceeded"


def extract_json_from_response(response_text: str) -> Dict:
    """Extract and parse JSON from LLM response"""
    if not response_text or response_text.startswith('ERROR'):
        return {}
    
    # Remove markdown code blocks
    text = response_text.replace('``````', '').strip()
    
    # Find JSON boundaries
    start = text.find('{')
    end = text.rfind('}') + 1
    
    if start == -1 or end <= start:
        return {}
    
    try:
        json_str = text[start:end]
        data = json.loads(json_str)
        return data
    except json.JSONDecodeError:
        # Fallback: manual extraction
        result = {}
        
        # Extract predicted_stars
        stars_match = re.search(r'"predicted_stars"\s*:\s*(\d+)', text)
        if stars_match:
            result['predicted_stars'] = int(stars_match.group(1))
        
        # Extract explanation
        expl_match = re.search(r'"explanation"\s*:\s*"(.*?)"', text, re.DOTALL)
        if expl_match:
            result['explanation'] = expl_match.group(1)
        
        # Extract summary
        summary_match = re.search(r'"summary"\s*:\s*"(.*?)"', text, re.DOTALL)
        if summary_match:
            result['summary'] = summary_match.group(1)
        
        # Extract sentiment
        sentiment_match = re.search(r'"sentiment"\s*:\s*"(.*?)"', text, re.DOTALL)
        if sentiment_match:
            result['sentiment'] = sentiment_match.group(1)
        
        # Extract actions array
        actions_match = re.search(r'"actions"\s*:\s*\[(.*?)\]', text, re.DOTALL)
        if actions_match:
            actions_text = actions_match.group(1)
            actions = re.findall(r'"(.*?)"', actions_text)
            result['actions'] = actions[:3]  # Limit to 3
        
        return result


def predict_rating(review_text: str, prompt_version: str = "v3") -> Dict:
    """Predict rating using specified prompt version"""
    prompt_func = PROMPT_FUNCTIONS.get(prompt_version, prompt_v3)
    raw_response = call_llm(review_text, prompt_func)
    return extract_json_from_response(raw_response)


# ============================================
# AI SUMMARY & RECOMMENDATIONS
# ============================================

def generate_summary_and_actions(review_text: str, user_rating: int, predicted_rating: int) -> Tuple[str, list, str]:
    """Generate AI summary, recommended actions, and sentiment"""
    
    prompt = f"""Analyze this restaurant review and provide actionable insights.

Review: "{review_text}"
User Rating: {user_rating} stars
AI Predicted: {predicted_rating} stars

Provide a JSON response with:
1. A brief 2-sentence summary of the customer's experience
2. Exactly 3 specific, actionable recommendations for the restaurant owner
3. Overall sentiment (must be exactly one of: Positive, Negative, or Mixed)

Example format:
{{
  "summary": "Customer enjoyed the food quality and ambiance. Service speed could be improved.",
  "actions": [
    "Train staff on faster order processing",
    "Maintain current food quality standards", 
    "Improve table turnover during peak hours"
  ],
  "sentiment": "Positive"
}}

Respond ONLY with valid JSON matching this format:"""
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=400
        )
        
        # Extract JSON from response
        raw_response = response.choices[0].message.content
        result = extract_json_from_response(raw_response)
        
        # Validate and extract fields with better fallbacks
        summary = result.get("summary", "").strip()
        actions = result.get("actions", [])
        sentiment = result.get("sentiment", "Mixed").strip()
        
        # Ensure sentiment is valid
        if sentiment not in ["Positive", "Negative", "Mixed"]:
            sentiment = "Positive" if user_rating >= 4 else "Negative" if user_rating <= 2 else "Mixed"
        
        # Generate fallback summary if empty
        if not summary or len(summary) < 20:
            if user_rating >= 4:
                summary = f"Customer had a positive {user_rating}-star experience with the restaurant. They appreciated various aspects of their visit."
            elif user_rating <= 2:
                summary = f"Customer had a disappointing {user_rating}-star experience. Several issues affected their satisfaction."
            else:
                summary = f"Customer had a mixed {user_rating}-star experience with both positive and negative aspects noted."
        
        # Generate fallback actions if empty or invalid
        if not actions or len(actions) < 3:
            if user_rating >= 4:
                actions = [
                    "Continue maintaining the high standards that earned this positive review",
                    "Share this positive feedback with the team to boost morale",
                    "Identify and replicate the successful elements mentioned"
                ]
            elif user_rating <= 2:
                actions = [
                    "Investigate the specific issues mentioned in this review immediately",
                    "Follow up with the customer to address their concerns",
                    "Implement corrective measures to prevent similar issues"
                ]
            else:
                actions = [
                    "Analyze the mixed feedback to identify improvement areas",
                    "Strengthen the positive aspects mentioned in the review",
                    "Address the concerns raised to enhance customer satisfaction"
                ]
        
        # Ensure exactly 3 actions
        actions = actions[:3]
        while len(actions) < 3:
            actions.append("Gather additional customer feedback for continuous improvement")
        
        return summary, actions, sentiment
        
    except Exception as e:
        print(f"LLM Error in generate_summary_and_actions: {str(e)}")
        
        # Intelligent fallback based on rating
        if user_rating >= 4:
            summary = f"Customer had a positive {user_rating}-star experience, expressing satisfaction with their visit."
            sentiment = "Positive"
            actions = [
                "Continue maintaining the high standards that earned this positive review",
                "Share this positive feedback with the team",
                "Monitor consistency in service quality"
            ]
        elif user_rating <= 2:
            summary = f"Customer had a disappointing {user_rating}-star experience with several concerns raised."
            sentiment = "Negative"
            actions = [
                "Investigate the specific issues mentioned in this review",
                "Follow up with the customer to address their concerns",
                "Implement immediate corrective measures"
            ]
        else:
            summary = f"Customer had a mixed {user_rating}-star experience with both positive and negative feedback."
            sentiment = "Mixed"
            actions = [
                "Analyze the balanced feedback to identify improvement areas",
                "Strengthen the positive aspects while addressing concerns",
                "Gather more customer feedback to understand patterns"
            ]
        
        return summary, actions, sentiment
    
# ============================================

def generate_user_response(review_text: str, rating: int) -> str:
    """Generate personalized response for user"""
    
    prompt = f"""Generate a friendly, empathetic 2-sentence response to this customer review.

Review: "{review_text}"
Rating: {rating} stars

Be genuine and acknowledge their specific feedback. Respond naturally, not in JSON."""
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except:
        if rating >= 4:
            return "Thank you so much for your wonderful feedback! We're thrilled you enjoyed your experience with us."
        elif rating == 3:
            return "Thank you for your honest feedback. We appreciate hearing about your experience and will work to improve."
        else:
            return "We sincerely apologize for falling short of your expectations. Your feedback helps us improve our service."
