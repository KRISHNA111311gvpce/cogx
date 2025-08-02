!pip install streamlit google-generativeai plotly pandas
import streamlit as st
import google.generativeai as genai
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Personal Finance Chatbot", 
    page_icon="💰", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4037 0%, #99f2c8 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
        color: white;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #28a745;
    }
    .user-profile-card {
        background: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #2196f3;
    }
    .budget-summary {
        background: #fff3e0;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #ff9800;
    }
    .insight-card {
        background: #f3e5f5;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #9c27b0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'financial_data' not in st.session_state:
    st.session_state.financial_data = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'budget_data' not in st.session_state:
    st.session_state.budget_data = {}

# Header
st.markdown('<div class="main-header"><h1>💰 Personal Finance Chatbot</h1><p>Your AI-Powered Financial Advisor</p></div>', unsafe_allow_html=True)

# Sidebar for configuration and user profile
with st.sidebar:
    st.header("🔑 Configuration")
    api_key = st.text_input("Enter your Gemini API Key:", type="password")
    
    if api_key:
        genai.configure(api_key=api_key)
        
        st.header("👤 User Profile Setup")
        
        # Demographic information for personalized communication
        user_type = st.selectbox(
            "User Type:",
            ["Select...", "Student", "Young Professional", "Mid-Career Professional", "Senior Professional", "Retiree"]
        )
        
        age_group = st.selectbox(
            "Age Group:",
            ["Select...", "18-25", "26-35", "36-45", "46-55", "56-65", "65+"]
        )
        
        income_range = st.selectbox(
            "Monthly Income Range (₹):",
            ["Select...", "Below 25,000", "25,000-50,000", "50,000-1,00,000", "1,00,000-2,00,000", "2,00,000+"]
        )
        
        financial_goals = st.multiselect(
            "Financial Goals:",
            ["Emergency Fund", "Investment", "Retirement Planning", "Home Purchase", "Education", "Debt Reduction", "Tax Planning"]
        )
        
        risk_tolerance = st.selectbox(
            "Risk Tolerance:",
            ["Select...", "Conservative", "Moderate", "Aggressive"]
        )
        
        if st.button("Save Profile"):
            st.session_state.user_profile = {
                "user_type": user_type,
                "age_group": age_group,
                "income_range": income_range,
                "financial_goals": financial_goals,
                "risk_tolerance": risk_tolerance,
                "created_at": datetime.now().isoformat()
            }
            st.success("Profile saved successfully!")

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    # Financial Data Input Section
    st.header("📊 Financial Information")
    
    # Income and Expenses Input
    with st.expander("💼 Income & Expenses", expanded=False):
        monthly_income = st.number_input("Monthly Income (₹):", min_value=0, value=0)
        
        st.subheader("Monthly Expenses:")
        rent = st.number_input("Rent/EMI (₹):", min_value=0, value=0)
        food = st.number_input("Food & Groceries (₹):", min_value=0, value=0)
        transport = st.number_input("Transportation (₹):", min_value=0, value=0)
        utilities = st.number_input("Utilities (₹):", min_value=0, value=0)
        entertainment = st.number_input("Entertainment (₹):", min_value=0, value=0)
        miscellaneous = st.number_input("Miscellaneous (₹):", min_value=0, value=0)
        
        if st.button("Update Financial Data"):
            st.session_state.financial_data = {
                "monthly_income": monthly_income,
                "expenses": {
                    "rent": rent,
                    "food": food,
                    "transport": transport,
                    "utilities": utilities,
                    "entertainment": entertainment,
                    "miscellaneous": miscellaneous
                },
                "total_expenses": rent + food + transport + utilities + entertainment + miscellaneous,
                "updated_at": datetime.now().isoformat()
            }
            st.success("Financial data updated!")

    # Chatbot Interface
    st.header("🤖 Personal Finance Assistant")
    
    # Display user profile summary
    if st.session_state.user_profile:
        with st.expander("👤 Your Profile Summary", expanded=False):
            profile = st.session_state.user_profile
            st.markdown(f"""
            <div class="user-profile-card">
                <strong>User Type:</strong> {profile.get('user_type', 'Not set')}<br>
                <strong>Age Group:</strong> {profile.get('age_group', 'Not set')}<br>
                <strong>Income Range:</strong> {profile.get('income_range', 'Not set')}<br>
                <strong>Goals:</strong> {', '.join(profile.get('financial_goals', []))}<br>
                <strong>Risk Tolerance:</strong> {profile.get('risk_tolerance', 'Not set')}
            </div>
            """, unsafe_allow_html=True)

    # Chat interface
    if api_key and st.session_state.user_profile:
        model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
        
        # Quick action buttons
        st.subheader("🚀 Quick Actions")
        col_a, col_b, col_c, col_d = st.columns(4)
        
        with col_a:
            if st.button("📋 Generate Budget Summary"):
                if st.session_state.financial_data:
                    with st.spinner("Creating personalized budget summary..."):
                        profile = st.session_state.user_profile
                        financial_data = st.session_state.financial_data
                        
                        prompt = f"""
                        As a personal finance advisor, create a detailed budget summary for a {profile.get('user_type', 'user')} 
                        aged {profile.get('age_group', 'unknown')} with income range {profile.get('income_range', 'unknown')}.
                        
                        Financial Data:
                        - Monthly Income: ₹{financial_data.get('monthly_income', 0)}
                        - Total Expenses: ₹{financial_data.get('total_expenses', 0)}
                        - Savings: ₹{financial_data.get('monthly_income', 0) - financial_data.get('total_expenses', 0)}
                        
                        Expense Breakdown:
                        {json.dumps(financial_data.get('expenses', {}), indent=2)}
                        
                        Goals: {', '.join(profile.get('financial_goals', []))}
                        Risk Tolerance: {profile.get('risk_tolerance', 'unknown')}
                        
                        Provide:
                        1. Budget health assessment
                        2. Savings rate analysis
                        3. Personalized recommendations based on user type and goals
                        4. Action items for improvement
                        
                        Adjust your communication style for a {profile.get('user_type', 'general user')}.
                        """
                        
                        try:
                            response = model.generate_content(prompt)
                            st.session_state.budget_data = {
                                "summary": response.text,
                                "generated_at": datetime.now().isoformat()
                            }
                        except Exception as e:
                            st.error(f"Error generating budget summary: {e}")
        
        with col_b:
            if st.button("💡 Spending Insights"):
                if st.session_state.financial_data:
                    with st.spinner("Analyzing spending patterns..."):
                        profile = st.session_state.user_profile
                        financial_data = st.session_state.financial_data
                        
                        prompt = f"""
                        Analyze spending patterns for a {profile.get('user_type', 'user')} and provide actionable insights:
                        
                        Monthly Income: ₹{financial_data.get('monthly_income', 0)}
                        Expense Breakdown: {json.dumps(financial_data.get('expenses', {}), indent=2)}
                        
                        Provide:
                        1. Spending pattern analysis
                        2. Areas where they're overspending
                        3. Cost-cutting suggestions specific to their lifestyle
                        4. Optimization recommendations
                        5. Benchmark comparisons for their demographic
                        
                        Communicate in a tone appropriate for a {profile.get('user_type', 'general user')}.
                        """
                        
                        try:
                            response = model.generate_content(prompt)
                            st.markdown(f'<div class="insight-card"><h4>💡 Spending Insights</h4>{response.text}</div>', unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error generating insights: {e}")
        
        with col_c:
            if st.button("🎯 Goal Planning"):
                with st.spinner("Creating personalized goal plan..."):
                    profile = st.session_state.user_profile
                    financial_data = st.session_state.financial_data
                    
                    prompt = f"""
                    Create a personalized financial goal plan for a {profile.get('user_type', 'user')}:
                    
                    Profile: {json.dumps(profile, indent=2)}
                    Financial Data: {json.dumps(financial_data, indent=2)}
                    
                    For each goal in {profile.get('financial_goals', [])}, provide:
                    1. Recommended monthly allocation
                    2. Timeline to achieve
                    3. Investment strategy based on risk tolerance
                    4. Specific action steps
                    
                    Adjust complexity and terminology for a {profile.get('user_type', 'general user')}.
                    """
                    
                    try:
                        response = model.generate_content(prompt)
                        st.markdown(f'<div class="feature-card"><h4>🎯 Your Goal Plan</h4>{response.text}</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error generating goal plan: {e}")
        
        with col_d:
            if st.button("📈 Investment Advice"):
                with st.spinner("Generating investment recommendations..."):
                    profile = st.session_state.user_profile
                    financial_data = st.session_state.financial_data
                    
                    available_savings = financial_data.get('monthly_income', 0) - financial_data.get('total_expenses', 0)
                    
                    prompt = f"""
                    Provide investment advice for a {profile.get('user_type', 'user')} with:
                    - Available monthly savings: ₹{available_savings}
                    - Risk tolerance: {profile.get('risk_tolerance', 'unknown')}
                    - Age group: {profile.get('age_group', 'unknown')}
                    - Goals: {', '.join(profile.get('financial_goals', []))}
                    
                    Recommend:
                    1. Asset allocation strategy
                    2. Specific investment products suitable for Indian market
                    3. SIP recommendations
                    4. Tax-saving investments
                    5. Emergency fund planning
                    
                    Use terminology and complexity appropriate for a {profile.get('user_type', 'general user')}.
                    """
                    
                    try:
                        response = model.generate_content(prompt)
                        st.markdown(f'<div class="feature-card"><h4>📈 Investment Recommendations</h4>{response.text}</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error generating investment advice: {e}")

        # Free-form chat
        st.subheader("💬 Ask Your Financial Questions")
        user_question = st.text_area("Ask me anything about personal finance...", height=100)
        
        if st.button("Get Personalized Advice") and user_question.strip():
            with st.spinner("Generating personalized response..."):
                profile = st.session_state.user_profile
                financial_data = st.session_state.financial_data
                
                context_prompt = f"""
                You are a personal finance advisor. Respond to the user's question with personalized advice.
                
                User Profile: {json.dumps(profile, indent=2)}
                Financial Data: {json.dumps(financial_data, indent=2)}
                
                User's Question: {user_question}
                
                Provide advice that is:
                1. Personalized to their profile and financial situation
                2. Appropriate for their user type ({profile.get('user_type', 'general user')})
                3. Considers their risk tolerance and goals
                4. Uses appropriate complexity level for their demographic
                5. Includes specific actionable steps
                
                Adjust your communication style and terminology for a {profile.get('user_type', 'general user')}.
                """
                
                try:
                    response = model.generate_content(context_prompt)
                    st.markdown(f'<div class="feature-card"><h4>🤖 Personalized Response</h4>{response.text}</div>', unsafe_allow_html=True)
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "question": user_question,
                        "response": response.text,
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as e:
                    st.error(f"Error: {e}")
    
    elif api_key and not st.session_state.user_profile:
        st.info("👈 Please set up your user profile in the sidebar to get personalized financial advice.")
    else:
        st.info("👈 Please enter your Gemini API Key in the sidebar to start.")

with col2:
    # Budget Summary Display
    if st.session_state.budget_data:
        st.header("📊 Budget Summary")
        budget_summary = st.session_state.budget_data.get('summary', '')
        st.markdown(f'<div class="budget-summary">{budget_summary}</div>', unsafe_allow_html=True)
    
    # Financial Overview Charts
    if st.session_state.financial_data and st.session_state.financial_data.get('monthly_income', 0) > 0:
        st.header("📈 Financial Overview")
        
        financial_data = st.session_state.financial_data
        
        # Pie chart for expenses
        expenses = financial_data.get('expenses', {})
        if any(expenses.values()):
            fig_pie = px.pie(
                values=list(expenses.values()),
                names=list(expenses.keys()),
                title="Expense Breakdown"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Income vs Expenses bar chart
        income = financial_data.get('monthly_income', 0)
        total_expenses = financial_data.get('total_expenses', 0)
        savings = income - total_expenses
        
        fig_bar = go.Figure(data=[
            go.Bar(name='Income', x=['Monthly'], y=[income], marker_color='green'),
            go.Bar(name='Expenses', x=['Monthly'], y=[total_expenses], marker_color='red'),
            go.Bar(name='Savings', x=['Monthly'], y=[savings], marker_color='blue')
        ])
        fig_bar.update_layout(title="Income vs Expenses vs Savings")
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Stock Market News (keeping from original)
    st.header("📰 Latest Market News")
    if api_key:
        if st.button("Refresh Market News"):
            with st.spinner("Fetching latest market news..."):
                try:
                    model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
                    prompt = """
                    Give me 5 latest Indian stock market news headlines that are relevant for personal finance decisions.
                    Focus on news that might impact individual investors and their portfolio decisions.
                    Format each as a brief, informative headline.
                    """
                    response = model.generate_content(prompt)
                    news_items = [line.strip() for line in response.text.split('\n') if line.strip()]
                    for item in news_items[:5]:
                        if item:
                            st.write(f"• {item}")
                except Exception as e:
                    st.error(f"Error fetching news: {e}")
    
    # Chat History
    if st.session_state.chat_history:
        st.header("💭 Recent Conversations")
        for i, chat in enumerate(reversed(st.session_state.chat_history[-3:])):  # Show last 3
            with st.expander(f"Q: {chat['question'][:50]}..."):
                st.write(f"**Question:** {chat['question']}")
                st.write(f"**Response:** {chat['response'][:200]}...")
                st.caption(f"Asked on: {datetime.fromisoformat(chat['timestamp']).strftime('%Y-%m-%d %H:%M')}")

# Footer
st.markdown("---")

st.markdown("💡 **Tips:** Use the quick action buttons for instant insights, or ask specific questions in the chat for personalized advice!")

