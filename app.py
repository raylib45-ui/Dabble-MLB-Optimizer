import streamlit as st
import numpy as np
import pandas as pd
import requests
from dataclasses import dataclass
from typing import List

st.set_page_config(page_title="MLB K Model - Live", layout="wide")

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

class KModel:
    def __init__(self):
        self.bpi = 4.32
    def true_talent(self, p):
        base = p.k_pct * 0.75
        sw_adj = (p.swstr - 0.11) * 0.6
        put_adj = (p.putaway - 0.20) * 0.15
        ars_adj = (p.arsenal_k - 0.20) * 0.25
        velo_adj = (p.velo - 93.0) * 0.004
        recent = float(np.mean(p.l5)) / (p.avg_ip * self.bpi)
        return float(np.clip(base+sw_adj+put_adj+ars_adj+velo_adj*0.8+recent*0.2,0.14,0.33))
    def workload(self, p, ctx, n=6000):
        std = {"A+":0.4,"A":0.6,"B+":0.8,"B":0.9,"C":1.3,"D":1.6}.get(p.grade,0.9)
        ip = np.clip(np.random.normal(p.avg_ip,std,size=n),0.5,9.0)
        ip[np.random.rand(n)<0.05] *= np.random.uniform(0.4,0.75,size=(np.random.rand(n)<0.05).sum())
        return ip
    def project(self, p, opp_k, ctx, n=6000):
        adj = float(np.clip(self.true_talent(p)*(opp_k/0.22)*ctx.park_k,0.10,0.38))
        ip = self.workload(p,ctx,n)
        bf = np.clip(ip*4.32*np.random.normal(1,0.07,n),12,36)
        conc = {"A+":180,"A":120,"B+":80,"B":60,"C":30,"D":15}.get(p.grade,60)
        k_sims = []
        for b in bf:
            ps = np.random.beta(max(adj*conc,1),max((1-adj)*conc,1),size=int(round(float(b))))
            k_sims.append(np.random.binomial(1,ps).sum())
        k_sims = np.array(k_sims)
        return {"mean":float(k_sims.mean()),"sims":k_sims,"exp_ip":float(ip.mean())}
    @staticmethod
    def p_over(sims,line):
        return float((sims>line).mean())
    @staticmethod
    def amer(p):
        if p<=0.01: return 9900
        if p>=0.99: return -9900
        return int(-(p*100)/(1-p)) if p>=0.5 else int((1-p)*100/p)

BASE_SLATE = [
    Pitcher("Ian Seymour","TB","NYM","L",6.5,[9,7,9,8,5],0.28,0.13,0.26,93.5,0.23,5.2,"B",0.7,1.1),
    Pitcher("Payton Tolle","SEA","BOS","L",6.5,[7,14,4,6,7],0.29,0.14,0.27,94.8,0.24,5.3,"B+",1.2,0.7),
    Pitcher("Jacob deGrom","TEX","ATH","R",6.5,[3,9,3,10,2],0.33,0.15,0.31,97.2,0.28,6.0,"A+",1.0,1.0),
    Pitcher("Michael King","SD","CIN","R",5.5,[5,6,4,4,7],0.27,0.13,0.26,93.8,0.24,5.4,"B",1.1,0.9),
    Pitcher("Kyle Harrison","MIL","CHC","L",5.5,[2,10,8,8,5],0.25,0.125,0.24,93.0,0.22,5.1,"C",0.9,1.1),
    Pitcher("Taj Bradley","DET","MIN","R",5.5,[2,7,3,7,11],0.26,0.13,0.25,95.1,0.23,5.2,"B",1.1,0.9),
    Pitcher("Gage Jump","ATH","TEX","L",5.5,[5,11,1,3,9],0.26,0.12,0.23,92.2,0.21,4.8,"C",1.0,1.0),
    Pitcher("Peter Lambert","CWS","HOU","R",5.5,[8,3,6,3,5],0.20,0.105,0.20,93.1,0.19,5.0,"C",0.9,1.1),
    Pitcher("Walbert Urena","NYY","LAA","R",5.5,[7,2,5,7,3],0.24,0.115,0.22,94.0,0.21,4.9,"C",1.0,1.1),
    Pitcher("Brady Singer","SD","CIN","R",4.5,[6,3,4,3,5],0.21,0.105,0.20,92.5,0.19,5.5,"B",0.9,1.1),
    Pitcher("George Kirby","SEA","BOS","R",4.5,[8,3,2,3,9],0.22,0.10,0.21,95.5,0.20,6.2,"A",1.0,1.0),
    Pitcher("Will Dion","MIA","WSH","L",4.5,[1,7,1,4,3],0.19,0.095,0.18,90.2,0.18,4.7,"C",0.7,1.2),
    Pitcher("Clay Holmes","MIL","CHC","R",4.5,[8,1,3,1,5],0.23,0.11,0.22,95.8,0.21,4.5,"B",0.7,1.2),
    Pitcher("Anthony Kay","CWS","HOU","L",4.5,[3,4,4,6,4],0.20,0.10,0.19,92.0,0.18,4.8,"C",0.7,1.1),
    Pitcher("Tanner Gordon","BAL","COL","R",4.5,[3,2,4,2,6],0.18,0.09,0.17,92.3,0.17,5.0,"C",1.0,1.0),
    Pitcher("Elmer Rodriguez-Cruz","NYY","LAA","R",4.5,[3,2,1,4,6],0.23,0.11,0.20,93.4,0.20,4.6,"C",0.7,1.1),
    Pitcher("Aaron Nola","PHI","AZ","R",4.5,[5,9,9,8,7],0.23,0.11,0.22,92.8,0.21,5.8,"B",1.1,0.9),
    Pitcher("Robert Stock","NYM","TB","R",3.5,[4,4,5,6,2],0.19,0.095,0.18,94.5,0.18,4.2,"C",0.7,1.2),
    Pitcher("Jackson Jobe","DET","MIN","R",3.5,[4,9,4,7,4],0.26,0.125,0.24,96.2,0.22,4.7,"B+",1.0,1.0),
]

TEAM_K = {"NYM":0.225,"TB":0.25,"SEA":0.255,"BOS":0.23,"ATH":0.26,"TEX":0.24,"SD":0.21,"CIN":0.24,"MIL":0.24,"CHC":0.25,"DET":0.26,"MIN":0.27,"CWS":0.28,"HOU":0.215,"NYY":0.23,"LAA":0.26,"MIA":0.26,"WSH":0.235,"BAL":0.23,"COL":0.26,"PHI":0.22,"AZ":0.22}
PARK_K = {"COL":0.88,"CIN":0.98,"BOS":0.99,"TEX":1.02,"CHC":1.01,"MIN":1.03,"HOU":0.97,"LAA":0.99,"WSH":1.01,"AZ":1.04,"TB":1.03}

@st.cache_data(ttl=3600)
def fetch_live(year=2025):
    try:
        url = f"https://www.fangraphs.com/api/leaders/major-league/data?age=&pos=all&stats=pit&lg=all&qual=0&season={year}&season1={year}&startdate={year}-03-01&enddate={year}-11-01&month=0&hand=&team=0&pageitems=2000000000&pagenum=1"
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=20)
        df = pd.DataFrame(r.json().get("data", []))
        return df
    except:
        return pd.DataFrame()

st.title("MLB Pitcher K Model - Live Statcast")
st.caption("Live Fangraphs API - No pybaseball needed")

use_live = st.checkbox("Use Live Statcast (auto-update K%, SwStr%, velo)", value=True)
year = st.selectbox("Season", [2025,2026,2024], index=0)

slate = BASE_SLATE
if use_live:
    with st.spinner(f"Pulling live Fangraphs {year}..."):
        live_df = fetch_live(year)
        if not live_df.empty:
            st.success(f"Live pulled {len(live_df)} pitchers")
            name_col = "PlayerName" if "PlayerName" in live_df.columns else "Name"
            if name_col in live_df.columns:
                live_df["Name_lower"] = live_df[name_col].astype(str).str.lower()
                for i, p in enumerate(slate):
                    m = live_df[live_df["Name_lower"].str.contains(p.name.split()[-1].lower(), na=False)]
                    if not m.empty:
                        row = m.iloc[0]
                        try:
                            k = row.get("K%")
                            if isinstance(k, str): k = float(k.replace("%",""))/100
                            else: k = float(k)/100 if float(k)>1 else float(k)
                            slate[i].k_pct = float(np.clip(k,0.12,0.40))
                        except: pass
        else:
            st.warning("Live fetch blocked, using estimates")

if st.button("Run Full Slate (19 pitchers)"):
    model = KModel()
    rows = []
    for p in slate:
        ctx = GameContext(p.opp, PARK_K.get(p.opp,1.0))
        proj = model.project(p, TEAM_K.get(p.opp,0.23), ctx)
        pover = model.p_over(proj["sims"], p.line)
        rows.append({
            "Pitcher": p.name,
            "Line": p.line,
            "Live K%": f"{p.k_pct*100:.1f}%",
            "Model": round(proj["mean"],2),
            "Exp IP": round(proj["exp_ip"],1),
            "P OVER": f"{pover*100:.1f}%",
            "Fair OVER": model.amer(pover),
            "Lean": f"{'MORE' if pover>0.55 else 'LESS' if pover<0.45 else 'PASS'} {p.line}"
        })
    df = pd.DataFrame(rows).sort_values("Model", ascending=False)
    st.dataframe(df, use_container_width=True)