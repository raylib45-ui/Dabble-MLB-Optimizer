import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict
import streamlit as st

# ==========================================
# 1. CORE DATA STRUCTURES & CONFIGURATION
# ==========================================

@dataclass
class PitcherProfile:
    name: str
    base_k_pct: float          # Strikeout rate per batter faced (K%)
    sw_str_pct: float          # Swinging-strike rate
    called_str_pct: float      # Called strike percentage
    projected_innings: float   # Expected workload

@dataclass
class LineupContext:
    team_name: str
    k_pct_vs_handedness: float # Opponent team K% vs pitcher hand
    lineup_missing_power: bool # Late scratch or missing high-K hitters
    weather_wind_outward: bool # Environmental factor affecting pitcher/hitter approach

@dataclass
class SimulationResult:
    expected_value: float
    probability_distribution: Dict[str, float]
    prob_over_line: float
    prob_under_line: float
    implied_over_odds: str
    implied_under_odds: str
    recommendation: str


# ==========================================
# 2. THE ATSWINS STRIKEBAIT PROJECTION ENGINE
# ==========================================

class ATSWinsStrikeoutEngine:
    def __init__(self, simulations: int = 5000):
        self.simulations = simulations

    def compute_core_ability(self, pitcher: PitcherProfile, lineup: LineupContext) -> float:
        skill_score = (pitcher.base_k_pct * 0.5) + (pitcher.sw_str_pct * 0.3) + (pitcher.called_str_pct * 0.2)
        opponent_adjustment = lineup.k_pct_vs_handedness - 0.220
        lineup_penalty = -0.02 if lineup.lineup_missing_power else 0.0
        weather_adjustment = -0.01 if lineup.weather_wind_outward else 0.0
        
        adjusted_k_rate = skill_score + opponent_adjustment + lineup_penalty + weather_adjustment
        return max(0.10, min(0.45, adjusted_k_rate))

    def run_simulation(self, pitcher: PitcherProfile, adjusted_k_rate: float) -> np.ndarray:
        expected_batters_faced = pitcher.projected_innings * 4.2
        simulated_batters = np.random.normal(loc=expected_batters_faced, scale=1.5, size=self.simulations)
        simulated_batters = np.clip(simulated_batters, 12, 35)
        strikeouts = np.random.binomial(n=simulated_batters.astype(int), p=adjusted_k_rate)
        return strikeouts

    def evaluate_prop(self, pitcher: PitcherProfile, lineup: LineupContext, market_line: float) -> SimulationResult:
        adjusted_k_rate = self.compute_core_ability(pitcher, lineup)
        strikeout_samples = self.run_simulation(pitcher, adjusted_k_rate)
        
        ev = float(np.mean(strikeout_samples))
        n_total = float(len(strikeout_samples))
        
        distribution = {
            "4 or fewer": round(np.sum(strikeout_samples <= 4) / n_total * 100, 1),
            "5": round(np.sum(strikeout_samples == 5) / n_total * 100, 1),
            "6": round(np.sum(strikeout_samples == 6) / n_total * 100, 1),
            "7": round(np.sum(strikeout_samples == 7) / n_total * 100, 1),
            "8+": round(np.sum(strikeout_samples >= 8) / n_total * 100, 1)
        }
        
        line_threshold = int(np.floor(market_line)) + 1
        prob_over = np.sum(strikeout_samples >= line_threshold) / n_total
        prob_under = 1.0 - prob_over
        
        fair_over_odds = self._probability_to_american_odds(prob_over)
        fair_under_odds = self._probability_to_american_odds(prob_under)
        
        # Strict Threshold Rule (>56% probability required for locks)
        if prob_over >= 0.56:
            rec = "🔒 MORE (Over)"
        elif prob_under >= 0.56:
            rec = "🔒 LESS (Under)"
        else:
            rec = "⚠️ PASS"
        
        return SimulationResult(
            expected_value=round(ev, 2),
            probability_distribution=distribution,
            prob_over_line=round(prob_over * 100, 1),
            prob_under_line=round(prob_under * 100, 1),
            implied_over_odds=fair_over_odds,
            implied_under_odds=fair_under_odds,
            recommendation=rec
        )

    @staticmethod
    def _probability_to_american_odds(prob: float) -> str:
        if prob <= 0 or prob >= 1:
            return "N/A"
        if prob > 0.5:
            odds = -int((prob / (1 - prob)) * 100)
            return str(odds)
        else:
            odds = int(((1 - prob) / prob) * 100)
            return f"+{odds}"


# ==========================================
# 3. STREAMLIT UI DASHBOARD
# ==========================================

st.set_page_config(page_title="ATSwins MLB Strikeout Model", layout="wide")

st.title("🎯 ATSwins MLB Strikeout Projection Dashboard")
st.markdown("Simulating pitcher outcome distributions and automatically evaluating **More / Less / Pass** signals.")

engine = ATSWinsStrikeoutEngine()

slate_data = [
    {"name": "Ian Seymour (P)", "line": 6.5, "k_pct": 0.28, "sw_str": 0.14, "called": 0.18, "ip": 6.0, "opp_k": 0.24},
    {"name": "Payton Tolle (P)", "line": 6.5, "k_pct": 0.27, "sw_str": 0.13, "called": 0.17, "ip": 5.8, "opp_k": 0.22},
    {"name": "Jacob deGrom (P)", "line": 6.5, "k_pct": 0.31, "sw_str": 0.16, "called": 0.19, "ip": 6.2, "opp_k": 0.25},
    {"name": "Michael King (P)", "line": 5.5, "k_pct": 0.26, "sw_str": 0.12, "called": 0.17, "ip": 5.5, "opp_k": 0.21},
    {"name": "Kyle Harrison (P)", "line": 5.5, "k_pct": 0.25, "sw_str": 0.13, "called": 0.16, "ip": 5.2, "opp_k": 0.23},
    {"name": "Taj Bradley (P)", "line": 5.5, "k_pct": 0.27, "sw_str": 0.14, "called": 0.17, "ip": 5.5, "opp_k": 0.24},
    {"name": "Gage Jump (P)", "line": 5.5, "k_pct": 0.24, "sw_str": 0.11, "called": 0.15, "ip": 5.0, "opp_k": 0.20},
    {"name": "Peter Lambert (P)", "line": 5.5, "k_pct": 0.21, "sw_str": 0.10, "called": 0.15, "ip": 5.0, "opp_k": 0.19},
    {"name": "Walbert Urena (P)", "line": 5.5, "k_pct": 0.22, "sw_str": 0.10, "called": 0.16, "ip": 5.0, "opp_k": 0.20},
    {"name": "Brady Singer (P)", "line": 4.5, "k_pct": 0.22, "sw_str": 0.11, "called": 0.16, "ip": 5.5, "opp_k": 0.21},
    {"name": "George Kirby (P)", "line": 4.5, "k_pct": 0.23, "sw_str": 0.12, "called": 0.18, "ip": 6.0, "opp_k": 0.20},
    {"name": "Clay Holmes (P)", "line": 4.5, "k_pct": 0.22, "sw_str": 0.11, "called": 0.15, "ip": 4.8, "opp_k": 0.22},
    {"name": "Anthony Kay (P)", "line": 4.5, "k_pct": 0.21, "sw_str": 0.10, "called": 0.14, "ip": 4.5, "opp_k": 0.21},
    {"name": "Tanner Gordon (P)", "line": 4.5, "k_pct": 0.20, "sw_str": 0.09, "called": 0.14, "ip": 4.5, "opp_k": 0.20},
    {"name": "Elmer Rodriguez-Cruz (P)", "line": 4.5, "k_pct": 0.21, "sw_str": 0.10, "called": 0.15, "ip": 4.5, "opp_k": 0.21},
    {"name": "Aaron Nola (P)", "line": 4.5, "k_pct": 0.27, "sw_str": 0.13, "called": 0.17, "ip": 6.0, "opp_k": 0.23},
    {"name": "Robert Stock (P)", "line": 3.5, "k_pct": 0.20, "sw_str": 0.09, "called": 0.14, "ip": 4.2, "opp_k": 0.19},
    {"name": "Will Dion (P)", "line": 3.5, "k_pct": 0.19, "sw_str": 0.08, "called": 0.13, "ip": 4.0, "opp_k": 0.18},
    {"name": "Jackson Jobe (P)", "line": 3.5, "k_pct": 0.23, "sw_str": 0.11, "called": 0.15, "ip": 4.5, "opp_k": 0.21}
]

st.sidebar.header("⚙️ Model Controls")
selected_pitcher_name = st.sidebar.selectbox("Select Pitcher to Inspect", [p["name"] for p in slate_data])

selected_data = next(p for p in slate_data if p["name"] == selected_pitcher_name)

st.sidebar.subheader("Adjust Pitcher Metrics")
custom_line = st.sidebar.number_input("Market Line", value=float(selected_data["line"]), step=0.5)
custom_ip = st.sidebar.number_input("Projected Innings", value=float(selected_data["ip"]), step=0.1)
custom_k_pct = st.sidebar.slider("Base K%", min_value=0.10, max_value=0.45, value=float(selected_data["k_pct"]), step=0.01)
custom_sw_str = st.sidebar.slider("Swinging Strike %", min_value=0.05, max_value=0.25, value=float(selected_data["sw_str"]), step=0.01)

missing_power = st.sidebar.checkbox("Opponent Missing Power Hitter?", value=False)
wind_outward = st.sidebar.checkbox("Wind Blowing Out?", value=False)

pitcher_obj = PitcherProfile(
    name=selected_data["name"],
    base_k_pct=custom_k_pct,
    sw_str_pct=custom_sw_str,
    called_str_pct=selected_data["called"],
    projected_innings=custom_ip
)
lineup_obj = LineupContext(
    team_name="Opponent",
    k_pct_vs_handedness=selected_data["opp_k"],
    lineup_missing_power=missing_power,
    weather_wind_outward=wind_outward
)

sim_result = engine.evaluate_prop(pitcher_obj, lineup_obj, custom_line)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Model EV", f"{sim_result.expected_value} K's")
col2.metric("Market Line", f"{custom_line}")
col3.metric("Over Prob", f"{sim_result.prob_over_line}%")
col4.metric("Under Prob", f"{sim_result.prob_under_line}%")
col5.metric("Model Signal", f"{sim_result.recommendation}")

st.markdown("---")
st.subheader(f"📊 Outcome Distribution for {selected_pitcher_name}")
dist_df = pd.DataFrame(list(sim_result.probability_distribution.items()), columns=["Strikeouts", "Probability (%)"])
st.bar_chart(dist_df.set_index("Strikeouts"))

st.markdown("---")
st.subheader("📋 Full Slate Automatic Signals & Recommendations")

results_list = []
for item in slate_data:
    p = PitcherProfile(item["name"], item["k_pct"], item["sw_str"], item["called"], item["ip"])
    l = LineupContext("Opp", item["opp_k"], False, False)
    res = engine.evaluate_prop(p, l, item["line"])
    results_list.append({
        "Pitcher": item["name"],
        "Line": item["line"],
        "Model EV": res.expected_value,
        "Over %": res.prob_over_line,
        "Under %": res.prob_under_line,
        "Signal": res.recommendation
    })

st.dataframe(pd.DataFrame(results_list), use_container_width=True)
