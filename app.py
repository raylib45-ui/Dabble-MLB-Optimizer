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
player_name = st.text_input("Player Name", "Enter Pitcher Name")
st.set_page_config(page_title="Dabble MLB Strikeout Optimizer", page_icon="⚾", layout="centered")

st.title("⚾ Dabble MLB Strikeout Optimizer")
st.markdown("Live Expected Value Engine for Pitcher Strikeout Props (Recalibrated Model)")

# Inputs
player_name = st.text_input("Player Name", "Enter Pitcher Name")
line = st.number_input("Dabble Strikeout Line", value=5.5, step=0.5)
l5_input = st.text_input("Last 5 Game Logs (comma-separated)", "5, 6, 4, 5, 7")
multiplier = st.number_input("Dabble Multiplier", value=1.0, step=0.1)

# Advanced Recalibration Parameters
st.markdown("---")
st.markdown("**Model Recalibration Weights**")
col1, col2 = st.columns(2)
with col1:
    opponent_k_pct = st.slider("Opponent K% vs Handedness Factor", 0.7, 1.3, 1.0, 0.05)
with col2:
    workload_cap = st.slider("Workload / Pitch Count Factor", 0.7, 1.3, 1.0, 0.05)

if st.button("Calculate Recalibrated EV"):
    try:
        # Parse L5 game logs
        games = [float(x.strip()) for x in l5_input.split(",")]
        
        if len(games) > 0:
            # 1. Weighted Recent Form (Exponential decay: recent games weighted heavier)
            weights = [0.10, 0.15, 0.20, 0.25, 0.30] # 5 games total
            # Adjust weights if fewer or more than 5 games are entered
            if len(weights) != len(games):
                weights = [1.0 / len(games)] * len(games)
            
            weighted_avg = sum(g * w for g, w in zip(games, weights)) / sum(weights)
            
            # 2. Apply Opponent and Workload Factors
            recalibrated_projection = weighted_avg * opponent_k_pct * workload_cap
            
            # 3. Simple Probability Estimation based on distance from line
            diff = recalibrated_projection - line
            over_prob = max(0.01, min(0.99, 0.50 + (diff * 0.15)))
            under_prob = 1.0 - over_prob
            
            st.markdown("---")
            st.subheader(f"Results for {player_name}")
            st.write(f"**Recalibrated Projection:** {recalibrated_projection:.2f} Ks")
            st.write(f"**Over Probability:** {over_prob * 100:.1f}%")
            st.write(f"**Under Probability:** {under_prob * 100:.1f}%")
            
            # Recommendation logic based on strict consistency / EV
            if over_prob > 0.55:
                st.success("Recommendation: Take the MORE (Over) 🔒")
            elif under_prob > 0.55:
                st.success("Recommendation: Take the LESS (Under) 🔒")
            else:
                st.warning("Recommendation: Pass (Too close to call / Coin flip)")
        else:
            st.error("Please enter valid game logs.")
            
    except Exception as e:
        st.error(f"Error processing input: {e}")


