import streamlit as st
import pandas as pd

st.set_page_config(page_title="Rick Sanchez MLB K Model - Full Slate", page_icon="⚾", layout="wide")

st.markdown("<h1 style='text-align: center; color: #00ffcc;'>Rick Sanchez Advanced MLB K Model — Full Slate</h1>", unsafe_allow_html=True)

# Comprehensive dataset of all pitchers from today's Dabble slate screenshots
pitchers_data = {
    "Paul Skenes": {"line": 6.5, "logs": [7, 6, 4, 5, 4], "matchup": "SF @ PIT"},
    "MacKenzie Gore": {"line": 6.5, "logs": [4, 9, 5, 7, 4], "matchup": "ATH @ TEX"},
    "Gerrit Cole": {"line": 6.5, "logs": [5, 9, 5, 8, 5], "matchup": "NYY @ LAA"},
    "Gavin Williams": {"line": 5.5, "logs": [10, 7, 5, 11, 3], "matchup": "TOR @ CLE"},
    "Bryan Woo": {"line": 5.5, "logs": [8, 5, 5, 5, 5], "matchup": "SEA @ BOS"},
    "Sean Burke": {"line": 5.5, "logs": [4, 8, 2, 4, 3], "matchup": "CWS @ HOU"},
    "Grayson Rodriguez": {"line": 5.5, "logs": [6, 8, 5, 6, 4], "matchup": "NYY @ LAA"},
    "Jesús Luzardo": {"line": 5.5, "logs": [7, 12, 9, 9, 9], "matchup": "PHI @ AZ"},
    "Freddy Peralta": {"line": 4.5, "logs": [3, 5, 2, 6, 4], "matchup": "NYM @ TB"},
    "Logan Webb": {"line": 4.5, "logs": [8, 2, 7, 2, 6], "matchup": "SF @ PIT"},
    "Nick Lodolo": {"line": 4.5, "logs": [4, 5, 2, 2, 5], "matchup": "SD @ CIN"},
    "Sean Manaea": {"line": 4.5, "logs": [7, 11, 7, 4, 3], "matchup": "NYM @ TB"},
    "AJ Smith-Shawver": {"line": 4.5, "logs": [1, 1, 4, 3, 3], "matchup": "ATL @ WSH"},
    "Jake Irvin": {"line": 4.5, "logs": [3, 4, 6, 4, 6], "matchup": "ATL @ WSH"},
    "Matthew Boyd": {"line": 4.5, "logs": [3, 3, 2, 3, 5], "matchup": "MIL @ CHC"},
    "Troy Melton": {"line": 4.5, "logs": [4, 5, 4, 3, 4], "matchup": "DET @ MIN"},
    "Ronel Blanco": {"line": 4.5, "logs": [8, 4, 4, 1, 3], "matchup": "CWS @ HOU"},
    "Kyle Bradish": {"line": 4.5, "logs": [3, 4, 3, 5, 4], "matchup": "BAL @ COL"},
    "Eduardo Rodriguez": {"line": 4.5, "logs": [4, 9, 5, 4, 9], "matchup": "PHI @ AZ"},
    "Randy Vásquez": {"line": 3.5, "logs": [1, 1, 5, 3, 2], "matchup": "SD @ CIN"},
    "Spencer Arrighetti": {"line": 3.5, "logs": [2, 6, 0, 4, 4], "matchup": "TOR @ CLE"},
    "Randy Dobnak": {"line": 3.5, "logs": [1, 4, 6, 4, 5], "matchup": "MIA @ KC"},
    "Robert Gasser": {"line": 3.5, "logs": [6, 3, 7, 4, 6], "matchup": "MIL @ CHC"},
    "Tyler Phillips": {"line": 3.5, "logs": [3, 4, 6, 3, 7], "matchup": "MIA @ KC"},
    "Gabriel Hughes": {"line": 3.5, "logs": [7, 3, 2, 2, 3], "matchup": "BAL @ COL"},
    "Eric Lauer": {"line": 3.5, "logs": [4, 1, 6, 6, 1], "matchup": "STL @ LAD"},
    "Michael McGreevy": {"line": 3.5, "logs": [5, 4, 6, 4, 3], "matchup": "STL @ LAD"},
    "Andrew Morris": {"line": 1.5, "logs": [1, 0, 0, 1, 2], "matchup": "DET @ MIN"},
    "Brady Basso": {"line": 0.5, "logs": [1, 0, 0, 2, 1], "matchup": "ATH @ TEX"}
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
