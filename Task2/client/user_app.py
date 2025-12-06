import streamlit as st
import requests

# ============================================
# CONFIGURATION
# ============================================

API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Submit Review",
    page_icon="⭐",
    layout="centered"
)

# ============================================
# USER DASHBOARD
# ============================================

st.title("⭐ Submit Your Review")
st.caption("Share your dining experience")

with st.form("review_form"):
    st.subheader("Rate Your Experience")
    
    # 1. Select star rating
    rating = st.select_slider(
        "Select Rating:",
        options=[1, 2, 3, 4, 5],
        value=3,
        format_func=lambda x: "⭐" * x
    )
    
    st.write(f"**Selected:** {rating} {'⭐' * rating}")
    
    # 2. Write review with character counter
    review_text = st.text_area(
        "Write your review (10-5000 characters):", 
        placeholder="Tell us about your experience...",
        height=200,
        max_chars=5000
    )
    
    # Character counter
    char_count = len(review_text)
    if char_count < 10:
        st.caption(f"❌ {char_count}/5000 characters (minimum 10 required)")
    elif char_count > 4500:
        st.caption(f"⚠️ {char_count}/5000 characters")
    else:
        st.caption(f"✅ {char_count}/5000 characters")
    
    # 3. Submit button
    submitted = st.form_submit_button("🚀 Submit Review", use_container_width=True)
    
    if submitted:
        if len(review_text.strip()) < 10:
            st.error("❌ Review must be at least 10 characters")
        elif len(review_text.strip()) > 5000:
            st.error("❌ Review exceeds 5000 characters")
        else:
            with st.spinner("🤖 AI is analyzing your review..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/user/submit",
                        json={"rating": rating, "review_text": review_text},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.success("✅ Review submitted successfully!")
                        st.balloons()
                        
                        # Display AI response
                        st.divider()
                        st.subheader("📊 AI Analysis")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Your Rating", f"{rating} ⭐")
                        with col2:
                            st.metric("AI Predicted", f"{result['predicted_stars']} ⭐")
                        with col3:
                            st.metric("Sentiment", result['sentiment'])
                        
                        st.info(f"**Submission ID:** {result['submission_id']}")
                        
                        st.divider()
                        
                        st.subheader("📝 Summary")
                        st.write(result['ai_summary'])
                        
                        st.subheader("💡 Business Recommendations")
                        for i, action in enumerate(result['recommended_actions'], 1):
                            st.write(f"{i}. {action}")
                        
                        with st.expander("🔍 AI Explanation"):
                            st.write(result['explanation'])
                        
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                
                except Exception as e:
                    st.error(f"Connection Error: {str(e)}")
                    st.info("Please ensure the backend server is running")

st.divider()
st.caption("Powered by AI | Your feedback helps businesses improve")
