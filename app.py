import streamlit as st;

with st.sidebar:
    st.header("Housing Preferences")
    st.slider("Price Importance", 0.0, 1.0, 0.5, key="price_weight")
    st.slider("Distance Importance", 0.0, 1.0, 0.5, key="distance_weight")
    st.slider("Review Importance", 0.0, 1.0, 0.5, key="review_weight")

input = st.chat_input("Tell me what you're looking for...") 
st.chat_message("assistant").write("Hello! I'm here to help you find the perfect housing option based on your preferences. Please provide me with some details about what you're looking for, such as location, budget, and any specific features you want in a house or apartment.")
