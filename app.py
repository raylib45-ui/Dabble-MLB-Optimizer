import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Rick Sanchez Advanced MLB K Model", page_icon="📊", layout="wide")

st.markdown("<h1 style='text-align: center; color: #00ffcc;'>Rick Sanchez Advanced MLB K Model</h1>", unsafe_allow_html=True)

# Sidebar configuration
st.sidebar.header("Model Inputs")
pitcher_name = st.sidebar.text_input("Pitcher Name", "Cristopher Sánchez", key="rick_pitcher_name")
dabble_line = st.sidebar.number_input("Dabble Strikeout Line", value=5.5, step=0.5, key="rick_line")
odds_over = st.sidebar.text_input("Over Odds", "+139", key="rick_over_odds")
odds_under = st.sidebar.text_input("Under Odds", "-137", key="rick_under_odds")

# Main Dashboard Layout
col1, col2 = st.columns(2)

with col1:
    st.markdown("**🎯 EXACT MODEL: 5.42K (OVER +0.30)**")
    
    st.markdown("**BATTER vs PITCHER PROJECTED MATCHUP**")
    bvp_data = {
        "Batter": ["Bell (SOH)", "Lee (SOH)", "Kessell (LHS)", "Clemens (LHS)", "Lewis (SOH)"],
        "vK%": ["21.5%", "14.4%", "14.7%", "22.4%", "25.1%"],
        "vWhiff": ["21.4%", "13.6%", "14.2%", "22.5%", "24.2%"]
    }
    st.dataframe(pd.DataFrame(bvp_data), hide_index=True)

    st.markdown("**PITCH ARSENAL & WHIFF GRADES**")
    arsenal_data = {
        "Pitch": ["Sinker", "Sweeper", "Four-seam FB", "Slider"],
        "Usage": ["41.2%", "25.1%", "18.3%", "15.4%"],
        "Whiff%": ["12.4%", "38.2%", "22.1%", "34.5%"]
    }
    st.dataframe(pd.DataFrame(arsenal_data), hide_index=True)

    st.markdown("**LAST 10 STARTS TREND**")
    l10_vals = [7, 5, 8, 4, 6, 9, 6, 7, 5, 6]
    st.bar_chart(l10_vals)
    st.write("L5 Avg: 6.6 | L10 Avg: 6.3 | Line: 5.5")

    oc1, oc2 = st.columns(2)
    with oc1:
        st.metric(label="OVER EV / ODDS", value=odds_over, delta="57% model")
    with oc2:
        st.metric(label="UNDER EV / ODDS", value=odds_under, delta="43% model")

    st.error("🚨 **K REGRESSION RISK - ACT NOW**\n\n* **Less:** OVER K s/s Matchup confirms. 4 straight above 5.5. Line is likely inflated. Today's lineup makes a lot of contact (21.5% below league avg K-rate) - the matchup where K streaks end. Strong UNDER signal.")

with col2:
    st.markdown("**📊 COMPARISON / SECONDARY PROP ENGINE**")
    st.info("Switch view or load secondary pitcher from feed to compare lines simultaneously.")
    
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("ERA", "2.62")
    m2.metric("K/9", "10.4")
    m3.metric("WHIP", "1.22")
    m4.metric("IP", "168.1")
    m5.metric("FIP / LF", "4.1")

    st.markdown("---")
    st.markdown("**LINE SET HIGH - ABOVE HISTORY**")
    st.markdown("Line 7.5 is above L5 avg 6.7 and L10 avg 6.2 - only 20% of last 10 cleared this line.")
    st.markdown("Opponents K% required to hit Over is high, 8-pitcher lineup improves chances - genuine OVER opportunity if metrics hold.")
import pandas as pd

# Dabble MLB Strikeout Projections Engine
def calculate_ev(line, projection, odds_multiplier):
    diff = projection - line
    prob_over = 0.5 + (diff * 0.1)  # heuristic probability adjustment
    prob_over = max(0.1, min(0.9, prob_over))
    prob_under = 1 - prob_over
    
    ev_over = (prob_over * odds_multiplier) - 1
    return {
        "prob_over": round(prob_over, 3), 
        "prob_under": round(prob_under, 3),
        "ev_over": round(ev_over, 3)
    }

if __name__ == "__main__":
    print("Running Dabble MLB Strikeout Optimizer...")
    # Example: Cristopher Sánchez 7.5 K's line test
    result = calculate_ev(line=7.5, projection=6.8, odds_multiplier=1.1)
    print("Analysis Result:", result)
