import streamlit as st
import requests

# Title and caption of UI app
st.title("AI-Powered E-commerce Journey Analyzer")
st.caption("Analyzing a balanced mix of converted and abandoned customer sessions for actionable insights.")

uploaded_file = st.file_uploader("Upload customer_journeys.json", type="json")
# Scroll bar to control number of customer session to analyze
sample_size = st.slider("Number of sessions to analyze", min_value=5, max_value=50, value=10, step=5)

if uploaded_file:
    with st.spinner("Analyzing with GPT..."):
        response = requests.post(
            "http://localhost:8000/analyze",
            files={"file": uploaded_file},
            data={"sample_size": sample_size}
        )
        insights = response.json().get("insights", "No insights returned.")
        st.subheader("AI-Generated Insights")
        st.markdown(insights)