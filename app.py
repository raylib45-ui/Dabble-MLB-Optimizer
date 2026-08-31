import streamlit as st
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List

st.set_page_config(page_title="MLB K Model - ATS WINS Logic", layout="wide")

@dataclass
class Pitcher:
    name: str
    team: str
    opp: str
    throws: str
    line: float
    l5: List[int]
    k_pct: float
    swstr: float
    putaway: float
    velo: float
    arsenal_k: float
    avg_ip: float
    grade: str
    less_x: float = 1.0
    more_x: float = 1.0

@dataclass
class GameContext:
    park: str
    park_k: float = 1.0
    wind_mph: int = 5
    wind_dir: str = "neutral"
    ump_boost: float = 0.0
    opp_strength: float = 1.0
    pen_fatigue: float = 1.0

class KModel:
    def __init__(self):
        self.bpi = 4.32

    def true_talent(self, p):
        base = p.k_pct * 0.75
        sw_adj = (p.swstr - 0.11) * 0.6
        put_adj = (p.putaway - 0.20) * 0.15
        ars_adj = (p.arsenal_k - 0.20) * 0.25
        velo_adj = (p.velo - 93.0) * 0.004
        recent = float(np.mean(p.l5)) / (p.avg_ip * self.bpi) if p.avg_ip else 0.22
        talent = base + sw_adj + put_adj + ars_adj + velo_adj
        blended = talent * 0.80 + recent * 0.20
        return float(np.clip(blended, 0.14, 0.33))

    def workload(self, p, ctx, n=10000):
        exp_ip = p.avg_ip * ctx.pen_fatigue
        std_map = {"A+": 0.4, "A": 0.6, "B+": 0.8, "B": 0.9, "C": 1.3, "D": 1.6}
        std = std_map.get(p.grade, 0.9)
        ip = np.random.normal(exp_ip, std, size=n)
        ip = np.clip(ip, 0.5, 9.0)
        early = np.random.rand(n) < 0.05
        ip[early] = ip[early] * np.random.uniform(0.4, 0.75, size=early.sum())
        return ip

    def context_mult(self, ctx):
        m = ctx.park_k * ctx.opp_strength + ctx.ump_boost
        if ctx.wind_dir == "in" and ctx.wind_mph > 8:
            m = m * 1.03
        if ctx.wind_dir == "out" and ctx.wind_mph > 10:
            m = m * 0.97
        return float(np.clip(m, 0.85, 1.15))

    def project(self, p, opp_k_avg, ctx, n=8000):
        adj = self.true_talent(p) * (opp_k_avg / 0.22) * self.context_mult(ctx)
        adj = float(np.clip(adj, 0.10, 0.38))
        ip_sims = self.workload(p, ctx, n)
        bf_sims = ip_sims * self.bpi * np.random.normal(1, 0.07, n)
        bf_sims = np.clip(bf_sims, 12, 36)
        conc_map = {"A+": 180, "A": 120, "B+": 80, "B": 60, "C": 30, "D": 15}
        conc = conc_map.get(p.grade, 60)
        alpha = max(adj * conc, 1.0)
        beta_p = max((1 - adj) * conc, 1.0)
        k_sims = []
        for bf in bf_sims:
            size = int(round(float(bf)))
            ps = np.random.beta(alpha, beta_p, size=size)
            k_sims.append(np.random.binomial(1, ps).sum())
        k_sims = np.array(k_sims)
        mean_k = float(k_sims.mean())
        exact = round(mean_k + float(np.random.normal(0, 0.05)), 3)
        dist = {}
        for i in range(16):
            dist[i] = float((k_sims == i).mean())
        return {"mean": mean_k, "exact": exact, "exp_ip": float(ip_sims.mean()), "sims": k_sims, "dist": dist, "adj_k": adj}

    @staticmethod
    def p_over(sims, line):
        return float((sims > line).mean())

    @staticmethod
    def amer(p):
        if p <= 0.01: return 9900
        if p >= 0.99: return -9900
        if p >= 0.5: return int(-(p * 100) / (1 - p))
        else: return int((1 - p) * 100 / p)

SLATE = [
    Pitcher("Ian Seymour", "TB", "NYM", "L", 6.5, [9,7,9,8,5], 0.28, 0.13, 0.26, 93.5, 0.23, 5.2, "B", 0.7, 1.1),
    Pitcher("Payton Tolle", "SEA", "BOS", "L", 6.5, [7,14,4,6,7], 0.29, 0.14, 0.27, 94.8, 0.24, 5.3, "B+", 1.2, 0.7),
    Pitcher("Jacob deGrom", "TEX", "ATH", "R", 6.5, [3,9,3,10,2], 0.33, 0.15, 0.31, 97.2, 0.28, 6.0, "A+", 1.0, 1.0),
    Pitcher("Michael King", "SD", "CIN", "R", 5.5, [5,6,4,4,7], 0.27, 0.13, 0.26, 93.8, 0.24, 5.4, "B", 1.1, 0.9),
    Pitcher("Kyle Harrison", "MIL", "CHC", "L", 5.5, [2,10,8,8,5], 0.25, 0.125, 0.24, 93.0, 0.22, 5.1, "C", 0.9, 1.1),
    Pitcher("Taj Bradley", "DET", "MIN", "R", 5.5, [2,7,3,7,11], 0.26, 0.13, 0.25, 95.1, 0.23, 5.2, "B", 1.1, 0.9),
    Pitcher("Gage Jump", "ATH", "TEX", "L", 5.5, [5,11,1,3,9], 0.26, 0.12, 0.23, 92.2, 0.21, 4.8, "C", 1.0, 1.0),
    Pitcher("Peter Lambert", "CWS", "HOU", "R", 5.5, [8,3,6,3,5], 0.20, 0.105, 0.20, 93.1, 0.19, 5.0, "C", 0.9, 1.1),
    Pitcher("Walbert Urena", "NYY", "LAA", "R", 5.5, [7,2,5,7,3], 0.24, 0.115, 0.22, 94.0, 0.21, 4.9, "C", 1.0, 1.1),
    Pitcher("Brady Singer", "SD", "CIN", "R", 4.5, [6,3,4,3,5], 0.21, 0.105, 0.20, 92.5, 0.19, 5.5, "B", 0.9, 1.1),
    Pitcher("George Kirby", "SEA", "BOS", "R", 4.5, [8,3,2,3,9], 0.22, 0.10, 0.21, 95.5, 0.20, 6.2, "A", 1.0, 1.0),
    Pitcher("Will Dion", "MIA", "WSH", "L", 4.5, [1,7,1,4,3], 0.19, 0.095, 0.18, 90.2, 0.18, 4.7, "C", 0.7, 1.2),
    Pitcher("Clay Holmes", "MIL", "CHC", "R", 4.5, [8,1,3,1,5], 0.23, 0.11, 0.22, 95.8, 0.21, 4.5, "B", 0.7, 1.2),
    Pitcher("Anthony Kay", "CWS", "HOU", "L", 4.5, [3,4,4,6,4], 0.20, 0.10, 0.19, 92.0, 0.18, 4.8, "C", 0.7, 1.1),
    Pitcher("Tanner Gordon", "BAL", "COL", "R", 4.5, [3,2,4,2,6], 0.18, 0.09, 0.17, 92.3, 0.17, 5.0, "C", 1.0, 1.0),
    Pitcher("Elmer Rodriguez-Cruz", "NYY", "LAA", "R", 4.5, [3,2,1,4,6], 0.23, 0.11, 0.20, 93.4, 0.20, 4.6, "C", 0.7, 1.1),
    Pitcher("Aaron Nola", "PHI", "AZ", "R", 4.5, [5,9,9,8,7], 0.23, 0.11, 0.22, 92.8, 0.21, 5.8, "B", 1.1, 0.9),
    Pitcher("Robert Stock", "NYM", "TB", "R", 3.5, [4,4,5,6,2], 0.19, 0.095, 0.18, 94.5, 0.18, 4.2, "C", 0.7, 1.2),
    Pitcher("Jackson Jobe", "DET", "MIN", "R", 3.5, [4,9,4,7,4], 0.26, 0.125, 0.24, 96.2, 0.22, 4.7, "B+", 1.0, 1.0),
]

TEAM_K = {"NYM":0.225,"TB":0.25,"SEA":0.255,"BOS":0.23,"ATH":0.26,"TEX":0.24,"SD":0.21,"CIN":0.24,"MIL":0.24,"CHC":0.25,"DET":0.26,"MIN":0.27,"CWS":0.28,"HOU":0.215,"NYY":0.23,"LAA":0.26,"MIA":0.26,"WSH":0.235,"BAL":0.23,"COL":0.26,"PHI":0.22,"AZ":0.22}
PARK_K = {"COL":0.88,"CIN":0.98,"BOS":0.99,"TEX":1.02,"CHC":1.01,"MIN":1.03,"HOU":0.97,"LAA":0.99,"WSH":1.01,"AZ":1.04,"TB":1.03}

def run_model():
    model = KModel()
    rows = []
    for p in SLATE:
        opp_k = TEAM_K.get(p.opp, 0.23)
        park_k = PARK_K.get(p.opp, 1.0)
        ctx = GameContext(p.opp, park_k)
        proj = model.project(p, opp_k, ctx, n=6000)
        pover = model.p_over(proj["sims"], p.line)
        punder = 1 - pover
        fair_over = model.amer(pover)
        fair_under = model.amer(punder)
        ev_more = pover * p.more_x - punder * 1
        ev_less = punder * p.less_x - pover * 1
        lean = "PASS"
        if ev_more > 0.08 and pover > 0.55:
            lean = f"MORE {p.line}"
        elif ev_less > 0.08 and punder > 0.55:
            lean = f"LESS {p.line}"
        elif ev_more > 0.03:
            lean = f"Lean MORE {p.line}"
        elif ev_less > 0.03:
            lean = f"Lean LESS {p.line}"
        l5_str = "+".join(map(str, p.l5))
        l5_avg = float(np.mean(p.l5))
        rows.append({
            "Pitcher": p.name, "Matchup": f"{p.team}@{p.opp}", "Line": p.line,
            "L5": f"{l5_str} ({l5_avg:.1f})", "Model": round(proj["mean"], 2),
            "Exact": proj["exact"], "Exp IP": round(proj["exp_ip"], 1),
            "P OVER": f"{pover*100:.1f}%", "Fair OVER": fair_over,
            "Dabble More": f"{p.more_x}x", "Dabble Less": f"{p.less_x}x",
            "EV More": round(ev_more, 3), "EV Less": round(ev_less, 3), "Lean": lean
        })
    df = pd.DataFrame(rows)
    df = df.sort_values("EV More", ascending=False)
    return df

st.title("MLB Pitcher K Model - ATS WINS Logic (Fixed)")
st.caption("No scipy - runs on Streamlit Cloud. Full 19 pitcher Dabble slate.")

if st.button("Run Full Slate (19 pitchers)"):
    with st.spinner("Simulating 6k sims per pitcher..."):
        df = run_model()
        st.dataframe(df, use_container_width=True)
else:
    st.info("Click Run to generate projections.")