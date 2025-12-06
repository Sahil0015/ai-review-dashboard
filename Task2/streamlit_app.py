import streamlit as st
import requests
import pandas as pd
import time

# ============================================
# CONFIGURATION
# ============================================

API_BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="Yelp Review System", layout="wide")

# Initialize session state
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

# ============================================
# SIDEBAR
# ============================================

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["User Dashboard", "Admin Dashboard"])

st.sidebar.divider()

# Auto-refresh for Admin
if page == "Admin Dashboard":
    st.sidebar.subheader("Live Updates")
    auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh", value=True)
    
    if auto_refresh:
        refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 2, 30, 5)
        st.sidebar.info(f"Auto-refreshing every {refresh_interval}s")
        
        current_time = time.time()
        if current_time - st.session_state.last_refresh > refresh_interval:
            st.session_state.last_refresh = current_time
            st.rerun()

st.sidebar.divider()
st.sidebar.caption("Data Source: submissions.csv (shared)")
st.sidebar.caption(f"Backend: {API_BASE_URL}")

# ============================================
# USER DASHBOARD
# ============================================

if page == "User Dashboard":
    st.title("👤 User Dashboard - Submit Review")
    
    with st.form("review_form"):
        st.subheader("Rate & Review")
        
        # 1. Select star rating
        rating = st.selectbox("Select Rating (1-5 stars):", [1, 2, 3, 4, 5], index=2)
        
        # 2. Write review
        review_text = st.text_area(
            "Write your review:", 
            placeholder="Share your experience...",
            height=150
        )
        
        # 3. Submit button
        submitted = st.form_submit_button("Submit Review", use_container_width=True)
        
        if submitted:
            if len(review_text.strip()) < 10:
                st.error("❌ Review must be at least 10 characters")
            else:
                with st.spinner("Processing your review..."):
                    try:
                        # Submit to backend (writes to submissions.csv)
                        response = requests.post(
                            f"{API_BASE_URL}/api/user/submit",
                            json={"rating": rating, "review_text": review_text},
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            st.success("✅ Review submitted successfully!")
                            
                            # Display AI-generated response
                            st.divider()
                            st.subheader("AI Response")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Your Rating", f"{rating} ⭐")
                            with col2:
                                st.metric("AI Predicted", f"{result['predicted_stars']} ⭐")
                            
                            st.write(f"**Submission ID:** {result['submission_id']}")
                            st.write(f"**Timestamp:** {result['timestamp']}")
                            
                            st.divider()
                            st.info(f"**AI Summary:** {result['ai_summary']}")
                            
                            st.write("**Recommended Actions:**")
                            for i, action in enumerate(result['recommended_actions'], 1):
                                st.write(f"{i}. {action}")
                            
                            st.divider()
                            st.success("✨ Your submission is now visible in the Admin Dashboard!")
                            
                        else:
                            st.error(f"Error {response.status_code}: {response.text}")
                    
                    except Exception as e:
                        st.error(f"Connection Error: {str(e)}")
                        st.info("Make sure the backend is running: `python app.py`")

# ============================================
# ADMIN DASHBOARD
# ============================================

elif page == "Admin Dashboard":
    st.title("👨‍💼 Admin Dashboard - Live Submissions")
    
    # Manual refresh
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Refresh Now"):
            st.rerun()
    with col2:
        st.caption(f"Last updated: {time.strftime('%H:%M:%S')}")
    
    try:
        # Fetch data from backend (reads from submissions.csv)
        submissions_response = requests.get(f"{API_BASE_URL}/api/admin/submissions", timeout=10)
        analytics_response = requests.get(f"{API_BASE_URL}/api/admin/analytics", timeout=10)
        
        if submissions_response.status_code == 200:
            submissions = submissions_response.json()
            
            # ==========================================
            # ANALYTICS (Optional but Useful)
            # ==========================================
            if analytics_response.status_code == 200:
                analytics = analytics_response.json()
                
                st.subheader("📊 Analytics")
                col1, col2, col3, col4 = st.columns(4)
                
                col1.metric("Total Submissions", analytics['total_submissions'])
                col2.metric("Avg User Rating", f"{analytics['average_user_rating']:.2f} ⭐")
                col3.metric("Avg AI Prediction", f"{analytics['average_predicted_rating']:.2f} ⭐")
                col4.metric("Accuracy", f"{analytics['accuracy']:.1f}%")
                
                st.divider()
            
            # ==========================================
            # LIVE-UPDATING SUBMISSIONS LIST (Required)
            # ==========================================
            if submissions:
                st.subheader(f"📋 All Submissions ({len(submissions)})")
                st.caption("Latest submissions appear first")
                
                for idx, sub in enumerate(submissions, 1):
                    # Check if new (< 30 seconds old)
                    try:
                        sub_time = pd.to_datetime(sub['timestamp'])
                        is_new = (pd.Timestamp.now() - sub_time).total_seconds() < 30
                    except:
                        is_new = False
                    
                    # Display each submission
                    with st.expander(
                        f"{'🆕 ' if is_new else ''}#{idx} | {sub['submission_id']} | {sub['timestamp'][:19]}",
                        expanded=(idx <= 2)
                    ):
                        # ========================================
                        # REQUIRED FIELDS (As per specification)
                        # ========================================
                        
                        # 1. USER RATING
                        st.write(f"**1️⃣ User Rating:** {sub['user_rating']} ⭐")
                        
                        # 2. USER REVIEW
                        st.write(f"**2️⃣ User Review:**")
                        st.text_area("", sub['review_text'], height=80, disabled=True, key=f"review_{idx}")
                        
                        # 3. AI-GENERATED SUMMARY
                        st.write(f"**3️⃣ AI-Generated Summary:**")
                        st.info(sub['ai_summary'])
                        
                        # 4. AI-SUGGESTED RECOMMENDED ACTIONS
                        st.write(f"**4️⃣ AI-Suggested Recommended Actions:**")
                        for i, action in enumerate(sub['recommended_actions'], 1):
                            st.write(f"   • {action}")
                        
                        # Additional info
                        st.divider()
                        col1, col2, col3 = st.columns(3)
                        col1.write(f"AI Predicted: {sub['ai_predicted_rating']} ⭐")
                        col2.write(f"Sentiment: {sub['sentiment']}")
                        col3.write(f"Match: {'✅' if sub['rating_match'] else '❌'}")
                
                st.divider()
                
                # Download option
                df = pd.DataFrame(submissions)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Download All Submissions (CSV)",
                    csv,
                    f"submissions_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv",
                    use_container_width=True
                )
            else:
                st.info("📭 No submissions yet")
                st.caption("Waiting for users to submit reviews...")
        
        else:
            st.error(f"Error: {submissions_response.status_code}")
    
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        st.info("Make sure the backend is running: `python app.py`")

# ============================================
# SHARED DATA SOURCE CONFIRMATION
# ============================================
st.sidebar.divider()
st.sidebar.success("✅ Both dashboards connected to same data source")
st.sidebar.caption("User writes → submissions.csv")
st.sidebar.caption("Admin reads ← submissions.csv")
