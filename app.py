"""
MLB Pitcher K Model - Streamlit - NO SCIPY VERSION
Fixes ModuleNotFoundError: scipy.stats import beta, truncnorm
Uses only numpy + pandas - works on Streamlit Cloud
"""
import streamlit as st
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List

st.set_page_config(page_title="MLB K Model - ATS WINS Logic", layout="wide")

@dataclass
class Pitcher:
    name: str; team: str; opp: str; throws: str; line: float; l5: List[int]
    k_pct: float; swstr: float; putaway: float; velo: float; arsenal_k: float
    avg_ip: float; grade: str; less_x: float = 1.0; more_x: float = 1.0

@dataclass
class GameContext:
    park: str; park_k: float = 1.0; wind_mph: int = 5; wind_dir: str = "neutral"
    ump_boost: float = 0.0; opp_strength: float = 1.0; pen_fatigue: float = 1.0

class KModel:
    def __init__(self): self.bpi =