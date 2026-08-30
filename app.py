import streamlit as st

st.set_page_config(page_title="Dabble MLB Optimizer", page_icon="⚾", layout="centered")

st.title("⚾ Dabble MLB Optimizer")

p_name = st.text_input("Enter Pitcher Name Here", value="Pitcher Name", key="unique_pitcher_name_input")
d_line = st.number_input("Select Strikeout Line", value=5.5, step=0.5, key="unique_strikeout_line_input")
game_logs = st.text_input("Enter Last 5 Game Logs", value="5, 6, 4, 5, 7", key="unique_game_logs_input")

st.markdown("---")
st.markdown("**Recalibration Sliders**")
col1, col2 = st.columns(2)
with col1:
    opp_factor = st.slider("Opponent K Factor", 0.7, 1.3, 1.0, 0.05, key="unique_opp_factor_slider")
with col2:
    work_factor = st.slider("Workload Factor", 0.7, 1.3, 1.0, 0.05, key="unique_work_factor_slider")

if st.button("Calculate EV Now", key="unique_calculate_ev_button"):
    try:
        games = [float(x.strip()) for x in game_logs.split(",")]
        if games:
            weights = [0.10, 0.15, 0.20, 0.25, 0.30]
            if len(weights) != len(games):
                weights = [1.0 / len(games)] * len(games)
            weighted_avg = sum(g * w for g, w in zip(games, weights)) / sum(weights)
            proj = weighted_avg * opp_factor * work_factor
            diff = proj - d_line
            over_p = max(0.01, min(0.99, 0.50 + (diff * 0.15)))
            under_p = 1.0 - over_p
            
            st.subheader(f"Results for {p_name}")
            st.write(f"**Projection:** {proj:.2f} Ks")
            st.write(f"**Over Probability:** {over_p * 100:.1f}%")
            st.write(f"**Under Probability:** {under_p * 100:.1f}%")
            
            if over_p > 0.55:
                st.success("Recommendation: Take MORE 🔒")
            elif under_p > 0.55:
                st.success("Recommendation: Take LESS 🔒")
            else:
                st.warning("Recommendation: Pass (Coin Flip)")
        else:
            st.error("Enter valid logs.")
    except Exception as e:
        st.error(f"Error: {e}")
https://snappy-api-tjfdt5qepa-uc.a.run.app/c/x0tAQkpKczGNXpmH
