import streamlit as st
import pandas as pd

st.title("⚾ Dabble MLB Strikeout Optimizer")
st.write("Live Expected Value Engine for Pitcher Strikeout Props")

line = st.number_input("Dabble Strikeout Line", value=7.5, step=0.5)
projection = st.number_input("Model Projection", value=6.8, step=0.1)
odds = st.number_input("Dabble Multiplier", value=1.1, step=0.05)

if st.button("Calculate EV"):
    diff = projection - line
    prob_over = max(0.1, min(0.9, 0.5 + (diff * 0.1)))
    prob_under = 1 - prob_over
    
    st.write(f"**Over Probability:** {prob_over:.1%}")
    st.write(f"**Under Probability:** {prob_under:.1%}")
    
    if prob_under > 0.55:
        st.success("Recommendation: Take the **LESS (Under)** 🔒")
    else:
        st.info("Recommendation: Take the **MORE (Over)**")
player_name = st.st.text_input("Player Name", "Enter Pitcher Name")
