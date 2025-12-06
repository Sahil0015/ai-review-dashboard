import streamlit as st
import requests
import pandas as pd
import time
import plotly.express as px

# ============================================
# CONFIGURATION
# ============================================

API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Admin Dashboard",
    page_icon="👨‍💼",
    layout="wide"
)

# Initialize session state
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

# ============================================
# ADMIN DASHBOARD
# ============================================

st.title("👨‍💼 Admin Dashboard - Live Monitoring")

# ============================================
# SETTINGS SIDEBAR
# ============================================

st.sidebar.title("⚙️ Settings")

# Auto-refresh
auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh", value=True)

if auto_refresh:
    refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 2, 30, 5)
    st.sidebar.success(f"Auto-refreshing every {refresh_interval}s")
    
    current_time = time.time()
    if current_time - st.session_state.last_refresh > refresh_interval:
        st.session_state.last_refresh = current_time
        st.rerun()

st.sidebar.divider()

# Manual refresh
if st.sidebar.button("🔄 Refresh Now", use_container_width=True):
    st.rerun()

st.sidebar.divider()
st.sidebar.info("**Data Source:** MongoDB")
st.sidebar.caption(f"Backend: {API_BASE_URL}")

# ============================================
# FETCH DATA
# ============================================

col1, col2 = st.columns([4, 1])
with col2:
    st.caption(f"Last updated: {time.strftime('%H:%M:%S')}")

try:
    submissions_response = requests.get(f"{API_BASE_URL}/api/admin/submissions", timeout=10)
    analytics_response = requests.get(f"{API_BASE_URL}/api/admin/analytics", timeout=10)
    
    if submissions_response.status_code == 200:
        submissions = submissions_response.json()
        
        # ==========================================
        # ANALYTICS SECTION
        # ==========================================
        if analytics_response.status_code == 200:
            analytics = analytics_response.json()
            
            st.subheader("📊 Real-Time Analytics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            col1.metric(
                "Total Submissions",
                analytics['total_submissions'],
                delta=None
            )
            col2.metric(
                "Avg User Rating",
                f"{analytics['average_user_rating']:.2f}",
                delta=None
            )
            col3.metric(
                "Avg AI Prediction",
                f"{analytics['average_predicted_rating']:.2f}",
                delta=None
            )
            col4.metric(
                "Prediction Accuracy",
                f"{analytics['accuracy']:.1f}%",
                delta=None
            )
            
            st.divider()
            
            # Charts
            if analytics['rating_distribution'] and analytics['sentiment_distribution']:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Rating distribution
                    rating_df = pd.DataFrame(
                        list(analytics['rating_distribution'].items()),
                        columns=['Rating', 'Count']
                    )
                    rating_df['Rating'] = rating_df['Rating'].astype(str) + ' ⭐'
                    
                    fig1 = px.bar(
                        rating_df,
                        x='Rating',
                        y='Count',
                        title='Rating Distribution',
                        color='Count',
                        color_continuous_scale='Blues'
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    # Sentiment distribution
                    sentiment_df = pd.DataFrame(
                        list(analytics['sentiment_distribution'].items()),
                        columns=['Sentiment', 'Count']
                    )
                    
                    fig2 = px.pie(
                        sentiment_df,
                        names='Sentiment',
                        values='Count',
                        title='Sentiment Distribution',
                        color='Sentiment',
                        color_discrete_map={
                            'Positive': '#00CC96',
                            'Negative': '#EF553B',
                            'Mixed': '#FFA15A'
                        }
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                
                st.divider()
        
        # ==========================================
        # SUBMISSIONS LIST
        # ==========================================
        if submissions:
            st.subheader(f"📋 All Submissions ({len(submissions)})")
            st.caption("Newest submissions appear first • 🆕 indicates submissions from last 30 seconds")
            
            for idx, sub in enumerate(submissions, 1):
                # Check if new
                try:
                    sub_time = pd.to_datetime(sub['timestamp'])
                    is_new = (pd.Timestamp.now() - sub_time).total_seconds() < 30
                except:
                    is_new = False
                
                # Display submission
                with st.expander(
                    f"{'🆕 ' if is_new else ''}#{idx} | {sub['submission_id']} | {sub['timestamp'][:19]}",
                    expanded=(idx <= 2)
                ):
                    # Required fields
                    col1, col2 = st.columns([2, 3])
                    
                    with col1:
                        st.write(f"**1️⃣ User Rating:** {sub['user_rating']} ⭐")
                        st.write(f"**AI Predicted:** {sub['ai_predicted_rating']} ⭐")
                        st.write(f"**Sentiment:** {sub['sentiment']}")
                        st.write(f"**Rating Match:** {'✅ Yes' if sub['rating_match'] else '❌ No'}")
                    
                    with col2:
                        st.write(f"**2️⃣ User Review:**")
                        st.text_area("", sub['review_text'], height=100, disabled=True, key=f"review_{idx}")
                    
                    st.write(f"**3️⃣ AI-Generated Summary:**")
                    st.info(sub['ai_summary'])
                    
                    st.write(f"**4️⃣ AI-Suggested Recommended Actions:**")
                    for i, action in enumerate(sub['recommended_actions'], 1):
                        st.write(f"   • {action}")
            
            st.divider()
            
            # Download data
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

st.divider()
st.caption("Admin Panel • Real-time monitoring powered by MongoDB")
