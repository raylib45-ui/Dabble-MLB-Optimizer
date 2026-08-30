import streamlit as st
import pandas as pd

st.set_page_config(page_title="Rick Sanchez MLB K Model - Full Slate", page_icon="⚾", layout="wide")

st.markdown("<h1 style='text-align: center; color: #00ffcc;'>Rick Sanchez Advanced MLB K Model — Full Slate</h1>", unsafe_allow_html=True)

# Complete dataset of all pitchers from today's Dabble slate screenshots
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
    "Mason Adams": {"line": 3.5, "logs": [5, 5, 5, 5, 5], "matchup": "COL @ ATL"},
    "Seth Lugo": {"line": 3.5, "logs": [3, 5, 4, 3, 5], "matchup": "KC @ CLE"},
    "Ethan Pecko": {"line": 3.5, "logs": [4, 1, 3, 3, 3], "matchup": "HOU @ NYM"},
    "Zach Thornton": {"line": 3.5, "logs": [2, 3, 2, 7, 4], "matchup": "HOU @ NYM"},
    "Janson Junk": {"line": 2.5, "logs": [1, 2, 2, 2, 0], "matchup": "MIA @ WSH"},
    "Jordan Hicks": {"line": 1.5, "logs": [0, 3, 2, 2, 2], "matchup": "CWS @ MIN"}
}

# Build summary dataframe for all pitchers
rows = []
for name, data in pitchers_data.items():
    l5_avg = sum(data["logs"]) / len(data["logs"])
    diff = l5_avg - data["line"]
    if diff > 0.3:
        rec = "MORE (Over) 🔒"
    elif diff < -0.3:
        rec = "LESS (Under) 🔒"
    else:
        rec = "Pass"
    
    rows.append({
        "Pitcher": name,
        "Matchup": data["matchup"],
        "Line": data["line"],
        "L5 Avg": round(l5_avg, 2),
        "Edge": round(diff, 2),
        "Recommendation": rec
    })

df_slate = pd.DataFrame(rows)

st.markdown("### 📋 Complete Today's Slate Overview")
st.dataframe(df_slate, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown("### 🔍 Deep Dive Individual Pitcher")
selected_pitcher = st.selectbox("Select a pitcher to view detailed trend chart:", list(pitchers_data.keys()))
p_info = pitchers_data[selected_pitcher]
logs = p_info["logs"]
l5_avg = sum(logs) / len(logs)
dabble_line = p_info["line"]

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"**Matchup:** {selected_pitcher} ({p_info['matchup']})")
    st.markdown(f"**Model Projection:** `{l5_avg:.2f}K` vs Line `{dabble_line}`")
    st.bar_chart(logs)

with col2:
    st.markdown("**Quick Metrics**")
    st.metric(label="Dabble Line", value=dabble_line)
    st.metric(label="L5 Average", value=f"{l5_avg:.2f} Ks")
    diff = l5_avg - dabble_line
    if diff > 0.3:
        st.success("Recommendation: Take MORE (Over) 🔒")
    elif diff < -0.3:
        st.success("Recommendation: Take LESS (Under) 🔒")
    else:
        st.warning("Recommendation: Pass")
