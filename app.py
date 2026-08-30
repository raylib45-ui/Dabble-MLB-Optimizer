import streamlit as st
import pandas as pd

st.set_page_config(page_title="Rick Sanchez MLB K Model - Today Slate", page_icon="⚾", layout="wide")

st.markdown("<h1 style='text-align: center; color: #00ffcc;'>Rick Sanchez Advanced MLB K Model (Today's Slate)</h1>", unsafe_allow_html=True)

# Complete dataset extracted from today's Dabble screenshots
pitchers_data = {
    "Chase Burns": {"line": 5.5, "logs": [9, 6, 8, 8, 5], "matchup": "CIN @ CHC"},
    "Shota Imanaga": {"line": 5.5, "logs": [6, 6, 5, 10, 4], "matchup": "CIN @ CHC"},
    "Andrew Alvarez": {"line": 4.5, "logs": [5, 2, 4, 5, 6], "matchup": "MIA @ WSH"},
    "Will Warren": {"line": 4.5, "logs": [7, 5, 3, 5, 4], "matchup": "BOS @ NYY"},
    "Max Scherzer": {"line": 4.5, "logs": [5, 4, 4, 1, 4], "matchup": "SEA @ TOR"},
    "Framber Valdez": {"line": 4.5, "logs": [6, 5, 3, 5, 0], "matchup": "LAD @ DET"},
    "Robbie Ray": {"line": 4.5, "logs": [6, 2, 4, 4, 5], "matchup": "SD @ TB"},
    "Dustin May": {"line": 4.5, "logs": [3, 5, 6, 1, 0], "matchup": "TEX @ MIL"},
    "Kumar Rocker": {"line": 4.5, "logs": [5, 5, 3, 3, 8], "matchup": "TEX @ MIL"},
    "Zebby Matthews": {"line": 4.5, "logs": [10, 4, 4, 4, 7], "matchup": "CWS @ MIN"},
    "Chris Bassitt": {"line": 4.5, "logs": [2, 1, 3, 6, 5], "matchup": "BAL @ ATH"},
    "Jeffrey Springs": {"line": 4.5, "logs": [2, 0, 2, 1, 3], "matchup": "BAL @ ATH"},
    "Mason Adams": {"line": 3.5, "logs": [5], "matchup": "COL @ ATL"},
    "Seth Lugo": {"line": 3.5, "logs": [3, 5, 4, 3, 5], "matchup": "KC @ CLE"},
    "Ethan Pecko": {"line": 3.5, "logs": [4, 1], "matchup": "HOU @ NYM"},
    "Zach Thornton": {"line": 3.5, "logs": [2, 3, 2, 7, 4], "matchup": "HOU @ NYM"},
    "Janson Junk": {"line": 2.5, "logs": [1, 2, 2, 2, 0], "matchup": "MIA @ WSH"},
    "Jordan Hicks": {"line": 1.5, "logs": [0, 3, 2, 2, 2], "matchup": "CWS @ MIN"}
}

selected_pitcher = st.sidebar.selectbox("Select Pitcher for Today's Slate", list(pitchers_data.keys()), key="slate_pitcher_select_v2")
p_info = pitchers_data[selected_pitcher]

dabble_line = st.sidebar.number_input("Dabble Strikeout Line", value=p_info["line"], step=0.5, key="slate_line_v2")
logs_str = st.sidebar.text_input("Last 5 Game Logs", ", ".join(map(str, p_info["logs"])), key="slate_logs_v2")

try:
    logs = [float(x.strip()) for x in logs_str.split(",")]
except:
    logs = p_info["logs"]

l5_avg = sum(logs) / len(logs) if logs else 0.0
diff = l5_avg - dabble_line

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"**Matchup: {selected_pitcher} ({p_info['matchup']})**")
    st.markdown(f"**Exact Model Projection:** `{l5_avg:.2f}K` vs Dabble Line `{dabble_line}`")
    
    st.markdown("**Last 5 Starts Trend**")
    st.bar_chart(logs)
    st.write(f"L5 Avg: `{l5_avg:.1f}` | Line: `{dabble_line}`")
    
    if diff > 0.3:
        st.success("Recommendation: Take MORE (Over) 🔒")
    elif diff < -0.3:
        st.success("Recommendation: Take LESS (Under) 🔒")
    else:
        st.warning("Recommendation: Pass (Close to line)")

with col2:
    st.markdown("**Slate Quick Stats & Breakdown**")
    st.metric(label="Dabble Strikeout Line", value=dabble_line)
    st.metric(label="Model L5 Average", value=f"{l5_avg:.2f} Ks")
    st.info("All active pitchers from today's slate are pre-loaded in the sidebar dropdown. Switch pitchers instantly to view projections and trend graphs.")
